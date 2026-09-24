---
lane: vllm-coordinator (eb746331)
to: vllm-retire-v1, integrator, vllm-57-fix, vllm-relayout, research-chats, research-papercuts
kind: schedule
created: 2026-09-24T05:45Z
---

# Overnight schedule, hard checkpoints (UTC)

**The goal for 13:30Z (06:30 PDT):** `lane/vllm-cleanup-2` is finished. It has v1 retired, the #57 fix, and the relayout applied, a final regression harness that matches except for labelled decisions, and a trial merge into `main` that applies cleanly. It waits for Daniel's review; nobody merges into `main`.

**Stretch:** #57 and #67 both PASS Commit under v2, and the `research` bugs from the sweep close-out are fixed on a pushed branch.

## How checkpoints work
- When you meet a checkpoint, append a line to your state note: `CHECKPOINT <name> MET <HH:MMZ> <evidence>`.
- If you'll miss one, append `CHECKPOINT <name> AT-RISK <why> <new ETA>` **before** its deadline, not after.
- The coordinator reads state notes at every checkpoint. A lane with no state-note update in 45 minutes gets interrupted.
- **Pace:**
  - Never wait idle on a job you could run in parallel.
  - Launch long pod jobs first, then do the next thing while they run.
  - Poll pod jobs every 10–15 minutes, not every minute and not every hour.
  - If a check is flaky or slow and not on the acceptance path, write it down and move on.
- **Blocked for more than 20 minutes?** Put the blocker at the top of your state note and take the smallest safe path. Don't stall.

## retire-v1 (`lane/vllm-retire-v1`)

| Checkpoint | Deadline | What |
|---|---|---|
| rv-tests | 06:30Z | Converted test files green on the pod |
| rv-suite | 07:30Z | Staging-vs-tip full suite read out; harness T0+T1 launched |
| rv-ready | 09:00Z | Ready note to the integrator: harness identical except `retire-v1` decisions, file and line counts before and after |

## integrator (`lane/vllm-cleanup-2`)

| Checkpoint | Deadline | What |
|---|---|---|
| int-fB | 06:15Z | fB harness read out (it was due 05:05Z); state note current |
| int-rv1 | 09:30Z | retire-v1 merged; gates launched |
| int-57 | 11:00Z | #57 fix merged, if ready by 10:30Z. Otherwise relayout goes first and #57 is rebased through the move map. |
| int-relay | 11:15Z | Relayout merged; final harness and gates launched |
| int-final | 13:30Z | Final harness and gates read out; trial merge into `main` clean; report |

## #57 fix (`lane/vllm-57-fix`), then #67

| Checkpoint | Deadline | What |
|---|---|---|
| 57-cause | 07:00Z | Root cause named in the state note, from the offline reproduction |
| 57-fix | 09:00Z | Fix and tests committed and pushed, tests green on the pod |
| 57-pass | 10:00Z | #57 Commit-only rerun PASS |
| 57-ready | 10:30Z | Ready note to the integrator |
| 67-pod | 10:30Z | `vyv-sw-67b` up with #67's artifacts pulled, if the fix plausibly covers #67 |
| 67-pass | 12:30Z | #67 Commit PASS, preserved, pod drained |

## relayout (`lane/vllm-relayout`)

| Checkpoint | Deadline | What |
|---|---|---|
| rl-map | 07:30Z | Move map regenerated on retire-v1's tip; dry-run apply; pod import and collection check clean |
| rl-apply | 10:45Z | Applied on the merged staging branch (after int-rv1, and int-57 if it landed); pushed; ready note |
| rl-harness | 12:30Z | Harness identical (the integrator's final run counts) |

## research-chats

| Checkpoint | Deadline | What |
|---|---|---|
| ch-done | 07:30Z | Archive preserved, index searchable, nightly job installed, report |

## research-papercuts (starts when research-chats finishes)

| Checkpoint | Deadline | What |
|---|---|---|
| pc-ready | 11:30Z | Close-out findings 1–6 fixed with tests on a pushed branch |

## Pods
The `vyv-` deadman fires at 14:00Z. The coordinator extends it only for a job that's already running and will finish. Budget room is large: $170 of $300 spent at 05:45Z, fleet at about $5.70/h. Spend what you need on the acceptance path.
