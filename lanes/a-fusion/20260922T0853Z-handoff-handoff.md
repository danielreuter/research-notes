---
id: r20-proof/a-fusion/20260922T0853Z-handoff-handoff
campaign: r20-proof
lane: a-fusion
kind: handoff
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/gkr/packed/HANDOFF.md
---

# a-fusion lane -- HANDOFF

Branch `lane/a-fusion` (worktree `/Users/danielreuter/projects/verity-a-fusion`), pod `vy-g4` (H100, id uktx6i8dejuunk).
Pod working copy: `/workspace/fusion` (synced with `tar | ssh`; ssh `-i ~/.runpod/ssh/runpodctl-ssh-key -p 11461 root@64.247.201.61`).
Kernel cache `PACKED_KERNEL_CACHE=/workspace/fusion/kcache`.  Nothing is running on the pod.

## State (2026-09-22 ~02:30 PDT): deliverables 1-5 done and committed

* Report: `note:r20-proof/a-fusion/20260922T0853Z-report-a-kernels-h100-v2` / `.json`; raw results `backends/numerical/reports/a_fusion/`
  (`notes-asset:campaigns/r20-proof/assets/a-fusion/reports/a_fusion/logup_graph_v1.json`, `notes-asset:campaigns/r20-proof/assets/a-fusion/reports/a_fusion/logup_graph_v2.json`, `logup_graph_v2_concurrent.json`, `bench_fused_k3.json`, `notes-asset:campaigns/r20-proof/assets/a-fusion/reports/a_fusion/bench_fused_2p26_ks.json`).
* Ledger `backends/numerical/reports/ledger/a-fusion.jsonl`: 2 component entries (graphed logUp v1; U-pass sumcheck), 2 vu
  entries (A v1 7.06e6, A v2 4.64e6; no breakthrough).  Plots regenerated (`plots/overhead_a-fusion.png`).
* Code: `logup_graph.py`, `kernels_graph.py`, `kernels_fused.py`, `kernels_triton.py` (`packed_u_{k}`, `ext_fold_ip`),
  `sumcheck_packed.py` (`round_fusion`, `fold_fusion`, `prove_device`, `prepare_inputs`), `bench_fused.py`, `logup_graph_bench.py`
  (`--modes concurrent`), `reprice_v2.py`, `kernels.py` entry points, tests (`test_logup_graph.py`, `test_vectors.py`,
  `test_kernel_agreement.py::test_round_fusion_matches_reference`).  All CUDA tests green on vy-g4.

## Next three steps (if the lane continues)

1. logUp small levels: a persistent per-level kernel for levels under one wave (17 ms of v1's 89 ms; most of v2's
   per-instance floor), or -- protocol change, needs accounting -- one batched instance over all v2 tables (estimate 25-35 ms).
2. v2 concurrent: the per-round (Fiat-Shamir) segmentation on streams was not measured; the host launch loop (~750 graph
   replays / pinned H2D per proof) limits the overlap -- capture the level graphs of all instances into one graph per level.
3. Sumcheck SIMT floor: the `F_{p^6}` product (36 mmul) in `ext_ip` / `fold_ext` is the bound now (2.87x HBM floor);
   Karatsuba over the 6 coefficients or 2x16-bit limbs feeding `tl.dot` directly.
