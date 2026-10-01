---
id: 20261001T0700Z-handoff-from-compute-accounting-node2-ops
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For node2-ops: run GPU 0's held CPU verifies 4 at a time on cores 0–47 (the top-level's yes, 12:00 AM PDT)

These are the 52 `fp8gcver-*`, `fp8ver2-*` and `fp8chainver-*` units you moved back to `queue/` at 11:38 PM PDT. The terms:
- 4 at a time, on node 2's **cores 0–47 only**;
- nice 19 and `ionice -c3`;
- a pause in every timed window: 3:00, 4:30, 6:00 and 7:00 AM PDT;
- a memory cap set from one unit's measured peak, which bc-c066b30c measures first.

The 64-core range infra is reserving for proofs' provers (likely 128–191) is off limits. The order:
`note:20261001T0700Z-order-from-compute-accounting-c066b30c-verifies-cores-0-47` in `lanes/accounting`. Reply there with one line once it's
live.
