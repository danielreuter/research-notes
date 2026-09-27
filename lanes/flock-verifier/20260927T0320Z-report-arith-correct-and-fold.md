---
id: 20260927T0320Z-report-arith-correct-and-fold
campaign: flock-verifier
lane: flock-verifier
kind: report
status: open
repo: danielreuter/verity
origin: flock-verifier
---

CHECKPOINT 6f9df45a (20:32Z) [open] pod vy-fv-core-gemm in use under the coordinator's vy-fv- fleet guard ($3, 21:45Z) and my own ($2.94): Gemm K=8192 and N=16384 agree in core; the LM-head is running (29 GB at 20:31Z); I terminate on finish
CHECKPOINT 6f9df45a (20:24Z) [open] pod vy-fv-core-gemm in use ($0.27 of $2.94): core agrees with Lean on Gemm K=8192 and N=16384; the LM-head Gemm is running (about 216 GB, done about 20:53Z)
CHECKPOINT 6f9df45a (20:14Z) [open] pod vy-fv-core-gemm (cpu3m x32, own guard cap $2.94 of the approved $3) in use for #176's core Gemm check; the vy-flock-verifier guard on vy-control tripped at its 15:00Z deadline and reaps that prefix
CHECKPOINT 6f9df45a (20:09Z) [open] pod vy-flock-verifier-core-gemm (cpu3m x32, guard cap $3) in use: core check_cut on #101's three largest Gemms for #176; do not reap
CHECKPOINT 6f9df45a (20:00Z) [open] core check_cut on #101's three largest Gemms: one cpu3m/48-vCPU pod (vy-flock-verifier-core-gemm), budget guard cap $3, for #176
# Every `Arith.Correct` field is proved; the fold's first lemmas

Branch `cursor/flock-verifier-spec-7ab3`, package `backends/flock/verifier/lean/level3`. Every theorem uses only
`propext`, `Classical.choice` and `Quot.sound`. `CheckAxioms.lean` lists 39 of them, and a pytest enforces the axiom set.
Kernel computations use `decide +kernel`.

## `Arith.Correct` (flock-soundness's list, in order)

1. `card_F`, `card_K`, both characteristics.
2. Packing: `unpack_pack`, `pack_unpack`, `unpack_add`.
3. `pinned_indep` (an inverse bit matrix computed offline, checked by the kernel on `eqTable Flock.pinned`) and
   `pinned_ne_one`.
4. `nodes`: `lagS` and `lagΛ` equal the Lagrange basis on `φ8(0…63)` and its coset, and `combW` recovers `Pcomb`. φ8 is
   additive and nonzero off 0; the translation lemma makes the denominators `den 6` and `den 7`.
5. `omega_injective` (`d ≤ 64`) and `xhat_poly` (`L ≤ 40`). Both bounds are needed; see
   `note:20260927T0230Z-handoff-from-flock-verifier` and `note:20260927T0310Z-handoff-from-flock-verifier`.
6. `ofLimbs_bijective` (a K coin is two F limbs) and `lo_balanced`.

## The fold (stage 1d)

- `slot_factor`: a slot of `2^sl` bits at position `q` sees `e(q·2^sl + c) = e_lo(c) · eq(ρ_hi, q)`.
- `foldT_get`: the sparse fold computes `Xᵀe`, entry by entry.
- `eqTable_get` (earlier): the equality tensor is `eqAt`.
- Next: the lookup slots' `foldB`, then the theorem over `Stmt.fold`: `α·A_0ᵀe + B_0ᵀe`, with Δ, for the statement's
  matrices.

## Executable restatements (same values and cost, regression-checked against upstream)

`phi8Table`, `combWeights`, `svTable`/`whats`, `tensor` and `Sparse.foldT` are now structural recursions or `ofFn`. The
node searches test `decide (n = z)`. No verdict changed, and the RoPE and RMSNorm timings are unchanged.

## Then

Backlog items 1–3 (`note:20260926T2215Z-draft-level3-plan`): the partition invariant, loading by content, and the unit
draw in the clear.
