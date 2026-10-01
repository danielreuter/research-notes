---
cursor:
  subagentId: "bc-f2161f00-1952-55d3-af65-3ed9def14ace"
id: infra/20261001T1625Z-handoff-from-verity-root-friction-job-envelope
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root (daily friction pass, worker bc-f2161f00)
---

# verity-root -> infra: three small fixes from today's friction pass (a job's CPU and quota envelope, and a one-line Nebius key)

These are yours or your workers'. Each one is small, and none has an open PR (checked against `main` `d784c58e` and the 8 open PRs at 16:20Z).
The pass is `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/friction/20261001-pass.md`.

1. **Queue jobs get thread pools sized to `--cpus`** (`tools/cluster`, the queue's builder). `submit.wrappers` pins the
   job with `taskset` and `MemoryMax` but sets no thread variables, so numpy/OpenBLAS starts one thread per host CPU.
   `r20261001-073938-d76d` (`--cpus 4`) ran 32 threads, did 0.54 cores of work, spent 78% of its time in the system and hit its
   60-minute stage timeout (`note:pouw-fp8-security/20261001T0846Z-friction-queue-cpu-jobs-blas-threads`). Fix: the runner's `env`
   prefix sets `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS` and `NUMEXPR_NUM_THREADS` to `j.cpus`, as
   `dispatch.render` already does for `OMP_NUM_THREADS` and `pod_bootstrap.sh` does for pods. Add a `test_submit` case for it.
   Optional: export `BUILD_RAM_BUDGET_GB={j.memory_gib}` too, because circuits is being asked to skip the manifest's host-wide lock
   when a budget is set (`lanes/circuits/20261001T1625Z-handoff-from-verity-root-friction-vllm-pools-and-guard.md`).
2. **The pack pilot only goes in when it fits** (node1-dispatcher, `dispatch.pack_pods`). A 192G, 1-GPU pilot that
   deployments-gpu couldn't fit sat at the head of the queue, and Kueue re-tried it (`PreemptionNoCandidates`) without admitting an
   8G workload behind it that fit. That cost 13 minutes of a proof row's deadline, and the row was admitted 15 s after the
   pilot was deleted (`note:circuits-replay-keep-leaves/20261001T0723Z-friction-pack-pilot-blocks-fitting-gpu-workloads`). Fix:
   `pack_pods` submits only when deployments-gpu's unused nominal quota covers the pilot's request (`n2_commit.sh` around
   line 548 already reads it), or it sizes the request to the Commits it claims. #681 changes `PACK_MODELS` only, so it doesn't
   conflict.
3. **`common.sh` accepts a one-line Nebius key.** Lines of the multi-line PEM `NEBIUS_SA_PRIVATE_KEY` reached agent
   transcripts at least five times, the latest at 14:55Z (`note:circuits-grid-models/20261001T1517Z-friction-env-names-printed-key-lines`,
   `severity: incident`). Two of those came after `kb/cloud-lane-setup.md` gained the names-only rule on Sep 30 at 21:21Z, and
   that rule names the exact command used today. Fix: `nebius_auth` reads `NEBIUS_SA_PRIVATE_KEY_B64` (base64 of the PEM)
   when it is set, and `NEBIUS_SA_PRIVATE_KEY` otherwise, the same pattern as `RUNPOD_SSH_KEY_B64`. It is backward compatible
   and needs no ruling. Whether to rotate now and enter the new key as `_B64` is Daniel's call (he deferred rotation on
   Sep 30 at 18:42Z), and root is asking him.

When each one lands, reply with its PR number. If you decline one, say which and why.
