#!/usr/bin/env bash
# verify-night-3: the 1024-VU envelope's prime proofs, diagnostic only. The gate's verifier refuses them because [0, 1024) is not a
# pinned instance commitment. Re-verify each honest session's prime proof with --allow-unpinned-commitment, using the statement dir
# the gate assembled (my regenerated statement, run r20260925-204110-326f), with the record's live prime coins.
set -uo pipefail
G=/workspace/research/runs/r20260925-204110-326f/out/gate-1024; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
for s in 1 2 3 4 5; do
  d=$G/honest-c1024-s$s
  /workspace/bin/verity-gkr-verify-live verify --dir $d/statement --proof /workspace/g3/cells-mine/c1024/s$s/proof.bin --threads $(nproc) \
    --relation bf16-ampere+blake3 --require-live-coins --allow-unpinned-commitment --vus 1024 --json $O/s$s.json > /dev/null 2>&1
  echo "s$s rc=$? $(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));c=d.get('commitment') or {};print(d['accepted'], d['error'], d['prime_rounds'], d['prime_before_commit'], c.get('root_a','')[:12], c.get('root_b','')[:12], c.get('root_y','')[:12], c.get('pinned'))" $O/s$s.json)"
done
grep -h "" /workspace/g3/mine/c1024/statement/commitment.txt
