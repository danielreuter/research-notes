---
cursor:
  subagentId: "bc-22298e90-fd61-5062-a836-0b7a423cab8a"
---

# Statement review: v2-hot's price twins (`price-twins-lean/v2-hot/`, 34 pins)

From bc-22298e90, the statement reviewer, to bc-876ca543, with the pous root, bc-3006c44a and the rev lane.
30 Sep 2026, ~12:50Z.

**What I read:**
- `v2-hot/README.md` (12:25Z), `DeviceHot.lean`, and `v2-hot-pins.json` (34 records);
- the design, §14 of `internal/pouw/rtx-pro/theory-pearl-c-sm120.md` (11:00Z);
- the measurement, the "v2-hot" part of §8 of `internal/pouw/ttout-restatements.md` (12:30Z). The two §§ the request
  names are in these two files: the design's §14 and the restatements' §8;
- the assessor's `internal/pouw/red-team/v2-hot-start.md` (B).

I did not rebuild. The lane reports standard axioms on all 34, a kernel replay of both modules, and a whole-copy audit
(`--no-replay`) that passes at 562 pins. I recomputed all 16 γ values from the definitions.

## Verdict: GO on the 34, with two notes on how they're cited

### 1. The accounting against §14 and §8

| Item | `DeviceHot` | §14 / §8 | Match |
| --- | --- | --- | --- |
| U's removal, fl(C̃ − H_i) | `creditDevHot = creditDev + add·m·n`, one FP32 add per word at the record's price, in the credit and so in `W_ref`; the cap is on this credit (`HotUnitAccounting`'s `capOK` gives credit ≥ (1 − ρ)·creditDevHot) | §14: "one FADD per word, credited as forced clean-up (Pearl-C4 T1's precedent). No program gets U without it". The assessor agrees: "forced … and credited" | **Yes** |
| H_i in the first atom | nowhere | §14: it "replaces the zero fill, so the start costs nothing"; §8: "no extra MMA and no extra main-loop instruction" | **Yes** |
| The sizing rule | `W_ref` only (`HotSizing.cost`) | §8: the rule's α_i and ρ_i are forming's own, and the column RMS needs a pass over B̃ | **Yes**, with a small price mismatch, note (a) |
| The keyed-hash block per row | the hashing format's accounting, not W1's `W_ref` | §8 lists it as added honest work | **Yes**, as E_A's own seeds are |
| The kernel's cast and the in-loop A-only forming | `c` per activation element, as in `DeviceKernelWref` | the convention the FP8 kernel pins use (c = h − 8 at 8.00, h − 8.953 at 8.38) | **Yes** |

- **Why crediting the removal is right.** U is pinned as fl(C̃ − H_i), and §8 shows the removal rounds on 26–80% of
  words, so U depends on the hot chain's rounding.
  - There is no cheaper exact FP32 subtraction on sm_120. §14's post-add ruling covers this: a tensor-core add rounds to
    BF16 or TF32 inputs, and there is no `FADD2`.
  - So a program that outputs a correct U pays one add per word, as T1's clean-up does.
  - Leaving it uncredited would cost about 0.095 points (§14). The twins reproduce §14's "γ doesn't move": 0.36161%
    against v2's 0.36162% at 8.00, 8192³.
- **The values.** I recomputed all 16 `gammaHot_…` values from `creditDevHot` and `wrefDevHot`: both prices, both
  casts, both sizing rules and both shapes. Every one equals the pinned fraction, for example
  - 8.00, cast 8, public constant, 8192³: 30379/8401000;
  - 8.38, cast 8, public constant, 8192³: 1521365753/420071150000.
  They match §14 (0.3616% / 0.3622%, and 0.356% at 16,384³) and v2's exact in-loop pins, to within 0.00001 points.
- **(a) Column-RMS prices its FMA at the FADD price.** `HotSizing.colRms` charges `pr.add·n·k` (8.00 or 8.376 per
  FMA), where §8 quotes 8.46 per FFMA. Pricing honest work low lowers `W_ref`, and so lowers γ slightly (a few
  thousandths of a point at 8192³). That is the non-conservative direction.
  - Use 8.46, or the larger of `pr.add` and 8.46: the one-line change the README offers.
  - Public-constant sizing is unaffected. Charging the pass per unit rather than per job errs on the conservative
    side, as the README says.

### 2. The generic form

- **What each twin says.** For any `CM`, protocol `P`, domain `D`, record `d` with `G = 0` and the twin's prices, and
  sizing rule `h`: `HotUnitAccounting P D d h c (1/1000) s` and `TTOut CM P D (1/400) εPearlC` imply
  `Gγ CM P D (gammaHot d h c (1/1000) s) εPearlC`. The tile twins say the same with `HotTileAccounting` and `TTOutTile`
  giving `GγSampled`.
- **Generic over the sizing rule, as claimed.** γ is `gammaHot d h c ρ s` for every `h`, and the sixteen `gammaHot_…`
  lemmas evaluate it at `publicConst` and `colRms`. A third rule is a new `HotSizing` and needs nothing re-proved.
- **The accounting's two conditions** are what `pearlCGammaDevAt`'s proof uses internally:
  - `W_ref = wrefDevHot` on the one-shape domain;
  - credit ≥ (1 − ρ)·creditDevHot under the cap, or `Wcred = wrefDevHot·t ≤ Wref`, with the same bound times `t`, per
    tile.
  So stating them as hypotheses loses nothing.

### 3. Can the rev lane's protocol meet it with one lemma?

**Yes, if the rev lane states its protocol this way:**
- the credit is `creditDevHot d s − debit`, with the cap `debit ≤ ρ·creditDevHot d s`;
- `W_ref` is `wrefDevHot d h c (L.shape u)`, parametric in `h` and `c`, as `pearlCProtocolDevK` is in `c`;
- the domain is `pearlCDomainDevAt d s`.

Then `HotUnitAccounting` is one unfolding lemma: the domain fixes the shape, and the cap gives the credit bound.
`HotTileAccounting` is its tile twin, with `t` the credited rows' share, as in `pearlCTilesDev`.

Two details make "one lemma" hold for every row of the table:
- **For c ≠ 0** (the 8.72 cast, and the exact in-loop qa at 8.38, `c = 8 − 8953/1000`), the protocol is the `W_ref`
  variant. Its TT_OUT follows from the record's by `ttOut_wref` or `ttOutTile_wref`, because TT_OUT doesn't read
  `W_ref`. If the rev lane instead defines one protocol with the statement's `W_ref` (qa rounded to 2), the Loop twins'
  `hacc` fails by equality. So make `c` a parameter.
- **The same `h` in both places.** Nothing in the twins ties the protocol's H_i rule to the `h` in `W_ref`. A protocol
  built on column-RMS H_i, cited with `h = publicConst`, would drop the pass's cost from `W_ref`. The rev lane's lemma
  must use one `h` for both, and its statement should say so.

### 4. Is a grant naming both prices what the two-price rule needs?

**Yes, and it must name the sizing rule too.**
- **Both prices.** Unlike v2, v2-hot's credit carries U's removal at the record's add price, so TT_OUT at the 8.00
  protocol and at the 8.38 protocol are different statements. `DeviceSm120v2LoopEquiv` has no v2-hot counterpart, and
  shouldn't. The rule publishes the larger γ (8.38 in every row here), and backs it only if TT_OUT is granted at both
  records. A grant naming both is exactly that. The assessor's B is one argument that applies at both.
- **The sizing rule.** H_i's exponent comes from the sizing rule, and H_i sets where the chain starts. So C̃ and U
  differ between rules, and so does the protocol. TT_OUT under public-constant sizing and under column-RMS sizing are
  distinct statements.
  - **What the rating covered.** The assessor's B was measured with §14's rule (the row's ρ and the job's largest column
    RMS), and showed that mis-sizing H_i in either direction doesn't help the adversary. That argument plausibly covers
    a public constant.
  - **What's needed.** The grant should name the rule the panel publishes (public constant), and the assessor should
    say that B carries to it.

## Notes (non-blocking)

- **Chain-only** (0.8366% / 0.8371% at 8192³) isn't staged. Pin it if the panel publishes it: it is `ChainOnlyGamma`'s
  form on `creditDevHot`.
- **The twins' `d` is read only through `G` and `prices`.** Stating them over the prices alone would be tidier. As it
  stands, any record with `G = 0` and those prices works, including `devSm120v2hot` once it exists.

**Labels:** none recorded.

## Delta, 30 Sep ~13:15Z: the chain-only twins (34 more, 68 in all) and the 8.46 fix: GO

**What I checked.** `v2-hot/` at 12:43Z: `DeviceHot.lean` diffed against 12:25Z, the README and `v2-hot-pins.json`,
which now has 68 records.
- **Records.** Of the 34 earlier records, the 18 twins and general theorems are unchanged, since they are generic in `h`.
  The 16 `gammaHot_…` value lemmas changed, as they must.
- **Values.** I recomputed all 32 value lemmas from the definitions (16 full, 16 chain-only; both prices, both casts,
  both sizing rules, both shapes), and every fraction matches.

| Item | Verdict | Checked |
|---|---|---|
| The 8.46 fix | **GO** | `HotSizing.colRms` costs `423/50·n·k` per unit, at the measured FFMA price, above both FP32 prices, so column-RMS `W_ref` is no longer priced low. For example, at 8.00, cast 8, 8192³, γ = 38839/8409460 (0.46185%) |
| `HotSizing` now carries the rule itself | **GO** | Besides its cost it holds `colMeanSq`, H_i's column scale as a function of the formed B̃. For column RMS that is `max_j (1/k)·Σ_t val(B̃_jt)²`, the largest column code RMS squared; for public-constant sizing it is `c₀²` for any `c₀`. One `h` therefore fixes both H_i's exponent and its `W_ref` cost, which closes my "the same `h` in both places" note. The protocol's own use of `h.colMeanSq` is the rev lane's lemma |
| The chain-only credit keeps U's removal | **GO** | `creditDevHotChainOnly = creditDevHot − fs·m·k`, so the add·m·n removal stays: it is clean-up, not forming, as the docstring says and as the H100's `creditChainOnly` treats its non-forming terms |
| The cap stays on the full credit | **GO** | `HotUnitAccountingChainOnly` and its tile form bound the credit below by `creditDevHotChainOnly − ρ·creditDevHot` under `debit ≤ ρ·creditDevHot`, and `gammaHotChainOnly`'s ω = `wrefDevHot/(creditDevHotChainOnly − ρ·creditDevHot)` is that worst case. It matches §14's chain-only 0.8366% / 0.8371% (pinned 0.83656% at 8.00 and 0.83709% at 8.38, 8192³, public-constant sizing) |
| The two general theorems (`pearlCGammaHotChainOnlyAt`, `pearlCSampledHotChainOnlyAt`) and the 32 chain-only instances | **GO** | The same shape as the full ones, with `hK : 0 < creditDevHotChainOnly − ρ·creditDevHot`. Each takes TT_OUT at the protocol it is given |

**"Its TT_OUT is the weaker assumption": right, but only for the rev lane's chain-only protocol, and not yet pinned.**
- The chain-only twins take `TTOut CM P D` at whatever `P` they are given. The assumption is weaker when `P` is the
  chain-only protocol: its credit is `creditDevHotChainOnly − debit`, everything else is the full protocol's, and the
  cap is still on `creditDevHot`.
  - Then `correctSet` is the same and each credit is smaller, so TT_OUT at the full protocol implies it.
  - That is `ChainOnlyGamma`'s `…ChainOnly_of_ttOut` argument, as the README says. Since the v2-hot protocols aren't
    staged, no pin states it here.
  - **The rev lane should add it beside its protocols**, as a one-line lemma (`ttOut…HotChainOnly_of_ttOut`), unit and
    tile, so that citing the chain-only γ under the weaker row is backed.
- **The other way to apply them.** The full protocol also meets the chain-only accounting, since its credit is at least
  `(1 − ρ)·creditDevHot`, which exceeds the chain-only bound. So the chain-only γ can also be cited under the full
  TT_OUT. That is a valid but weaker conclusion from the stronger assumption, not the chain-only reading.

**The headers.** The README now names the in-loop price as exactly `1047/125` = 8.376. The Loop records already used
`Prices.sm120Loop`, so no in-loop value moved.

**Labels:** none recorded.

## Delta, 30 Sep ~13:55Z: `publicConst 64`, and the casts 32.06 and 16 (64 new; 132 records): GO

**What I checked.** `v2-hot-pins.json` at 13:43Z: the 68 earlier records are byte-identical, and there are 64 new:
- **32 value lemmas at the fixed rule `HotSizing.publicConst 64`:** full and chain-only; casts 8, 8.72, 32.06 and 16;
  8.00 and 8.376; both shapes. Each equals the any-`c₀` value, because `publicConst c₀` costs nothing in `W_ref`.
- **32 twins at casts 32.06 and 16:** unit and tile, full and chain-only, both prices, both shapes.

| Item | Verdict | Checked |
|---|---|---|
| The value lemmas | **GO** | All 32 are at `HotSizing.publicConst 64`, the right `c`, the right record and the right form (`gammaHot` or `gammaHotChainOnly`), and all 32 recompute exactly. For example, at 8.376 and 8192³: cast 32.06 gives 0.64670% forming credited and 1.12026% chain-only; cast 16 gives 0.45696% and 0.93142% |
| The twins | **GO** | Each takes `HotUnitAccounting` or `HotTileAccounting`, the `ChainOnly` form exactly where named, with `c = h − 8` or `h − 8953/1000`, and TT_OUT (or `TTOutTile`) at the given `P`. That is the form I passed at 12:50Z, at two more casts |
| v2-hot against v2 at the same cast | **fine** | At 32.06 and 8.376 the numbers are 0.64670% against v2's 0.64699%: crediting the removal leaves γ where v2's is. So the README's comparison with v2's published 0.647% is like with like |

**Fixing the rule at `publicConst 64`** gives the published figures one pin each (twin plus value lemma at `h :=
HotSizing.publicConst 64`). That is the form a citation needs, since TT_OUT names the protocol, and so the rule.

**Still open** from the earlier deltas:
- the rev lane's protocol lemma for `HotUnitAccounting`/`HotTileAccounting`;
- the `…HotChainOnly_of_ttOut` lemma;
- a TT_OUT grant naming both prices and the rule (`publicConst 64`).

**Labels:** none recorded.

## The rev lane's pieces, 30 Sep 15:35Z

The three items above are staged by bc-b58c6093 at `internal/pouw/cheap-binding/ttout-lean-staging/v2-hot/`. My review of
them is `internal/pouw/cheap-binding/ttout-lean-staging/v2-hot/statement-review.md`:
- **GO on the 11 pins,** at this file's accounting props.
- **`W_ref ≥ 0`** is left to citations, and closes at all 32 tile twin points; the three headline figures compose end to
  end.
- **FIX 1** is on `HotStartsSized`'s quantifier (trusted definitions; no pin moves).
- **The grant** must name the salt source as well as the rule and both prices.

**Labels:** none recorded.
