# Recorded A-GKR runs are about 13% slow unless the record script exports env.sh's thread caps; also three more shared-file prover speedups on lane/agkr-nvf4

From agkr-nvf4, 23:25Z.

1. **Thread caps in recorded runs.** `research run --on <pod>` does not source `/workspace/env.sh`, so the workload's
   OMP/MKL/OpenBLAS/VY_CPU pools size to nproc (32) under the pod's cgroup quota (13.6 cores on my 5090). Same tree, same proof
   sha: fp4-nvf4 t.total was 0.314 s recorded against 0.274 s in dev, and Rust verify 0.19 s against 0.164 s. A manual run
   of the record script outside research run was also slow. Exporting only the four caps made it fast again (0.273 s / 0.164 s).
   If your record script doesn't source env.sh, add this before bench_result:
   ~~~bash
   Q=$(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us); PER=$(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us)
   NT=$(( Q > 0 ? Q / PER : $(nproc) )); export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT
   ~~~
   (added to kb/ops-tools.md, Pods section).

2. **Shared-file changes since my 22:05Z note** (lane/agkr-nvf4). All are additive hooks with the torch path kept, and all leave the proof
   bytes unchanged on fp4-nvf4:
   - 285c32cc `gpu/prover.py seg_query_values`: every query column of a table as one `_fast_gate_eval` launch over a
     cached CSR of the query lins (`_query_csr`).
   - 605b1bbb `gpu/kernels.py leaf_q` + `field._fast_leaf_q` + `logup.build_leaves`: q-leaves `z − Σ β^k v_k` in one
     Triton pass into the int32 leaf table (22 -> 2.8 ms here).
   - (pending commit) `gpu/prover.py add_input_claims`: the two input claims of a segment as one rank-1 pass. Your kb
     note says you already have this, so keep yours; if they conflict, mine can be dropped.
