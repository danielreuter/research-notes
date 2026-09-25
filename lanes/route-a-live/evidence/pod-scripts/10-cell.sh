#!/usr/bin/env bash
# route-a-live: the route (a) cell with live prime coins. Builds flock-link + verity-gkr-verify from this tree, runs the
# unit tests and the flock-link selftest, builds (or reuses) the 4096-VU statement, then SESSIONS sessions (+ WARMUP)
# against VERIFIER (host:port) or a loopback cell-serve (never evidence), and with NEGS=1 the full-scale negatives
# (a stale prime state: a coin before its commitment; a Fiat-Shamir prime prover against the live verifier) and the
# gate battery (gate_battery.py: admission, G2 replay, tampered records, cross-session prime coins).
# env: VUS=4096 SESSIONS=2 WARMUP=1 VERIFIER= RTT_PROBE=host:sshport SELFTEST=1 NEGS=1 RESULT= STATEMENT_ONLY=
set -uxo pipefail
SRC=$(pwd); I=$RESEARCH_RUN_DIR/inputs; source /workspace/env.sh; source $HOME/.cargo/env
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC:$SRC/backends/gkr"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
O=$RESEARCH_RUN_DIR/out; mkdir -p $O
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH
F=/workspace/flock-link/flock
cd $F && git checkout -q -- . && rm -rf crates/flock-live && git apply $SRC/backends/flock/flock-link-b684b12.patch || exit 1
cp -r $SRC/backends/flock/live crates/flock-live
grep -q '"crates/flock-live"' Cargo.toml || sed -i 's|    "crates/flock-transcript",|    "crates/flock-transcript",\n    "crates/flock-live",|' Cargo.toml
cargo build --release -p flock-live -j $TH 2>&1 | grep -E '^(error|warning)|-->|Finished' | head -30
B=${CARGO_TARGET_DIR:-$F/target}/release/flock-link; [ -x $B ] || exit 1
cd $SRC/backends/gkr/verifier && cargo build --release 2>&1 | grep -E '^error|Finished' | head; cargo test --release 2>&1 | grep -E 'test result|FAILED' | tee $O/cargo-test.txt
VB=/workspace/bin/verity-gkr-verify-live; mkdir -p /workspace/bin; cp ${CARGO_TARGET_DIR:-target}/release/verity-gkr-verify $VB; sha256sum $VB $B | tee $O/binaries.sha256
cd $SRC/backends/gkr
$PY -m pytest -q tests/test_live_coins.py tests/test_cell_gate.py tests/test_commit.py tests/test_circuit_pins.py 2>&1 | tail -3 | tee $O/pytest.txt
[ -n "${SELFTEST:-}" ] && { $B selftest --vus 8 > $O/selftest-8.txt 2>&1; grep -E '^(NEG|SELFTEST)' $O/selftest-8.txt | cut -c1-260; grep -c '"pass":false' $O/selftest-8.txt; }
lscpu | grep 'Model name'; nvidia-smi --query-gpu=name --format=csv,noheader
v=${VUS:-4096}; CELL=/workspace/cell/c$v
[ -f $CELL/cell.json ] || $PY tools/cell.py statement --cell $CELL --instances /workspace/bench-instances/v1 --vus $v --flock $B || exit 1
cp -r $CELL/statement $O/statement-$v; cp $CELL/cell.json $O/cell-$v.json; cp $CELL/leaf_digests.bin $O/leaf_digests-$v.bin
[ -n "${STATEMENT_ONLY:-}" ] && exit 0
PC=$($PY -c "import json;print(json.load(open('$CELL/cell.json'))['prime_commitment'])")
ADDR=${VERIFIER:-}
if [ -z "$ADDR" ]; then
  $B cell-serve --listen 127.0.0.1:7200 --out $O/sessions-$v --vus $v --digests $CELL/leaf_digests.bin --prime-commitment $PC \
    --operator loopback-selftest > $O/serve-$v.log 2>&1 &
  SP=$!; ADDR=127.0.0.1:7200
  for i in $(seq 120); do grep -q SERVING $O/serve-$v.log && break; sleep 1; done
fi
RTT=; if [ -n "${RTT_PROBE:-}" ]; then
  RTT=$($PY -c "import socket,time,statistics as S;h,p='${RTT_PROBE}'.split(':');t=[]
for _ in range(20):
    a=time.perf_counter();c=socket.create_connection((h,int(p)),timeout=3);t.append((time.perf_counter()-a)*1e3);c.close();time.sleep(0.05)
print(round(S.median(t),3))"); echo "RTT probe $RTT_PROBE: $RTT ms" | tee -a $O/rtt.txt
fi
$PY tools/cell.py prove --cell $CELL --flock $B --verifier $ADDR --sessions ${SESSIONS:-2} --warmup ${WARMUP:-1} --rust $VB --threads $TH \
  ${VERIFIER:+--result ${RESULT:-$O/result-$v.json}} ${RTT:+--rtt-ms $RTT --rtt-method "median of 20 TCP connects to the verifier pod's ssh port ($RTT_PROBE)"} 2>&1 | tee $O/cell-$v.txt
mkdir -p $O/cell-$v; for s in $CELL/s*; do d=$O/cell-$v/$(basename $s); mkdir -p $d; cp $s/*.json $s/*.txt $s/*.jsonl $s/proof.bin $d/ 2>/dev/null; done
if [ -n "${NEGS:-}" ]; then
  # a stale prime state at round 5 (the message after its coin), and a Fiat-Shamir prime prover: one session each
  for neg in stale fs; do
    NC=/workspace/cell/neg-$neg; rm -rf $NC; mkdir -p $NC; cp -r $CELL/statement $CELL/cell.json $CELL/leaf_digests.bin $CELL/operands.bin $CELL/y.npy $NC/
    [ -f $CELL/prime_soundness.json ] && cp $CELL/prime_soundness.json $NC/
    if [ $neg = stale ]; then X="--neg-stale-round 5"; else X="--prime-coins fs"; fi
    timeout 900 $PY tools/cell.py prove --cell $NC --flock $B --verifier $ADDR --sessions 1 --warmup 0 --rust $VB --threads $TH $X > $O/neg-$neg.txt 2>&1
    echo "neg-$neg rc=$?" | tee -a $O/neg-rc.txt; tail -3 $O/neg-$neg.txt
    mkdir -p $O/neg-$neg; for s in $NC/s*; do d=$O/neg-$neg/$(basename $s); mkdir -p $d; cp $s/*.json $s/*.txt $s/*.jsonl $s/*.stderr $s/proof.bin $d/ 2>/dev/null; done
  done
fi
[ -n "${SP:-}" ] && { sleep 3; kill $SP; wait $SP 2>/dev/null; unset SP; }
if [ -n "${NEGS:-}" ] && [ -z "${VERIFIER:-}" ]; then
  $PY $I/gate_battery.py --sessions $O/sessions-$v --cells $O/cell-$v --neg-stale $O/neg-stale --statement $O/statement-$v \
    --digests $CELL/leaf_digests.bin --prime-commitment $PC --vus $v --rust $VB --flock $B --threads $TH \
    --producer route-a-live --producer loopback-selftest --out $O/gate 2>&1 | tail -40
fi
true
