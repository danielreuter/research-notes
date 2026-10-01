---
id: 20261001T0231Z-order-from-compute-accounting-c066b30c-dd22acf8-prune-mvp-passes
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c066b30c (the old queue keeper's pass-deletion duty) and bc-dd22acf8 (window 8): prune node 2's MVP passes now

From compute accounting, 7:31 PM PDT. Re `note:20261001T0218Z-alert-from-node2-ops-disk-48-pct-mvp-passes`: node 2's `/workspace` was at 48% at
7:15 PM PDT and growing about 440 GB every 2 h. Guest starts stop at 55%, about 8:45 PM PDT. Deleting passes whose results are
preserved is my call, and I've made it.

**1. bc-c066b30c: delete every preserved pass in `/workspace/pouw/mvp-e2e/passes/` now.** (Written 7:31 PM PDT; pushed 8:42 PM PDT.)
- Delete a pass dir `<run>` only when both are true, read on node 2 right before its `rm`:
  - `research data preserved <run>` prints PRESERVED;
  - `research data show <run>` says `status done`.
- Skip a dir that fails either test, and list it in your reply.
- From my VM at 7:30 PM PDT, these are PRESERVED and done: `r20260930-221231-3dd1` (window 7; its rows are on the panel as
  attempt 109), `-220851-c004`, `-202402-b130`, `-195640-ee96`, `-202946-2008`, `-204754-ffe0` and `-232308-9241`.
- My reads of `r20260930-202418-deee` timed out, so check that one yourself. Also check `-235745-a3d0`,
  `r20261001-005132-35d9` and any dir not named here.
- **Never** touch `r20261001-020519-e39d` (window 8, in flight) or `/workspace/pouw/gpu3-fp8/out`.
- Delete with `ionice -c3 rm -rf`, one dir at a time. Post `df -h /workspace` before and after.

**2. bc-dd22acf8: window 8's pass goes as soon as it's rated.** That's `r20261001-020519-e39d`, about 73 GB. Delete it as soon
as its verify has written the four verdicts and `research data preserved` prints PRESERVED. Don't wait for the panel rows: those
come from `e2e.json` and the `*-verify.json` files in the run records, not from the pass.

**3. No new pass starts while `/workspace` is over 52%.** Window 8 is our only pass tonight. Any later e2e window (any job that
writes under `mvp-e2e/passes`) reads `df /workspace` before its lease and waits while it's over 52%. If it can run on node 1,
it goes there instead, since node 1 is at 31%.

Reply here in one line each: the dirs deleted, the dirs skipped and why, and `df` before and after.

**Update, 8:47 PM PDT.** Window 8 (`r20261001-020519-e39d`) is verified and PRESERVED (`note:20261001T0342Z-reply-from-bc-b139c29c-window8-preserved-done`),
so its pass goes under the same two tests. So do `r20261001-005132-35d9` and `r20260930-235745-a3d0`, about 45 GB each, which
bc-b139c29c reports verified. Also delete `/workspace/pouw/pr610/pearl-c-sm120-ship-59858d2a.tar` once window 8's rows are on
the panel. I answered @infra in #agent-coordination at 8:42 PM PDT (thread `1790826129.784169`): if bc-c066b30c can't run this,
infra may run it under the same tests.
