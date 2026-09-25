#!/usr/bin/env bash
# verify-night-2: instance-equiv/v1 artifacts (kb/bench-instances.md, rule I). For each ART: fetch, `instance_equiv --check` (re-derives
# every field from the relation its candidate ref names, with this tree's loaders), print the refs, and with LABEL=1 label it
# verified=accepted through 11-label.py when the check reproduces with equal=True.
#   LABEL=0|1 bash 26-equiv.sh ART [ART...]
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
I=$RESEARCH_RUN_DIR/inputs; E=/workspace/verify-night-2/equiv; mkdir -p $E
C=$(python3 -c "import json;print(json.load(open('/workspace/src/.research-source.json'))['commit'][:8])")
for A in "$@"; do
  S=$(date +%s); D=$E/${A#art:}; D=${D:0:${#E}+17}
  echo "=== [$(date -u +%H:%M:%S)] $A"
  F=$($PY -m research data fetch $A --to $D 2>/dev/null | tail -1)
  [ -d "$F" ] && F=$(find "$F" -name '*.json' | head -1)
  [ -f "$F" ] || { echo "FAIL $A: no file fetched"; continue; }
  $PY - "$F" <<'EOF' | tee $D.refs.txt
import json, sys
d = json.load(open(sys.argv[1]))
print("schema", d.get("schema"), "equal", d.get("equal"), "relation", d.get("relation"), "vus", d.get("vus"))
for k in ("candidate", "frozen"):
    r = d.get(k) or {}
    r = r.get("ref", r)
    print(k, {x: r.get(x) for x in ("dataset", "tier", "range", "manifest_sha256")})
EOF
  timeout 1800 $PY -m verity_numerical.bench.instance_equiv --check "$F" > $D.check.txt 2>&1; rc=$?
  tail -3 $D.check.txt
  ok=0; [ $rc = 0 ] && grep -q "reproduces; equal=True" $D.check.txt && grep -q "^schema instance-equiv/v1 equal True" $D.refs.txt && ok=1
  T=$(( $(date +%s) - S ))
  echo "$([ $ok = 1 ] && echo PASS || echo FAIL) $A: --check rc=$rc, $(grep -o 'reproduces; equal=[A-Za-z]*' $D.check.txt | head -1)"
  if [ "${LABEL:-0}" = 1 ] && [ $ok = 1 ]; then
    $PY $I/11-label.py $A --tree $A --verifier "verity_numerical.bench.instance_equiv --check @ main $C (verify-night-2 pod vy-verify-night-2)" \
      --detail "verify-night-2: instance-equiv/v1 re-derived with --check at main $C: every field reproduces, equal=True. $(head -3 $D.refs.txt | tr '\n' ' ')" \
      --seconds $T $D.refs.txt $D.check.txt 2>&1 | tail -2
  fi
done
echo "=== [$(date -u +%H:%M:%S)] 26 done"
