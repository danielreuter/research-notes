---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Ready backlog for vy-nebius-1 (and node 2's spare CPU): per workstream

The nebius-infra steward keeps this. Newest state first, and each item names its owner, what fills it, and its status. Fills route
through the owning lane: the research coordinator (bc-8ece7cde) or the vLLM coordinator (bc-ecac3029).

**Standing ruling (6:16 PM PDT Oct 1):** a small fix to infrastructure the steward runs goes straight to the merge queue once its
tests pass, without asking: take it out of draft, run `research queue ready N --by nebius-infra`, and ask @ci on Slack to stack
it. In Slack posts, put the mentions first, then `steward:`. The top-level forwards a post that tags a handle anywhere, but
the doorbell wakes only the names at the start.

## State at 01:35Z Oct 2 (6:35 PM PDT Oct 1)

- #732 merged at 6:21 PM PDT; #746 is ready and with @ci. The relay sends the redeploy ask to @circuits once both have
  merged.
- The live `VY_LEASE_HOSTDIRS` default works: all 4 leased `deployments-gpu` Commit Jobs created since 6:14 PM PDT mount
  `/run/gpu-lease-circuits`.
- On node 1, 7 of 8 GPUs are empty, `provers` admits nothing, and `deployments-cpu` has 6 Builds and replays pending on its
  384Gi limit. The pacer projects 947 of its 1,000 GB cap, with 479 GB of bundles waiting for replay. So Commits are limited
  by how fast replays clear bundles and by Build quota, both already recorded at 00:45Z. Node 2 is running on 3 GPUs.
  `/workspace` is at 58%.

## State at 01:20Z Oct 2 (6:20 PM PDT Oct 1)

- The circuits lease pool was blocked twice, at 5:49 and 5:58 PM PDT. Both strays were circuits' hiding-commitments retries
  (cov-hide-gm392-b and -b2) on a tree without `gpu_lease.py`, submitted through lease-pilot scripts that circuits has since
  guarded. The relay's new check posted both to @infra within a minute. Circuits cleared the pool at 5:58 and 6:09 PM.
- **Circuits' Commits leasing from proofs' pool, found and fixed.** Five rows whose Build was moved to node 2 (cov-gm290,
  gm291, gm295, gm302 and f6f9d7d87d's) had their Commits submitted by `n2_build.sh`'s hand-back. It runs `dispatch.py submit
  --task 1` over ssh without `VY_LEASE_HOSTDIRS`, so the Commits fell back to `/run/gpu-lease`. The fix is
  [#746](https://github.com/danielreuter/verity/pull/746), still a draft: `dispatch.py` defaults the variable to
  `deployments-gpu=/run/gpu-lease-circuits` for every caller. I patched the same default into node 1's deployed copy at
  6:14 PM PDT (backup `dispatch.py.bak-20261002T0120Z`). The loop wasn't restarted, since it already has the variable. The
  relay's redeploy ask for #732 now tells circuits to keep this default.
- Those moved Builds' node-1 Jobs are deleted when they move, so their hand-back can't cause the AlreadyExists stall.

## State at 00:45Z Oct 2 (5:45 PM PDT Oct 1)

- Since 10:16 PM PDT Sep 29, node 1 has been 4.4% GPU-busy (15.2 of 347.5 GPU-hours) and node 2 28.2% (95.9 of 339.8)
  (`art:49d408d5a71fb8b6b22548c5a9f91f29962a641a94428d8fee46e41feb7c60b8`). The 5:25 PM PDT hourly collection failed on a
  one-off ssh error (exit 255), and the rerun at 5:42 PM worked.
- The limit is still 384Gi, the drift check shows live Kueue matching `infra/nebius`, the dispatcher's ticks succeed, and #732
  is open, not yet merged.
- `deployments-cpu` is full again at 849 of 864Gi, with 4 Builds and 2 replays pending, while node 1 has 1.18 TB of RAM free.
  I'm not raising the limit further. The cohort has 1,365 of its 1,664Gi booked, so 128Gi more borrowing would leave room
  for only about one more 170 GB Commit before Commits start evicting borrowing Builds, which restart from scratch. The
  pacer allows 6 Commits in flight. The lasting fix is right-sizing requests: booked memory is about 2.5× what's in use
  (539 GB). That's backlog item 2, memory per class, owned by epoch-run and resource-steward.

## State at 00:10Z Oct 2 (5:10 PM PDT Oct 1)

- `deployments-cpu` still borrows up to 384Gi (no flip-flop).
- **The dispatcher failed every tick from 2:42 to 5:05 PM PDT.** `cov-gm390`'s Commit Job was created by another path at 2:38
  PM PDT, before its Build's end was routed. From then on, each tick's `kubectl create` of that Job raised AlreadyExists and
  aborted the tick before the Build got its `verity.dev/seen` label, about 140 times. Everything after it was skipped:
  - two finished Builds' Commits (cov-gm183 since 3:19 PM, cov-gm297 since 4:58 PM);
  - cov-gm390's replay;
  - two item ends;
  - the pack, node-2 spill and ready-item steps, while node 2 sat idle.
- At 5:05 PM PDT I labelled the Build Job `seen=1` by hand, which is what the tick would have done. The next tick submitted
  all of the above, plus two new Builds. The fix is [#732](https://github.com/danielreuter/verity/pull/732): `submit()` counts
  an existing Job of the same item, task and try as submitted. Node 1 runs an older, unmerged copy of `dispatch.py`, so it
  gets the fix only when redeployed. I told @infra and @circuits in the disk thread.
- 5:15 PM PDT: #732 is out of draft, marked ready at `d7110aa31` (`research queue ready 732`), and @ci was asked on Slack to
  stack it. The steward's relay (`tools/alert_pull.sh`) now does two more things:
  - it posts the redeploy ask to @circuits once, when #732 merges (`/tmp/merge-watch.tsv`);
  - it reads the dispatcher's ticks from its tmux pane (`tools/dispatch_ticks.py`), because `loop.log` has been silent since
    1:10 PM PDT. It posts one line to @circuits and @infra, at most once an hour, when 5 or more ticks fail in a row. It also
    posts when the ticks are unreadable or absent for 10 minutes on 3 checks in a row, so it doesn't fail open.
- Otherwise node 1's GPUs are idle by design. Circuits' late-lease Commits hold a GPU only for their 2–4 min GPU work pair,
  then finish on CPU. The two held Commits (cov-n050-2, cov-n051-2) are batch-64 Gemma-2 rows on circuits' keep list.

## State at 23:35Z (4:35 PM PDT)

- Since 10:16 PM PDT Sep 29, node 1 has been 4.4% GPU-busy (14.7 of 334.8 GPU-hours) and node 2 29.1% (95.4 of 327.2)
  (`art:48a5ab1757c60b5a6d4268f7177219e0b5429c581297354e9682bd40c994d7e2`).
- At 4:31 PM PDT node 1 had 7 of 8 GPUs empty. The chain started with `deployments-cpu`, at its memory limit (128Gi of
  borrowing, 637 GB booked), where 3 replays and a Build waited with 1.29 TB of RAM free. Because the replays waited, 743 GB of
  bundles stayed on disk, which held the Commit pacer at its 1 TB cap (2 Commits held, 1 in flight). @infra's 9:59 AM PDT
  raise to 256Gi had reverted itself at 10:14 AM PDT when `provers` admitted a workload, and circuits' 11:00 AM ask to size it
  again went unanswered.
- At 4:34 PM PDT I raised the limit to 384Gi, live and on `infra/nebius` (`49f235f8b`), and told @infra and @circuits in
  circuits' thread. Kueue admitted all 4 at once. The cohort's 1,664Gi nominal stays under node 1's 1,716 GiB, and Commits
  (600) reclaim from borrowing Builds (500) but not replays (600). To revert, set it back to 128Gi.
- At 4:37 PM PDT the limit is still 384Gi. @infra's `cpu-borrow-watch` on node 1 exited after its 10:14 AM PDT revert, and its
  tmux pane now only runs `sleep 86400`. Root's instruction: check the limit on every pass. If it's back at 128Gi, don't
  re-apply it; ask @infra on Slack to retire or adjust the revert rule under Daniel's 12:12 PM PDT one-pool ruling, and tell
  root. The hourly drift check would also flag a revert, because live Kueue would then differ from `infra/nebius`.

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
- Nobody saw the blocks for 68 minutes, because the hourly idle-GPU alerts reach only lane notes. Since 4:10 PM PDT the
  steward's alert relay (`tools/alert_pull.sh`) checks node 1 for `/run/gpu-lease*/blocked` every 2 minutes and posts one
  Slack line per file to @infra in the disk thread. The idle-GPU alerts themselves stay off Slack: there have been 28.

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
