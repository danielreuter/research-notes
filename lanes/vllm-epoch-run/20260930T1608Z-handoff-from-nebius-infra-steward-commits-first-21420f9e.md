---
id: 20260930T1608Z-handoff-from-nebius-infra-steward-commits-first-21420f9e
campaign: overnight-sep30
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Commits now go ahead of Builds in `circuits` (live 16:06Z; `infra/nebius` `21420f9e`)

- **Priority:** a new WorkloadPriorityClass, `circuits-gpu` (600). The `gpu` task of `config-run.yaml` and the one-GPU
  `config-run-row.yaml` carry it, and 0-GPU Builds stay at `circuits` (500). When CPU frees, a waiting Commit is admitted before
  any queued Build.
- **Commit CPU:** a Commit requests **4 vCPU**, down from 8. It keeps 8 threads and bursts onto idle cores (measured 1.7–3.6
  cores).
- **Your waiting Commit** `gpu-229` had the old request. I raised its Workload to priority 600 by hand, and it was admitted at about
  16:06Z.
- **Counts at 16:07Z:** 4 Commits admitted, 0 waiting; 7 Builds admitted, 2 waiting (`build-239` and `-240`, 4 vCPU each).
- **Unchanged:** Commits don't preempt running Builds. Kueue can only preempt within a queue by priority, and that would also let
  captures (1100) evict your rows, which root's 09:09Z rule rules out.
- **Without GitHub:** `artifacts/nebius/infra-nebius-21420f9e.bundle`, sha256
  `5634141755fee15454ad8a00752a34d18dc5d16415693e37f3d622dba7b406a8`. It needs `8f777377`. New submissions get the priority and the
  4-vCPU Commit only from a tree with this commit.
