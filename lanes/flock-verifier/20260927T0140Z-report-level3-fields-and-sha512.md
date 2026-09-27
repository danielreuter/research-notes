---
id: 20260927T0140Z-report-level3-fields-and-sha512
campaign: flock-verifier
lane: flock-verifier
kind: report
status: final
repo: danielreuter/verity
origin: flock-verifier
---

# Milestone: the fields proved, the SHA-512 statement verified, two recorded agreement runs

Branch `cursor/flock-verifier-spec-7ab3`. Level-3 proofs in `backends/flock/verifier/lean/level3` (Mathlib at the
soundness package's pin; every theorem on `propext`, `Classical.choice`, `Quot.sound`, pytest-enforced; no
`native_decide`: kernel computations are `decide +kernel`).

## Level 3

- **GF(2^128).** `F128.poly_mul`: the executable's product (carry-less multiply, Karatsuba, the GHASH reduction) is
  polynomial multiplication modulo `G`. `F128 ≅ GF(2)[X]/(G)`, bijectively. `G_irreducible` is Rabin's test, with the
  kernel checking `x^(2^128) = x` and a Bézout witness on the executable's own multiply. So `GF128` is a `Field` whose
  `+`, `*` and `inv` are the executable's, `inv 0 = 0` included.
- **GF(2^256) ladder.** `Q_irreducible` (the trace of `x⁻¹` is 1): `GF256` is a `Field` whose `+` and `*` are the
  executable's three-product ladder.
- **Seam** (`note:20260927T0025Z-handoff-from-flock-verifier` to flock-soundness): `embed`, `u`, `ofLimbs`, `u_root`.
- **Assembly, first lemma:** `eqTable_get` (the executable's equality tensor is `eqAt`).
- Next: packing and `lo` for the seam, once the soundness lane names the `Arith.Correct` facts it needs; then the fold
  theorem.

## SHA-512 statement (PR #83 at 631567f7, `note:20260927T0033Z-handoff-from-flock-netlist`)

Lean vs upstream `from_record` + `finish`:
- RoPE: 2/2 (`art:82c73709`) and 14 forgeries (`art:2fb50856`);
- RMSNorm Triton: 2/2 (`art:24aba3a2`) and 15 forgeries (`art:d13d622c`);
- M0's selftest records `art:1100e385`: 70/70.

D3 and D4 are closed upstream. The RMSNorm "abort" was the OOM killer
(`note:20260927T0127Z-handoff-from-flock-verifier`).

## Recorded agreement runs (`research run --tool flock_agreement`, CPU pods)

- `r20260926-232948-22a9`: 4 sets (9294e161, 19c7269a, fd02e847 RoPE and RMSNorm), 217/217, preserved (result
  `art:ab9fa582`, run record `art:b8a09731`).
- `r20260927-012244-342d`: 8 sets, the SHA-512 ones included, 412/412, preserved (result `art:a59f3cb2`, run record
  `art:d5ca1e5c`).

Pod spend for both runs: under $1 (16 vCPU at $0.64/h for 20 min, then 8 vCPU at $0.44/h for about 55 min).

## Backlog

In the plan note (`note:20260926T2215Z-draft-level3-plan`): the partition invariant, loading by content, and the unit draw
in the clear. Multi-table statements wait for M0.
