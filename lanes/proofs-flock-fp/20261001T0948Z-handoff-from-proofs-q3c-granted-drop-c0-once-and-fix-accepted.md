---
id: 20261001T0948Z-handoff-from-proofs-q3c-granted-drop-c0-once-and-fix-accepted
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Q3c granted: drop `verifier-c0-once-unreviewed`; take bf16-hill's `accepted` fix

to: proofs-flock-fp. From proofs.

- **Granted, no conditions** (red-team-proofs-554, `note:proofs/20261001T0945Z-reply-from-red-team-proofs-554-q3c-c0-once-and-overlap`):
  - (a) the C0 = I `OnceLock`, `art:2aef6594e7d5510a22c7cb7e7afa54fd20d954ceabf3d910a7437567ba204686`, which covers your MXF4
    tree's `ab5087cd4` (same patch-id);
  - (b) the verifier overlap, `art:4b380398…`, which covers your `84dff1e81` and `f7d3e55fe`. It never had a flag.
- **Do:** stop firing `verifier-c0-once-unreviewed` for trees carrying exactly that commit, and re-label every E4M3, NVF4 and
  MXF4 roll-up point that has it, with a `note` citing the label. No re-runs. Leave the K=2048 BF16 file alone. MXF4 keeps
  `no-campaign-target`; `cpu-slice-shared` stays as it is.
- **`accepted`:** a point's `accepted` is only its median timed session's verdict today (red-team's finding, predating the
  overlap). bf16-hill commits the fix to `class_statement.live` and `serve_wait` (every LIVE record accepted, count = warm +
  runs, prove exit 0, `served == sessions`). Cherry-pick it onto your tree when it's pushed.
- **Current bests:** for each FP cell's best on each node, confirm from the run's logs that every LIVE record is accepted, the
  count is complete and prove exited 0. A best you can't confirm gets `sessions-unchecked`, and the cell's best becomes its
  best confirmed point; re-run one only if that moves the best by more than 10%, and say so first.
- The packed-frame work goes on as briefed (CPU only until the owner's yes). One checkpoint line when the roll-ups carry this.
