---
id: vllm-coordinator/handoff-for-project-coordinator
lane: vllm-coordinator
kind: handoff
from: vLLM coordinator chat eb746331 (veritor window)
created: 2026-09-24T19:25Z
---
# Handoff: the vLLM workstream, to the Project coordinator

## In one paragraph
We are refactoring `integrations/vllm` against a survey-grounded plan (`vllm-refactor/SYNTHESIS.md`). Six lanes are in flight:
- **Phase 0**, the correctness fixes: f1, f24, f3 and f56.
- **Phase 1**, the first mechanical cleanup: a1 and a23.

All six branched from `72884c8a`, the merge of `lane/vllm-cleanup-2` into `main`. `main` is now `22741456` and contains that merge. None of the refactor lanes has merged yet.

The lanes are subagents of the old vLLM chat. Their completion messages go to that chat, not to you, so watch their notes. The old chat stops coordinating once you write your took-over note (see the end).

## Read in this order
1. This file.
2. `~/.research/notes/lanes/vllm-refactor/COORDINATOR.md`: the lane table, incidents, liveness signals and old merge procedure. Merging is superseded below.
3. `vllm-refactor/LANE_BRIEF.md`: the rules every lane follows (laptop limits, worktrees, pod naming, gates, crash-only state notes, finish).
4. `vllm-refactor/SYNTHESIS.md`: the plan of record.
   - Section 2: correctness defects D1..D17.
   - Section 4: practices P1..P12, each enforced by a lint.
   - Section 5: target package tree and public API.
   - Section 6: phases and the per-lane gate, as corrected.
   - Section 7: the owner decisions.
5. `vllm-refactor/*coordinator-checks-*.md` (four notes): claims I verified against the code, and corrections to the surveys. The notes win over the surveys.
6. `vllm-rf-a1/baseline.md`: the test baseline at `72884c8a`, plus a pod environment recipe.
7. `vllm-rf-<lane>/STATE.md` for each lane, and `READY.md` when one appears.
8. `vllm-refactor/LANE_PROMPTS.md`: every lane's launch prompt verbatim, plus a restart preamble.
9. On demand:
   - the four `vllm-refactor/survey-*.md` reports (673 findings, full detail);
   - `integrator/20260924T1352Z-final.md` and `integrator/20260924T1410Z-coordinator-addendum.md`, which say what cleanup-2 contains;
   - `~/.cursor/skills/durable-campaign-orchestration/SKILL.md`, on local agent limits and crash-only lanes.
10. The owner's view of the plan is a canvas: `~/.cursor/projects/Users-danielreuter-projects-veritor/canvases/vLLM-integration-refactor-plan-f0810a11.canvas.tsx`.

## Lanes at 19:20Z
Worktrees are in `~/projects/verity-wt/rf-<lane>`, branches are `lane/vllm-rf-<lane>`, and notes are in `~/.research/notes/lanes/vllm-rf-<lane>/`.

| lane | scope | branch head | pod | state |
|---|---|---|---|---|
| a1 | baseline and guardrail lints | `39c5ee7a` (2 commits) | `vyv-rf-a1` = `y2uelocmg62eu0` | Baseline written at 18:30Z. The lint suite (41 tests, about 9 s) is committed. The base gate (a) run was still in progress. STATE 18:54Z. Survived the 18:02Z restart. |
| a23 | dead code, data and paths | `c1cf11ef` (4 commits) | `vyv-rf-a23` = `qcky3qlmvh896c` | The deletions are done: `tools/`, CMT-1, `engine_rs`, dead PoC files. Two modules the survey called dead are live and were kept (`resolve_decomp`, `hidden_engine`). Data and paths not started. **Silent since 18:02Z although its session exists: treat as stuck.** |
| f1 | D1: value check over opened values | none | none yet | Died at 18:02Z and resumed at 18:46Z. STATE 19:04Z; it is mapping compared vs opened positions. The largest lane, and it will need GPU pods for a dense, a MoE and a TP2 row. |
| f24 | D5, D6, D7, D10, D11, D13 | `76020a66` (5 commits) | `vyv-rf-f24` = `0zb24mk1w6nb4o` | The most advanced lane: identity designs done, D10 (no core monkeypatching) under test on its pod. Survived. |
| f3 | D3, D4, D14, D15 | `0f970b0e` (2 commits) | none yet | Died and resumed at 18:46Z. Its inventory says the D3 and D15 fixes should not change any root or digest: nothing ever set `VERITY_LEAF_LAYOUT`, and the environment tables only ever pointed at the shipped files. |
| f56 | D16, D17 | none | none yet (needs a 2-GPU pod, an L40S and an H100) | Died and resumed at 18:48Z. It found recorded TP4 all-reduce evidence (`art:53e58b1c…`), so the order can be fixed rather than refused. The FA-tap cross-check scripts were deleted by our own cleanup (`ca5d65e8`); they are recovered in `/tmp/rff56` and become the property check. |

**Liveness.**
- Subagent transcripts stop updating after a Cursor host restart, even for agents that survived, so they are not a signal.
- Use instead: the STATE.md mtime, the newest file mtime in the lane's worktree, and the lane's commands in the old chat's terminals folder (`~/.cursor/projects/Users-danielreuter-projects-veritor/terminals/`, whose `cwd:` field names the worktree).
- STATE.md older than about 40 minutes with no worktree edits means stuck or dead.

**Pods and money.**
- Three CPU pods (cpu3g, 16 vCPU, 64 GB) at $0.64/h each, $1.92/h in total.
- The budget and deadline daemons run on `vy-control-verity`: `ssh -i ~/.runpod/ssh/runpodctl-ssh-key -p 11754 root@213.173.105.92`.
  - **Budget:** tag `2026-09-23-vyv-rebuild`, spent $241.80 against a cap of $600 (the file `/root/dm/CAP`), rate cap $45/h, owns the `vyv-` prefix. To raise it, write the CAP file and log the change to `/root/dm/dm.log`.
  - **Deadline:** `bash /root/dm/deadline.sh vyv- 1790305200` terminates every `vyv-` pod at 2026-09-25T03:00Z. To re-arm, kill it and start `setsid nohup bash /root/dm/deadline.sh vyv- <epoch>`; `dm.log` has the exact past commands.
- The research watcher runs with `--exclude vllm*`, and these lanes are `vllm-rf-*`, so its reaper leaves their pods alone. My two daemons are the guard.

## Decisions you must keep
**Owner decisions of 2026-09-24 17:20Z**, all as recommended:
- Branch from `main`, after the cleanup-2 merge.
- Start Phase 0 plus lanes A1 to A3 now.
- D1: value checks compare opened, verified values inside the Commit process now. A separate verifier process becomes the result of record later, in Phase 2 lane B1.
- Delete CMT-1 (`commit/reference_engine/`, its adapter, `cmt_ref_*`) and `engine_rs`. The PoC bundle chain goes later, once `merkle` comes from core.
- Refuse tensor-parallel world > 2 with a clear error until collectives land.

**Standing rules** (from the owner over the last two days):
- Phases 0 to 2 must not change Program digests, manifest digests, commitment roots, leaf ids or regression verdicts. Every digest-changing fix waits for Phase 3 and one reviewed re-baseline.
- The regression harness (`integrations/vllm/tests/regression/`, 12 frozen rows, tiers T0 to T2) is the behavior-preservation gate.
- Gate (b) is judged as **no new failures** against `baseline.md`. The base has 65 known failures and errors, so "0 failures" is impossible there.
- No heavy work on the laptop: no pytest, no torch, no builds. It has about 9 GB of disk free, and a guardian kills Python processes over 1 GB. Tests run on pods only.
- No new Markdown files in the repo. Notes live in `~/.research/notes/`. The v2 ontology (Q_module_body, BoundaryValues, correspondence, acquisition) is settled; implementation quality is what's open.
- Don't touch `~/projects/verity`: it is the owner's checkout, detached at `f0810a11`, for browsing.

**Open decisions**, which need the owner. My recommendations:
1. Commitment scheme: production adopts core's `commitments.merkle`, gated on a pod throughput measurement, with core adopting production's rules as the fallback.
3. The colliding and changed Definition ids: retire the integration copies and cite core's ids, including `AmpereBF16TcDot16` v2.
4. Re-baseline: one batched epoch.
5. Upstreaming: consolidate in the integration first, except the IR analyses (boundary, partition, liveness), which move to core now.
8. API scope: start with engines built from a `RowSpec` only.

## Merging to main
- **The research coordinator owns every merge to `main`.** I agree with the owner's proposal. I pushed the cleanup-2 merge myself at 17:24Z on the owner's instruction; the research coordinator then merged `main` into its own line, giving `f08314ae` and `22741456`. From now on, nobody on the vLLM side pushes to `main`.
- **For each lane:**
  1. When its READY.md appears, check the gate evidence against `baseline.md` and spot-check the diff.
  2. Make sure the branch is pushed and rebases cleanly on current `main`.
  3. Hand the branch and head commit to the research coordinator for a `--no-ff` merge.
  4. After each merge, tell the remaining lanes to rebase. Deleting stale lint-allowlist entries during that rebase is expected.
- **Order:** a1, a23 (or a23b), then f24, f3, f56 and f1 as each becomes ready.
- **For reference, my old procedure** was a scratch worktree: from `~/projects/verity`, `git worktree add --detach /tmp/rf-merge origin/main`, then `git merge --no-ff`, check that the diff outside `integrations/vllm` is what you expect, and push only if `origin/main` hasn't moved.

## Open items, in priority order
1. **a23 is stuck.** Relaunch it as a23b, using the prompt and restart preamble in `LANE_PROMPTS.md`, on a new branch `lane/vllm-rf-a23b` from `origin/lane/vllm-rf-a23`, worktree `rf-a23b`, notes `vllm-rf-a23b`. That way a late wake-up of the old agent can't collide. Its pod `vyv-rf-a23` has the base tree and environment and can be reused.
2. **Watch the other five lanes** through their notes, and relaunch any that die, with the restart preamble.
3. **Merge in order** through the research coordinator.
4. **Next phases:**
   - A4 (move into the 12-package tree) after the Phase 0 lanes merge;
   - then A5 (one CLI and typed config; it needs decision 8);
   - then Phase 2, lanes B1 to B5 in parallel;
   - Phase 3 needs decisions 1, 3, 4 and 5.
5. **The baseline's 65 failures** deserve their own small lane:
   - about 34 are test setup: subprocess builds can't import core `verity`, because the bootstrap puts core on `PYTHONPATH` instead of into the venv;
   - 10 read files that are missing from the tree;
   - 21 are CPU-host numerics and real-HF checks.
6. **Owner laptop actions:** Cursor's `state.vscdb` is 72.7 GB. Delete the old chats, then VACUUM it with Cursor quit.
7. **Older follow-ups:**
   - the OLMoE replay-reuse key includes FA2-tap counters in `binding_map_p{pair}.json`, which costs about 55 min per Commit but doesn't affect correctness;
   - sweep Builds should become fixture descriptors;
   - the #23 harness candidate table was not regenerated.
8. **Headless agents on pods:** if you run lanes as headless CLI agents on pods, test the model first. Last night the pod CLI's premium quota ran out, and only composer-2.5 and auto worked.

## `integrations/vllm/verity_vllm_numerics/` in `~/projects/verity-main-wt/main`
- **Mine.** It's left over from the relayout.
- **Contents:** `cpp/libtc_model.so` plus three `.so.lock` files, written at 17:24Z by a run on the pre-relayout tree.
- **Safe to delete:** current code builds these libraries under `verity_vllm/program/numerics/cpp/build/` (gitignored, per `program/numerics/_jit.py`), and nothing at `main` reads the old path. Delete the directory.

## Laptop services this workstream set up
- `~/.veritor/mem_guardian.py` kills runaway Python processes in the verity and veritor trees (1 GB per process, 3 GB total).
- `~/.veritor/exthost_watch.sh` logs Cursor extension-host memory to `~/.veritor/exthost_mem.log` and raises a macOS alert at 2.8 GB and 3.4 GB.
- A launchd job archives chats nightly at 03:17 local (branch `lane/research-chats`, `c313a38c`).
- The podlane-sync launchd job is unloaded.

## Took over
When you have read this, write `~/.research/notes/lanes/vllm-coordinator/<UTC timestamp>-took-over.md`, naming yourself and the time. From that moment, the old chat (eb746331):
- stops coordinating: no merges, no launches, no messages to lanes;
- stays open only as the host of the six lanes it launched, until they finish or the owner stops it.

If the owner stops it earlier, those lanes may stop too; a host restart at 18:02Z killed three of them. In that case, relaunch them from `LANE_PROMPTS.md`.
