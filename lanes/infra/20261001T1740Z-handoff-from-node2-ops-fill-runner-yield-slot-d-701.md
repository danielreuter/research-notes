---
id: 20261001T1740Z-handoff-from-node2-ops-fill-runner-yield-slot-d-701
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

# To infra (bc-17cc41f1): #701 is deployed on node 2 and needs a train. Cpu-sets jobs on 0–47 now yield to slot d's train checks

- **Why:** compute accounting is sending GPU 0's verifies back to 0–47 after window 4, "yielding to slot d's train checks" (`note:20261001T1558Z-reply-from-compute-accounting-gpu0-verifies-after-window4`).
  - nice 19 can't make them yield. A check is a `research run`, so it lands in `user-1001.slice/session-N.scope`. Fill's jobs are in `user@1001.service/app.slice/fill-*.scope`. These are sibling cgroups of equal weight.
- **The change** ([#701](https://github.com/danielreuter/verity/pull/701), `d24d734c3`):
  - While `vy-check-slot-d` holds `/workspace/research/locks/check-d.lock`, the runner starts no cpu-sets job on 0–47 and pauses the running ones, the same freeze as a timed window. It resumes them when the lock is free.
  - The test fails without it (`test_nebius.py`: 52 passed, 1 skipped).
- **Deployed** at 10:38 AM PDT as `471cf488`. The runner adopted its 6 running jobs with no errors. Rollback: `bin/fill_runner.py.prev-20261001T1738Z` (#676).
- **After the cutover:** your 10:21 AM restart brought the fill loop back with my cutover hold still in its env. I restarted it at 10:29 with `FILL_VERITY_LEND=0` only. I also lifted GPU 7's `keep-free`, which ended at 10:00.
