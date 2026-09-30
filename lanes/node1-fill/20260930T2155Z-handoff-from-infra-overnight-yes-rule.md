---
id: 20260930T2155Z-handoff-from-infra-overnight-yes-rule-node1-fill
campaign: verity
lane: node1-fill
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node1-fill: overnight, run nothing without the owning lane's explicit yes and a named research question; PoUS and network accounting are paused

**New standing rule (Daniel, 2:52 PM PDT):** every overnight queue needs an explicit yes from its lane's research owner, and every job names the research question it answers. Idle beats padded.
- **The yes:** before a job runs overnight (tonight from about 9 PM PDT), its lane's owner must have said yes to that queue in
  `lanes/node1-fill/` or on Slack. That is circuits for Commits and TP2, and proofs for the K=2048 row and sampled units. The job's header names its
  question.
- **No yes, no run:** leave the GPU idle, and report the gap.
- **Focus (Daniel):** PoUS (memory accounting) stays paused and network accounting is pausing, so run nothing of theirs overnight. The
  one exception is network's #326 check, already planned for the train on node 1.
- **A new lane, resource-steward,** takes over disk, cache and RAM policy on both nodes, including cleanup on node 1. Send it disk and
  RAM questions in `lanes/resource-steward/`.
