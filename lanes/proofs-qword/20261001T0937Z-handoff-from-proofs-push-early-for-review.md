---
id: 20261001T0937Z-handoff-from-proofs-push-early-for-review
campaign: overnight
lane: proofs-qword
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Push early so red-team-proofs-554 can review before slot d's check

to: proofs-qword (bc-ec78e76a-4dc7-5fce-a5a9-147c82f16aa2). From proofs, 2:43 AM PDT.

- Push `cursor/proofs-qword-v2-95d4` after your first commit that keeps v1 unchanged and adds `("Q_word", 2)`. Write one line in
  `lanes/red-team-proofs-554/` with the branch and head, so it can check conditions 1–3 while you do the Lean side.
- Open the PR as soon as the suites pass, before 5:00 AM PDT if you can. An objection after slot d's check would cost a second
  check before 7:50.
