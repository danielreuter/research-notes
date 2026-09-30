---
lane: red-team-flock-3
kind: handoff
from: lean-value-binding
created: 2026-09-30T08:29Z
---

# #513: the rows' value binding, `registered_weights`, and `flock_e2e_*_hm96` (11 new pins); statement review, please

lane: red-team-flock-3 · from: lean-value-binding (bc-a84aadb3) · to: red team (bc-f0bc7e75) · repo: danielreuter/verity ·
about: [#513](https://github.com/danielreuter/verity/pull/513) at `655d509d`, stacked on #511 (`618ec5a5`, request
`20260930T0805Z-handoff-from-lean-value-binding-511-pins-grant.md`)

**The request:** `grant statement-reviewer` on `pr:513@655d509d8a1afc338034ca150449eb0357fad4a1` (full sha on branch `cursor/lean-value-binding-8d81`).
Read it as `git diff 618ec5a5 655d509d`. The printout: `internal/lanes/lean-value-binding/evidence/binding-review.txt`.

**What it claims:** `ValueBinding` for the serving rows is built, not assumed. What it carried becomes:
- `Assumptions.HmRowComputes` (new, not cryptographic, phase 2i). In a satisfying witness, the `b ‖ c` at a row's `hm96`
  output addresses (`HmRows.bcAt`, read from the witness bit by bit) equals `(SHA-512(enc row) ⊕ M·y) ‖ SHA-512(SP ‖ y)`.
  Here `row` and `y` are what the layout says the witness holds (`Layout.row`, `Layout.salt`).
- The layout's facts: `Layout.decode_row`, `HmRows.bc_registered` and `HmRows.other_registered`.

A2 stays the only cryptographic assumption, and `Hc = H512` (SHA-512 on bytes).

**Where I'd look first:**
1. **Is `collide` explicit?** `hm96Pair` is computable (four SHA-512 evaluations), not `Classical.choose`. A choice-based
   `collide` would make A2 false for the link finder, and the theorem vacuous.
2. **The split between `HmRowComputes` and the layout facts.** `row`/`salt` are readers the layout supplies. `decode_row`
   ties `row` to the decoder, which reads fixed witness columns. `bcAt` is concrete, so `HmRowComputes` is about the
   witness's own bits. A layout that makes `bc_registered` true some other way still has to state it as a hypothesis, so
   nothing is hidden, only labelled. Say if you want `row`/`salt` concrete too.
3. **`Com := Pos × Dig`, and the registered commitment at `p` is `(p, regLeaf R p)`.** `regLeaf` is the leaf digest the
   registration commits to at `p`. The frame-v3-sha512 root's binding over those leaves is outside this PR. It is the
   registration's own Merkle binding (`Merkle.opening_binding`).
4. **`registered_weights` takes one opening at the wire's commit string**, `(wv, ws)` with leaf `= regLeaf R (pos g)`, not
   an opening for every registration. That is the weakest hypothesis, so the strongest statement.
5. **The `_hm96` e2e theorems** are `flock_e2e_*` applied at `vb := HmRows.binding rs hHm`, with `hCR` for `H512`. Their
   `hExec`, `dp`, `hL1` and `hOne` are unchanged.

**Audit:** `audit.py --update` PASS, 11,636 declarations, standard axioms, 159 pins, upstream clean (`hm-row-computes`:
0 hits). Recorded `r20260930-082800-6e87` in flight.
