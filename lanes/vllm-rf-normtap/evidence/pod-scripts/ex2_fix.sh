#!/usr/bin/env bash
# ex2_fix.sh: the MufuEx2Ftz shift clamp (fa2_model.cpp mufu_ex2_bits) on the CPU, in git clones of the shipped fix commit and of MAIN_SHA.
#  (1) the two new tests on the fix, and on main's code with the fix's test files laid over it (they must fail there); the core
#      evaluation tests (packages/verity/tests/evaluation) on the fix;
#  (2) ex2_sweep.py: all 2^32 f32 words through each tree's compiled rule and the fix's numpy twin;
#  (3) SP1: `cargo test --release -p veritor-zk-common` on the fix, and a sweep crate over its `mufu_ex2_tab`; flock: ir_tail.rs's
#      `mufu_ex2` compiled standalone in the same crate; both digest-compared with the fix's compiled rule over all 2^32 words;
#  (4) ex2_census.py: #101's committed layer-0 FA2 streams (steps 0 and 1, sent with the run).
# usage: research run --on <pod> --project verity --source <fix worktree> --cwd source --custody-r2 --env MAIN_SHA=<sha> [--env WAIT_RUN=..]
#          --send ex2_fix.sh --send ex2_sweep.py --send ex2_census.py --send <the two dumps> -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/ex2_fix.sh"'
set -u
S=$PWD; OUT=$RESEARCH_RUN_DIR; IN=$OUT/inputs; EV=$OUT/evidence; mkdir -p "$EV"; ROOT=/workspace/research; W=/workspace/gc3
T=$W/fix; TM=$W/main; TMO=$W/main_newtests
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
export PATH=/workspace/venv312/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=""
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO VERITY_NUMERICS_BUILD_DIR
mkdir -p $W; rm -rf $T $TM $TMO
git clone -q --no-checkout $ROOT/git/verity.git $T && git -C $T checkout -q --detach "$RESEARCH_SOURCE_SHA" || { echo "CLONE-FAIL $RESEARCH_SOURCE_SHA"; exit 3; }
d=$(diff -rq -x .git -x __pycache__ -x READY.json $S $T | grep -v "^Only in $S" | wc -l); echo "tree $T @ $(git -C $T rev-parse HEAD) vs shipped: $d differing entries"
[ "$d" = 0 ] || exit 4
for R in $TM $TMO; do git clone -q --no-checkout $ROOT/git/verity.git $R && git -C $R checkout -q --detach "${MAIN_SHA:?}" || { echo "CLONE-FAIL main"; exit 3; }; done
cp $T/integrations/vllm/tests/program/test_derived_rows.py $T/integrations/vllm/tests/program/test_kernel_self_check.py $TMO/integrations/vllm/tests/program/
echo "main $(git -C $TM rev-parse HEAD); fix parents $(git -C $T log -1 --format=%P); fix vs main: $(git -C $T diff --stat $MAIN_SHA | tail -1)"
pp() { echo "$1/integrations/vllm:$1/packages/verity/src:$1/tools/research/src:$1/protocols/sampled_proofs"; }

# (1) the new tests: pass on the fix, fail on main's code
NEW="integrations/vllm/tests/program/test_derived_rows.py::test_ex2_every_exponent_class_equals_the_exact_rule integrations/vllm/tests/program/test_kernel_self_check.py::test_attention_kernels_on_scores_below_two_to_the_minus_63"
for R in $T $TMO; do
  n=$(basename $R)
  (cd $R && PYTHONPATH=$(pp $R) python -m pytest $NEW -q -p no:cacheprovider -rA > $EV/newtests_$n.log 2>&1)
  echo "new tests on $n rc=$? $(tail -1 $EV/newtests_$n.log)"
done
(cd $T && PYTHONPATH=$(pp $T) python -m pytest packages/verity/tests/evaluation -q -p no:cacheprovider > $EV/core_evaluation_fix.log 2>&1)
echo "packages/verity/tests/evaluation on fix rc=$? $(tail -1 $EV/core_evaluation_fix.log)"

# (2) the exhaustive sweep (each tree compiles its own libfa2_model.so under its cpp/build)
LIBS=()
for R in $T $TM; do
  LIBS+=("$(cd $R/integrations/vllm && PYTHONPATH=$(pp $R) python -c 'from verity_vllm.program.kernels import fa2_model as F; print(F.build(force=True))' 2>>$EV/build.log | tail -1)")
done
echo "libs ${LIBS[*]}"
(cd $T && PYTHONPATH=$(pp $T) python -c 'from verity_vllm.program.kernels import fa2_relation as R; import sys; R.tables().ex2.astype("<u4").tofile(sys.argv[1])' $W/ex2.u32)
python $IN/ex2_sweep.py $T $TM "${LIBS[0]}" "${LIBS[1]}" $EV > $EV/sweep.log 2>&1; echo "sweep rc=$? $(date -u +%FT%TZ)"

# (3) SP1 and flock
command -v cargo >/dev/null || (curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable > $EV/rustup.log 2>&1)
echo "cargo $(cargo --version 2>&1)"
(cd $T/backends/sp1 && cargo test --release -j 6 -p veritor-zk-common > $EV/sp1_common_tests.log 2>&1); echo "sp1 cargo test rc=$? $(grep -E '^test result' $EV/sp1_common_tests.log | awk '{p+=$4; f+=$6} END {print p" passed, "f" failed"}')"
grep -E "ex2_reduction|inv_sum_rule" $EV/sp1_common_tests.log
X=$W/ex2sweep; rm -rf $X; mkdir -p $X/src
cat > $X/Cargo.toml <<EOF
[package]
name = "ex2sweep"
version = "0.1.0"
edition = "2021"

[dependencies]
veritor-zk-common = { path = "$T/backends/sp1/common" }
sha2 = "0.10.9"

[workspace]
EOF
python - $T/backends/flock/live/src/ir_tail.rs $X/src/flock_mufu_ex2.rs <<'PY'
import sys
src = open(sys.argv[1]).read()
i = src.index("\nfn mufu_ex2(")
open(sys.argv[2], "w").write(src[i:src.index("\n}\n", i) + 3])
PY
cat > $X/src/main.rs <<'EOF'
use sha2::{Digest, Sha256};
use std::sync::Arc;
use veritor_zk_common::ftz::{mufu_ex2_index, mufu_ex2_tab};

include!("flock_mufu_ex2.rs");

fn main() {
    let mut args = std::env::args().skip(1);
    let mode = args.next().expect("sp1 | flock");
    let raw = std::fs::read(args.next().expect("ex2.u32")).expect("table");
    let t: Arc<Vec<u32>> = Arc::new(raw.chunks_exact(4).map(|c| u32::from_le_bytes([c[0], c[1], c[2], c[3]])).collect());
    assert_eq!(t.len(), 1 << 23);
    const PER: u64 = 1 << 24;
    const CHUNKS: u64 = 256;
    const THREADS: u64 = 6;
    let handles: Vec<_> = (0..THREADS)
        .map(|w| {
            let (t, sp1) = (t.clone(), mode == "sp1");
            std::thread::spawn(move || {
                let (mut out, mut buf) = (Vec::new(), Vec::with_capacity((PER * 4) as usize));
                let mut k = w;
                while k < CHUNKS {
                    buf.clear();
                    for x in k * PER..(k + 1) * PER {
                        let y = if sp1 {
                            let j = mufu_ex2_index(x);
                            mufu_ex2_tab(x, (j << 32) | u64::from(t[j as usize])).expect("the opened row") as u32
                        } else {
                            mufu_ex2(x as u32, &t)
                        };
                        buf.extend_from_slice(&y.to_le_bytes());
                    }
                    let d: String = Sha256::digest(&buf).iter().map(|b| format!("{b:02x}")).collect();
                    out.push((k, d));
                    k += THREADS;
                }
                out
            })
        })
        .collect();
    let mut all: Vec<(u64, String)> = handles.into_iter().flat_map(|h| h.join().unwrap()).collect();
    all.sort();
    for (_, d) in all {
        println!("{d}");
    }
}
EOF
(cd $X && cargo build --release -j 6 > $EV/ex2sweep_build.log 2>&1); echo "ex2sweep build rc=$?"
cp $X/src/flock_mufu_ex2.rs $X/src/main.rs $X/Cargo.toml $EV/ 2>/dev/null
for mode in sp1 flock; do
  t0=$(date +%s); $X/target/release/ex2sweep $mode $W/ex2.u32 > $EV/rust_$mode.sha256 2> $EV/rust_$mode.err
  echo "rust sweep $mode rc=$? lines $(wc -l < $EV/rust_$mode.sha256) $(( $(date +%s) - t0 ))s"
done
python - $EV <<'PY'
import json, sys
ev = sys.argv[1]
s = json.load(open(f"{ev}/sweep.json"))
out = {k: (open(f"{ev}/rust_{k}.sha256").read().split() == s["chunk_sha256"]) for k in ("sp1", "flock")}
print(json.dumps({"rust_equals_compiled_rule_over_2^32": out}))
json.dump(out, open(f"{ev}/rust_vs_cpp.json", "w"))
PY

# (4) the #101 census
python $IN/ex2_census.py $T $EV $IN/dump_step0_pair0_fa2.m1_L0_g32x256x2.bin $IN/dump_step1_pair0_fa2.m1_L0_g8x4x3.bin > $EV/census.log 2>&1
echo "census rc=$? $(date -u +%FT%TZ)"
python - $EV <<'PY'
import json, sys
ev = sys.argv[1]
s = json.load(open(f"{ev}/sweep.json")); c = json.load(open(f"{ev}/census.json")); r = json.load(open(f"{ev}/rust_vs_cpp.json"))
summ = {"sweep": {k: v for k, v in s.items() if k != "chunk_sha256"}, "rust_equals_compiled_rule_over_2^32": r, "census_101_layer0": c}
json.dump(summ, open(f"{ev}/summary.json", "w"), indent=1)
print(json.dumps(summ, indent=1))
PY
echo "EX2-FIX-DONE $(date -u +%FT%TZ)"
