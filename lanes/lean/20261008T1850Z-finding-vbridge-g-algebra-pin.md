---
id: lean/20261008T1850Z-finding-vbridge-g-algebra-pin
campaign: lean
lane: lean
kind: finding
status: active
repo: danielreuter/verity
origin: bc-19c498a8 (lean), outcome (a) part 2; item 1 of note:lean/20261008T1756Z-finding-vbridge-g-inner
---

# VBridge G: pin V*'s algebra units against the verifier's own S, and check parts by renumbering

## Landed on `cursor/vbridge-g-compose-741b`

Every theorem below uses only `propext`, `Classical.choice` and `Quot.sound`.

- `e7bb28184`: `unit_innerUnit`. A copy of `VStar.innerUnit S name` computes `resVal (gfS S.gf)` at its input columns.
- `84ab6c537`: `params_of_check` and `unit_check_pinned`. These give the pinned `(L, H)`. They need no `String.splitOn`
  lemma, only `unitName`'s injectivity and its `rec-open/` prefix.
- `11dcce84e`: `Algebra.residuals_toV`. E's `Algebra.residuals S w v` is V*'s `resVal (gfS S.toV)` at `w.getD · 0`,
  provided every `wt` bit is below 128, which `VStar.checkS` checks.

## What item 1 would cost as planned

The plan pinned each algebra unit by equating V*'s generator with E's definitions. That takes two lemmas:

1. **`VStar.Algebra.structure_ sh` = E's `structureOf sh`.** These are two unrelated algorithms. V*'s tracks supports
   (`supports`, `buildRes`). E's builds linear forms (`build`, `buildAll`). A general proof would run to thousands of
   lines. Checking each shape in the kernel is out: the computation uses `qsort`, HashMaps and well-founded recursion.
2. **`VStar.parts` renumbers correctly.** `wmap` and `vmap` hand out positions as `map.size`, so `V` having no repeats
   matters, and that rests on `sortDedup`'s `qsort` being a sorted permutation. Neither core, Batteries nor Mathlib
   proves anything about `Array.qsort`. `union` does keep every element of both inputs even when they are unsorted.

## A route that needs neither

Soundness only reads what the verifier checks. So item 1's verifier check (the analogue of #1391) can work as follows:

- The verifier computes S itself, with E's `structureOf` moved from `Security/Proofs` into the verifier's library. Then
  `structure_ = structureOf` is never needed. If V*'s generator disagreed, that would cost completeness, not soundness.
- For each algebra circuit, the verifier reads the part's `res`, `P` and `v` and computes the part's S with a plain
  renumbering. It does not rerun `parts`. A part's `w` is ports `P` laid end to end, its `v` is `v[V[j]]`, its residual
  `k` is S's residual `res[k]`, and an operand is renumbered by its position among those the part uses, read by index.
  The verifier compares the circuit's unit with `innerUnit` of that S, as `RecOpen.check` does.
- A coverage check confirms that every residual of S lies in some part.

The lemma G then needs is small: a part's residuals are S's residuals at `res[k]`, whenever the part's ports carry ports
`P` and its `v` carries `v[V[j]]`. It chains with `residuals_toV` and `unit_innerUnit`, and no `qsort` or HashMap
appears. This is a change to the verifier of record, so the owners decide. Note that `lean-agreement` compares against
upstream's Rust verifier, as it did for the `rec-open` check.

## What doesn't change

Items 3 to 6 of note:lean/20261008T1756Z-finding-vbridge-g-inner are the same under either route.
