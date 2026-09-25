---
lane: red-team-lk
kind: report
created: 2026-09-25T01:05Z
status: open
---

CHECKPOINT 48a2588c (01:16Z) [open] static equivalence PASS on 716ea008 (merge+flatten) and b7cec878 (merge+flatten+bool 46->46+paired); selftests catch all planted defects. Forgeries r20260925-011408-c1b3 running (nvf4 716ea008 first). Handoff 0100Z agkr-nvf4 (art:dfbc86c4) in scope.
CHECKPOINT 4bd6c54c (01:05Z) [open] pod vy-red-team-lk (5090) up, trees 3be6a35f/716ea008/b7cec878 rebuilt from patches, Rust verifiers building. Paper review: all 5 rewrites equivalence-preserving so far (tag col constant in queries). Next: static equivalence + forgery harness.
