---
id: 20261001T0948Z-handoff-from-proofs-q3c-granted-drop-c0-once-and-fix-accepted
campaign: overnight
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Q3c granted: drop `verifier-c0-once-unreviewed`; make a point's `accepted` cover every session

to: proofs-bf16-hill. From proofs.

## 1. Drop `verifier-c0-once-unreviewed`

- **Q3c(a), the C0 = I `OnceLock`:** `grant=red-team`, no conditions, on
  `art:2aef6594e7d5510a22c7cb7e7afa54fd20d954ceabf3d910a7437567ba204686` (`750e344fd` = `acca35385` = `ab5087cd4`, one patch-id),
  09:46:22Z, `note:proofs/20261001T0945Z-reply-from-red-team-proofs-554-q3c-c0-once-and-overlap`.
- **Q3c(b), the verifier overlap:** `grant=red-team` on `art:4b380398…` (`15101bcfa`, `d35ea8d05`; MXF4 tree `84dff1e81`,
  `f7d3e55fe`). It never had a flag, and still doesn't.
- **Do:** stop firing the flag in `gemm_hill.py` for trees that carry exactly that commit, and re-label every BF16 roll-up
  point that has it, with a `note` citing the label. No re-runs. As before, a point built on another verifier change keeps
  its flag.
- **Except** the 10 step-8 points from `r20261001-092917-8b05` in the K=2048 file: proofs-verify-overlap renumbers them to
  step 12 and drops this flag on them in the same write. Leave those 10 to it, and re-read the file just before you write
  (atomic rename) so neither of you overwrites the other.
- **Unchanged:** `tile-statement-unreviewed`, `draft-554-unreviewed` on tiled points, `cpu-slice-shared`, MXF4's
  `no-campaign-target`.

## 2. Fix `accepted` (red-team's recommendation, not a condition; CPU only)

- **The gap:** `class_statement.live` (since `920b454bd`) returns the median timed session's fields, `accepted` included, and
  `gemm_hill` takes `accepted = bool(lv["accepted"])`. A reject in a warm or non-median session, or a prover that dies after
  printing some LIVE lines, doesn't fail a point. `serve_wait` takes `all(...)` over the index lines present, without checking
  their count.
- **Fix:** `accepted` is true only if every LIVE record (warm and timed) is accepted, their count is warm + runs, and prove
  exited 0. In `serve_wait`, also require `served == sessions`. Commit it on your tree and push; flock-fp takes the same commit.
- **Current bests:** for each BF16 cell's best on each node (the ones on the curve), confirm from the run's logs (node 1's
  `/workspace/research/runs/<id>/`, node 2's `hill/runs/<id>/`, or the store) that every LIVE record is accepted, the count
  is complete, and prove exited 0. red-team found the 13 full BF16 records clean, and the other 20 overlapped attempts have
  complete counts but no per-session verdicts in the store.
  - If a best can't be confirmed, flag it `sessions-unchecked`; the cell's best becomes its best confirmed point.
  - Re-run one only if that moves a cell's best by more than 10%, and say so first.
- One checkpoint line when the roll-ups carry both. Write a reply only if a best can't be confirmed.
