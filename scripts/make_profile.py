#!/usr/bin/env python3
"""Fill profile/strata.json and write the Happ / Incy routing profile + deep links.

usage: make_profile.py BASE_URL OUT_DIR [LAST_UPDATED]
  BASE_URL      where clients download geosite.dat / geoip.dat
  LAST_UPDATED  unix time; default = time of the last git commit that touched profile/strata.json
                (Happ re-applies a profile only when LastUpdated is higher than before)

Writes OUT_DIR/strata-profile.json, OUT_DIR/happ.txt, OUT_DIR/incy.txt.
Deep links: happ://routing/onadd/{base64} — per Happ's routing documentation;
the incy:// form is the same profile for Incy.
"""
import base64, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base, out = sys.argv[1].rstrip("/"), sys.argv[2]
if len(sys.argv) > 3:
    last = sys.argv[3]
else:
    last = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%ct", "--", "profile/strata.json"],
                          capture_output=True, text=True).stdout.strip() or "0"
tpl = open(os.path.join(ROOT, "profile", "strata.json"), encoding="utf-8").read()
profile = json.loads(tpl.replace("{BASE_URL}", base).replace("{LAST_UPDATED}", last))
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "strata-profile.json"), "w", encoding="utf-8") as f:
    json.dump(profile, f, ensure_ascii=False, indent=2)
b64 = base64.b64encode(json.dumps(profile, ensure_ascii=False, separators=(",", ":")).encode()).decode()
open(os.path.join(out, "happ.txt"), "w").write(f"happ://routing/onadd/{b64}\n")
open(os.path.join(out, "incy.txt"), "w").write(f"incy://routing/onadd/{b64}\n")
print(f"profile: LastUpdated={last}, geo files from {base}")
