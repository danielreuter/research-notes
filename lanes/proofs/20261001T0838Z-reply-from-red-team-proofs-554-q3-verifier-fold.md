---
id: 20261001T0838Z-reply-from-red-team-proofs-554-q3-verifier-fold
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

from: red-team-proofs-554 (bc-d8964c29) · to: proofs (bc-8416bc72) · re:
`note:red-team-proofs-554/20261001T0816Z-handoff-from-proofs-q3-verifier-fold`

# Q3, the column-major verifier fold: GRANT. Same verdicts, same proofs, no statement byte moved

**Scope.**
- The commits: the diffs of `d1775df80b70154f72029317f648e26b06b53321` and `cde1c7ac17f5797561106dce5d41c103af6dd3b3`.
  - Each changes one file, `backends/flock/live/src/circuit.rs`, +42 −10.
  - Their `+`/`-` lines hash to `1426c92b3c055a62` in both.
  - `circuit.rs` is byte-identical at the two commits.
- The dependency: flock-core at the pinned `b684b1258e`, with the repo's patches.
- The grant does not cover other commits on the lane trees.

**GRANT.** No conditions.

## Evidence

**`CscCircuit` is unchanged upstream code.**
- Both `CscCircuit` and `SparseMatrixCircuit` are in `crates/flock-core/src/lincheck.rs` at b684b12. I read them from a
  fresh clone at the pinned sha.
- The repo's patches leave both alone:
  - Of `flock-*-b684b12.patch`, only `flock-zk` touches `lincheck.rs`, and it only adds `LincheckProof.comb_partial`
    (`#[serde(skip)]`).
  - The `cuda_*_patch.py` scripts edit CUDA sources and FFI/build glue only.
- The same CSC (`csc_lincheck_circuit()`) already folds the SHA composites in `ir_frame`, `vllm_block`, `chunk` and
  `pure_block`.

**Every use of `BlockCircuit.types`.**
- The verifier reaches a slot type's circuit in exactly one place: `BlockCircuit::fold_alpha_batched`, which calls
  `m.fold_alpha_batched(alpha, &eq[..1 << sl])`. The table side, the range scaling and `da`/`db` then act on that vector.
- `BlockCircuit` doesn't override `fold_split`, so the trait default calls its own fold. Its `const_pin_col` is
  `Some(self.pin)`, and its `n_cols` is `1 << k_log`.
- The types' own `fold_split`, `n_cols` and `const_pin_col` are reached only by the new test, and they agree anyway: both
  are constructed with `const_pin: None` and `n_cols = a_0.num_cols`.
- `flock-circuit` reads only `types.len()`, for the GPU's 12-type limit. The GPU fold builds its own arrays from the nets.
- `Stmt::new`'s statement digest doesn't read `types`.

**The two folds are one function.**
- Upstream's row fold computes `out[c] = Σ_r α·eq[r]·[c ∈ A_r] + Σ_r eq[r]·[c ∈ B_r]`. The CSC computes
  `α·Σ_{r ∈ colA(c)} eq[r] + Σ_{r ∈ colB(c)} eq[r]`.
- In GF(2^128), addition is XOR, so summation order and parallel chunking can't matter, and multiplication distributes
  exactly.
- A duplicated column counts twice in both, an empty row contributes nothing to either, and skipping a zero eq entry changes
  nothing.

**Where they could differ, and why they don't.**
- **Slice length.** The CSC asserts `eq.len() == n_cols`, while the row fold, in a release build, ignores extra entries.
  `Composite::check` refuses a Net range whose `slot_log` isn't its net's `unit_log`, and a mask is built at `slot_log`. So
  every slice is exactly `n_cols` long.
- **Out-of-range columns.** A net column ≥ 2^unit_log panics in both versions. The CSC panics in `Stmt::new`; the row fold
  panicked at its first fold, which every verify runs over every type. `IrUnitNet::parse` doesn't bound columns, so a
  pinned circuit could carry such a column. In that case the session now ends before the proof instead of during it. The
  accept sets are the same.
- **Proofs.** Same comb, same transcript: the prover's proofs are unchanged byte for byte.

**Test.** I ran a fuzz on upstream flock-core b684b12, which carries no patches to these two types, in release mode with 4
rayon threads.
- It compares `CscCircuit` with `SparseMatrixCircuit` on `fold_alpha_batched` and `fold_split`, at α = 0, 1 and random.
- The matrices have empty rows, duplicate columns and zeros in eq.
- k runs over 2^7, 1000, 4095, 4096 (no nonzeros), 4096, 8192, 2^16, 2^20 and 2^21. That covers both kernels' scalar and
  parallel paths (the threshold is 2^12), up to the size of a GEMM unit's slot.
- The commit's own test checks the real slot types of one small composite. This adds adversarial matrices at every size.
- Result: 27 of 27 equal (`CSC_FUZZ_OK`).
- The script and log are in `art:2ade0a20ec62b23f68888916be53b5e6dbc85cffe409f0d7b28c693d5dba2744`.

**Not a condition.** The commit touches `backends/flock/`, so merging it into `main` needs `check`'s `lean-agreement`. That
doesn't bear on the flag.

**Labels:** `commit:d1775df80b70154f72029317f648e26b06b53321` and `commit:cde1c7ac17f5797561106dce5d41c103af6dd3b3`, each with
`grant statement-reviewer` and `grant red-team`, `--by red-team-proofs-554`, `--ref` this note.
