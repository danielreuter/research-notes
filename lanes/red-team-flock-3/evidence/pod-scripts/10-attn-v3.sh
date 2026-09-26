#!/usr/bin/env bash
# red-team-flock-3: verity/flock-ir-frame/v3 attention (PR #54 @ 22dc6320, the registered cells' commit; 0839742b differs by the
# statement-digest TAG string only), CPU only (the pod's GPU is unused).
#  1. build flock-ir-frame (CPU) unpatched, then with my prover-side RT3 knobs (rtf3_frame_patch.py) + my tail harness rtf3-tail
#  2. stage the verifier's own files (ir_frame.stage) from captured #101 heads (T 4, 129, 130, 287) and my adversarial sets
#  3. the producer's selftest (every case) on my captured files; `--only honest` on every adversarial file (the Rust tail vs the
#     IR at load, the units vs the IR in the proof)
#  4. RT3 attacks (must be refused), load tampers (frame_tamper3.py; must be refused at load), consistent restatements (pass load,
#     the proof must refuse), cross-T and cross-set sessions against a live `serve`
#  5. numeric differentials at scale: tail prims (exhaustive unary), the TC unit netlist vs the IR, end-to-end on all 1024 heads
set -uxo pipefail
[ -d backends/flock ] || exit 1
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O; SRC=$(pwd)
sha256sum $I/* | tee $O/inputs.sha256
git log -1 --format=%H 2>/dev/null | tee $O/source.txt; echo "${RESEARCH_SOURCE_SHA:-}" >> $O/source.txt
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build-base.txt 2>&1 || { tail -60 $O/build-base.txt; exit 1; }
source $HOME/.cargo/env
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH; echo "threads $TH" | tee $O/host.txt
W=/workspace/flock-gpu-link/flock
F=$W/crates/flock-live/src/bin/flock-ir-frame.rs   # 20-gpu-link.sh copies backends/flock/live there: the build compiles the copy
diff -r backends/flock/live $W/crates/flock-live > $O/live-copy.diff 2>&1; echo "live copy diff rc=$?"
(cd $W && cargo build --release -p flock-live --bin flock-ir-frame -j $TH) > $O/build-ir.txt 2>&1 || { tail -40 $O/build-ir.txt; exit 1; }
mkdir -p $O/bin && cp $W/target/release/flock-ir-frame $O/bin/flock-ir-frame.orig
{ echo 'use flock_live::ir_tail;'; cat $I/rtf3_tail_main.rs; } > $W/crates/flock-live/src/bin/rtf3-tail.rs
cp $F $O/flock-ir-frame.rs.orig; python3 $I/rtf3_frame_patch.py $F | tee $O/patch.txt || exit 1
diff -u $O/flock-ir-frame.rs.orig $F > $O/rtf3-frame.diff
(cd $W && cargo build --release -p flock-live --bin flock-ir-frame --bin rtf3-tail -j $TH) > $O/build-rt3.txt 2>&1 || { tail -40 $O/build-rt3.txt; exit 1; }
PO=$O/bin/flock-ir-frame.orig; PF=$W/target/release/flock-ir-frame; H=$W/target/release/rtf3-tail; sha256sum $PO $PF $H | tee $O/binary.sha256
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh > $O/uv-install.txt 2>&1; }
export PATH=$HOME/.local/bin:$HOME/.cargo/bin:$PATH
uv python install 3.12 > $O/uv-python.txt 2>&1 || { tail -5 $O/uv-python.txt; exit 1; }
PY="uv run --python 3.12 --no-project --with numpy --with blake3 python3"
export PYTHONPATH=$SRC/backends/flock/python:$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/integrations/vllm PYTHONDONTWRITEBYTECODE=1
E=$O/ev; mkdir -p $E; cp $I/*.py $E/
P=$O/parent; mkdir -p $P && tar -xf $I/captured-6312cb50.tar -C $P || exit 1
PS=$(dirname $(find $P -name manifest.json | head -1))
D=$O/files; S=$O/sets; T=$O/tables; mkdir -p $D $S
$PY -c "from verity_flock import ir_lower as IL; print(IL.write_tables('$T'))" | tee $O/tables.txt
st() {  # tag setdir n
  $PY $E/mkset.py stage $2 $3 $D/$1 > $O/stage-$1.txt 2>&1 || { tail -5 $O/stage-$1.txt; return 1; }
}
for tn in 4:8 129:4 130:2 287:2; do t=${tn%%:*}; n=${tn##*:}
  $PY $E/mkset.py captured $PS $t $n $S/cap-t$t > /dev/null && st cap-t$t $S/cap-t$t/attention-head-fa2-d64-bn128 $n
done
for t in 4 129; do n=$([ $t = 4 ] && echo 8 || echo 2)
  for c in typical extreme_scores nan_inf all_neg_inf subnormal one_hot v_extreme zeros uniform_bits; do
    $PY $E/mkset.py adversarial $t $n 31 $c $S/adv-t$t-$c > /dev/null && st adv-t$t-$c $S/adv-t$t-$c/attention-head-fa2-d64-bn128 $n
  done
done
ls $D | tee $O/staged.txt
fr() {  # tag dir [bin] [args]  -> selftest (or $CMD) on the staged file
  local tag=$1 d=$D/$2 b=${BIN:-$PF}; shift 2
  $b ${CMD:-selftest} --instances $(ls $d/frame-*.bin | head -1) --netlist $d/net.txt --pin $(cat $d/pin) --tables $T "$@" > $O/$tag.txt 2>&1; local rc=$?
  echo "== $tag rc=$rc $(grep -h 'SELFTEST\|REFUSED\|panicked' $O/$tag.txt | head -1 | cut -c1-260)"; grep -h '"pass":false' $O/$tag.txt | cut -c1-300
}
# 3. the producer's selftest, unpatched binary, on my captured files; honest sessions on every adversarial file
for t in 4 129 287; do BIN=$PO fr S-cap-t$t cap-t$t; done
for f in $(ls $D | grep '^adv-'); do BIN=$PO fr H-$f $f --only honest; grep -h '^NEG' $O/H-$f.txt | grep -o '"accepted":[a-z]*' | head -1; done
# 4a. RT3 prover-side attacks (patched binary; each must be refused)
for t in 4 129 287; do
  for a in zero_leaf_run_message zero_leaf_run_published hole_cut_input; do
    RT3=$a fr A-t$t-$a cap-t$t --only honest; grep -h '^NEG' $O/A-t$t-$a.txt | grep -o '"accepted":[a-z]*\|"reps_ok":[^]]*]]' | head -2; grep -h '^RT3' $O/A-t$t-$a.txt | head -1
  done
done
for t in 129 287; do
  for a in pv_acc_rescale_forged pv_p_word_forged short_chunk_end_moved short_chunk_counter short_chunk_cv_public; do
    RT3=$a fr A-t$t-$a cap-t$t --only honest; grep -h '^NEG' $O/A-t$t-$a.txt | grep -o '"accepted":[a-z]*\|"reps_ok":[^]]*]]' | head -2; grep -h '^RT3' $O/A-t$t-$a.txt | head -1
  done
done
# 4b. load tampers (must be REFUSED at load), consistent restatements (load passes, the honest-plan proof must be refused)
for t in 129 287; do
  FT=$D/ft-t$t; mkdir -p $FT
  $PY $E/frame_tamper3.py $(ls $D/cap-t$t/frame-*.bin | head -1) $D/cap-t$t/net.txt $FT $D/cap-t130/net.txt > $O/frame-tamper-t$t.txt 2>&1; cat $O/frame-tamper-t$t.txt
  for f in $FT/f-*.bin; do n=$(basename $f .bin)
    $PO loadcheck --instances $f --netlist $D/cap-t$t/net.txt --pin $(cat $D/cap-t$t/pin) --tables $T > $O/L-t$t-$n.txt 2>&1; rc=$?
    echo "== L-t$t-$n rc=$rc $(grep -h 'REFUSED\|panicked' $O/L-t$t-$n.txt | head -1 | cut -c1-240)"
  done
  for f in $FT/r-*.bin; do n=$(basename $f .bin)
    $PO loadcheck --instances $f --netlist $D/cap-t$t/net.txt --pin $(cat $D/cap-t$t/pin) --tables $T > $O/R0-t$t-$n.txt 2>&1; rc=$?
    echo "== R0-t$t-$n load rc=$rc (want 0) $(grep -h 'REFUSED' $O/R0-t$t-$n.txt | head -1 | cut -c1-200)"
    $PO selftest --only honest --instances $f --netlist $D/cap-t$t/net.txt --pin $(cat $D/cap-t$t/pin) --tables $T > $O/R-t$t-$n.txt 2>&1
    echo "== R-t$t-$n $(grep -h '^NEG' $O/R-t$t-$n.txt | grep -o '"accepted":[a-z]*\|"reps_ok":[^]]*]]' | head -2 | tr '\n' ' ')"
  done
done
# the T=129 file under the T=130 netlist and pin (the verifier's pin fixes T)
$PO loadcheck --instances $(ls $D/cap-t129/frame-*.bin) --netlist $D/cap-t130/net.txt --pin $(cat $D/cap-t130/pin) --tables $T > $O/L-t129-under-t130.txt 2>&1
echo "== L-t129-under-t130 rc=$? $(grep -h REFUSED $O/L-t129-under-t130.txt | head -1 | cut -c1-200)"
# 4c. live sessions: a T=129 prover against a T=130 verifier; a prover with other T=129 heads against the verifier's
sess() {  # tag verifier_dir prover_dir
  local port=$((7600 + RANDOM % 300))
  $PO serve --listen 127.0.0.1:$port --out $O/sess-$1 --instances $(ls $D/$2/frame-*.bin) --netlist $D/$2/net.txt --pin $(cat $D/$2/pin) --tables $T --sessions 1 > $O/serve-$1.txt 2>&1 &
  local sp=$!; sleep 4
  timeout 600 $PO prove --verifier 127.0.0.1:$port --instances $(ls $D/$3/frame-*.bin) --netlist $D/$3/net.txt --tables $T > $O/prove-$1.txt 2>&1
  sleep 2; kill $sp 2>/dev/null; wait $sp 2>/dev/null
  echo "== X-$1 $(grep -ho '"accepted":[a-z]*' $O/prove-$1.txt | head -1) $(grep -h 'SESSION' $O/serve-$1.txt | cut -c1-200) $(grep -h 'REFUSED' $O/prove-$1.txt | head -1 | cut -c1-200)"
}
$PY $E/mkset.py captured $PS 129 8 $S/cap-t129b > /dev/null
$PY - $S/cap-t129b/attention-head-fa2-d64-bn128 $D/cap-t129b <<'EOF'
import hashlib, sys
from pathlib import Path
from verity_numerical.bench.input_sets import InputSet
from verity_flock import ir_frame
from verity_flock.templates import attention_head as AH
s = InputSet.open(sys.argv[1]); low = AH.lowering_for_set(s)
print(ir_frame.stage(low, s, 4, 8, sys.argv[2])); Path(sys.argv[2], "pin").write_text(hashlib.sha256(low.text.encode()).hexdigest())
EOF
sess honest-t129 cap-t129 cap-t129
sess t129-prover-t130-verifier cap-t130 cap-t129
sess other-heads-t129 cap-t129 cap-t129b
# 5. the tail primitives through the crate's own ir_tail (this build) vs the IR: exhaustive unary, 10^6 per binary/ternary
$PY $E/tail3_diff.py $H $T 1000000 AB 256 > $O/tail3-diff.txt 2>&1; cat $O/tail3-diff.txt
true
