#!/usr/bin/env bash
# b-ligero-standard-hash: the TABLES.md batch sweep of one +blake3 line (sweep_vu, lane blake3-80gb 8c50b497 + dc2cae87):
#   doubling --total-vus from START at fixed per-proof settings (l = L, pipeline P, REPS timed reps, --commit-per-rep: every rep
#   commits its own batch) until two doublings gain < 2 % in e2e.vu_per_second; each point stamped with sweep / protocol;
#   rep 1 of the plateau point kept and checked by the pod's pinned ligero-verify (producer check, not the verification label).
# (research pods sync POD first)
# research run --on POD --project verity --cwd /workspace/src --custody-r2 --custody-ttl 8h \
#     --send lib.sh --send 30-sweep.sh --env REL=fp8-ada+blake3 --env L=4096 --env P=2 \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/30-sweep.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
REL=${REL:?}; L=${L:-4096}; P=${P:-2}; REPS=${REPS:-5}; START=${START:-1024}; MAX=${MAX:-65536}
RD=${RESEARCH_RUN_DIR:?}
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
gpu_idle || exit 3
t0=$(date +%s)
$PY -m backends.direct.ligero.sweep_vu --relation $REL --out-dir $RD/sweep --start $START --max $MAX --dump plateau -- \
    --zk --mode interactive --auth included-hash --commit-per-rep --batch $L --pipeline $P --target -128 --reps $REPS \
    --device cuda ${EXTRA:-} 2>&1 | tee $RD/sweep.log
rc=${PIPESTATUS[0]}
echo "sweep rc=$rc wall=$(( $(date +%s) - t0 ))s"
for d in $RD/sweep/p*; do echo "$(basename $d): $(grep -E '^rep ' $d/bench.log | tail -n 1 | cut -c1-260)"; done
[ $rc -eq 0 ] || exit $rc
PD=$RD/sweep/$($PY -c "import json,sys;s=json.load(open('$RD/sweep/sweep.json'));print([p['dir'] for p in s['points'] if p['point']==s['plateau_point']][0])")
cp $PD/result.json $RD/result.json
cd $PD/proofs || exit 4
$V system-digest --system system.bin > rust_digest.json 2> rust_digest.err; echo "system-digest rc=$? $(head -c 400 rust_digest.json)"
t1=$(date +%s)
$V batch --system system.bin --dir rep1 --jobs $NT --threads 1 --target-bits 128 --json rust_batch.json > rust_batch.out 2>&1
echo "rust batch rc=$? wall=$(( $(date +%s) - t1 ))s $(tail -n 1 rust_batch.out | cut -c1-300)"
sha256sum $V > ligero_verify.sha256
