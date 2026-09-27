#!/usr/bin/env bash
# sv_build.sh: #101 then #4, Build stage only, from the shipped tree (the record run r20260926-035624-a133's source, 11d453e0).
# #101 must reproduce the record's request Program ccc21347...; if not, stop before #4. #4 must reproduce its 16 recorded request
# Programs. Each row's Build files (no captures) go to $RESEARCH_RUN_DIR/builds/<row>/ in the sweep layout, preserved by --custody-r2;
# its program.json (main's program_graph, from inputs/main-graph.tar.gz) to $RESEARCH_RUN_DIR/program-graphs/.
set -u
T=$PWD; I=$RESEARCH_RUN_DIR/inputs; OUT=$RESEARCH_RUN_DIR
echo "start $(date -u +%FT%TZ) source ${RESEARCH_SOURCE_SHA:-?}"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
bash verity_vllm/ops/pod_bootstrap.sh --cases B0,LLAMA32_1B --out /workspace/sv/bootstrap > $OUT/bootstrap.log 2>&1; echo "bootstrap rc $? $(date -u +%FT%TZ)"
tail -1 $OUT/bootstrap.log
python -c "import verity_sampled_proofs; print('verity_sampled_proofs ok')"
export HIDDEN_SO=/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so SWEEP_DIR=/workspace/sv/sweep PAIRS=1 VU_EXPORT=0
M=/workspace/sv/main; rm -rf $M; mkdir -p $M; tar -xzf $I/main-graph.tar.gz -C $M
build() {  # N ROW ROLE REPO REV
  local N=$1 ROW=$2 R=$SWEEP_DIR/$2 B=$OUT/builds/$2
  rm -rf "$R"
  verity-vllm row run "$ROW" "$3" "$4" "$5" --stages build < /dev/null > "$OUT/row-$N.log" 2>&1; echo "row $N build rc $? $(date -u +%FT%TZ)"
  cat "$R/stages.txt" 2>/dev/null | grep -E "^(build|precheck)"
  mkdir -p "$B"
  (cd "$R" && find . -maxdepth 1 -type f \( -name '*.json' -o -name '*.log' -o -name 'stages.txt' \) -exec cp {} "$B/" \; ;
   for d in build_*; do [ -d "$d" ] && mkdir -p "$B/$d" && find "$d" -maxdepth 1 -type f \( -name '*.json' -o -name '*.json.gz' -o -name '*.log' \) -exec cp {} "$B/$d/" \; ; done)
  du -sh "$B"
}
digests() {  # ROW -> "<dir> <program_digest>" per request Program
  python - "$SWEEP_DIR/$1" <<'PY'
import glob, json, os, sys
for a in sorted(glob.glob(sys.argv[1] + "/build_request*/artifact.json")):
    print(os.path.basename(os.path.dirname(a)), json.load(open(a))["program_digest"])
PY
}
graph() {  # N ROW
  (cd $M/integrations/vllm && PYTHONPATH=$M/integrations/vllm:$M/packages/verity/src:$M/tools/research/src:$M/protocols/sampled_proofs \
     VUX_REPO=$M/integrations/vllm python $I/program_graphs.py $OUT/program-graphs "$2" "$SWEEP_DIR/$2" --record expected \
     --run "${RESEARCH_RUN_ID:-}" --row "$1" < /dev/null); echo "graph $1 rc $? $(date -u +%FT%TZ)"
}
R101=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
R4=smollm2-135m__bf16__l40s__tp1__b16__i1024__o128__mixed__greedy__bi-eager
build 101 $R101 LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da
digests $R101 | tee $OUT/digests-101.txt
if ! grep -q " ccc213475e7c4eed04b3b0d3717e2144012be65f41d900a018dbd09d1e400c6b$" $OUT/digests-101.txt; then
  echo "STOP #101 did not reproduce ccc21347 (record r20260926-035624-a133); #4 not built $(date -u +%FT%TZ)"; exit 4
fi
echo "OK #101 == ccc21347"
graph 101 $R101
build 4 $R4 B0 HuggingFaceTB/SmolLM2-135M 93efa2f097d58c2a74874c7e644dbc9b0cee75a2
digests $R4 | tee $OUT/digests-4.txt
python - $OUT/digests-4.txt $I/expected-4.txt <<'PY'
import sys
have = {l.split()[1] for l in open(sys.argv[1]) if l.strip()}
want = {l.strip() for l in open(sys.argv[2]) if l.strip()}
print("#4 request Programs: %d built, %d recorded, %d match, missing %s" % (len(have), len(want), len(have & want), sorted(x[:12] for x in want - have)))
sys.exit(0 if want <= have else 5)
PY
rc4=$?
if [ $rc4 -ne 0 ]; then echo "STOP #4 did not reproduce its recorded request Programs; no graph $(date -u +%FT%TZ)"; exit 5; fi
graph 4 $R4
echo "SV-BUILD-DONE $(date -u +%FT%TZ)"
