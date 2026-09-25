#!/usr/bin/env bash
# blake3-80gb: TABLES.md sweeps (sweep_vu, --commit-per-rep, 5 reps, only the plateau point's rep-1 dump kept), each followed
# by the pod's pinned ligero-verify on the plateau dump (a producer check, never the verification label).
# SWEEPS="rel:l:p ..." [START MAX REPS]
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
rc=0
for s in ${SWEEPS:?}; do
  IFS=: read -r REL L PP <<<"$s"; tag=$(echo "$REL-l$L-p$PP" | tr '+' '_'); SD=$RD/$tag
  gpu_idle || exit 3
  echo "##### $(date -u +%H:%M:%SZ) sweep $tag"
  $PY -m backends.direct.ligero.sweep_vu --relation $REL --out-dir $SD --start ${START:-1024} --max ${MAX:-131072} --dump plateau -- \
      --zk --mode interactive --auth included-hash --commit-per-rep --batch $L --pipeline $PP --target -128 --reps ${REPS:-5} --device cuda --instance-procs ${IPROCS:-16}
  r=$?; [ $r -ne 0 ] && rc=$r
  for pd in $SD/p*/proofs; do [ -d $pd/rep1 ] || continue
    ( cd $pd; echo "rust on $pd"
      $V system-digest --system system.bin > rust_digest.json 2> rust_digest.err; echo "system-digest rc=$? $(head -c 200 rust_digest.json)"
      $V batch --system system.bin --dir rep1 --jobs $NT --threads 1 --target-bits 128 --json rust_batch.json > rust_batch.out 2>&1
      echo "rust batch rc=$? $(tail -n 1 rust_batch.out | cut -c1-300)"; sha256sum $V > ligero_verify.sha256 )
  done
done
$PY "$IN/50-outputs.py" $RD blake3-80gb
exit $rc
