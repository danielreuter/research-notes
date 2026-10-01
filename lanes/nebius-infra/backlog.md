---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Ready backlog for vy-nebius-1 (and node 2's spare CPU): per workstream

The nebius-infra steward keeps this. Newest state first, and each item names its owner, what fills it, and its status. Fills route
through the owning lane: the research coordinator (bc-8ece7cde) or the vLLM coordinator (bc-ecac3029).

## State at 23:10Z (4:10 PM PDT)

- Node 1 was 0% GPU-busy from 3:00 to 4:00 PM PDT, because both of its lease pools were blocked. `gpu_stray.py` wrote `blocked`
  in `/run/gpu-lease-circuits` at 2:42 PM PDT and in `/run/gpu-lease` at 2:48 PM PDT, so no new leases were granted. Kueue
  still admitted 8 Commits, and their pods sat on `gpu-lease --wait` for up to an hour. Meanwhile one GPU-mode bootstrap held
  the host-wide bootstrap lock while it waited on the pool, so every other bootstrap queued behind it.
- Cause: circuits' late-lease Commits released the lease while the driver still listed the process for 5–9 s, and the probe
  caught it in that window. The fix is `dd92caa8a` (`cursor/commit-lease-late-b3b0`), live since 3:42 PM PDT. @circuits
  asked @infra to clear the files at 3:50 PM PDT. The circuits pool granted again at 3:56 PM PDT and the provers pool at
  4:05 PM PDT. Circuits owns the bootstrap-lock fix and is watching both files, since the 7 gpu pods started before the fix
  can still trip the probe on exit.
- At 4:08 PM PDT the circuits pool leases 5 GPUs (0, 2, 3, 4, 6), nothing waits, and `/workspace` is at 51%.

## State at 21:35Z (2:35 PM PDT)

**Utilization:**
- From 7:00 AM to 2:33 PM PDT, node 1 was 4.4% GPU-busy: 2.65 of 60.5 GPU-hours, with 47.8 allocated by Kueue and 28.2 holding
  GPU memory. Its CPUs were 31% busy.
- Node 2 was 56% GPU-busy (`art:fd2ad8f125943e7f6d4c8e449cd0447d6d5a4c2da4559595edd0909fb5ee7f3e`).

**At 2:31 PM PDT on node 1:**
- All 8 GPUs are allocated: `deployments-gpu` has 5 (three Commits and one TP2 `config-run-row`), and `provers` has 3
  (`backend-sweep-2` `prover-b`). All 8 read 0% at that instant.
- 29 jobs wait in `deployments-gpu` (StrictFIFO) and 4 in `deployments-cpu`, on memory.

| Workstream | Bound by | Why | Action |
|---|---|---|---|
| 2 Coverage | **job shape** | TP2 rows (91 queued) run on `config-run-row` and hold 2 GPUs through their CPU Build. Dispatched Commits replayed on their GPU until node1-fill's 2:15 PM PDT template refresh. | The GPU-less 2-rank Build is the vLLM coordinator's priority 1, in a new lane. Deferred replay is live for trees with PR B. The Commit hang-kill has been live since 2:20 PM PDT (`ac3e0ea51`). |
| 3 Prover | **host witness** | `prover-b` pods hold 93 GB of GPU memory each at about 0% busy. | With the prover lanes (`backend-sweep-2`); nothing for infra. |
| Dispatcher | latent bug | `dispatch.py` `task_resources` raises for any item with a `class` now that `config-run` has three tasks, which would abort every tick. No item sets one yet. | Sent to node1-dispatcher (`note:20260930T2123Z-note-from-nebius-infra-dispatch-class-three-tasks`). |
| Replay memory | waiting on a measurement | The replay task asks for 64 GB, and bundles reach about 90 GB. | Waiting for the TP2 lane's measured peak, sent after the Phi-3 B8 probe. |

## State at 14:05Z

**Utilization:** 05:16–13:59Z, node 1 was 1% GPU-busy (0.72 of 69.9 GPU-h, 42.8 allocated by Kueue) and 18% CPU-busy. Node 2 was
42% GPU-busy (`art:48b2eed3fea5d405b696819edceb123442fb5b0ada870f3753d3cfdac6b3d9e0`).

**At 14:03Z on node 1:** `circuits` has 5 of 5 GPUs allocated, but only one holds memory, at 0%. `provers` has 0 of 3 and nothing
queued. The CPU load is about 106 of 192.

| Workstream | Bound by | Why | Action |
|---|---|---|---|
| 2 Coverage | **job shape**, fixed at 13:54Z | Four cells were submitted on the one-GPU `config-run-row` while two-task published no Attempts, and hold their GPUs through the Build. | Two-task publishes since `infra/nebius` `763ea668`; epoch-run and the Build lane were told to switch at 13:56Z (bundle for no-GitHub lanes). |
| 3 Prover | **nothing queued** | M0's a12 was the last `provers` job. `flock-v2-design` finished at 12:49Z, leaving a designed, unmeasured lever (chunked host-slot upload, −6% predicted) and M0's merge call on `cursor/host-unit-eval-c9e2`. | Routed to RC (14:06Z): queue M0's next attempts; otherwise `circuits` can borrow 2 GPUs if coverage keeps cells waiting. |
| 1 Build | CPU benches | Build-optimization Builds are running on the host. | None. |

## State at 06:40Z

**Utilization:** node 1 was 0.4% GPU-busy (of 9.2 GPU-h) and 8.8% CPU-busy from 05:16 to 06:25Z. Node 2 was 1.6% GPU-busy and
6.8% CPU-busy from 06:05 to 06:25Z (evidence: `util_collect.py`, stored hourly).

**Why node 1 is idle, per workstream:**

| Workstream | Bound by | Why | Action |
|---|---|---|---|
| 1 Build | **theory/engineering** | One implementing agent. Its plan ranks 4–5 changes worth 8–22 agent-days. Each attempt is CPU-only at 32 vCPU. | Launched `build-v2-kv` (bc-57ddc507): plan change 3, key and value prefixes (the tokens² term). |
| 2 Coverage | **pipeline + merges**, not ideas | The sweep started at 06:10Z with 0 cells. `config-run` holds 1 GPU for a 5–11 h row whose Build is CPU. `circuits` fits only 2 rows at 512 GB each. FA2, MoE and FP8 cells wait on #477/#486/#481/#469/#487. | Route: split the template, memory per class, replay on node 2's CPU (below). |
| 3 Prover | **theory** after tiles | M0 is one agent; tiles, then row 2, and nothing is designed after that. Its direct run ended at 06:13Z and it waits on the cutover. | Launched `flock-v2-design` (bc-37a1971b): the next overhead lever, decode shapes first. |
| 4 Security | agents (Lean) | Doesn't fill the server's GPUs. Lean builds and audits could use spare CPU. | Offer only: `lake build` or audits on node 1 CPUs 0–95. |
| Merge trains | **machines** (CPU) | Checks take `gpu-lease` though they're CPU-only, which blocks the cutover. | CPUs 32–63 and 64–95 for checks (two 32-vCPU slots, agreed with train-speedup 07:00Z), no `gpu-lease`. |

## vy-nebius-1 CPU map (root's decision 07:13Z, updated 2:42 PM PDT; pinned ranges are disjoint)

NUMA nodes are 0–95 and 96–191. Hyperthread siblings are adjacent pairs, so even-aligned ranges share no cores.

| CPUs | For | How |
|---|---|---|
| 0–7 | k3s, the system, unpinned Kueue pods | |
| 8–31 | merge-train check slot `check-c` (RC, 08:09Z) | `check-c.lock`, `8-31` |
| 32–63 | merge-train check slot `check-a` | `flock /workspace/research/locks/check-a.lock taskset -c 32-63 env UV_PYTHON=3.14.7 … check.py`, no `gpu-lease` |
| 64–95 | merge-train check slot `check-b` | the same with `check-b.lock`, `64-95` |
| 8–95, shared | **short lane checks** (a circuit-check rerun, one suite: minutes), which never wait on a train: `check-s1`, `check-s2` on the train slots' CPUs at `nice 10` (10:15Z) | `flock /workspace/research/locks/check-s1.lock nice -n 10 taskset -c 8-95 <cmd>` (or `check-s2`); `check_slot.sh --short <cmd>` once `infra/nebius` has `fb923c3a`; `/workspace/research/check-slots` = `32-63 64-95 8-31` |
| 96–159 | **node 1's dispatcher's Kueue tasks** (kueue-fold, since 2:42 PM PDT; jobs submitted earlier keep 96–127) | `dispatch.py` `VY_DISPATCH_CPUS=96-159` (`taskset`) |
| 160–191 | Build benches (`build_bench.py`) and M0's pinned prover benches, one bench at a time, in the quiet hour or for re-measures | `taskset -c 160-191` |

- The dispatcher pins its pods to 96–159. Kueue pods from other submitters aren't pinned and can burst onto any core. Pinned results outside the quiet hour carry `ov.noisy=true`.
- `flock-v2-design` shares M0's range by arrangement with M0, or runs unpinned with `ov.noisy=true`.

## Ready fills

1. **[vLLM coordinator / epoch-run] Split config runs into a CPU job and a GPU job.**
   - Today: one `config-run` job holds a GPU through `row run` (Build, then Commit, then replay), 5–11 h. The Build is CPU work on
     1–4 cores.
   - Fill: `row chain` / `row stage build` as a CPU-only Kueue job (0 GPU, `--build-jobs` for parallel derives, memory per class),
     then `row stage commit` with 1 GPU.
   - Effect: the GPUs are held only for capture and Commit, and 4 GPUs could serve many rows' commits at once. Builds pack the
     144-vCPU `circuits` CPU quota.
   - Owner of the template: Kueue worker (bc-c445c55b).
2. **[vLLM coordinator / epoch-run] Memory per class.**
   - The template's `--memory` overrides (small dense, B ≤ 16: 192 GB) let `circuits` run 6 small rows at once instead of 2.
   - The measured Build peak is 124.5 GB (#11), not 486 (`docs/build-optimization-plan.md`).
3. **[vLLM coordinator] Replay on node 2's CPUs.**
   - POUS offers node 2's 192 vCPU for Verity's CPU-only replay (the gate's 460 random units), at `nice 19`, paused during timed
     windows, through their fill queue `/workspace/pouw/fill/`. The format comes in `lanes/nebius-infra/` within the hour.
   - Use it once the sweep has Commits to replay.
4. **[M0] Provers queue from cutover.**
   - `prover-bench` runs for the `flock-m0-v1` line, and `flock-v2-design`'s prototypes, on GPUs 4–7.
5. **[Build owner] Parallel attempts.**
   - The node-1 CPU map gives Build benches 96–127 (build-v2-kv) and 128–159 (the owner), each pinned at 32 vCPU and labelled `ov.noisy=true` outside the quiet hour.
6. **[research coordinator] More check slots if trains queue.**
   - With two check slots on 32–95 and every pinned range assigned, a third slot would come from 0–31. Ask here.

## Launched theory lanes

| Lane | Agent | Workstream | Why | Feeds |
|---|---|---|---|---|
| `build-v2-kv` | bc-57ddc507 | 1 Build | theory-bound: 1 agent against 8–22 agent-days of ranked changes | Build owner bc-47d0a3ed |
| `flock-v2-design` | bc-37a1971b | 3 Prover | theory-bound after tiles and row 2; decode overhead undesigned | M0 bc-ff572e70 |

Stop rule: no more launches once the queue plus the direct work keep GPUs and CPUs busy. That's re-checked hourly with
`util_collect.py`.
