#!/usr/bin/env bash
# agkr-real-k: tools/cell_gate.py on every timed session of a registered A-route-a cell, from the store alone (no pod): the
# verifier run's session records (its "verifier-records" output) against the prover run's timed proofs (run_files) and the
# statement it proved (run_record out/statement-<n>).  A producer's pre-check of what the verify lane's G3 runs: every check
# should pass except non_producer (the lane operated the verifier).
#   bash 30-gate-cells.sh PROVER_RECORD PROVER_FILES VERIFIER_RECORDS N RELATION VB FLOCK OUT
set -uo pipefail
PR=$1; PF=$2; VR=$3; N=$4; REL=$5; VB=$6; FL=$7; OUT=$8
GKR=$(cd "$(dirname "$0")" && git -C /workspace rev-parse --show-toplevel)/backends/gkr
S=$PR/out/statement-$N
PC=$(python3 -c "import json;print(json.load(open('$S/cell.json'))['prime_commitment'])")
echo "prover digests $(sha256sum $S/leaf_digests.bin | cut -c1-16); verifier's own: $(grep -h "c$N/leaf_digests" $VR/out/statements/digests.sha256 | cut -c1-16)"
mapfile -t SES < <(ls -d $VR/sessions-$N/l* | sort)
i=1
for ses in "${SES[@]}"; do
  o=$OUT/k-$N-s$i; mkdir -p $o
  python3 $GKR/tools/cell_gate.py --session $ses --sigma $S/sigma.txt --producer agkr-real-k --producer loopback-selftest --out $o \
    --rust $VB --statement $S --proof $PF/out/cell-$N/s$i/proof.bin --vus $N --relation $REL --threads $(nproc) \
    --flock $FL --digests $S/leaf_digests.bin --prime-commitment $PC > $o/gate.txt 2>&1
  python3 -c "import json;d=json.load(open('$o/gate.json'));print('$N s$i', {k: v['ok'] for k, v in d['checks'].items() if not v['ok']} or 'all ok', d['checks']['prime']['detail'][:120])"
  i=$((i + 1))
done
