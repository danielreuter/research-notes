---
id: 20260930T2342Z-handoff-from-circuits-build-speed-worker
campaign: verity
lane: build-optimization
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); cc vllm-coordinator (@old-circuits-and-proofs)
---

# @circuits: a circuits worker is taking "Llama-3.2-1B Build ≤ 6 min by 11:40 PM PDT"; tell it what you have in flight so you don't collide

Daniel's goal of record (4:37 PM PDT): the Llama-3.2-1B config-run Build (reference: B8 1k/128 greedy, ~28 min today) at 6 minutes or
less by 11:40 PM PDT, digests identical. Your lane has posted nothing since about 7:30 AM PDT, so circuits started worker
`circuits-build-speed` (branch `cursor/build-speed-8c79`, notes lane `circuits-build-speed`). It starts from your plan: parallel derives
by default, the parallel and cached word check, and dropping the second export.

If you're mid-change on any of these, or on #517 / #522, write one line in `lanes/circuits-build-speed/` with the branch and state, and
split the work with it; otherwise it builds on your branches as they are. Still wanted from you: the per-Build RSS / cores / admission
measurement (the old coordinator's 1:03 PM PDT ask), to `lanes/circuits/`.
