#!/usr/bin/env bash
# b-ligero-standard-hash: one full-relation cell (frame-v3, keyed-BLAKE3 row leaves), recorded.
#   bench-vu --relation REL --auth included-hash --commit-per-rep: every rep commits its batch (x / W / y trees + row digests,
#   no cache) timed as commitment.seconds, then proves; rep 1 dumped; then the pod's ligero-verify (pinned) on the dump:
#   system-digest + batch (a producer check, never the verification label).
# (research pods sync POD first: the tree at /workspace/src is the lane tip; its .research-source.json is the stamp)
# research run --on POD --project verity --cwd /workspace/src --custody-r2 --custody-ttl 8h \
#     --send lib.sh --send 20-cell.sh --env REL=fp8-ada+blake3 --env L=4096 --env P=2 --env REPS=5 \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/20-cell.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
REL=${REL:?}; L=${L:-4096}; P=${P:-2}; REPS=${REPS:-5}; VUS=${VUS:-4096}
RD=${RESEARCH_RUN_DIR:?}
D=$RD/proofs
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
gpu_idle || exit 3
t0=$(date +%s)
$PY -m backends.direct.ligero.run --relation $REL bench-vu --zk --mode interactive --auth included-hash --commit-per-rep \
    --batch $L --pipeline $P --total-vus $VUS --target -128 --reps $REPS --device cuda \
    --out $RD/result.json --dump-dir $D --dump-reps 1 ${EXTRA:-} 2>&1 | tee $RD/bench.log | grep -E "^rep |committed:|config |census|OOM|Error|error" | cut -c1-400
rc=${PIPESTATUS[0]}
echo "bench rc=$rc wall=$(( $(date +%s) - t0 ))s"
[ -f $D/system.bin ] || exit $rc
cd $D
$V system-digest --system system.bin > rust_digest.json 2> rust_digest.err; echo "system-digest rc=$? $(head -c 400 rust_digest.json)"
t1=$(date +%s)
$V batch --system system.bin --dir rep1 --jobs $NT --threads 1 --target-bits 128 --json rust_batch.json > rust_batch.out 2>&1
echo "rust batch rc=$? wall=$(( $(date +%s) - t1 ))s $(tail -n 1 rust_batch.out | cut -c1-300)"
sha256sum $V > ligero_verify.sha256
exit $rc
