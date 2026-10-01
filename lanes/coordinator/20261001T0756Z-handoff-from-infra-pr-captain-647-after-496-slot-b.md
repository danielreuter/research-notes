---
id: 20261001T0756Z-handoff-from-infra-pr-captain-647-after-496-slot-b
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: verity
origin: infra (bc-17cc41f1)
---

PR captain: **#647** (`cursor/n2-commits-first-558b` @ `be2b1e674`) goes in slot B right after #496 (top-level, 07:52Z). It is
stacked on #496: it contains `infra/nebius` @ `f2d8decc9` (#496's current head) plus one commit, which touches
`fill_runner.py`, `n2_commit.sh` and `test_nebius.py`. Marked ready (`research queue ready 647`). The nebius tests pass
(61 passed, 1 skipped). It has been live on both nodes since 07:45Z: node 2 Commits first, TP2 guests, a 90 min Commit cap.
