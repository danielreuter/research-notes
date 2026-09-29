---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: handoff
from: constant-API rollout (bc-613ddf45)
to: flock-verifier (bc-8e519ca0), for item 1e; cc flock-soundness (bc-9e538dc5), coordinator
created: 2026-09-28T10:20Z
---

# The Rust block of a typed template statement, for the Lean verifier's reading (1e)

[#273](https://github.com/danielreuter/verity/pull/273) makes `flock-circuit` prove GEMM's typed statement (`verity/flock-circuit/types`). The session's statement digest (`Stmt::digest`) hashes Δ entry by entry. So a Lean verifier reading typed statements must split the block into the same slot types and Δ, in the same order, or the digests differ. Here is the split, so 1e can match it or ask to change it before any typed cell is recorded.

- **Slot types.**
  - The root is the unit's own region, `[0, own)` in unit coordinates, with entries at `>= own` left out. It's one slot per VU, in META's `root` range.
  - Each placed layout's rows are one slot per part, in the range named by its layout digest.
- **Unit coordinates to block columns.**
  - `[0, own)` maps into VU g's root slot.
  - Part p, with base `b_p` and its layout's q-th slot in the VU, maps `[b_p, b_p + 2^range_log)` into `slot_col(net_p, g, q)`.
  - Bases are aligned after `own` in item order, as `verity_flock.derive` places them.
- **Δ order.** First the flat statement's entries, unchanged: every slot's constant to the pin, the rows' midstate and padding constants, then the row wires. Then, for each VU g in order:
  1. **Inputs.** Each input bit w of the instance type, as a copy (`(i,i)`, `(i,src)` in A and in B) of its message bit. Input w is bit `w % 16` of row word `w / 16`, words in port order. Its column is the root's own input row, or, when exported, the part's input row.
  2. **Bindings.** Each part's non-exported input rows, in item order and bits ascending. Each is `(i,i)` plus `(i, s)` for every source column s of its form, in A and in B. A form's constant is the root's constant column.
  3. **Cross entries.** The root rows' entries at part columns: A's and B's separately, each `(row, col)` once.

`flock-circuit rows --circuit C --out D` writes the Rust derivation as staging's `rows/` (`root.txt` in unit coordinates, `<layout>.txt`, `delta.txt`), so the Rust, Python and Lean mirrors can be diffed file for file.
