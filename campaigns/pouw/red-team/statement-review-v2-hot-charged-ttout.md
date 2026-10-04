---
cursor:
  subagentId: "bc-22298e90-fd61-5062-a836-0b7a423cab8a"
---

# Statement review: v2-hot's charged TT_OUT (`TTOutV2HotCharged`, `V2HotCharged`)

30 Sep 2026, 1:45 PM PDT. The statement reviewer (bc-22298e90), through the pous root, for bc-b58c6093 and
bc-824e54a2. It answers `internal/pouw/cheap-binding/ttout-lean-staging/v2-hot/review-request-2030.md` (1:30 PM PDT).
Δ's value is out of scope, as asked.

## Verdict

- **GO on the four forms and on their derivation from the reviewed TT_OUT.** Also GO on the four `…Atγ₀` compositions and
  the two monotonicity lemmas.
- **Held: the verdict on Δ's definition** (`deltaHotFirst`). The assessor found Δ must read the unit's width n as well
  as k, and bc-b58c6093 is revising it: a pinned table of Δ by width that never decreases in n, or Props restricted to
  n ≤ 8,192. I'll review that in the revised request, with the new hash pins for the Δ scripts and for the region
  lemma's statement.

## What I checked

- **The snapshot** (my copy of 1:36 PM PDT):
  - `TTOutV2HotCharged.lean` `d8607478…` and `V2HotCharged.lean` `4f15d461…`;
  - the eight GO'd files, byte-identical to the 10:30 AM PDT re-GO;
  - `DeviceV2Hot` `39a331fd…` and `NoAlignedExactRegionHot` `9ef3d835…`.
- **The build** was on my post-M1 tree, with the price twins and the rest of v2-hot. `Pouw.PearlC.V2HotCharged` built
  cleanly (2,088 jobs).
- **Axioms and sources:** `#print axioms` on all 11 theorems gives `propext`, `Classical.choice` and `Quot.sound` only.
  There is no `sorry`, `axiom`, `opaque`, `native_decide`, `#eval` or `set_option`.

## The four forms

- **The same games as before.** Each form is the GO'd form's game (`TTOut` or `TTOutTile`), at the same protocol and
  tiles (kernel term 0, which TT_OUT doesn't read). Only two things change:
  - the domain is the one-shape `pearlCDomainDevAt d.dev s`;
  - γ₀ is `1/400 + deltaHotFirst s`.
- **The chain-only forms** use the chain-only protocol and tiles, as the GO'd chain-only forms do.
- **Additive is the right composition.** TT_OUT at γ₀ says a program needs time T ≥ (1 − γ₀)·(credited work). The
  charge covers a rewrite window that starts at atoms 0–3, which saves at most Δ·(credit) per unit. So the reviewed
  bound (399/400) less the saving gives T ≥ (399/400 − Δ)·credit, which is γ₀ = 1/400 + Δ.
- **"At most one early window per word"** holds: a word's windows are disjoint and at least 4 atoms long, so two can't
  both start before atom 4.
- **Per shape.** Δ is a fixed amount of work per word, so it has to be stated on the one-shape domain. A workload that
  mixes shapes isn't covered by any single charged `Prop`. That's fine, since every γ theorem is per shape anyway.
- **"The credit is at least the chain."** Δ's normalization (work per word over k/32 atoms) is a share of the credit
  only if each form's least credit per word under the cap is at least one chain, k W1.
  - I checked all four forms at both prices and both headline shapes:

    | Shape | Forming-credited credit per word | Chain-only credit per word | Chain |
    |---|---|---|---|
    | 8,192³ | 8,391.6 | 8,351.6 | 8,192 |
    | 16,384³ | 16,575.4 | 16,535.4 | 16,384 |

  - It holds on the whole domain at ρ = 1/1,000: the non-chain terms give at least 2·bf16·r + add ≈ 136 W1 per word,
    against ρ·credit ≤ about 66 at k = 2¹⁶.
  - It would fail at a larger cap (about ρ ≥ 1/480 for chain-only at k = 2¹⁶). **Nit:** the docstring should state the
    condition, ρ ≤ 1/1,000 at sm_120's prices.

## The derivation from the reviewed TT_OUT

- **What the four `…Charged_of_ttOut` lemmas do:** they restrict the GO'd form's domain to the one shape
  (`ttOut_mono_domain` / `ttOutTile_mono_domain`), then raise γ₀ from 1/400 to 1/400 + Δ(s) (`ttOut_mono_gamma` /
  `ttOutTile_mono_gamma`).
- **The direction is right.** TT_OUT at γ₀ bounds Pr[T/(1 − γ₀) < credit], and T/(1 − γ₀) only grows with γ₀. So each
  charged form is weaker than the GO'd one, and whatever supports the GO'd TT_OUT also supports it.
- **What the proofs read of Δ:** only `0 ≤ Δ(s)` (`deltaHotFirst_nonneg`) and the hypothesis `1/400 + Δ(s) < 1`. So
  they survive any revised Δ that stays nonnegative. A width table needs its own nonnegativity lemma, and a restriction
  to n ≤ 8,192 would add one hypothesis.
- **Checked in scratch:** `ttOutTilePearlCDevHotCharged_of_ttOut` gives the charged form from the GO'd one at
  `devSm120v2hot Prices.sm120Loop`, 8,192³.

## γ at any γ₀

- **The formula:** `pearlCGammaHotAtγ₀` and its three siblings give γ = 1 − (1 − γ₀)·(1 − gammaHot)/(1 − 1/400). That is
  exactly 1 − (1 − γ₀)/ω, since 1 − gammaHot = (399/400)/ω.
- **They don't read Δ,** and the tile forms carry `γ₀ < 1`, as `gammaSampled` needs.
- **End to end in scratch** (standard axioms): the charged per-tile form at `devSm120v2hot Prices.sm120Loop`,
  `publicConst 64`, ρ = 1/1,000, 8,192³, cast 8, gives `GγSampled` at the numeral
  `4535326101659/672113840000000`, which is 0.67479%. It goes through `hotTileAccounting_sm120v2hot`, with `hw0` from
  `wrefDevHot_nonneg_devAt`, and `pearlCSampledHotAtγ₀`.
- **The values at the provisional Δ,** for reference (they move with Δ):

  | Figure | At FADD 8.376 | At FADD 8.00 |
  |---|---|---|
  | Forming credited, 8,192³ | 0.67479% | 0.67423% |
  | Chain-only, 8,192³ | 1.14821% | |
  | Chain-only, 16,384³ | 0.75244% | |
  | Forming credited, 16,384³ | 0.51236% | |

- **Recommended once Δ is final:** stage the numeral compositions for the charged headlines, as `V2HotHeadline` does
  for the uncharged ones.

## Inputs a grant will name, for the revised request

- **The block table.** `v2hot-blocks-corrected.json` (`76436412…`) is stale. The catalogue audit's 12:55 PM PDT entry
  in `ttout-restatements.md` §8 finds the published W*(L) too high from 6 atoms up, because Smirnov's ⟨3,3,6;40⟩ was
  missing. So the regenerated table's hash has to replace this one.
- **The region family's docstring.** `NoAlignedExactRegionHot.lean` (`9ef3d835…`) still names t₀ = 6 and the free
  family's minimal shapes widened. This route needs t₀ = 4 and the corrected F, as §8 says will follow GPU 3's rerun.
  - Neither docstring change moves a pin.
  - The planned hash pin on the region lemma's statement should be taken after both land.


## Δ's definition, 30 Sep 1:58 PM PDT: GO, with two conditions

This answers `review-request-2045.md` (1:45 PM PDT), with its addendum (1:52 PM PDT), and supersedes the hold above.

**GO on Δ's definition.** Three conditions are below: (1) is met, (2) and (3) are open.

### The snapshot

At 1:52 PM PDT:
- `TTOutV2HotCharged.lean` `e1d69cb6…` and `V2HotCharged.lean` `178d2200…`, the addendum's hashes;
- `NoAlignedExactRegionHot.lean` `24af905b…`;
- the other GO'd files, byte-identical.

**Checks:**
- **The build:** `Pouw.PearlC.V2HotCharged` built cleanly (2,088 jobs) on my post-M1 tree.
- **Axioms and sources:** `#print axioms` on all 15 theorems gives the three standard axioms only, and the files have no
  `sorry`, `axiom`, `opaque`, `native_decide`, `#eval` or `set_option`.
- **The four forms' definitions** are unchanged from 1:45 PM PDT, apart from their docstrings.

### What the definition says, and why it is right

- **The table, then the lookup.** `deltaHotAtoms n` is `some 0.8012` for n ≤ 8,192 and `none` above. `deltaHot s` maps
  it to a·32/k, and each form is `∀ δ, deltaHot s = some δ → TTOut … (1/400 + δ)`.
- **Why it reads n.** A wider unit spreads A′'s pre-adds over more columns, so a window's saving per word grows with the
  column cap.
  - The pinned result (`deltafast_p8.0_copy.json` `067fc7a9…`) was computed with the unit's width fixed at 8,192. A
    narrower unit only lowers the cap, so 0.8012 bounds every n ≤ 8,192.
  - `deltaHotAtoms_mono` pins that shape for the table's later rows. It is a fact about the table, and the computation
    is what makes the table true.
- **Rows don't need a column.** The 0.8012 comes from the whole-composition bound with fit ignored, and each row
  interval's bound depends on its column cap, not its row count. So a taller unit doesn't raise it.
- **The empty rows.** Above 8,192 columns the forms say nothing (`deltaHot_eq_none`). A grant of them there is empty,
  and no γ can be derived from them there.
- **Nonnegativity:** `deltaHot_nonneg` goes through `deltaHotAtoms_nonneg`. So the `_of_ttOut` lemmas survive any longer
  table that re-proves that one lemma.
- **Inputs:** the Δ scripts, the result file, the region file and the block table are pinned by full sha256 in the
  docstring.
- **Checked in scratch** (standard axioms):
  - through the lookup, the charged per-tile form at 8,192³, FADD 8.376 and cast 8 still gives `GγSampled` at 0.67479%;
  - at 16,384³ the forms are provably empty.

### The conditions

1. **The credit condition: met.** The docstring now states it. Δ is a share of the credit only while each form's credit
   per word after the cap is at least one chain.
   - The tightest case is chain-only at k = 2¹⁶ on wide units: 136 − ρ·(k + 136) W1 to spare, about 70 at ρ = 1/1,000.
   - It fails at ρ = 136/65,672 ≈ 1/483. That matches my check, with add taken at its smaller price, 8.
2. **The block table: open.** It is marked provisional in the docstring and will be rebuilt on the audited floors, with
   every contraction factor up to 2L. The grant has to name the rebuilt table's hash, and Δ has to be recomputed on it.
3. **Window lengths: open (new).**
   - **The gap.** The pinned result covers window lengths 4 to 256 atoms (`LMAX = 256`), that is, units with
     k ≤ 8,192. But `deltaHot` gives a value at any k once n ≤ 8,192. In scratch, `deltaHot ⟨8192, 8192, 16384⟩ =
     some (2003/1280000)`.
   - **Why it matters.** A unit that deep has windows up to k/32 atoms, 512 at k = 16,384 and 2,048 at k = 2¹⁶, and none
     longer than 256 was computed. The maximum is flat at 0.80115 from L = 8 to L = 201, which suggests longer windows
     don't save more. But that is neither computed nor argued.
   - **The fix:** either restrict the table to k ≤ 8,192 as well (`if n ≤ 8192 ∧ k ≤ 8192`, reading (k, n) in the
     table), or pin a result or stated argument covering every L up to k/32.
   - **What it touches:** not the headline, which is at k = 8,192. It changes only the four forms' records.

### Consequence for the published figures

- **16,384³ has no charged form until the width table extends past 8,192 columns.** So the charged figures at 16,384³
  (0.75244% chain-only and 0.51236% forming credited, at the provisional Δ) can't be cited yet.
- **Only 8,192³ can be cited:** 0.67479% forming credited, 1.14821% chain-only, at FADD 8.376.

**No label** was requested.

**Condition 3: met (1:57 PM PDT addendum, checked 1:58 PM PDT).** At `TTOutV2HotCharged.lean` `06d07896…` and `V2HotCharged.lean` `b7fbb88f…`, the table is one cell, `deltaHotAtoms k n = some 0.8012` for k ≤ 8,192 and n ≤ 8,192, and `none` beyond. `deltaHot_eq_none` covers an excess in either dimension. The build is clean, and all 15 theorems use only the standard axioms. In scratch, 8,192³ gets 2003/640000 and the charged headline still composes. 8,192 × 16,384 deep, 8,192 × 2^16 deep, 16,384³, and any shape one past the cell in k or n get `none`. Condition 2, the block table, stays open.

**The extension beyond 8,192 (2:36 PM PDT):** reviewed in `statement-review-v2-hot-charged-ttout-extended.md` beside this file. It is GO on the table to 65,536, with a new width caveat condition, and this file's 8,192³ GO stands.
