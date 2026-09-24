#!/usr/bin/env bash
# lane fp4-decode-3: put + preserve (push to R2, verify) one fetched suite run's cited files; appends "art:... <what>" to store_ids.txt.
#   $1 = run id (fetched with `research fetch <id> --all`), $2 = device string, $3 = commit, $4 = bench stages (comma list)
set -euo pipefail
RUN=$1; DEV=$2; COMMIT=$3; BENCHES=$4
R=~/.research/runs/$RUN; OUT=~/.research/notes/lanes/fp4-decode-3/evidence/store_ids.txt
export PYTHONPATH=~/projects/verity-main-wt/qol/tools/research/src
set -a; source ~/.config/verity/r2.env; set +a
PY=~/projects/verity-main-wt/main/.venv/bin/python
put() {  # $1 kind, $2 --file|--tree, $3 path, $4 meta json, $5.. extra args ; echoes the art id
  local id
  id=$($PY -m research data put --kind "$1" "$2" "$3" --meta "$4" "${@:5}" --preserve --json | $PY -c "import json,sys; d=json.load(sys.stdin); print(d.get('id') or d.get('art') or d)")
  echo "$id"
}
meta() {  # $1 relation, $2 note
  $PY -c "import json,sys; print(json.dumps({'by':'fp4-decode-3','commit':sys.argv[1],'device':sys.argv[2],'run':sys.argv[3],'relation':sys.argv[4],'note':sys.argv[5]}))" \
    "$COMMIT" "$DEV" "$RUN" "$1" "$2"
}
for S in ${BENCHES//,/ }; do
  case $S in *hashed*) REL=fp4-nvf4+hash;; *) REL=fp4-nvf4;; esac
  D=${S##*_p}; case $S in ab_*) D="4 (A/B LIGERO_WITNESS_PTX_ARCH=${S#ab_*_}; ${S##*_} of 2)";; esac
  P=$(put proof/v1 --tree "$R/$S/proofs" "$(meta $REL "proof dump: 4096 VUs, l=16384, --zk --mode interactive, local coins, --pipeline $D, rep 1 (7 sub-batches) + system.bin")")
  echo "$P $RUN/$S proofs" | tee -a "$OUT"
  B=$(put bench-result/v1 --file "$R/$S/result.json" "$(meta $REL "bench result.json (--pipeline $D, 3 reps)")" --ref "proof=$P")
  echo "$B $RUN/$S result.json" | tee -a "$OUT"
  V=$(put verification-verdict/v1 --file "$R/$S/rust_batch_pinned.json" "$(meta $REL "pinned ligero-verify batch (no --allow-any-system) over the rep-1 dump")" --ref "proof=$P")
  echo "$V $RUN/$S rust_batch_pinned.json" | tee -a "$OUT"
done
for G in gate_hashed gate_bare; do
  [ -f "$R/$G/gate.json" ] || continue
  case $G in gate_hashed) REL=fp4-nvf4+hash;; *) REL=fp4-nvf4;; esac
  I=$(put run-files/v1 --file "$R/$G/gate.json" "$(meta $REL "gate-vu 2048 VUs --batch 16384 + negatives, LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1")")
  echo "$I $RUN/$G gate.json" | tee -a "$OUT"
done
L=$(put run-files/v1 --file "$R/stdout.log" "$(meta fp4-nvf4+hash "suite stdout (pipe_test, gates, benches, pinned Rust)")")
echo "$L $RUN stdout.log" | tee -a "$OUT"
