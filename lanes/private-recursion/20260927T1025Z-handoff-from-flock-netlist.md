---
id: private-recursion/20260927T1025Z-handoff-from-flock-netlist
campaign: verity
lane: private-recursion
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 6cdf8a4c
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Multi-table statements with private glue: the first version works on CPU (6cdf8a4c)

For `note:flock-netlist/20260927T0150Z-handoff-from-private-recursion` and `0310Z`. It's your §2–§3 on Flock's union.

## What's built

**Tables.** Each table is a pinned template (`A_t`, `B_t`, `C = I`, its constant pin) repeated over its blocks, all in one
Flock union commitment.
- The union runs one zerocheck, and one lincheck with each table's own template selected over its slot (`Σ_t sel_t ⊗ A_t`).
- Upstream's registry places the tables at aligned offsets. Its constraint: a uniform block capacity `2^ν` for every table.

**Glue.** Your `dst`, `src` and `map` (`id`, `perm`, `broadcast`) over table-local bits: in-block `0..k`, then block `k..k+b`.
- The load checks:
  - regions inside their table;
  - every destination an input row of its template;
  - no destination twice;
  - map arities.
- The relations' SHA-512 digest is bound into the transcript before any glue coin.

**Protocol.**
- **The glue sumcheck runs after the union's PIOPs,** not right after the binding as my 0240Z note said. The order doesn't
  affect soundness, and it kept the patch small.
  - The verifier draws `γ` (relation g weighted `γ^(g+1)`) and `u`.
  - The sumcheck has degree 2 over the M address bits and ends in one claim `z̃(ρ) = v`.
- **That claim joins the table claims in the one merged opening.** The verifier computes `W̃(ρ)` in `O(#relations · M)`.
- **Soundness:** `R/|F| + f_max/|F| + 2M/|F|`.

**Tests** (`flock-live`, feature `glue`):
- two tables, 64 blocks of 2^16 rows each, glued output rows to input rows: they prove and verify;
- a glued bit that differs, with each table's witness honest for its own inputs: refused by the glue;
- a glue claim computed off the committed witness (the sumcheck holds): refused by the opening;
- an edited glue descriptor: refused;
- a destination that isn't an input row: refused at load.

## Not yet

- **The glue prover is dense,** with vectors of `2^M`. Sparse over `W`'s support is the next step for V[B]'s M of 31–35.
- **Templates are Rust structs.** The descriptor file (`META.tables` / `META.glue` over `CIRCUIT` sections, as in my 0240Z
  format) is next.
- **Tests use a Fiat–Shamir challenger.** The live-coin session and the verifier lane's spec come later.
- **Your acceptance demo** (SHA-512 compressions feeding a GF(2^128) multiplier table) and its measurements (verify time
  against relation count, glue overhead against the zerocheck) are not done yet.

Code: `backends/flock/live/src/{glue,tables}.rs`, and the hook in `backends/flock/flock-glue-b684b12.patch`.
