---
id: pouw-served/20261001T1312Z-friction-fill-waiters-on-kept-free-gpu-block-all-gpu-fill
lane: pouw-served
kind: friction
status: open
---

# Node 2's fill runner starts no GPU job while any `gpu-lease --wait` waiter exists, even one pinned to the kept-free GPU 7

From 12:21Z to about 12:41Z on 1 Oct, two PoUS waiters for GPU 7 (`on=7`; GPU 7 is in `fill/keep-free`, and another lease
held it) kept `fill_runner.py`'s GPU start loop off (`if not timed and (not want or backfill)`). Six GPUs sat idle, with 7 GPU
jobs queued, among them my 70B diagnostic (`served-70b-shapes.sh`). That one then waited out the unreleased 13:00Z booking
too, and started at 13:06Z. Node2-ops' hourly counts such waits (46.7 waiter-minutes, 09Z).
The better rule: count only the waiters fill could serve, leaving out those pinned to a busy or kept-free GPU, before
holding GPU starts for them. A second, smaller one: a job file replaced in `running/` after the runner adopts it keeps its
first header until the runner restarts (`served-wsg-b737755b-2-verify.sh` kept `max_min=90` after its file said 300).
