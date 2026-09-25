#!/usr/bin/env bash
# route-a-live: the route (a) cell with live prime coins, and its batch sweep (the recipe of agkr-flock-cell 7585828d:
# the frozen set tiled past 4,096 VUs and flagged, the interactive record, the RTT probe).
#   MODE=probe  build flock-link + verity-gkr-verify from this tree, unit tests, statements for every size in VUS, one
#               loopback live session per size (which sizes fit: $O/probe.tsv), then at NEG_VUS the full-scale
#               negatives (a stale prime state; a Fiat-Shamir prime prover) and gate_battery.py over the loopback records
#   MODE=sweep  per size: 1 local warm-up (loopback verifier) + SESSIONS sessions against VERIFIER, the RTT probe,
#               and the result envelope result-<v>.json (points above 4,096 are tiled: timing only)
# env: MODE  VUS="1024 4096 8192 16384 32768"  SESSIONS=5  VERIFIER=host:port  RTT_PROBE=host:sshport  NEG_VUS=4096
set -uxo pipefail
SRC=$(pwd); I=$RESEARCH_RUN_DIR/inputs; source /workspace/env.sh; source $HOME/.cargo/env
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC:$SRC/backends/gkr"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
O=$RESEARCH_RUN_DIR/out; mkdir -p $O
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH
F=/workspace/flock-link/flock; B=${CARGO_TARGET_DIR:-$F/target}/release/flock-link; VB=/workspace/bin/verity-gkr-verify-live
if [ "${MODE:-probe}" = probe ]; then
  cd $F && git checkout -q -- . && rm -rf crates/flock-live && git apply $SRC/backends/flock/flock-link-b684b12.patch || exit 1
  cp -r $SRC/backends/flock/live crates/flock-live
  grep -q '"crates/flock-live"' Cargo.toml || sed -i 's|    "crates/flock-transcript",|    "crates/flock-transcript",\n    "crates/flock-live",|' Cargo.toml
  cargo build --release -p flock-live -j $TH 2>&1 | grep -E '^(error|warning)|-->|Finished' | head -30
  [ -x $B ] || exit 1
  cd $SRC/backends/gkr/verifier && cargo build --release 2>&1 | grep -E '^error|Finished' | head; cargo test --release 2>&1 | grep -E 'test result|FAILED' | tee $O/cargo-test.txt
  mkdir -p /workspace/bin; cp ${CARGO_TARGET_DIR:-target}/release/verity-gkr-verify $VB
  cd $SRC/backends/gkr
  $PY -m pytest -q tests/test_live_coins.py tests/test_cell_gate.py tests/test_commit.py tests/test_circuit_pins.py 2>&1 | tail -3 | tee $O/pytest.txt
fi
sha256sum $VB $B | tee $O/binaries.sha256
cd $SRC/backends/gkr
lscpu | grep 'Model name'; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
loopback() {  # $1 = vus, $2 = out dir; sets SP
  $B cell-serve --listen 127.0.0.1:7200 --out $2 --vus $1 --digests /workspace/cell/c$1/leaf_digests.bin \
    --prime-commitment $(pc $1) --operator loopback-selftest > $2.log 2>&1 &
  SP=$!; for i in $(seq 240); do grep -q SERVING $2.log && break; sleep 0.5; done
}
pc() { $PY -c "import json;print(json.load(open('/workspace/cell/c$1/cell.json'))['prime_commitment'])"; }
keep() {  # $1 = cell dir, $2 = dest
  mkdir -p $2; for s in $1/s*; do d=$2/$(basename $s); mkdir -p $d; cp $s/*.json $s/*.txt $s/*.jsonl $s/*.stderr $s/proof.bin $d/ 2>/dev/null; done
}
for v in ${VUS:-1024 4096 8192 16384 32768}; do
  CELL=/workspace/cell/c$v
  [ -f $CELL/cell.json ] || $PY tools/cell.py statement --cell $CELL --instances /workspace/bench-instances/v1 --vus $v --flock $B || { echo "statement $v failed"; continue; }
  mkdir -p $O/statements; cp $CELL/cell.json $O/statements/cell-$v.json; cp $CELL/leaf_digests.bin $O/statements/leaf_digests-$v.bin
  [ $v = ${NEG_VUS:-4096} ] && cp -r $CELL/statement $O/statement-$v
  if [ "${MODE:-probe}" = probe ]; then
    loopback $v $O/probe-sessions-$v
    timeout 3000 $PY tools/cell.py prove --cell $CELL --flock $B --verifier 127.0.0.1:7200 --sessions 1 --warmup 0 --rust $VB --threads $TH > $O/probe-$v.txt 2>&1
    rc=$?; kill $SP 2>/dev/null; wait $SP 2>/dev/null
    printf '%s\t%s\t%s\n' $v $rc "$(grep -E '^session|CELL-PROVE|Error|error' $O/probe-$v.txt | tail -2 | tr '\n' ' ' | cut -c1-400)" | tee -a $O/probe.tsv
    keep $CELL $O/probe-cell-$v
  else
    RTT=$($PY -c "import socket,time,statistics as S;h,p='${RTT_PROBE}'.split(':');t=[]
for _ in range(20):
    a=time.perf_counter();c=socket.create_connection((h,int(p)),timeout=3);t.append((time.perf_counter()-a)*1e3);c.close();time.sleep(0.05)
print(round(S.median(t),3))"); echo "$v RTT probe $RTT_PROBE: $RTT ms" | tee -a $O/rtt.txt
    loopback $v $O/warmup-sessions-$v
    $PY tools/cell.py prove --cell $CELL --flock $B --verifier $VERIFIER --warmup-verifier 127.0.0.1:7200 --sessions ${SESSIONS:-5} --warmup 1 \
      --rust $VB --threads $TH --result $O/result-$v.json --rtt-ms $RTT --rtt-method "median of 20 TCP connects to the verifier pod's ssh port ($RTT_PROBE)" 2>&1 | tee $O/cell-$v.txt
    kill $SP 2>/dev/null; wait $SP 2>/dev/null
    keep $CELL $O/cell-$v
  fi
done
if [ "${MODE:-probe}" = probe ] && [ -n "${NEG_VUS:-4096}" ]; then
  v=${NEG_VUS:-4096}; CELL=/workspace/cell/c$v
  loopback $v $O/neg-sessions-$v
  timeout 1800 $PY tools/cell.py prove --cell $CELL --flock $B --verifier 127.0.0.1:7200 --sessions 2 --warmup 0 --rust $VB --threads $TH > $O/neg-honest.txt 2>&1
  echo "neg-honest rc=$?" | tee -a $O/neg-rc.txt; keep $CELL $O/neg-honest
  for neg in stale fs; do
    NC=/workspace/cell/neg-$neg; rm -rf $NC; mkdir -p $NC; cp -r $CELL/statement $CELL/cell.json $CELL/leaf_digests.bin $CELL/operands.bin $CELL/y.npy $NC/
    if [ $neg = stale ]; then X="--neg-stale-round 5"; else X="--prime-coins fs"; fi
    timeout 900 $PY tools/cell.py prove --cell $NC --flock $B --verifier 127.0.0.1:7200 --sessions 1 --warmup 0 --rust $VB --threads $TH $X > $O/neg-$neg.txt 2>&1
    echo "neg-$neg rc=$?" | tee -a $O/neg-rc.txt; tail -3 $O/neg-$neg.txt; keep $NC $O/neg-$neg
  done
  sleep 3; kill $SP 2>/dev/null; wait $SP 2>/dev/null
  $PY $I/gate_battery.py --sessions $O/neg-sessions-$v --cells $O/neg-honest --neg-stale $O/neg-stale --statement $O/statement-$v \
    --digests $CELL/leaf_digests.bin --prime-commitment $(pc $v) --vus $v --rust $VB --flock $B --threads $TH \
    --producer route-a-live --producer loopback-selftest --out $O/gate 2>&1 | tail -30
fi
true
