---
id: 20260930T2155Z-handoff-from-infra-overnight-yes-rule-node2-ops
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: overnight, run nothing without the owning lane's explicit yes and a named research question; PoUS and network accounting are paused

**New standing rule (Daniel, 2:52 PM PDT):** every overnight queue needs an explicit yes from its lane's research owner, and every job names the research question it answers. Idle beats padded.
- **The yes:** before a job runs overnight (tonight from about 9 PM PDT), its lane's owner must have said yes to that queue in
  `lanes/node2-ops/` or on Slack. That is compute-accounting for PoUW, and circuits for its Commits. The job's header names its
  question.
- **No yes, no run:** leave the GPU idle, and report the gap.
- **Focus (Daniel):** PoUS (memory accounting) stays paused and network accounting is pausing, so run nothing of theirs overnight. The
  one exception is network's #326 check, already planned for the train on node 1.
- **A new lane, resource-steward,** takes over disk, cache and RAM policy on both nodes. Keep your OOM guard and the 55% start-stop as
  enforcement, and hand it cleanup decisions. Its handoff will arrive in your lane.
