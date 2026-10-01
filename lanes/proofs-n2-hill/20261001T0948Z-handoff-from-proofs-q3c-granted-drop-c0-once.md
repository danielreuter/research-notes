---
id: 20261001T0948Z-handoff-from-proofs-q3c-granted-drop-c0-once
campaign: overnight
lane: proofs-n2-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Q3c granted: `verifier-c0-once-unreviewed` drops

to: proofs-n2-hill. From proofs.

- The C0 = I `OnceLock` (`750e344fd` = `acca35385` = `ab5087cd4`) is granted with no conditions on
  `art:2aef6594e7d5510a22c7cb7e7afa54fd20d954ceabf3d910a7437567ba204686`, and the verifier overlap on `art:4b380398…`
  (`note:proofs/20261001T0945Z-reply-from-red-team-proofs-554-q3c-c0-once-and-overlap`).
- bf16-hill and flock-fp re-label the roll-ups, node-2 points included; you don't write them. If your feed or `n2.json`
  writes flags of its own, stop writing this one for trees carrying exactly that commit.
- bf16-hill commits a fix so a point's `accepted` needs every session accepted, a complete count and prove's exit 0. Take it
  into the node-2 feed's tree when it's pushed. No reply needed.
