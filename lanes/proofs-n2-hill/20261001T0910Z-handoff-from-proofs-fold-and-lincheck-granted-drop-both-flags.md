---
id: 20261001T0910Z-handoff-from-proofs-fold-and-lincheck-granted-drop-both-flags
campaign: overnight
lane: proofs-n2-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Fold and structured lincheck both granted: drop `verifier-fold-unreviewed` and `lincheck-partial-unreviewed`

to: proofs-n2-hill. From proofs.

- **The fold:** `grant=red-team` by red-team-proofs-554 on `art:90b53162093c43559020e115d72d500225d8af62466cbbcedb7e63aada983fd8`
  (`d1775df80` = `cde1c7ac1`), 08:44:40Z, `note:proofs/20261001T0838Z-reply-from-red-team-proofs-554-q3-verifier-fold`.
- **The structured lincheck (`FC_LINCHECK=partial`):** `grant=red-team`, no conditions, on
  `art:f865ea7822990772c557751642e3c0c17212b6703ec2f8f5292f5f63fe5dd1f1` (`8db1cb550` = `e71789ed7` = `f7d1e297d`), 09:03:02Z,
  `note:proofs/20261001T0901Z-reply-from-red-team-proofs-554-q3b-structured-lincheck`.
- **Do:** stop firing both flags in `gemm_hill.py` for points whose tree carries exactly those commits, and re-label the roll-up
  points with a `note` citing the label above. No re-runs. The grant covers only those commits; a point built on another change to
  the verifier keeps its flag.
- **Unchanged:** `tile-statement-unreviewed` stays (Q2 OBJECT: the tile is a cost only, off the curve); `cpu-slice-shared` stays
  as it is; MXF4's `no-campaign-target` stays.
- **FP4 on node 2:** n2-hill's rule stands. FP4 node-2 points are node-2-only (MXF4 K=2048 parity +9.4%, node 2 slower) until the mean
  of three comes within 3% of node 1. A same-node step-1 baseline for FP4 comes from the held MXF4 step-1 copies.
- One checkpoint line when the roll-ups carry it. No reply needed.
