#!/usr/bin/env bash
# agkr-flock-cell: build flock-link (patch + live crate) and the gkr verifier from this tree, then per VUS: the cell
# statement and SESSIONS sessions of the prime prover + Flock prover against VERIFIER (host:port), or a loopback
# cell-serve when VERIFIER is empty (a self-test: the loopback operator is the producer, never evidence).
# env: RTT_PROBE=host:sshport  FRESH_STATEMENT=1 (rebuild, timing the serving commit)  VUS="8"  SESSIONS=2  WARMUP=1  VERIFIER=  WARMUP_LOCAL= (warm-ups against a loopback verifier)  RESULT=  STATEMENT_ONLY=
set -uxo pipefail
SRC=$(pwd); source /workspace/env.sh; source $HOME/.cargo/env
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC:$SRC/backends/gkr"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
O=$RESEARCH_RUN_DIR/out; mkdir -p $O
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH
F=/workspace/flock-link/flock
cd $F && git checkout -q -- . && rm -rf crates/flock-live && git apply $SRC/backends/flock/flock-link-b684b12.patch || exit 1
cp -r $SRC/backends/flock/live crates/flock-live
grep -q '"crates/flock-live"' Cargo.toml || sed -i 's|    "crates/flock-transcript",|    "crates/flock-transcript",\n    "crates/flock-live",|' Cargo.toml
cargo build --release -p flock-live -j $TH 2>&1 | tail -5
B=${CARGO_TARGET_DIR:-$F/target}/release/flock-link; [ -x $B ] || exit 1
cd $SRC/backends/gkr/verifier && cargo build --release 2>&1 | grep -E '^error|Finished' | head; cargo test --release 2>&1 | grep -E 'test result|FAILED' | head -4
VB=/workspace/bin/verity-gkr-verify-cell; cp $CARGO_TARGET_DIR/release/verity-gkr-verify $VB; sha256sum $VB $B | tee $O/binaries.sha256
cd $SRC/backends/gkr
[ -s /workspace/cell/commit-pin.txt ] || $PY -m gpu.commit pin bf16-ampere --leaf blake3 --instances /workspace/bench-instances/v1 > /workspace/cell/commit-pin.txt 2>&1
cp /workspace/cell/commit-pin.txt $O/
$PY -m pytest -q tests/test_cell_gate.py 2>&1 | tail -2
lscpu | grep 'Model name'; nvidia-smi --query-gpu=name --format=csv,noheader
for v in ${VUS:-8}; do
  CELL=/workspace/cell/c$v
  [ -n "${FRESH_STATEMENT:-}" ] && rm -f $CELL/cell.json
  [ -f $CELL/cell.json ] || $PY tools/cell.py statement --cell $CELL --instances /workspace/bench-instances/v1 --vus $v --flock $B || exit 1
  cp -r $CELL/statement $O/statement-$v; cp $CELL/cell.json $O/cell-$v.json; cp $CELL/leaf_digests.bin $O/leaf_digests-$v.bin
  [ -n "${STATEMENT_ONLY:-}" ] && continue
  ADDR=${VERIFIER:-}; WV=
  if [ -z "$ADDR" ] || [ -n "${WARMUP_LOCAL:-}" ]; then
    PC=$($PY -c "import json;print(json.load(open('$CELL/cell.json'))['prime_commitment'])")
    $B cell-serve --listen 127.0.0.1:7200 --out $O/sessions-$v --vus $v --digests $CELL/leaf_digests.bin --prime-commitment $PC \
      --operator loopback-selftest > $O/serve-$v.log 2>&1 &
    SP=$!; WV=127.0.0.1:7200; [ -z "$ADDR" ] && ADDR=$WV
    for i in $(seq 120); do grep -q SERVING $O/serve-$v.log && break; sleep 1; done
  fi
  RTT=; if [ -n "${RTT_PROBE:-}" ]; then
    # RTT: median TCP connect time to the verifier pod's ssh port (never its session port: a bare connection is a session)
    RTT=$($PY -c "import socket,time,statistics as S;h,p='${RTT_PROBE}'.split(':');t=[]
for _ in range(20):
    a=time.perf_counter();c=socket.create_connection((h,int(p)),timeout=3);t.append((time.perf_counter()-a)*1e3);c.close();time.sleep(0.05)
print(round(S.median(t),3))"); echo "RTT probe $RTT_PROBE: $RTT ms" | tee -a $O/rtt.txt
  fi
  $PY tools/cell.py prove --cell $CELL --flock $B --verifier $ADDR --sessions ${SESSIONS:-2} --warmup ${WARMUP:-1} --rust $VB --threads $TH ${WV:+--warmup-verifier $WV} --result ${RESULT:-$O/result-$v.json} ${RTT:+--rtt-ms $RTT --rtt-method "median of 20 TCP connects to the verifier pod's ssh port ($RTT_PROBE)"} 2>&1 | tee $O/cell-$v.txt
  mkdir -p $O/cell-$v; for s in $CELL/s*; do d=$O/cell-$v/$(basename $s); mkdir -p $d; cp $s/*.json $s/*.txt $s/*.jsonl $s/proof.bin $d/ 2>/dev/null; done
  [ -n "${SP:-}" ] && { sleep 3; kill $SP; wait $SP 2>/dev/null; unset SP; }
done
true
