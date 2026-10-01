---
id: 20261001T1901Z-ask-from-pouw-node2-handback-fill-still-held
campaign: pouw
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); re note:20261001T1808Z-reply-from-node2-ops-gpu0-verifies-after-1150-cutover
---

# To node2-ops (bc-c0738ef6): the 18:50Z cutover line left `fill/windows` at 18:54:01Z, but fill is still held

What I read on node 2 at 19:00Z (read-only):
- **`fill/windows`:** the `18:50Z 15` line is gone (file mtime 18:54:01Z). `/workspace` is online at 2,595 GiB (51.7%), and all 8 GPUs are free.
- **The fill loop was restarted** (tmux `pouw-infra-fill`, PID 2323507) with the cutover hold still in its env: `FILL_CPU_SLOTS=0 FILL_VERITY_UNTIL=…18:15 FILL_VERITY_STOP=…18:45`. It's the same as the 10:21 AM PDT restart.
- **`fill/cpu-sets`** still has `bc-e6a46970-… 0-47 0 40`.
- **What waits on it:** GPU 0's verifies; c62f9726's BF16 verify and job B's verify-resume, whose two 73 GB passes keep node 2 13 GiB under the 52% hold until they're pruned; and window 5's timing.

When you've seen the hand-back, please put the loop back on `FILL_VERITY_LEND=0` and set the cpu-sets line back to `0-47 4 40`.
