#!/usr/bin/env bash
# vo_build.sh LABEL ROW ROLE REPO REV TARGET_JSON JOBS: one real Build of ROW on this GPU-less pod (vo_row_build.py: the row's own Build
# stage under the declared TARGET_JSON), into /workspace/vo/sweep-LABEL/ROW.  Then: the record comparison (vo_digests.py against
# tests/regression/expected/ROW.json) into $RESEARCH_RUN_DIR/evidence/LABEL/, and the Build's outputs (every file of the row dir) copied
# to $RESEARCH_RUN_DIR/builds/LABEL/ for `research fetch --all` + `research data put` from the VM.  Run from the shipped tree's root.
set -u
LABEL=$1 ROW=$2 ROLE=$3 REPO=$4 REV=$5 TGT=$6 JOBS=$7
L=$RESEARCH_RUN_DIR; EV=$L/evidence/$LABEL; mkdir -p "$EV"; T=$PWD
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf CUDA_VISIBLE_DEVICES="" VU_EXPORT=0
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
export SWEEP_DIR=/workspace/vo/sweep-$LABEL PY=/workspace/venv312/bin/python
R=$SWEEP_DIR/$ROW
rm -rf "$R"; mkdir -p "$SWEEP_DIR"
cd "$T/integrations/vllm"
echo "build $LABEL start $(date -u +%FT%TZ) target $TGT jobs $JOBS"
python "$L/inputs/vo_row_build.py" "$TGT" "$ROW" "$ROLE" "$REPO" "$REV" --build-jobs "$JOBS" > "$L/build-$LABEL.log" 2>&1
echo "build $LABEL rc=$? $(date -u +%FT%TZ) $(grep '^build ' "$R/stages.txt" 2>/dev/null | tail -1 | cut -c1-200)"
cp "$R/stages.txt" "$R/row.log" "$R/build_summary.json" "$R"/target_family*.json "$R/timeline.jsonl" "$R/manifest.log" "$EV/" 2>/dev/null
for f in "$R"/build_*.log; do tail -c 4000 "$f" > "$EV/$(basename "$f").tail"; done 2>/dev/null
python "$L/inputs/vo_digests.py" "$R" "tests/regression/expected/$ROW.json" "$EV/digests.json"
mkdir -p "$L/builds"; cp -r "$R" "$L/builds/$LABEL"
echo "build $LABEL done $(date -u +%FT%TZ) $(du -sh "$L/builds/$LABEL" | cut -f1)"
