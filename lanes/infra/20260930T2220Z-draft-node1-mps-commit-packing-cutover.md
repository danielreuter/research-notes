---
id: 20260930T2220Z-draft-node1-mps-commit-packing-cutover
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1); for verity-top, then Daniel's review. NOT deployed.
---

# Node 1: packing small Commits 3 to a GPU with MPS, a cutover plan; plus the delivered-output metric

**Why.** Node 1 was 3.5% GPU busy from 2:13 to 3:13 PM PDT with every GPU reserved
(`note:20260930T2216Z-handoff-from-node1-fill-result`). Small-model Commits are light on the GPU even with their replay deferred, so
node 1's busy % is capped by the work mix and not by the scheduler. Packing puts 3 small Commits on one GPU at once.

## 1. What changes on node 1

The host changes as little as possible: no host MPS daemon, no change to the device plugin, no change to the GPU compute mode.
- **A new job template, `commit-pack`,** in `infra/nebius` `sky/jobs/`, resolved from git like the others.
  - It is one Kueue workload in `deployments-gpu` requesting **1 GPU** (so Kueue's accounting doesn't change), 12 CPUs and 3 × the
    Commit memory.
  - Inside it, the pod starts its own **MPS control daemon for its one GPU** (`nvidia-cuda-mps-control -d`, with
    `CUDA_MPS_PIPE_DIRECTORY` and `CUDA_MPS_LOG_DIRECTORY` under the pod's scratch), then runs **up to 3 Commits as MPS clients**,
    each a subprocess.
  - It is a pilot lease: when one Commit finishes, the pod takes the next eligible Commit from its list. It exits when the list is
    empty or its max wall time (120 min) is reached.
- **Dispatcher routing:** node1-dispatcher sends eligible Commits (§2) to `commit-pack` pods instead of 1-GPU Commit pods, behind a
  flag, `PACK_COMMITS=1`. Everything else is dispatched exactly as today.
- **Which GPUs:** only `deployments-gpu`'s share, at most 5 GPUs. `provers`' 3 GPUs are never used; the steward forbids
  co-tenants there, and M0's benches need them quiet.

## 2. Which Commits pack, and how many per GPU

- **Eligible:**
  - a 1-GPU (TP1) Commit whose model has ≤ 4B parameters: SmolLM2-135M/360M, TinyLlama-1.1B, Qwen2.5-0.5B/1.5B, Pythia-160M,
    Llama-3.2-1B, Phi-3-mini (3.8B), Qwen3-4B;
  - batch ≤ 8;
  - with `REPLAY_DEFERRED=1`, so its CPU replay runs as its own CPU task, as the refreshed template already does.
- **Never packed:** TP2, Gemma-2 (held), models of 7B and up, anything with a timed or quiet requirement, and bench or capture
  kinds.
- **Density:** **3 per GPU** to start. Move to 4 only after a night at 3 with no memory faults, and only for models ≤ 1.5B.

## 3. Isolation, memory limits, and what happens when one crashes

- **Memory:**
  - each client gets `CUDA_MPS_PINNED_DEVICE_MEM_LIMIT=0=28G`, and vLLM's `gpu_memory_utilization` is set to 0.28 on the 96 GB card,
    so the three together stay under about 86 GB;
  - `CUDA_MPS_ACTIVE_THREAD_PERCENTAGE=100` (no SM cap), since fairness between clients doesn't matter here;
  - host RAM and CPU are the pod's cgroup limits, with each Commit inside its share.
- **Crash blast radius:** on this generation, a fatal GPU fault in one MPS client can take down every client on that GPU. The rule is
  simple:
  - all Commits in the pod are marked failed-retryable and requeued, each once, unpacked (as a normal 1-GPU Commit);
  - a Commit that fails twice is held for circuits;
  - Commits are idempotent (small models rerun in minutes), so the cost is bounded to that pod's in-flight work.
- **Correctness:** MPS changes scheduling, not kernels. The KV-cache size follows `gpu_memory_utilization`, so the golden check in §4
  must show the packed record matches the unpacked one before any batch runs.

## 4. Verification, then rollback

1. **Golden check,** before anything else:
   - pack `cov-g217` (Llama-3.2-1B, already passed on node 1) with two other Llama-3.2-1B or SmolLM2 Commits;
   - its run root must equal node 1's unpacked run root, and all three must validate.

   If the run roots differ, stop: packing changes numerics, and the plan is withdrawn.
2. **The first hour, 2 `commit-pack` pods:** every packed Commit validates; that GPU's busy is ≥ 2.5× a single Commit's; GPU memory
   stays under 90 GB; there are 0 MPS faults.
3. **Nothing else moves:** `provers`' GPUs, the check slots on CPUs 8–95 and the quiet hour are unchanged. That is checked on DCGM
   and per-CPU busy before and after.

**Rollback, in one step:** set `PACK_COMMITS=0` in the dispatcher, so new Commits go back to 1-GPU pods. Running `commit-pack` pods
either finish or are deleted, in which case their Commits requeue as in §3. No host state to undo.

## 5. What must not be affected

- **Timed and quiet work:** node 2 is untouched. On node 1, `commit-pack` pods admit nothing new during the quiet hour
  (12:30–13:30Z). M0's benches keep `provers` with no co-tenants, and the Build benches' quiet re-measures are unaffected.
- **The Lean check and merge trains:** CPU slots a, b and c (CPUs 8–95) and `~/.cache/verity-check` are untouched. Pack pods get CPUs
  from Kueue's 96–159 range.
- **Commits already running:** they finish unchanged.

**Owners:** kueue-fold (the template and the dispatcher flag), circuits (the eligible list and the golden check), node1-fill (the
first hour's measurement).

**Effort:** a template, a dispatcher flag and a golden run, deployable in about 2 hours once approved.

---

# The delivered-output metric (draft)

**Definition.** Per node, per hour:
- **delivered share** = the leased GPU-seconds of jobs whose declared outputs landed and validated in the hour, divided by all leased
  GPU-seconds in the hour;
- **delivered GPU-h** = the numerator in hours.

A job counts as delivered when its Attempt is in the store with a passing verdict: `vllm.commit` valid with validation passed, a fill
job's exit 0 with its declared outputs present, or a check's `pass`. Filler-labeled jobs count as leased, never as delivered. Busy % is
still reported beside it, as a diagnostic: how hard the delivered work used the GPU.

**How kueue-fold computes it, from data that already exists:**
- **Leased GPU-seconds:**
  - node 2: `gpu-lease`'s per-lease `held_s` in `/workspace/research/lease-usage.jsonl`, the `gpu-lease/usage/v1` records;
  - node 1: Kueue's admitted-to-finished time × GPUs requested, from the Workload objects, which `pool_n1.py` already reads. Once
    the node-1 executor is live, this comes from its lease files instead.
- **Delivered:** join each lease or workload to its run id (from the lease's `run=` field, and the Kueue job name to the dispatcher
  key to the Attempt), then look up the Attempt's verdict in the evidence store (`research data select`, labels `valid` and
  `validation`) or, for fill jobs, the fill runner's `done/` versus `failed/` plus the declared outputs.
- **Where it's written:** add `leased_gpu_s`, `delivered_gpu_s` and `delivered_share` per node and per hour to
  `/workspace/usage/infra-pool-n1.json` and to node 2's `infra-pool.json`. Console shows `delivered_share` next to busy %, and
  `cluster usage --by lane|kind|question` reports the same split once the queue ledger carries run ids.
- **Lag:** a Commit's verdict can land up to about 30 minutes after its lease ends, so the hour is recomputed at +1 h and marked
  provisional until then.
