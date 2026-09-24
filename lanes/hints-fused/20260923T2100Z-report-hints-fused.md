---
lane: hints-fused
kind: report
created: 2026-09-23T21:00Z
status: superseded
---

CHECKPOINT none (00:03Z) [superseded] by hints-fused-2 (coordinator)
# hints-fused — a fused device hint kernel for the v2 / v3 families (unlock folding for the private-safe relations)

CHECKPOINT ff52e47 (21:14Z) fused kernel `hints_fused.py` written + hooked into pubsel/privsel `hints_v2/v3` (LIGERO_FUSED_HINTS, default on); microbench fused vs torch graph 12-31x (fp8-ada-v3x4 l=16384 20.38 -> 1.42 ms); first full differential run: every compared output equal, 4 test errors = 3 CUDA OOM (graph pools accumulated across tests) + 1 stale torch graph replayed via id(sys) reuse (a latent hazard of the torch path's `_GRAPHS` key, test-process only) -> tests now clear the graph caches; rerun + A/B queue chained on the pod.

CHECKPOINT 5e6b3e3 (21:00Z) worktree ~/projects/verity-main-wt/hints-fused on lane/hints-fused at open-fixes 5e6b3e3; 4090 pod vy-hints-fused (RunPod em6u0t7azwt5gu, reference 24564 MiB, US, EPYC 7K62, created 20:54:41Z) bootstrapped; same-pod baselines running on the pristine tree (/workspace/src-base); fused kernel being written.

## Setup

* Base `lane/open-fixes` @ 5e6b3e3 (per-stream hint graphs a0ff818). Predecessor-style reads done: relaunch brief §0/§1.8, leaf-campaign
  §0, open-fixes FINAL, fold-private, relmin-lookup, relmin-private.
* Pod `vy-hints-fused` = RunPod em6u0t7azwt5gu, RTX 4090 24564 MiB (reference part), host AMD EPYC 7K62 (96 threads visible, 12 vCPU
  quota), $0.74/h, created 20:54:41Z. Bootstrap = `lane/qol` `pod_bootstrap.sh` (BOOTSTRAP_OK). Env on every run:
  `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1` (`/workspace/run.sh`, open-fixes' recipe).
* Two trees on the pod: `/workspace/src-base` = pristine 5e6b3e3 (the "before"), `/workspace/src` = lane HEAD (the "after").

## Plan

The v3 hint generator (`privsel/hints.py::_hints_eager`) emits one torch op per hint row per group (~6000 hint rows for
fp8-ada-v3x4, several kernels each), replayed as one CUDA graph per (system, l, stream). At x4 the graph has 4x the groups per
column, so its cost does not fall with the sub-batch count. Replace it by ONE NVRTC kernel per system: one thread per unit (column),
the same integer program as `_hints_eager` (torch's int64 shift semantics mirrored exactly), each hint written through a row map
into `sys.hints` order. No static buffers (output allocated per call on the current stream), so it is per-stream safe without a
graph. Differential: fused vs the current torch path (eager and graph) on real sub-batches and adversarial units, `torch.equal`.
