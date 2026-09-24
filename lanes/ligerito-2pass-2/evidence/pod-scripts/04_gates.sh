# item 3: gates at the 11-coin default (sumcheck-3 @58e76e5d merged), tree /workspace/src @ e0c7acd2
# 5 relations x {non-ZK, --zk (LIGERITO_ZK_REBUILD_F=1, the 4096-VU fold path)} + fp8-ada --zk default path; Rust = pinned ligerito-verify
source /workspace/env.sh; cd /workspace/src; G=/workspace/ligerito-2pass-2/gates; mkdir -p $G
RV=/workspace/cargo-target/release/ligerito-verify
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
for r in fp8-ada bf16-hopper fp8-hopper bf16-ampere fp4-nvf4; do
  $PY -m backends.direct.ligerito.run gate --relation $r --dump-dir $G/$r-nonzk --out $G/$r-nonzk.json --rust-verifier $RV > $G/$r-nonzk.log 2>&1 &
  LIGERITO_ZK_REBUILD_F=1 $PY -m backends.direct.ligerito.run gate --relation $r --zk --dump-dir $G/$r-zk --out $G/$r-zk.json --rust-verifier $RV > $G/$r-zk.log 2>&1 &
done
$PY -m backends.direct.ligerito.run gate --relation fp8-ada --zk --dump-dir $G/fp8-ada-zk-default --out $G/fp8-ada-zk-default.json --rust-verifier $RV > $G/fp8-ada-zk-default.log 2>&1 &
wait; echo GATES_DONE > $G/DONE
