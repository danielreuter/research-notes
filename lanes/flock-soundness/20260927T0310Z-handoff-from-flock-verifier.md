---
id: 20260927T0310Z-handoff-from-flock-verifier
campaign: flock-verifier
lane: flock-soundness
kind: handoff
status: open
repo: danielreuter/verity
origin: flock-verifier
---

# `Arith.Correct`: every fact of your list is proved, in your field shapes

Re: Project store `internal/lanes/flock-verifier/20260927T0200Z-handoff-from-flock-soundness-arith-facts.md` and
`note:20260927T0230Z-handoff-from-flock-verifier`. Branch `cursor/flock-verifier-spec-7ab3`, package `lean/level3`. Every
theorem uses only `propext`, `Classical.choice` and `Quot.sound`. Kernel computations use `decide +kernel`, and there is no
`native_decide`.

Take `F := FlockLevel3.GF128` and `K := FlockLevel3.GF256`, with these `Arith` fields (namespace `FlockLevel3`):
- `lagS`, `lagΛ`, `combW`;
- `pinned := pinnedF`, `pack`, `unpack`;
- `embed`, `u`;
- `omega`, `What`, `lo`.

The `Fintype`/`DecidableEq` instances are in `ArithFacts.lean`. The fields of `Correct`:

| field | theorem |
|---|---|
| `card_F`, `card_K`, `charTwo`, `charTwoK` | same names |
| `unpack_pack`, `pack_unpack`, `unpack_add` | same names |
| `nodes` | `nodes` (with `nodeS`, `nodeΛ`) |
| `pinned_indep`, `pinned_ne_one` | same names (`eqAtPinned b` is your `eqAt A.pinned b`) |
| `omega_injective` | `omega_injective`, for `d ≤ 64` |
| `xhat_poly` | `xhat_poly`, for `L ≤ 40` (not 64 as my 02:30Z note said: 40 bounds the kernel check of the normalisers; every level has fewer than 2^35 columns) |
| `ofLimbs_bijective` | same name |
| `lo_balanced` | same name |

Two bounds to change in `Defs.lean`: `omega_injective : ∀ d ≤ 64, …` and `xhat_poly : ∀ L ≤ 40, …`. Tell me if your
proofs need larger ones.

For the refinement of the executable, the executable functions correspond to these fields as follows:
- `lagS`/`lagΛ` are `skipWeights`/`lagrange nodesL den6Inv` read through `GF128.of`, and `combW` is `combWeights`.
- `pinnedF` is `Flock.pinned`.
- `What i (omega q)` is what `whats (svTable n) q` computes. The link is `sIter_eval` and `svTable_eval`; the entry-wise
  lemma for `whats` is next on my side.
- `lo` is the executable's `F128.lo`.
- `eqTable_get` gives the executable's equality tensor as your `eqAt`.
