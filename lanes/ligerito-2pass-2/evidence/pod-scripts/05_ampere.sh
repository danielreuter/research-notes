# bf16-ampere gates need fixtures/bench-instances/v1 (pod_bootstrap BENCH_INSTANCES=1), then rerun its two gates
source /workspace/env.sh; G=/workspace/ligerito-2pass-2/gates
RELS=fp8-ada NS=4096 BENCH_INSTANCES=1 SKIP_RUST=1 bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh > /workspace/ligerito-2pass-2/bootstrap_bench.log 2>&1
cd /workspace/src; RV=/workspace/cargo-target/release/ligerito-verify
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2; r=bf16-ampere
rm -rf $G/$r-nonzk $G/$r-zk
$PY -m backends.direct.ligerito.run gate --relation $r --dump-dir $G/$r-nonzk --out $G/$r-nonzk.json --rust-verifier $RV > $G/$r-nonzk.log 2>&1 &
LIGERITO_ZK_REBUILD_F=1 $PY -m backends.direct.ligerito.run gate --relation $r --zk --dump-dir $G/$r-zk --out $G/$r-zk.json --rust-verifier $RV > $G/$r-zk.log 2>&1 &
wait; echo AMPERE_DONE > $G/AMPERE_DONE
