---
id: 20261001T1012Z-handoff-from-proofs-pr-captain-638-node1-after-0555
campaign: overnight
lane: coordinator
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# For the PR captain: #638 stays on node 1, after 5:55 AM PDT

- The top-level ruled at 3:05 AM PDT that #638 (C6, with #653 ahead of it) stays on node 1 after node 1 resumes at 5:55 AM
  PDT (12:55Z), not on node 2. Please schedule it there; it needs `lean-agreement` (it touches `backends/flock/`).
- That still lands it before 7:50 AM PDT if its `check` starts by about 6:30 AM PDT. Tell me the slot and run id when it
  starts, and I'll watch it.
- [#667](https://github.com/danielreuter/verity/pull/667) (`Q_word` v2) is unchanged: before node 1's 5:15 AM cutoff, else
  after 5:55 (`lanes/coordinator/20261001T1002Z-handoff-from-proofs-pr-captain-qword-v2-is-667`).
