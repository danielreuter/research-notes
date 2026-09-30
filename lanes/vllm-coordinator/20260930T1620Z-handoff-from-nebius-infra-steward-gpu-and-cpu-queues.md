---
id: 20260930T1620Z-handoff-from-nebius-infra-steward-gpu-and-cpu-queues
campaign: overnight-sep30
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# The GPU and CPU queues for your pipeline split are live on vy-nebius-1 (16:14Z; `infra/nebius` `ebf0d3f8`)

**The queues** (LocalQueues of the same names in `default`):

| Queue | Quota | For |
|---|---|---|
| `deployments-gpu` | 5 GPUs, **4 vCPU and 128 GiB per GPU** (20 vCPU, 640 GiB) | GPU-only Commits and port captures. It never waits on CPU. |
| `deployments-cpu` | 0 GPUs (it can't borrow one), 100 vCPU, 640 GiB | Builds, replay and checks |
| `provers`, `backfill` | unchanged | |
| `circuits` | 0 | Draining: in-flight vLLM deployments finish on borrowed idle quota |

- **Borrowing:** the deployments queues borrow idle cohort quota, the GPU queue up to 2 of `provers`' GPUs. They reclaim theirs from
  lower-priority borrowers only.
- **Preemption:** nothing is preempted within a queue.

**Rules a task must follow:**
- **A GPU task:** `kueue.x-k8s.io/queue-name: deployments-gpu`, **4 vCPU per GPU**, 64 GB per GPU, priority `circuits-gpu` (600).
  `test_nebius_sky` enforces the vCPU rule for every template.
- **A CPU task:** `deployments-cpu`, 0 GPUs, memory at the measured peak plus 25%, priority `circuits` (500).
- **Threads:** pods have no CPU limit, so they burst onto idle cores; set threads to the work, not to the request.
- **Kueue can't refuse a 0-GPU pod in the GPU queue:** it would take CPU the queue reserves for GPUs, so templates must never do it.

**Templates on `ebf0d3f8`:**
- `config-run.yaml`: Build → `deployments-cpu`; Commit → `deployments-gpu` with 4 vCPU and 64 GB (`submit.sh`'s tp2 class: 8 vCPU,
  128 GB).
- `config-run-row.yaml`: → `deployments-gpu` at 4 vCPU. It's transitional: it holds its GPU through its Build until your split
  replaces it.
- `port-capture.yaml`: → `deployments-gpu`, 4 vCPU.
- **Your replay/check task** should label itself `deployments-cpu`. If your templates live elsewhere, send them and I'll check them
  against the queues.

**Also:**
- **The quiet hour** holds both deployments queues and `circuits`.
- **`submit.sh`'s waiting cap** (4 vLLM deployments' tasks, 6 jobs in all) counts all three.
- **Terminology:** per Daniel, "cells" are now **vLLM deployments** in queue names, alerts and notes.
- **Without GitHub:** `artifacts/nebius/infra-nebius-ebf0d3f8.bundle`, sha256
  `a3d710ac409d9cffddd23b5069d124db10480449334cbabf4e94a3c49a016506`. It needs `8f777377`.
