#!/bin/bash
# One row's Build, Match and Commit from the tree in $PWD (research run --cwd source), stage by stage, into SWEEP.
#   usage: [KEEP_GOING=1] ab_row.sh head|base SWEEP ROW ROLE REPO REV [flags...]   (KEEP_GOING: run the next stage after a failed one)
#   head: verity-vllm row stage <st> ...;  base: run_row_v2.sh stage <st> ... (the base tree's shell)
SIDE=$1; SWEEP=$2; ROW=$3; ROLE=$4; REPO=$5; REV=$6; shift 6
export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src HF_HOME=/workspace/hf
for st in build match commit; do
  echo "=== $SIDE $st $(date -u +%FT%TZ)"
  if [ "$SIDE" = head ]; then
    /workspace/venv312/bin/python -m verity_vllm.pipeline.cli row stage $st "$ROW" "$ROLE" "$REPO" "$REV" --sweep-dir "$SWEEP" "$@"
  else
    bash integrations/vllm/verity_vllm/ops/run_row_v2.sh stage $st "$ROW" "$ROLE" "$REPO" "$REV" --sweep-dir "$SWEEP" "$@"
  fi
  rc=$?
  echo "=== $SIDE $st rc=$rc $(date -u +%FT%TZ)"
  mkdir -p /workspace/a5/ab/$SIDE; cp -a "$SWEEP/$ROW/verdict.json" "/workspace/a5/ab/$SIDE/verdict-$st.json" 2>/dev/null
  [ $rc -eq 0 ] || [ -n "${KEEP_GOING:-}" ] || exit $rc
done
