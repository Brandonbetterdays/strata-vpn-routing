#!/usr/bin/env python3
"""Gate before publishing: the new geo files must be usable by clients.

usage: validate.py DIR PROFILE_JSON --xray XRAY_BIN [--template SUB.json ...] [--previous PREV_DIR]

1. Every geosite:/geoip: code used by the profile (and by each subscription template) exists
   in DIR/geosite.dat / DIR/geoip.dat — Xray refuses the whole config if one is missing
   ("failed to check code X from geosite.dat").
2. Each category the profile uses is not suspiciously small, and (with --previous) did not
   shrink by more than 30% against the last published files — protects against an upstream
   list coming back empty.
3. Real start-up test: `xray run -test` (Xray docs, document/command) on a config that uses all
   of the profile's codes in the profile's order (block -> proxy -> direct), and on each template,
   with XRAY_LOCATION_ASSET=DIR so Xray loads exactly these files.
Exit code 1 on any problem.
"""
import argparse, json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geodat import entries  # noqa: E402

MIN = {"geosite": {"STRATA-DIRECT": 1000, "STRATA-TUNNEL": 300, "STRATA-ADS": 100,
                   "STRATA-BLOCK": 100, "PRIVATE": 10},
       "geoip": {"DIRECT": 5000, "RU": 5000, "PRIVATE": 5}}
REF = re.compile(r"\b(geosite|geoip):([A-Za-z0-9!@._-]+)")

ap = argparse.ArgumentParser()
ap.add_argument("dir"); ap.add_argument("profile")
ap.add_argument("--xray", required=True)
ap.add_argument("--template", action="append", default=[])
ap.add_argument("--previous")
a = ap.parse_args()

have = {"geosite": entries(os.path.join(a.dir, "geosite.dat")),
        "geoip": entries(os.path.join(a.dir, "geoip.dat"))}
problems = []


def refs(obj):
    return {(k, c.split("@")[0].upper()) for k, c in REF.findall(json.dumps(obj))}


profile = json.load(open(a.profile, encoding="utf-8"))
used = refs({k: profile.get(k, []) for k in
             ("DirectSites", "DirectIp", "ProxySites", "ProxyIp", "BlockSites", "BlockIp")})
templates = [(t, json.load(open(t, encoding="utf-8"))) for t in a.template]
for name, obj in [("profile", profile)] + templates:
    for kind, code in sorted(refs(obj)):
        if code not in have[kind]:
            problems.append(f"{name}: {kind}:{code} is not in {kind}.dat")

for kind, mins in MIN.items():
    for code, m in mins.items():
        n = have[kind].get(code, 0)
        if (kind, code) in used or code in ("RU",):
            if n < m:
                problems.append(f"{kind}:{code} has {n} entries (< {m}) — upstream list empty?")
if a.previous:
    for kind in ("geosite", "geoip"):
        p = os.path.join(a.previous, f"{kind}.dat")
        if os.path.exists(p):
            old = entries(p)
            for code in {c for k, c in used if k == kind}:
                if old.get(code) and have[kind].get(code, 0) < 0.7 * old[code]:
                    problems.append(f"{kind}:{code} shrank {old[code]} -> {have[kind].get(code, 0)} (> 30%)")


def xray_test(cfg, label):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(cfg, f)
    r = subprocess.run([a.xray, "run", "-test", "-c", f.name], capture_output=True, text=True,
                       env={**os.environ, "XRAY_LOCATION_ASSET": os.path.abspath(a.dir)})
    out = (r.stdout + r.stderr).strip().splitlines()
    ok = r.returncode == 0 and any("Configuration OK" in l for l in out)
    print(f"xray -test [{label}]: {'OK' if ok else 'FAILED'}")
    if not ok:
        problems.append(f"xray -test [{label}]: " + " | ".join(out[-3:]))


def rule(key, values, tag):
    return [{key: values, "outboundTag": tag}] if values else []


order = {"block": ("BlockSites", "BlockIp", "BLOCK"), "proxy": ("ProxySites", "ProxyIp", "proxy"),
         "direct": ("DirectSites", "DirectIp", "DIRECT")}
rules = []
for step in profile.get("RouteOrder", "block-proxy-direct").split("-"):
    s, i, tag = order[step]
    rules += rule("domain", profile.get(s, []), tag) + rule("ip", profile.get(i, []), tag)
synthetic = {
    "log": {"loglevel": "warning"},
    "dns": {"servers": [{"address": "77.88.8.8", "domains": profile.get("DirectSites", []),
                         "skipFallback": True}, "8.8.8.8"]},
    "inbounds": [{"tag": "socks", "listen": "127.0.0.1", "port": 10808, "protocol": "socks"}],
    "outbounds": [{"tag": "proxy", "protocol": "freedom"}, {"tag": "DIRECT", "protocol": "freedom"},
                  {"tag": "BLOCK", "protocol": "blackhole"}],
    "routing": {"domainStrategy": profile.get("DomainStrategy", "IPIfNonMatch"), "rules": rules},
}
xray_test(synthetic, "profile")
for name, obj in templates:
    cfg = json.loads(json.dumps(obj))
    if not any(o.get("tag") == "proxy" for o in cfg.get("outbounds", [])):
        cfg.setdefault("outbounds", []).append({"tag": "proxy", "protocol": "freedom"})  # the panel adds it
    xray_test(cfg, os.path.basename(name))

for kind in ("geosite", "geoip"):
    print(kind, {c: have[kind][c] for c in sorted({c for k, c in used if k == kind} | set(MIN[kind])) if c in have[kind]})
if problems:
    print("VALIDATION FAILED:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("VALIDATION OK")
