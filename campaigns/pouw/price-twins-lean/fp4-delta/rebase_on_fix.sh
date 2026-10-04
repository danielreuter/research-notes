#!/usr/bin/env bash
# Rebuild and audit fp4-delta/ on a Pearl-C4 staging that carries the base-split fix (F1′ + F2), in a private copy.
#
#   rebase_on_fix.sh PRIVATE_COPY FIXED_STAGING_POUW AUDIT_OUT
#
# PRIVATE_COPY is a copy built as ../README.md's build section says, with its own .lake (never a shared one).
# FIXED_STAGING_POUW is the fixed staging's Pouw/ directory (ttout-fp4-staging/Pouw once the fix lands there).
# Exits 0 when the whole-copy audit passes, every module below replays, and all of fp4-delta-pins.json's records
# are unchanged; the audit's printout then lists the definitions the fix changed, for the statement reviewer.
set -euo pipefail
copy=$(cd "$1" && pwd); staging=$(cd "$2" && pwd); out=$3
here=$(cd "$(dirname "$0")" && pwd)
audit=${POUW_LEAN_AUDIT:-/workspace/tools/lean/audit.py}
export PATH="$HOME/.elan/bin:$PATH"

cp -r "$staging"/. "$copy/Pouw/"
cp "$here"/Pouw/PearlC/*.lean "$copy/Pouw/PearlC/"
(cd "$copy" && lake build > "$out.build.log" 2>&1) || { tail -30 "$out.build.log"; exit 1; }

python3 "$audit" --update --no-replay --out "$out" "$copy" | tee "$out.audit.log"
grep -q '^AUDIT: PASS' "$out.audit.log"

mods=(DeviceFp4 TTOutFp4 DeviceFp4Gamma DeviceFp4Issue Fp4IssueGamma DeviceFp4ChainOnly TTOutFp4ChainOnly
  Fp4ChainOnlyGamma DeviceFp4Hot Fp4HotGamma)
(cd "$copy" && lake env lean --run "$(dirname "$audit")/Replay.lean" "$out.replay.json" "${mods[@]/#/Pouw.PearlC.}")
cat "$out.replay.json"; echo

python3 - "$copy/lean-audit.json" "$here/fp4-delta-pins.json" <<'EOF'
import json, sys
now = json.load(open(sys.argv[1]))["pins"]
staged = json.load(open(sys.argv[2]))["pins"]
moved = [n for n, r in staged.items() if now.get(n) != r]
print(f"{len(staged) - len(moved)} of {len(staged)} fp4-delta records unchanged")
for n in moved:
    print("CHANGED", n)
sys.exit(1 if moved else 0)
EOF
