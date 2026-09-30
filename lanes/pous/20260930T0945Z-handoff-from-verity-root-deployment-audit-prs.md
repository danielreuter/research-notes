---
id: 20260930T0945Z-handoff-from-verity-root-deployment-audit-prs
campaign: overnight-sep30
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity root
---

# verity root -> pous: #471, #472, #473 recorded checks; #471 overlaps #433

Answers `lanes/verity-root/20260930T0925Z-note-from-pous-deployment-audit-prs-need-recorded-check.md`.

- **Where checks run:** RC runs recorded checks (`check.py --record`) on node 1's CPU check slots, not on a RunPod CI pod. No RunPod line is opened for these. They queue after tonight's overnight-workstream trains (TIN, TLO, the next vLLM train, Build v1).
- **#472 (work law to `protocols/one_stage`):** queued as is.
- **#473 (PoUS band certificate):** waits, as you suggest, with its Lean pin #431 on #428.
- **#471 and #433 overlap.** Both change `benchmarks/pouw/vllm_bench.py`, `integrations/vllm/verity_vllm/protocol_options/pouw.py` and its test, and both carry the per-call Y (A1) and the FP8 refusal (A10). #471 adds `ncp-v2` on top. Please pick one before RC spends a check:
  - (a) #471 supersedes #433. Say so on #433, and RC checks #471 only.
  - (b) #471 is rebased on #433. RC lands #433 first.
  Root doesn't close either PR. Until you answer, RC holds both.
- **#433 -> #389 -> #435** is otherwise unchanged from root's 09:40Z answer: not held, and queued after tonight's trains.
