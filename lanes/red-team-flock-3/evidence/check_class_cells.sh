#!/usr/bin/env bash
# red-team-flock-3: a key-count class cell (bench-result/v1, relation irf:attention-head, fingerprint key_class): its verifier run's
# own class manifest (class.json) against the reviewed generator (manifest_check.py vs class_ref.py's table) and the cell's pin;
# every sub-batch's verifier-staged file and netlist through cell_check.py (one T each); key_counts = the T of the verified
# sub-batches; then placement_check.py.
#   check_class_cells.sh CLASS_REF.json ART...
set -uo pipefail
E=$(cd "$(dirname "$0")" && pwd); REF=$1; shift
for a in "$@"; do
  meta=$(research data show $a 2>/dev/null | awk '/^meta/{sub(/^meta +/,""); print}')
  read -r ver B set pin lo hi <<< "$(python3 -c "
import json, sys; d = json.loads(sys.argv[1]); wf = d['workload_fingerprint']; k = wf.get('key_class') or {}
print(d['derived_from']['verifier_run'], wf['B'], wf['instances']['art'], k.get('pin'), *(k.get('T') or [0, 0]))" "$meta")"
  rec=$(research data show $ver 2>/dev/null | grep -o '"run_record": "art:[0-9a-f]*"' | grep -o 'art:[0-9a-f]*')
  rd=$(research data fetch $rec 2>/dev/null | tail -1); sd=$(research data fetch $set 2>/dev/null | tail -1)
  sdir=$(dirname "$(find $sd -name manifest.json | head -1)")
  p=$(ls -d $rd/out/verifier/p*-$B 2>/dev/null | head -1)
  echo "== $a class [$lo, $hi] B=$B pin=${pin:0:16} verifier_run=$ver record=$rec point=$(basename "$p")"
  man=$(ls $rd/out/verifier/class.json 2>/dev/null || ls $p/../class.json 2>/dev/null | head -1)
  python3 $E/manifest_check.py $man $REF $pin | tail -1
  n=$(ls $p | grep -c '^instances-s'); pass=0; fail=0; Ts=""
  for f in $p/instances-s*.bin; do i=$(basename $f .bin); i=${i#instances-s}
    r=$(python3 $E/cell_check.py $f $p/stage-s$i/net.txt $sdir 2>&1)
    T=$(echo "$r" | grep -o 'NETLIST T=[0-9]*' | cut -d= -f2); Ts="$Ts $T"
    acc=$(grep -c '"accepted":true' $p/sessions-s$i/index.jsonl 2>/dev/null)
    if echo "$r" | grep -q 'CELL_CHECK PASS' && [ "${acc:-0}" -ge 2 ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "   s$i T=$T accepted=$acc $(echo "$r" | grep -h 'CELL_CHECK\|E2E' | cut -c1-200)"; fi
  done
  python3 - "$meta" "$Ts" <<'EOF'
import json, sys
d = json.loads(sys.argv[1]); kc = d["workload_fingerprint"].get("key_counts") or {}
Ts = [int(t) for t in sys.argv[2].split()]
mine = {str(t): Ts.count(t) for t in sorted(set(Ts))}
print("KEY_COUNTS", "match" if set(mine) == set(kc) else f"DIFFER sub-batch T {sorted(mine)[:5]}.. vs key_counts {sorted(kc)[:5]}..",
      f"{len(kc)} T values in key_counts; per_key_count {len(d.get('per_key_count') or {})}")
EOF
  echo "SUBBATCHES $n: $pass PASS, $fail FAIL"
  echo "CLASS_CELL_CHECK $([ $fail = 0 ] && [ $n -gt 0 ] && echo PASS || echo FAIL) $a"
done
