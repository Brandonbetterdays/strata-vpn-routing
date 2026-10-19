#!/usr/bin/env bash
# Build geosite.dat and geoip.dat from this repo's sources + upstreams, into ./out
#
#   geosite: data/ (ours) + data/ of hydraponique/roscomvpn-geosite (MIT, fetched fresh),
#            compiled by v2fly/domain-list-community (MIT) — the official geosite builder.
#   geoip:   geoip/config.json, compiled by Loyalsoldier/geoip (its RU list: CC BY-SA 4.0).
#
# Needs: git, go (the builders' go.mod versions; GOTOOLCHAIN=auto downloads them).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$ROOT/.build}"
OUT="${OUT:-$ROOT/out}"
export GOTOOLCHAIN="${GOTOOLCHAIN:-auto}"

clone() {  # repo dir [sparse patterns...]
  local repo="$1" dir="$2"; shift 2
  rm -rf "$dir"
  if [ $# -gt 0 ]; then
    git clone -q --depth 1 --filter=blob:none --no-checkout "https://github.com/$repo.git" "$dir"
    git -C "$dir" sparse-checkout set --no-cone "$@"
    git -C "$dir" checkout -q
  else
    git clone -q --depth 1 "https://github.com/$repo.git" "$dir"
  fi
  echo "$repo @ $(git -C "$dir" rev-parse --short HEAD) $(git -C "$dir" log -1 --format=%cs)" | tee -a "$OUT/SOURCES.txt"
}

rm -rf "$OUT"; mkdir -p "$WORK" "$OUT"
: > "$OUT/SOURCES.txt"
echo "strata-vpn-routing @ $(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo local)" >> "$OUT/SOURCES.txt"

# ---------- geosite ----------
clone v2fly/domain-list-community "$WORK/community" '/*' '!/data/'
clone hydraponique/roscomvpn-geosite "$WORK/roscom" '/data/' '/LICENSE'
rm -rf "$WORK/community/data"; mkdir -p "$WORK/community/data"
cp -a "$WORK/roscom/data/." "$WORK/community/data/"
for f in "$ROOT"/data/*; do   # ours must not silently replace an upstream list
  n=$(basename "$f")
  [ -e "$WORK/community/data/$n" ] && { echo "name clash with upstream list: $n" >&2; exit 1; }
  cp "$f" "$WORK/community/data/$n"
done
(cd "$WORK/community" && go run ./ -datapath=./data -outputdir="$OUT" -outputname=geosite.dat \
   -exportlists=strata-direct,strata-tunnel,strata-ads,strata-block,private)
mkdir -p "$OUT/lists"; mv "$OUT"/*.txt "$OUT/lists/" 2>/dev/null || true
mv "$OUT/lists/SOURCES.txt" "$OUT/SOURCES.txt"

# ---------- geoip ----------
clone Loyalsoldier/geoip "$WORK/geoip"
cp "$ROOT"/geoip/config.json "$ROOT"/geoip/*.txt "$WORK/geoip/"
(cd "$WORK/geoip" && go run ./ convert -c config.json)
cp "$WORK/geoip/output/dat/geoip.dat" "$OUT/geoip.dat"

(cd "$OUT" && sha256sum geosite.dat geoip.dat > sha256sums.txt)
ls -la "$OUT"
