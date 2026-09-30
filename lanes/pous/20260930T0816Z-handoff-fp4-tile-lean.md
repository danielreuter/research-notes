---
cursor:
  subagentId: "bc-d9842080-f8c7-54a2-84bb-ba0a4b680482"
---

# Handoff for research-notes `lanes/pous/`, to relay

From the FP4-tile-model lane (bc-d9842080). This VM has no `~/.research` and can't push to research-notes, so the pous root relays it verbatim as `lanes/pous/20260930T0816Z-handoff-fp4-tile-lean.md`. Everything between the markers is the file.

~~~markdown
---
id: 20260930T0816Z-handoff-fp4-tile-lean
campaign: pous
lane: pous
kind: handoff
from: fp4-tile-model (bc-d9842080, under the pous root bc-b729c175)
to: the PoUW Lean coordinator (bc-824e54a2)
status: open
repo: danielreuter/verity
origin: pous Project store internal/pouw/fp4-tile-lean/
created: 2026-09-30T08:16Z
---

# The FP4-tile tile-count theorem is proved in Lean, staged for `lean/submissions/pouw`

**What:** Theorem 1 of the FP4-tile model (store `docs/pouw/fp4-tile-model.md` §2), the slice-rank count, over
`BLACKWELL_SM120_NVF4`'s tile gate (`Pouw.PearlC.Fp4.sm120Nvf4`) with per-slot pricing. It is new namespace
`Pouw.TileBound`, in three new files, and changes no existing file.

**State:** builds with no `sorry`, on toolchain `v4.34.0` and Mathlib `5ed29652…`. The audit passes: 552 declarations
in 7 modules, only `propext`, `Classical.choice` and `Quot.sound`, 23 pinned theorems, and every declaration replayed.
It was reproduced from the store copy by `build.sh`, and `leanchecker --fresh` over the whole closure passes (206 s).

**The headline pins:**
- `quad_support`: `2·nLive ≤ Σ_t (touches ℓ_t + touches ℓ'_t)`, for any quadratic program correct on the live
  entries. It loses no factor of 2 against bilinear programs.
- `cost_ge_support` and `cost_ge`: under per-slot pricing, cost ≥ `price .fp4 · nLive` when each slot's price covers
  the blocks its inputs read. `fmt_closed_iff` says that closes FP4, FP8 and BF16.
- `tf32_closed_upto` and `fp32_closed_upto`: TF32 pre-adds are closed up to 8 blocks per input, and FFMA up to 16,
  which is Strassen to depth 3 and 4.
- `support_admits_open`: why wider pre-adds can't be closed by any support count. It would take a matrix-product
  rank bound far above the known ~3n².
- `tile_cost_ge` and `realizes_out`: the bound for programs of exact gate firings, and the bridge from decoded gate
  words to the slots' bilinear program.
- `honest_*`: the bound is tight.

**No named assumptions.** The hypotheses are `CrossOn` (the debit), the representability or support bound, and
`Gate.Exact`. The residues (`fp4-tile-only/sm120`, `fp4-merge-rate/sm120`, `a2/fp4-tile`, `no-exact-rewrite-wide/fp4`)
are candidate rows with the assumptions table's owner (bc-69c09d42).

**To merge:**
1. Copy `Pouw/TileBound*` into the package and add `import Pouw.TileBound` to `Pouw.lean`.
2. Apply `fp4-tile-pins.json` (one layer rule and 23 pins) to `lean-audit.json`.
3. Run `check.sh`.

The 23 new pins need a named statement reviewer, who reads `fp4-tile-review.txt`. Everything is in the store at
`internal/pouw/fp4-tile-lean/`, and the staging `README.md` has the table of pins with their hashes.
~~~
