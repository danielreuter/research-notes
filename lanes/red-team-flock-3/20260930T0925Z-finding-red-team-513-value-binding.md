---
id: 20260930T0925Z-finding-red-team-513-value-binding
campaign: verity
lane: red-team-flock-3
kind: finding
status: final
repo: danielreuter/verity
origin: red-team-flock-3
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75), as statement reviewer and red team · to:
lean-value-binding (bc-a84aadb3); cc verity-root and the research coordinator (bc-8ece7cde) · created: 2026-09-30T09:25Z

# #513 at `655d509d`: GRANTED, as statement reviewer and as red team, with three conditions

`HmRowComputes` and `decode_row` are not cryptographic, and not vacuous. `bc_registered` and `other_registered` hide
nothing inside the model, but that is because the model registers leaves, not roots. Discharging them means paying for
the roots' Merkle binding. That binding is cryptographic, and the `_hm96` bound leaves it out. `collide` is explicit,
and `registered_weights` has the right shape.

Re: `internal/lanes/red-team-flock-3/20260930T0829Z-handoff-from-lean-value-binding-513-binding-grant.md`. Evidence is in
the store's `private/red-team-reviews/pr513-evidence.log`. CPU only, $0.

## Checks

- **The record.** Against #511's there are 11 new pins, none changed or removed. 50 definitions enter `reads`, in three
  new modules, and no existing hash changes. The only other change is the upstream watch `hm-row-computes`.
- **The audit** at `655d509d`, compare mode with kernel replay: PASS, with 11,636 declarations in 168 modules, standard
  axioms and 159 pins.
- **Readers.** `HmRowComputes` is read by exactly the six pins that take `hHm`: `registered`, `registered_weights_hm96`
  and the four `_hm96` end-to-end theorems.

## The new assumption and the three layout facts

- **`HmRowComputes` is not cryptographic.**
  - It says that for every witness the constraints accept, the witness's own `b ‖ c` bytes (`bytesAt` at `bcAt`) equal
    `(SHA-512(enc row) ⊕ M·y) ‖ SHA-512(salt_prefix ‖ y)` for the layout's row and salt. That is the circuit's
    functional correctness, with no probability or hardness in it.
  - `HmRows.Computes` fixes SHA-512 and the executable's key. `K512.mask_len` proves the mask is 64 bytes, so the XOR
    can't truncate.
  - It is satisfiable, and it is what phase 2i has to prove.
- **`decode_row` is not cryptographic either.** It says the decoder's bit on each of the unit's wires is the bit of the
  row the layout reads there.
- **`bc_registered` and `other_registered` hide nothing in the model, because the model registers leaves.**
  - They say that in a satisfying witness, the leaf of what the witness holds at a commit string is `regLeaf R p`, "the
    leaf digest the registration commits to at p". The model's statements (`plan S R`) and `regLeaf` are both
    functions of `R`, so in the model this is wiring.
  - The planned discharge is "the refinement of `HmRow.regions` and `checkPublic`" (`e2e-checklist.md`). That shows only
    that the public `b ‖ c` hashes into the registered frame-v3-sha512 root.
  - That this leaf is `regLeaf R p` is the root's Merkle binding. `Merkle.opening_binding` gives only "equal, or an
    explicit SHA-512 collision". `DESIGN.md` §1 charges it: `δ_tree`, by rewinding under plain SHA-512 collision
    resistance, for the serving roots, and a straight-line reduction for the registrant's.
  - So "A2 stays the only cryptographic assumption" holds for the theorems. It does not hold for an audit bound read
    from registered roots: that bound adds `δ_tree` and `cr/sha-512`, which the `_hm96` bound leaves out.
- **`row` and `salt` should be concrete: yes, as you asked.**
  - The link finder evaluates them (`vb.opening` is `lay.openingAt`), and A2 is plausible only for explicit finders.
    That is the same reason `collide` must be explicit.
  - With abstract readers, nothing stops a layout from meeting `decode_row` and `HmRowComputes` non-constructively, for
    a circuit that doesn't hash the row. For each witness it would choose a salt and a row that explain the pinned
    `b ‖ c` and match the decoded bits.
  - A2 would then fail for a cheating prover's finder, instead of the rows being bound.

## The rest of your list

- **`collide` is explicit.** `hm96Pair` branches on list equality and evaluates SHA-512 at most four times; there is no
  choice. `hm96Pair_spec` is proved. `hm96_treeLeaf` shows the model's leaf is the executable's
  `Hm96.Default512.treeLeaf`, the one `checkPublic` computes.
- **`Com := Pos × Dig`, with `(p, regLeaf R p)` registered at `p`,** as described.
- **`registered_weights`** takes one opening of the registered leaf at the wire's commit string, which is the weakest
  hypothesis. Its conclusion is "the witness's row is `wv`, or `collide` is an explicit SHA-512 collision". The
  quantifiers are right.
- **The `_hm96` theorems** are `flock_e2e_*` at `vb := HmRows.binding rs hHm`, with `hExec`, `dp`, `hL1` and `hOne`
  unchanged. Their `hCR` is #511's every-prover form, now at `H512`.

## The conditions

- **C1, as for #511.** Don't cite `flock_e2e_*_hm96` as a bound for a given prover under A2 until `hCR` is restated per
  prover. For `H512`, the every-prover premise can't hold
  (`note:red-team-flock-3/20260930T0925Z-finding-red-team-511-knowledge-pins`).
- **C2.** Cite the `_hm96` bounds as bounds at the registered leaves. Read from registered roots, an audit bound adds the
  roots' binding: `δ_tree` (`DESIGN.md` §1, under `cr/sha-512`). Say so in one sentence in `ASSUMPTIONS.md`, and in the
  discharge column of `e2e-checklist.md` for `bc_registered` and `other_registered`.
- **C3.** `HmRowComputes` and `decode_row` count as discharged only for readers that read the witness at fixed
  addresses, as `bcAt` does; a choice-based reader discharges nothing. Better, make `row` and `salt` concrete before
  phase 2i.

## Merging, and the grants

- **Merging.** The head merges into `main` `cc0f4688`, and with #452, without textual conflicts. But the two
  `_exec_hm96` pins use the executable's draw law, as `flock_e2e_count_exec` does, and #452's record lists that as a
  `Flock.Draw` reader. So whichever of #452 and #513 lands second needs a re-record, and new grants on that head.
- **The grants.** The labels `grant = statement-reviewer` and `grant = red-team` are on
  `pr:513@655d509d8a1afc338034ca150449eb0357fad4a1`, by `red-team-flock-3`, with ref
  `note:red-team-flock-3/20260930T0925Z-finding-red-team-513-value-binding`, pushed to the remote. `queue.toml` requires
  both. A new push needs new grants.
