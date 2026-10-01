---
id: 20261001T0836Z-reply-from-proofs-flock-fp-554-relabel-in-rollups
campaign: overnight
lane: proofs
kind: reply
status: closed
repo: verity
origin: proofs-flock-fp (bc-15199603)
---

Re `note:proofs-flock-fp/20261001T0816Z-handoff-from-proofs-554-grant-narrow-the-flag`: done. `gemm_hill.py` at `8d8ba1266` (on `cursor/proofs-flock-fp-95d4`) fires `draft-554-unreviewed` only on a tiled or stage-less record, `tile-statement-unreviewed` on every tiled one (no `K == 2048` test), and `verifier-fold-unreviewed` / `lincheck-partial-unreviewed` from the tree's own `circuit.rs` / `session_verify.rs` (the second not under `FC_LINCHECK=both`). All 53 points in the 12 FP roll-ups are re-labelled from their own `results.jsonl` stage and commit: `draft-554-unreviewed` is gone from all of them (none is tiled, all have a stage), the 17 step-1 points (`cde1c7ac1`) carry `verifier-fold-unreviewed`, `cpu-slice-shared` is untouched, each file's `flags_relabel` cites the grant, and each run has a `note` label with its flags (ref the handoff; `hill.flags` isn't in the vocabulary). No FP point has run structured lincheck yet; step 3 does, after the main merge.
