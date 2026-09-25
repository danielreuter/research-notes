#!/usr/bin/env bash
# blake3-80gb: TABLES.md sweep of one config (sweep_vu, --commit-per-rep, 5 reps, plateau dump kept), then the pod's pinned
# ligero-verify on the plateau dump (a producer check, never the verification label).  REL L P [START MAX]
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
gpu_idle || exit 3
$PY -m backends.direct.ligero.sweep_vu --relation ${REL:?} --out-dir $RD/sweep --start ${START:-1024} --max ${MAX:-131072} --dump plateau -- \
    --zk --mode interactive --auth included-hash --commit-per-rep --batch ${L:?} --pipeline ${P:?} --target -128 --reps ${REPS:-5} --device cuda
rc=$?
pl=$($PY -c "import json;d=json.load(open('$RD/sweep/sweep.json'));print([p['dir'] for p in d['points'] if p['point']==d['plateau_point']][0])") || exit 1
cd $RD/sweep/$pl/proofs || exit 1
$V system-digest --system system.bin > rust_digest.json 2> rust_digest.err; echo "system-digest rc=$? $(head -c 300 rust_digest.json)"
t1=$(date +%s)
$V batch --system system.bin --dir rep1 --jobs $NT --threads 1 --target-bits 128 --json rust_batch.json > rust_batch.out 2>&1
echo "rust batch rc=$? wall=$(( $(date +%s) - t1 ))s $(tail -n 1 rust_batch.out | cut -c1-300)"
sha256sum $V > ligero_verify.sha256
exit $rc
