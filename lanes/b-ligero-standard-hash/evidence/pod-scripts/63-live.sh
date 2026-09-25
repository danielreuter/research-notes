#!/usr/bin/env bash
# b-ligero-standard-hash: the 4096 frozen cell with the verifier's OWN coins (coordinator 0915Z decision 2: only if cheap, on
# a pod already up). A same-pod live verifier (kb/live-verifier.md fallback: `live serve` niced, tcp://127.0.0.1:7000, the
# pod's pinned ligero-verify) draws every recorded rep's step-0 coins and verifies every sub-batch as it arrives; rep 1 is
# dumped too. Same bench flags as 20-cell.sh.
# research run --on POD --project verity --cwd /workspace/src --custody-r2 --custody-ttl 8h \
#     --send lib.sh --send 63-live.sh --env REL=fp8-ada+blake3 -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/63-live.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
REL=${REL:?}; L=${L:-4096}; P=${P:-2}; REPS=${REPS:-5}; VUS=${VUS:-4096}; JOBS=${LIVE_JOBS:-4}
RD=${RESEARCH_RUN_DIR:?}
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
gpu_idle || exit 3
nice -n 19 $PY -m backends.direct.ligero.live serve --listen 127.0.0.1:7000 --out $RD/live --ligero-verify $V \
    --jobs $JOBS --threads 1 --target-bits 128 > $RD/serve.log 2>&1 &
SP=$!
for i in $(seq 1 60); do (echo > /dev/tcp/127.0.0.1/7000) 2>/dev/null && break; sleep 1; done
echo "verifier pid $SP listening after ${i}s"
t0=$(date +%s)
$PY -m backends.direct.ligero.run --relation $REL bench-vu --zk --mode interactive --auth included-hash --commit-per-rep \
    --batch $L --pipeline $P --total-vus $VUS --target -128 --reps $REPS --device cuda --verifier tcp://127.0.0.1:7000 \
    --out $RD/result.json --dump-dir $RD/proofs --dump-reps 1 2>&1 | tee $RD/bench.log | grep -E "^rep |live|verdict|OOM|Error|error" | cut -c1-400
rc=${PIPESTATUS[0]}
echo "bench rc=$rc wall=$(( $(date +%s) - t0 ))s"
kill $SP; wait $SP 2>/dev/null
tail -n 4 $RD/serve.log | cut -c1-300
cut -c1-400 $RD/live/index.jsonl 2>/dev/null
[ -f $RD/proofs/system.bin ] || exit $rc
cd $RD/proofs
$V system-digest --system system.bin > rust_digest.json 2> rust_digest.err; echo "system-digest rc=$? $(head -c 300 rust_digest.json)"
$V batch --system system.bin --dir rep1 --jobs $NT --threads 1 --target-bits 128 --json rust_batch.json > rust_batch.out 2>&1
echo "rust batch rc=$? $(tail -n 1 rust_batch.out | cut -c1-300)"
sha256sum $V > ligero_verify.sha256
exit $rc
