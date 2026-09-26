#!/usr/bin/env bash
# red-team-flock-3: a key-count class cell (bench-result/v1, relation irf:attention-head, fingerprint key_class): its verifier run's
# own class manifest (class.json) against the reviewed generator (manifest_check.py vs class_ref.py's table) and the cell's pin;
# every sub-batch's verifier-staged file through cell_check.py (one T each) with T's netlist regenerated here from the reviewed
# generator (the file's header unit_sha256 must equal it and the manifest's nets[T]); each sub-batch's verifier sessions;
# key_counts = the T of the verified sub-batches. Fetches only those files of the (large) verifier record.
#   check_class_cells.sh CLASS_REF.json ART...
set -uo pipefail
E=$(cd "$(dirname "$0")" && pwd); REF=$1; shift; NETS=/tmp/rtf3/nets; mkdir -p $NETS
for a in "$@"; do
  meta=$(research data show $a 2>/dev/null | awk '/^meta/{sub(/^meta +/,""); print}')
  read -r ver B set pin lo hi <<< "$(python3 -c "
import json, sys; d = json.loads(sys.argv[1]); wf = d['workload_fingerprint']; k = wf.get('key_class') or {}
print(d['derived_from']['verifier_run'], wf['B'], wf['instances']['art'], k.get('pin'), *(k.get('T') or [0, 0]))" "$meta")"
  rec=$(research data show $ver 2>/dev/null | grep -o '"run_record": "art:[0-9a-f]*"' | grep -o 'art:[0-9a-f]*')
  research data fetch $rec --path 'out/verifier/class.json' --path "out/verifier/p*-$B/instances-s*.bin" \
    --path "out/verifier/p*-$B/sessions-s*/index.jsonl" --path job.json --path out/host.txt > /dev/null 2>&1
  rd=$HOME/.research/store/trees/${rec#art:}
  sd=$(research data fetch $set 2>/dev/null | tail -1); sdir=$(dirname "$(find $sd -name manifest.json | head -1)")
  p=$(ls -d $rd/out/verifier/p*-$B 2>/dev/null | head -1)
  echo "== $a class [$lo, $hi] B=$B pin=${pin:0:16} verifier_run=$ver record=$rec point=$(basename "$p")"
  python3 $E/manifest_check.py $rd/out/verifier/class.json $REF $pin | tail -1
  n=$(ls $p | grep -c '^instances-s'); pass=0; fail=0; Ts=""
  for f in $p/instances-s*.bin; do i=$(basename $f .bin); i=${i#instances-s}
    T=$(python3 -c "
import json, sys; b = open(sys.argv[1], 'rb').read(2000000); h = json.loads(b[:b.index(b'\n')]); print(h['in_ports'][1][1] // 64)" $f)
    [ -f $NETS/net-t$T.txt ] || python3 -c "
import sys
from verity_numerical.bench import templates as TM
from verity_flock.templates import attention_head as AH
open(sys.argv[2], 'w').write(AH.lowering(TM.subcircuit('attention-head', D=64, BN=128), int(sys.argv[1])).text)" $T $NETS/net-t$T.txt
    r=$(python3 $E/cell_check.py $f $NETS/net-t$T.txt $sdir 2>&1); Ts="$Ts $T"
    acc=$(grep -c '"accepted":true' $p/sessions-s$i/index.jsonl 2>/dev/null)
    if echo "$r" | grep -q 'CELL_CHECK PASS' && [ "${acc:-0}" -ge 2 ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "   s$i T=$T accepted=$acc $(echo "$r" | grep -h 'NETLIST\|CELL_CHECK\|E2E' | cut -c1-220)"; fi
  done
  python3 - "$meta" "$Ts" <<'EOF'
import json, sys
d = json.loads(sys.argv[1]); kc = d["workload_fingerprint"].get("key_counts") or {}
Ts = [int(t) for t in sys.argv[2].split()]
mine = {t: Ts.count(t) for t in sorted(set(Ts))}
same = set(map(str, mine)) == set(kc)
print("KEY_COUNTS", "match" if same else f"DIFFER sub-batch T {sorted(mine)[:5]}.. vs key_counts {sorted(kc)[:5]}..",
      f"({len(kc)} T values; {sum(kc.values())} heads; per_key_count {len(d.get('per_key_count') or {})})")
EOF
  echo "SUBBATCHES $n: $pass PASS, $fail FAIL"
  echo "CLASS_CELL_CHECK $([ $fail = 0 ] && [ $n -gt 0 ] && echo PASS || echo FAIL) $a"
done
