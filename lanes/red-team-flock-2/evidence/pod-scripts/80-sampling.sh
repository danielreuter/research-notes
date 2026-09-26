#!/usr/bin/env bash
# red-team-flock-2: verity/flock-ir-sampling/v1 at PR #65 @ af0bd416, CPU only.
#  1. build flock-ir-sampling; stage a synthetic GumbelTopPTokenSelect_v1{V=1280} set (3 rows) the way the verifier does
#  2. my checks on it (samp_check.py net / file / lanes) and the producer's selftest
#  3. samp_tamper.py's files through the real verifier path: serve (--pin, --native-checked <the file's public sha256>) and a
#     loopback prove on the same file; plus the chain-broken netlist under the honest pin and under its own
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O; SRC=$(pwd)
sha256sum $I/* | tee $O/inputs.sha256
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build-base.txt 2>&1 || { tail -60 $O/build-base.txt; exit 1; }
source $HOME/.cargo/env
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH
W=/workspace/flock-gpu-link/flock
(cd $W && cargo build --release -p flock-live --bin flock-ir-sampling -j $TH) > $O/build-ir.txt 2>&1 || { tail -40 $O/build-ir.txt; exit 1; }
B=$W/target/release/flock-ir-sampling; sha256sum $B | tee $O/binary.sha256
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh > $O/uv-install.txt 2>&1; }
export PATH=$HOME/.local/bin:$HOME/.cargo/bin:$PATH
uv python install 3.12 > $O/uv-python.txt 2>&1 || { tail -5 $O/uv-python.txt; exit 1; }
PY="uv run --python 3.12 --no-project --with numpy --with blake3 python3"
export PYTHONPATH=$SRC/backends/flock/python:$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/integrations/vllm:$SRC/backends/direct
D=$O/files; T=$O/tables; mkdir -p $D
$PY - <<'EOF' 2>&1 | tee $O/stage.txt
import hashlib, os
from verity_flock import ir_sampling as S, ir_lower as IL
from verity_numerical.bench import templates as TM
from verity_numerical.bench.generate import generate
from verity_numerical.bench.input_sets import InputSet
O = os.environ["RESEARCH_RUN_DIR"] + "/out"; D = O + "/files"
V = 1280
s = InputSet.open(generate(TM.subcircuit(S.TEMPLATE, V=V), 3, 20260926, D + "/set")["path"])
p = S.stage(S.lane(V), s, 0, s.n, D + "/st")
print("TABLES", IL.write_tables(O + "/tables"))
print("STAGED", p, S.public_sha256(p), S.check_native(p) or "check_native clean")
EOF
F=$D/st/frame-3.bin; NET=$D/st/net.txt; PIN=$(sha256sum $NET | cut -d' ' -f1)
$PY $I/samp_check.py net $NET 1280 2>&1 | tee $O/check-net.txt
$PY $I/samp_check.py file $F $NET 3 2>&1 | tee $O/check-file.txt
$PY $I/samp_check.py lanes $NET 1280 100000 11 2>&1 | tee $O/check-lanes.txt
$B selftest --tables $T --instances $F --netlist $NET > $O/selftest-cpu.txt 2>&1
grep -h 'SELFTEST\|"pass":false\|REFUSED' $O/selftest-cpu.txt | cut -c1-400
$PY $I/samp_tamper.py $F $NET $D/t 2>&1 | tee $O/tamper.txt
PORT=7410
sv() {  # tag file netlist pin native_checked
  local tag=$1 f=$2 net=$3 pin=$4 chk=$5; PORT=$((PORT + 1))
  $B serve --listen 127.0.0.1:$PORT --out $O/sess-$tag --tables $T --instances $f --netlist $net --pin $pin --native-checked $chk \
     --sessions 1 --operator red-team-flock-2 > $O/serve-$tag.log 2>&1 &
  local sp=$!
  for i in $(seq 600); do grep -q 'SERVING\|REFUSED' $O/serve-$tag.log && break; sleep 1; done
  if grep -q REFUSED $O/serve-$tag.log; then
    echo "== $tag: REFUSED at load: $(grep -h REFUSED $O/serve-$tag.log | cut -c1-300)"; wait $sp 2>/dev/null; return
  fi
  timeout 900 $B prove --verifier 127.0.0.1:$PORT --tables $T --instances $f --netlist $net --runs 1 > $O/prove-$tag.txt 2>&1
  for i in $(seq 60); do grep -q '^SESSION' $O/serve-$tag.log && break; sleep 1; done
  echo "== $tag: $(grep -h '^SESSION' $O/serve-$tag.log | cut -c1-320)"
  echo "   prover: $(grep -h '^LIVE' $O/prove-$tag.txt | grep -o '"accepted":[a-z]*' | head -1) $(grep -h 'REFUSED\|refused\|panicked' $O/prove-$tag.txt | head -1 | cut -c1-200)"
  kill $sp 2>/dev/null; wait $sp 2>/dev/null
}
sv honest $F $NET $PIN $($PY -c "from verity_flock import ir_sampling as S; print(S.public_sha256('$F'))")
while IFS=$'\t' read -r tag name path sha what nat; do
  [ "$tag" = CASE ] || continue
  echo "-- $name: $what; $nat"
  if [ "$name" = cut_chain_broken ]; then
    NB=$D/t/net-chain-broken.txt
    sv $name-honest-pin $path $NB $PIN $sha
    sv $name-own-pin $path $NB $(sha256sum $NB | cut -d' ' -f1) $sha
  else
    sv $name $path $NET $PIN $sha
  fi
done < $O/tamper.txt
K=$(awk -F'\t' '$2 == "kbit_forged" {print $4}' $O/tamper.txt)
sv attest_names_another_file $F $NET $PIN $K
true
