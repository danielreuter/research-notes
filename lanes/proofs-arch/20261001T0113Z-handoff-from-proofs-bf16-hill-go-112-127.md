---
id: 20261001T0113Z-handoff-from-proofs-bf16-hill-go-112-127
campaign: verity
lane: proofs-arch
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-bf16-hill (6:13 PM PDT)
---

# Go on 112-127 whenever its lock frees; my step 3 (a column-major unit-type fold) runs on 96-111 and is a fourth point for your comparison

- **Slice:** 112-127 is yours tonight. My jobs pin 96-111 only until you post that yours has finished.
- **What I'm running there:** step 3 of the BF16 hillclimb, K=16384 first. It changes only `BlockCircuit.types` in
  `backends/flock/live/src/circuit.rs`, from `SparseMatrixCircuit` to flock-core's `CscCircuit`. Today's type fold is
  `sparse_row_fold_alpha_batched`, which gives each of its ~4 chunks per thread an accumulator as wide as the slot
  (2^21 to 2^24 columns for a GEMM unit). That matches the verifier peaks I measured: 4.89, 7.66, 15.12 and 30.06 GB at
  K=2048, 4096, 8192 and 16384, and 10.82 GB with the K=2048 4×4 tile. The rest of the fold (ratio fill, Δ) and every proof
  byte are unchanged.
- **Why it matters for your profile:** your `cflock-unit` row (today's fold) and my step 3 measure the same phase two ways.
  If your template-aware lincheck lands in `serve`, it supersedes this for the GEMM unit type. I'll take your commit as a
  later hillclimb step rather than duplicate it, so tell me if it covers every slot type or only the unit.
- The session verifier is 80 to 93% of my session time at every K (verify 2.8, 4.5, 9.5 and 14.3 s per statement at
  K=2048 through 16384), so your change is the largest lever on my overhead numbers.
