---
id: 20260930T2355Z-handoff-from-circuits-workflow-fixes
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); Daniel asked for these to be fixed ASAP (4:54 PM PDT)
---

# circuits → infra: eight workflow fixes from tonight, ranked; Daniel wants them ASAP

What went wrong tonight, from circuits' seat, and the fix for each. Items 1, 2 and 6 are process, not tooling: take them to the
top-level if they aren't yours.

1. **Orders reach workers slowly, from too many directions.** Workers read handoffs only at checkpoints (20–30 min), while coordinators
   decide on Slack in minutes. Orders crossed three times: the TP2 route (root vs circuits), and the pacing handoff (steward ↔ @infra,
   twice). **Fix:** one order-giver per worker (circuits lanes → @circuits; others route through it), and a fast path for urgent orders:
   the top-level wakes a worker when a handoff titled URGENT lands in its lane, or workers poll their inbox every 5 min during an
   incident.
2. **Workers the coordinator can't direct.** The TP2, staging-bug and coverage-defs lanes belong to @old-circuits-and-proofs, so every
   instruction takes an extra hop. phi3b8g's replay never started, and phi3b8i launched against a hold. **Fix:** transfer those lanes to
   @circuits (or FINAL them and let @circuits relaunch).
3. **Safety limits arrived one incident at a time**, each with a 10-min deadline, and node 1 sat idle behind holds for ~1 h. **Fix:** make
   tonight's guards platform defaults, fail-closed, on both nodes and in `research run --queue`:
   - the disk guard (80/75%);
   - the bundle-estimate pacer (`release.py`: on-disk + in-flight estimates < 150 GB, ≤ 2 B8+);
   - failed-Commit bundle cleanup;
   - template pinning per item;
   - replays ahead of Builds.
   Coordinators set the limits once, not per incident.
4. **No one-command queue view.** Every decision needed hand-rolled SSH (`du`, `ps`, `log.jsonl` parsing). **Fix:** `research queue status
   [--owner circuits]`, per node:
   - running and queued items by key (row, batch, phase);
   - GPU-h ready;
   - unreplayed bundle GB;
   - holds and deactivated workloads;
   - disk %.
5. **The Slack CLI lives in `/tmp/slack-wt`** (#592's branch) and dies with a VM reset. **Fix:** merge #592.
6. **Goal churn:** six priority resets in four hours, each prompting a rewrite (the circuits goals doc was superseded in 10 min).
   **Fix (top-level):** fewer resets; ask coordinators for deltas, not new docs.
7. **Tooling papercuts:**
   - re-arming a Cursor timer under a name you just unsubscribed fails silently (returns the closed one);
   - store writes intermittently return EAGAIN (retries needed);
   - every post echoes back as a wake to its author. A filter in the delivery, or `match` exiting 1 on the reader's own handle before
     the model sees it, would save a turn per post.
8. **Coordinator time goes to ops:** circuits spent most of the evening approving disk and queue actions, and its research streams
   started at 4:40 PM PDT. With items 1–4, circuits sets policy once and infra runs it.
