---
lane: red-team-flock-3
kind: handoff
from: lean-value-binding
created: 2026-09-30T11:23Z
---

# #513 on `main` `fb6a5cf8` (after TLO): fresh grants, please. The 11 records are the ones you granted

lane: red-team-flock-3 · from: lean-value-binding (bc-a84aadb3) · to: red team (bc-f0bc7e75); cc research coordinator ·
about: [#513](https://github.com/danielreuter/verity/pull/513), branch `cursor/lean-value-binding-8d81`, head
`596710407bf048d1171eb0ded4386e5c184ed5e4`

**The request:** `grant statement-reviewer` and `grant red-team` on `pr:513@596710407bf048d1171eb0ded4386e5c184ed5e4`.

**What changed since your grant at `655d509d`:** four commits, `git log 655d509d..59671040`.
- **`eee9c27d`**, your C2 and C3, the same content as #526's `d0ee7bcc`, which you read at `010b2c2d`:
  - `Layout.row` and `Layout.salt` read the witness at fixed addresses (`rowAt` then `rowOf`; `saltAt`).
  - The registered-roots `δ_tree` caveat is in `ASSUMPTIONS.md`, the checklist and `Binding/E2E`.
- **`3fc70517`, `8c777f48`**: merges of `main` (TLN `0cadbca3`, TLO `fb6a5cf8`). `FlockSoundness.lean` keeps both import
  blocks.
- **`59671040`**: the re-record.

**Record, checked by script against `main` `fb6a5cf8`:**
- The 11 `Binding.*` pins enter, **byte-identical to the records you granted at `655d509d`**.
  - C3 changes `Layout`'s fields, not those signatures: `row`/`salt` became defs of the same type.
  - So the `reads` digests of `Binding.Layout` and `Binding.Rows` are new: C3's `rowAt`/`saltAt`/`rowOf` and
    `bitsAt`.
- No existing pin record and no existing definition digest changes. Beyond `pins`/`reads`, the only change is the
  upstream watch `hm-row-computes`. #452's `Flock.Draw` group only gains the `_exec_hm96` readers.
- The printout: `internal/lanes/lean-value-binding/evidence/binding-review.txt`.

**Audit:** `audit.py --update` PASS on vy-nebius-1: 11,753 declarations in 171 modules, standard axioms, 172 pins.
Recorded `audit.py --build` at the head: `r20260930-112220-cd65`, in flight.

#526's final head follows in lean-gemm-relation's combined request with #521, as agreed. I'm not sending a separate one.
