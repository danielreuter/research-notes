---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: audit-lean · kind: plan · created: 2026-09-28T03:40Z · repo: danielreuter/verity · about: #177's `parse_facts` over
#204's `table/v2` branch (`lanes/audit-lean/20260928T0325Z-handoff-from-flock-verifier-204-parse-gen.md`)

# Extending #177's `parse_facts` to #204's `table/v2` branch

**Status: planned, and half done on a WIP branch.** It lands after #204 as one small PR, stacked on #177. #177's merge
order doesn't change: #147, #156, #154, then #177.

## What #204 changes for #177

**One step of one proof.** In `HmRow.parse`'s lookups loop, the push of `Lookup.build`'s net becomes a bind over a
three-way match on META's `gen`:
- absent: `Lookup.build`;
- `"table/v2"`: `Lookup.buildV2 name pinned.sha512 words n lo 31`;
- anything else: refused.

I checked it on a trial merge of #204 `56511e4d` into #177 `81552896`, which merges cleanly:
- `parse_facts` (`ExecCircuit.lean`) fails at exactly that step;
- `ExecSetup.lean` fails in the two places that consume the nets' origin, `nets_ok` and `unit_parsed`.

Nothing else moves: `HmRow.check`, `setupH_spec`, the Δ proofs and `Layout.placement`. `Circuit.parse` also gains the
branch, but #177 never walks it.

## The extension

| Piece | Change | Lines |
|---|---|---|
| `ParseFacts.nets` | a third origin: `∃ nm sha tb n lo bits, Lookup.buildV2 nm sha tb n lo bits = .ok x.2` | 3 |
| `parse_facts` | the `gen` match's three branches meet at the push's join point (`lets`, then `split`) | ~15, **written and compiling** on `cursor/audit-parse-gen-f568` at `8686055e` |
| `netOK_lookupV2` | a `table/v2` slot is `NetOK`, has `7 ≤ unitLog`, and satisfies `ConstRow` when `unitLog ≤ 32`, from #202's `build_spec_v2` (below) | 60–90 |
| `nets_ok`, `unit_parsed` | the third case: `netOK_lookupV2`; and a v2 slot is not the unit, since `build_spec_v2` gives `lookup = some …` | ~6 |
| `Check.lean`, `README.md` §1.5 | the new lemma, and "text nets and lookup slots of either generator" | ~5 |

**`netOK_lookupV2`, from #202:**
- **The constant row.** `build_spec_v2` gives `net.a`/`net.b` as `Sparse.ofRows` of `fixKonst` of the output rows with
  `#[konst]` pushed. So row `konst` reads itself, by `sparseEntry_ofRows` and `ofRows_row`, as in #177's v1 case.
- **The lookup term is zero at the constant.** This is the same argument as v1, with the width `k` in place of `bits`:
  - `productRows_eq` and `outputRowsV2_eq` give `konst = prod0 + k · 2^(n−lo) + pad + 128`;
  - so `konst` is past every product row;
  - the lookup record's `bits` is `k`.
- **`konst < 2^unitLog`,** from `ofRows_spec`: every column is below the width, and the constant row reads `konst`. Since
  `konst ≥ 128`, this also gives `unitLog ≥ 8`.
- **`inGroups = #[⟨0, 1, #[n]⟩]` and `inWords = 1`** aren't in `build_spec_v2`'s statement. They're literal fields of the
  returned net, so a short walk of `buildV2` to its `return` gets them (about 25 lines, with #177's `lets`/`bindok`
  macros, and no loop invariants). The alternative is for flock-verifier to add the two conjuncts to `build_spec_v2`,
  which isn't pinned. I'll write the walk, so nothing waits on them.

**Total:** about 90–120 lines, CPU only.

## When, and on what

- **After #204** (and #202) settle. The PR is stacked on #177, with #204 merged in. Its base moves to `main` once #177
  lands.
- **If #204 reaches `main` before #177,** `main` plus #177 won't build until the extension is in. Then I fold the
  extension into #177 instead of a follow-up. Either order works; only the PR it lives in changes.
- **If #147 later adds its `Net.checkOrder` step to `buildV2` too,** as it did to `Lookup.build`, only the fields walk
  gains one step. `build_spec_v2`'s statement is flock-verifier's to keep.

## Update, 05:28Z

#177 is now `8e9b0176`: `ExecLookup` imports `FlockLevel3.LookupRows`, and its `build_spec` is `build_facts`. The fix is
for the audit's kernel replay, which refuses lemmas declared both in and outside the soundness set.
- **The WIP branch** (`8686055e`) merges that head before it continues.
- **`netOK_lookupV2`'s `buildV2` walk** goes in a module that imports `LookupRows`. Then the equation lemmas that
  `build_spec_v2` realizes are reused, not declared again.
