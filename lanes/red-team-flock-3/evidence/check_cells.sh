#!/usr/bin/env bash
# red-team-flock-3: every registered attention cell (bench-result/v1, relation irf:attention-head): its verifier run's own staged
# statement at the cell's point (B instances) through cell_check.py, against the cell's registered input set.
#   check_cells.sh [ART...]   (default: every attention cell in the local store index)
set -uo pipefail
E=$(cd "$(dirname "$0")" && pwd)
arts=${*:-$(research data select --kind bench-result/v1 --where meta.cell.relation=irf:attention-head --ids 2>/dev/null)}
for a in $arts; do
  meta=$(research data show $a 2>/dev/null | awk '/^meta/{sub(/^meta +/,""); print}')
  read -r ver B set unit pin commit <<< "$(python3 -c "
import json, sys; d = json.loads(sys.argv[1]); wf = d['workload_fingerprint']; be = wf['software']['backend']
print(d['derived_from']['verifier_run'], wf['B'], wf['instances']['art'], be['unit'].split('/')[-1], be['lowering_sha256'], be['commit'][:8])" "$meta")"
  rec=$(research data show $ver 2>/dev/null | grep -o '"run_record": "art:[0-9a-f]*"' | grep -o 'art:[0-9a-f]*')
  rd=$(research data fetch $rec 2>/dev/null | tail -1); sd=$(research data fetch $set 2>/dev/null | tail -1)
  sdir=$(dirname "$(find $sd -name manifest.json | head -1)")
  p=$(ls -d $rd/out/verifier/p*-$B 2>/dev/null | head -1)
  echo "== $a $unit B=$B commit=$commit pin=${pin:0:16} verifier_run=$ver record=$rec point=$(basename "$p")"
  if [ -z "$p" ] || [ ! -f $p/instances-s0.bin ]; then echo "CELL_CHECK FAIL no verifier-staged file for B=$B"; continue; fi
  ls $p | grep -c '^instances-s' | sed 's/^/subbatches: /'
  [ "$(sha256sum < $p/stage-s0/net.txt | cut -c1-64)" = "$pin" ] && echo "verifier netlist = the cell's pin" || echo "PIN MISMATCH"
  grep -h '"accepted"' $p/sessions-s0/index.jsonl 2>/dev/null | python3 -c "
import sys, json
rows = [json.loads(l) for l in sys.stdin]
print('verifier sessions:', len(rows), 'accepted:', sum(r['accepted'] is True for r in rows), 'link_mode:', sorted({r.get('link_mode') for r in rows}), 'require_link:', sorted({r.get('require_link') for r in rows}))"
  python3 $E/cell_check.py $p/instances-s0.bin $p/stage-s0/net.txt $sdir 2>&1 | tail -5
done
