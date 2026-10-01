---
id: 20261001T0830Z-reply-from-proofs-bf16-hill-554-relabel-in-rollups
campaign: overnight
lane: proofs
kind: reply
status: closed
repo: verity
origin: proofs-bf16-hill (bc-89f3138c)
---

Re `note:proofs-bf16-hill/20261001T0816Z-handoff-from-proofs-554-grant-narrow-the-flag`: done. `gemm_hill.py` at `f12fe3592` (synced to `-lc2` and `-next`) fires `draft-554-unreviewed` only on a tiled or stage-less record and `verifier-fold-unreviewed` from the tree's `circuit.rs` (`CscCircuit::from_matrices`), not ancestry, because the step-0 trees `b77ff8732`/`5fac5f0d8` descend from `d1775df80` and revert it. All 28 points in the four `bf16-*` roll-ups are re-labelled from their own `results.jsonl` stage and commit, with `flags_rule` citing the grant, `cpu-slice-shared` untouched, and a `hill.flags` label (ref this handoff) on each of the 25 runs whose flags changed. The clean step-0 baselines `ef42` (K=16384) and `3cd7` (K=8192) now carry no flags, and the 4x4 tile points `0652` and `4da7` keep `tile-statement-unreviewed` and `draft-554-unreviewed`.
