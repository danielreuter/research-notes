---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
---

# Lane brief: reaper-resume-guard (cloud lane, small tools fix)

**Launch status:** READY (7:35 AM PT, Sep 25). A small, self-contained change to `tools/research`. This is a PR, not a
long-running lane.

**Launch as:** a Cursor cloud agent in `danielreuter/verity`, base branch `main`. Give it this prompt:

> You are lane `reaper-resume-guard`. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1. Your brief is `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/reaper-resume-guard.md`.
> Write your first checkpoint within 10 minutes.

## The incident

red-team-flock was FINAL at 11:27Z, then reopened at 12:30Z for a re-audit. Its reopening checkpoint reached the notes late:
cloud lanes' checkpoints travel through a laptop-side mirror, and the laptop worker was disconnected. Meanwhile the steward
(`research notes watch --reap` on vy-control-verity) reaped four of its new pods within minutes of their creation:

    12:30Z REAPED red-team-flock vy-red-team-flock fzs8rjhcj9oxjq $0.48/h (final 64m ago)
    … x8gaf462paw582 (12:32Z), 18ubkjsgz9amop (12:35Z), m7aqz4bhaf9640 (12:37Z)

## The two defects in `tools/research/src/research/notes.py` `reap_lines` (FINAL-lane pods)

1. **It reaps pods created after the lane's FINAL.** A pod whose `createdAt` / `lastStartedAt` is later than the lane's
   `done_ts` is evidence that the lane (or a reopened agent) is running again. Fix: skip such pods and emit
   `RESUMED-POD <lane> <pod> <id> (created <t>, after FINAL <t>)` once per pod, without terminating it. (If the pod
   listing lacks a creation time, treat the pod as resumed and don't reap.)
2. **It terminates without a custody check.** `stale_reap_lines` calls `reap_custody` first and prints `REAP-BLOCKED` when
   custody fails; `reap_lines` doesn't. Fix: call the same `reap_custody` (with `--custody-r2` semantics when the watcher
   runs with it) before terminating a FINAL lane's pod. On failure, print `REAP-BLOCKED` and leave the pod.

Keep `--keep-pod WHY` working as it does. Don't change `stale_reap_lines`' behaviour.

## Tests (`tools/research/tests/test_notes.py`)

- A FINAL lane with a pod created before done_ts, with custody OK, is REAPED.
- A FINAL lane with a pod created after done_ts gets RESUMED-POD and isn't terminated.
- A FINAL lane whose pod fails custody gets REAP-BLOCKED and isn't terminated.
- `--keep-pod` is unchanged.
Run the research tool's test suite on a small pod or on your VM (it's light), not on the laptop.

## Deliverable

A PR against `main` from branch `lane/reaper-resume-guard`, with the tests passing. Send the coordinator a merge-ready
handoff: tip, test counts, and the new log lines. The coordinator merges it and restarts the steward. FINAL: 12:00Z + 4 h
(16:00Z). Budget: $3.
