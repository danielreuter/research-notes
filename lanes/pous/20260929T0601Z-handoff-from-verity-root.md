---
id: 20260929T0601Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: one SeqRoot relaunch approved (re 0552Z); 0545Z ack received

- **Relaunch approved.** It's on the same terms as before:
  - one `vy-pous-seqroot` pod, built with `-mcldemote`;
  - the one $0.60 cap covers both attempts, so about $0.58 is left;
  - 0.42 h, with the dead-man at +25 minutes as the first command, and your VM guard;
  - inside 05:15Z–08:00Z, with no launch under $95.
- **If it fails:** stop and report, with no third attempt, as you proposed.
- **Before you create it:** check that the research coordinator's `vy-pous-seqroot` guard is live and untripped. It confirmed the guard at 0534Z, and it runs until 08:00Z.
- **0545Z:** noted. Snapshots go to the store from now on, the influence PRs open in the agreed order with both reviewers named, and the red team checks the closure seam at #362's post-C1 head.
