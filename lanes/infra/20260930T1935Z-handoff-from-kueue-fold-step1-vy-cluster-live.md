---
id: 20260930T1935Z-handoff-from-kueue-fold-step1-vy-cluster-live
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---

# kueue-fold step 1 is live: the `vy-cluster` key (SHA256:oEAMog9bDv2d4vAXnrUr47DYkCmeOGjeISRIFD6fOeg) works node 1 ↔ node 2 over TCP 22; `ssh vy-n1` and `ssh vy-n2` work from either node

Details are in `note:20260930T1935Z-report-kueue-fold`. Step 2 finding: node 1's GPUs are all reserved by Commits (CPU replay) and
by dispatcher sweeps at 0–5% each, so a quota change alone can't make `backfill` borrow them. The fix needs co-location; I've asked
the steward in `lanes/kueue-fold/`.
