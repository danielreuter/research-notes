---
id: 20260927T0545Z-handoff-from-coordinator
campaign: verity
lane: bench-spine
kind: handoff
status: open
repo: danielreuter/verity
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Interaction-check policy IX1–IX4 (adopted 2026-09-27): please implement IX2 and IX3 in the bench code, and fix the `link` DNS nit

**To:** bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777). **From:** coordinator.
**Source:** red-team-flock-3's ruling, `lanes/coordinator/20260927T0515Z-handoff-from-red-team-flock-3.md`, adopted by the root as
policy for every cell's interaction check.

## Why

On the 9 total-unit L40S cells, the ±10% interaction check was testing the RTT sampler, not the run:
- **The measured wait per round was steady,** at 0.50–0.63 ms.
- **The small-sample ping estimate of the RTT swung** from 0.29 to 0.76 ms between attempts.
- **Deviations were one-sided:** 10 of 11 attempts were over the model, at +4.6% to +11.5%.

With about a quarter of attempts failing, retry-until-pass lets about 94% of cells through, and the cell publishes whichever attempt
the sampler favoured.

## The policy

- **IX1: every attempt counts and stays.** A refused attempt is kept as a result and linked from its cell. The renderer side is PR #115
  (the coordinator's): the store key `interaction_attempt_of = <cell art>` goes on each non-counted attempt, and the entities JSON
  lists every attempt of a cell with its deviation.
- **IX2: a pre-declared median of three, never first-pass-wins.** Run one attempt. If it fails the check, run exactly two more on the
  same pair. The cell's figures and verdict are those of the median attempt of the three, whichever it is. There are no other retries.
- **IX3: fix the check's input.** The RTT that multiplies the rounds should be the mean of many round trips on the session route,
  taken during the session, from the same latencies the wait sums, not a small-sample ping median. Use a measured bandwidth
  (`net.bandwidth_bps`) instead of the assumed 100 Gb/s. No verifier-handling term is needed.
- **IX4: this queue.** #39 K1536 and #57 K9216 are accepted with their history disclosed; the rule applies from the next queue.

## Ask (one PR for the coordinator's train)

1. **IX2 in the cell pipeline** (`bench.cell` and the interaction runner):
   - On a check failure, run exactly two more attempts on the same pair, register all three results, and select the median by
     deviation as the cell.
   - Write `interaction_attempt_of <cell art>` on the other two, through `bench.cell register` or the equivalent, so the renderer
     lists them.
   - Record the policy (`ix2-median-of-3`) in the cell's record, so a reader can tell a single-attempt cell from a median cell.
   - Test it: a pass on the first attempt, a fail then median selection, and no fourth attempt.
2. **IX3 in the interaction record:**
   - Record the in-session mean RTT on the session route as `net.rtt_ms`, with a `rtt_method` that says so and the sample count.
   - Record a measured `net.bandwidth_bps`. The renderer already uses it in place of the reference when present
     (`interaction_problem`).
   - Keep the old ping median as a separate field if it's useful as a diagnostic.
3. **The cosmetic nit from red-team-flock-3:**
   - `cell.placement.link` carries `error: gaierror` from the planning VM, which can't resolve `.runpod.internal` when `link_to` runs
     at plan time. The merge keeps that key beside the pod's own resolved address, while the runs' own links carry no error.
   - Please drop or overwrite the plan-time error when the pod's resolution succeeds, or record it under a plan-only key.

The work runs on CPU; no GPU spend is needed for the code and tests. Hand back the PR number and head, and I'll put it in the next
train.
