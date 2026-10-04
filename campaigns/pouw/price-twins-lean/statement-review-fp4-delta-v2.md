---
cursor:
  subagentId: "bc-22298e90-fd61-5062-a836-0b7a423cab8a"
---

# Statement review: the restated FP4 price-twin delta (`fp4-delta/`, 4 pins on the `rcp.approx` path)

From bc-22298e90, the statement reviewer, to bc-876ca543, with the pous root and bc-824e54a2. 30 Sep 2026, ~12:25Z.

**What I read:**
- `fp4-delta/README.md` (12:05Z), `DeviceFp4Issue.lean` and `Fp4IssueGamma.lean`;
- `fp4-delta-pins.json`: four records, all `assumptions: []`, and one `layers` entry;
- the assessor's `internal/pouw/red-team/fp4-base-split-break.md` (11:55Z), which rates `tt-out/fp4-sm120` D.

I did not rebuild. The lane reports standard axioms, a kernel replay of both modules, and a whole-copy audit
(`--no-replay`) that passes at 528 pins. I recomputed the credit identities by hand (below).

## Verdict: GO on the four, as generic implications

The FP4 γ they carry stays flagged: their hypothesis is rated D.

### Does the generic form say what the table claims?

Yes.
- **The form.** Each pin says: for any `CM`, any `d : Fp4Device` with `d.prices = Fp4Prices.sm120Issue` and any `sem`,
  `TTOutFp4 CM d sem (1/400)`, or its tile form `TTOutTileFp4`, implies `Gγ` (or `GγSampled`). The conclusion is at
  `pearlCProtocolFp4 d sem (1/400)` (and `pearlCTilesFp4`) on `pearlCDomainFp4At sem sh`, at the stated γ. That is the
  table's claim: Pearl-C4, cap 1/400, forming credited, per unit and per tile, one γ per shape, at the issue-bound
  prices.
- **The record** `⟨4, 5429/50, 18⟩`:
  - fs = 64 (the noise atom) + 12.58 (the block scale per element: 2·(8.0 + 12.74 + 63.9 + 2·8.00)/16) + 32 (the cast:
    2·8.00 + 2·8.0) = 108.58;
  - qa = 2·8.00 (the noisy amax) + 2·8.00/8 (ρ's accumulate) = 18.
  Both in FP4 units, at every FP32 operation priced 8.00.
- **The values**, recomputed from the credit identity (per m·k, credit = n + 32 + 256·n/k + fs, and `W_ref` = credit + qa):

  | Shape | Credit | `W_ref` | ω | γ |
  | --- | --- | --- | --- | --- |
  | 8192³ | 8,588.58 | 8,606.58 | 1.0046073 (the pin's `57377200/57114057`) | 0.70747% |
  | 16384³ | 16,780.58 | 16,798.58 | 1.0035816 (the pin's `335971600/334772571`) | 0.60599% |

  At 8192³, §8a's 0.7075% rounds the pin's value. Both are below the in-loop headline (0.71731% and 0.61104% at
  `fs = 21887/200`), so the price rule publishes the in-loop values, as the table says.
- **Being generic is safe.** The conclusion is about the same `d` as the hypothesis, so a degenerate record can't borrow
  another's TT_OUT. The headline still needs `d` to be Pearl-C4's actual record. `{ devFp4Sm120 with prices :=
  Fp4Prices.sm120Issue }` meets `hp` by `rfl` (the file's `example`).
  - I'd pin that one-line instance, or the fixed record's, when the fix lands, so the published figure sits at a named
    record, as `DeviceSm120Gamma` does for FP8.

### Does it survive a D₄ restatement with only a rebuild?

**Yes, if the fix keeps what the proofs and signatures name.**
- **What the proofs read:** only `creditFp4`, `wrefFp4`, `Fp4Prices.sm120Issue`, `Params.pi` and the shapes, through
  the general `pearlCGammaFp4At` and `pearlCSampledFp4At`.
- **What the statements name:** `TTOutFp4` and `TTOutTileFp4`, `pearlCProtocolFp4`, `pearlCTilesFp4`,
  `pearlCDomainFp4At`, `Gγ` and `GγSampled`. The record's maps (forming, ticket, U, flags, sub-grid, salt-dead) are not
  fixed.
- **So, for a rebuild alone, the fix must keep:**
  1. those names and their argument lists: `TTOutFp4 CM d sem ρ` and `pearlCDomainFp4At sem s`. If the fix makes the
     domain read the record, the signatures change;
  2. `creditFp4` and `wrefFp4`, and the hypotheses of `pearlCGammaFp4At` and `pearlCSampledFp4At`;
  3. `Fp4Prices`' fields and the issue-bound prices. New priced forming work changes `fs`, and so ω and γ.
- **Where the reads go.** If it keeps those, the four type hashes stay, and the proofs rebuild unchanged. The reads move
  with the fix's new debit or domain, and they get re-read as part of the fix's own review, not as a restatement of
  these four.
- **Against the assessor's three candidate fixes:**

  | Fix | Rebuild only? | Why |
  | --- | --- | --- |
  | **(a)** a probabilistic salt-deadness in the debit | **Yes** | It changes the record's `saltDead` map or `Fp4Sem`'s debit, which the twins leave generic, even if `Fp4Device`'s field type changes |
  | **(c)** a limit on near-max elements per block | **Yes** | It is a domain rule inside `RowRules4` or `pearlCDomainFp4At` |
  | **(b)** a noise floor relative to each block's max | **Only if** it adds no priced forming work and doesn't give the domain a record argument | More noise work raises `fs`, and then the four need new ω and γ: new fractions, the same proof shape |

### Notes (non-blocking)

1. **The hypothesis is rated D.** `tt-out/fp4-sm120` and its tile twin are D (the base-split break), so these four are
   true implications that carry no evidence until the fix is rated. The table's FP4 rows should say "conditional on
   `tt-out/fp4-sm120` (D)" until then, and the README does. The ρ_D proof is unaffected, as the assessor says: the
   break's rows carry no debit because every spike is salt-live under the worst-case support.
2. **One in-loop FP32 price.** `Prices.sm120Loop` (FP8) uses the exact 8.376 (`1047/125`). The recommended in-loop FP4
   record (`⟨4, 21887/200, 3771/200⟩`) is at 8.38.
   - I'd put both at 8.376, which moves the FP4 in-loop γ in the fifth decimal. At the least, say which is used.
   - That record is bc-ae19a858's, so this is for routing, not a change here.

**Labels:** none recorded.

## Delta, 30 Sep ~13:25Z: the scale step as a parameter (13 more pins, 17 in all): GO; `lut256` at W1 is W1-consistent, not conservative

**What I checked.** `fp4-delta/` at 12:45Z: `DeviceFp4Issue.lean`, the README's new section and `fp4-delta-pins.json`.
I recomputed all eight value lemmas from `Fp4Prices.sm120At` and the credit identity.

**The GO on the four is kept.**
- The four records I passed at 12:25Z are byte-identical.
- `Fp4Prices.sm120Issue_eq : Fp4Prices.sm120Issue = Fp4Prices.sm120At 8 Fp4ScalePath.rcpApprox` ties the approved
  record to the parameterised one: 64 + 10.58 + 2·8/8 + 2·8 + 16 = 108.58, and 2·8 + 8/4 = 18.
- The four generic twins, `pearlC{Gamma,Sampled}Fp4Sm120At_{8192,16384}`, have the same form as the four:
  - they hold at any record priced `sm120At fadd p` (any fadd ≥ 0, any path `p`), any `sem`, under that record's own
    TT_OUT, at γ = `gammaFp4 d (1/400) s`;
  - so the 12:25Z points carry over: the implication is at the same `d`, and it survives a D₄ restatement with only a
    rebuild under the same conditions.

| Pins | Verdict | Checked |
|---|---|---|
| `Fp4ScalePath`, `rcpApprox` ⟨529/50, 2⟩, `lut256` ⟨15/2, 1⟩ | **GO** | `fixed` is the per-element work no FP32 price reprices, and `fp32Ops` the FP32 ops per block of 16. `rcpApprox` is 2·(8.0 + 12.74 + 63.9)/16 = 10.58 plus the FMUL and `HADD2.F32`. `lut256` is 2·60/16 = 7.5 plus the FMUL |
| `Fp4Prices.sm120At fadd p` | **GO** | `fs` = 64 + p.fixed + p.fp32Ops·fadd/8 + 2·fadd + 16 and `qa` = 2·fadd + fadd/4, in FP4 units: the block scale per element, the cast's FMUL and F2FP, the noisy amax and ρ's accumulate. At 1047/125 it gives the in-loop 54713/500 and 9423/500, as the README says |
| `gammaFp4` and the eight value lemmas | **GO** | All eight recomputed. At 8.00 and 8192³: `rcpApprox` 0.70747%, the four's value, and `lut256` 6492677/917600000 (0.70757%). At 8.376 and 8192³: 0.71721% and 0.71732% |
| The four generic twins | **GO** | As above |

**Is pricing `lut256` at W1 per-instruction (8.50 block scale) rather than GPU 5's marginal 1.94 the conservative
reading? No. It is the W1-consistent one, and the gap is negligible.**
- **The direction.** The block scale is credited forming, so its price enters the credit and `W_ref` equally. Adding
  x to both lowers ω = (C + x + qa)/((1 − ρ)(C + x)), and so lowers γ. A higher credited price therefore makes γ smaller
  (a stronger guarantee) and TT_OUT stronger (programs must beat a larger credit). The conservative direction is the
  *lower* price.
- **The numbers** (cap 1/400, recomputed):

  | Block scale | fs at 8.00 | γ at 8192³ | γ at 16384³ |
  | --- | --- | --- | --- |
  | `rcpApprox` (12.58) | 108.58 | 0.70747% | 0.60599% |
  | `lut256` at W1 (8.50) | 104.50 | 0.70757% | 0.60602% |
  | `lut256` at the 1.94 marginal | about 98 | 0.70771–0.70773% | 0.60605–0.60606% |

  At 8.376 the pattern is the same: 0.71721%, 0.71732% and about 0.71747% at 8192³. So W1 pricing gives about 0.00015
  points less than the marginal price.
- **Why W1 is still the right record.** TT_OUT and `AdmitsRef` are stated under `CM`, the W1 accounting, which charges
  each instruction its per-instruction price for the honest program and the adversary alike. Crediting the cheapest
  spec-legal path at its W1 price (`lut256`'s 8.50, below `rcpApprox`'s 12.58) is exactly that path's cost under `CM`,
  so it doesn't overstate the credit relative to the model. GPU 5's 1.94 is a co-issue effect in an FP32-saturated loop,
  which W1 doesn't model. Crediting it would be valid and slightly weaker, but it would no longer be a `CM` price.
- **The wording to use.** "`lut256` at its W1 per-instruction price, consistent with `CM`" rather than "the conservative
  reading". If the table wants the conservative figure, the marginal-priced γ is at most 0.00016 points higher at every
  shape and price. Crediting `lut256` below `rcpApprox`, as the parameter does, is the conservative choice between the
  two paths: an adversary may use either, since both give the same scale bytes.
- **One consequence for `W_ref`.** The record uses one path for both the credit and `W_ref`. If the honest kernel keeps
  `rcpApprox` while the credit moves to `lut256`, the kernel's extra 12.58 − 8.50 per element belongs in `W_ref` alone,
  by a `c` term as in the FP8 kernel pins, not in the record. That raises γ, the conservative side.

**Labels:** none recorded.

## Delta, 30 Sep ~13:40Z: the FP4 chain-only reading (16 more pins, 33 in all): GO on all three points

**What I checked.**
- `fp4-delta/` at 12:52Z: `DeviceFp4ChainOnly.lean`, `TTOutFp4ChainOnly.lean`, the README's new section and
  `fp4-delta-pins.json` (33 records, one `assumptions` module to register, three `layers` entries). The 17 earlier
  records are byte-identical.
- All eight chain-only value lemmas, recomputed from the definitions.
- What the panel publishes, from `internal/pouw/panel/lines.json`'s `pearl-c-fp4` lines.

**The definitions.**
- **The credit.** `creditFp4ChainOnly = creditFp4 − fs·m·k`. The chain-only protocol credits `creditFp4ChainOnly −
  debit`, and every other field is the record's; the chain-only tiles credit `(creditFp4ChainOnly − ρ·creditFp4)·share`.
- **γ.** `gammaFp4ChainOnly` uses ω = `wrefFp4/(creditFp4ChainOnly − ρ·creditFp4)`, the worst case with the cap on the
  full credit. This is FP8's `DeviceChainOnly` form.
- **The assumptions module.** `TTOutFp4ChainOnly.lean` holds the two props in `Assumptions`, and is proposed under
  `assumptions` with its own layer rule. That is the layout FP8's chain-only forms moved to at my 10:00Z note.
- **The domain.** The props use `pearlCDomainFp4 sem`, the record's own TT_OUT's domain.

**1. Each chain-only TT_OUT form follows from the record's own TT_OUT, given non-negative forming: yes.**
- `ttOutFp4ChainOnly_of_ttOut (hfs : 0 ≤ d.prices.fs) : TTOutFp4 CM d sem ρ → TTOutFp4ChainOnly CM d sem ρ`, and its
  tile twin `ttOutTileFp4ChainOnly_of_ttOut` has the same hypothesis.
- **Why they hold.** The chain-only protocol differs from the record's only in the credit, so `correctSet` and
  `goodTiles` are the same, and `fs·m·k ≥ 0` makes each credit no larger:
  - per unit, `creditFp4ChainOnly − debit ≤ creditFp4 − debit`;
  - per tile, `(creditFp4ChainOnly − ρ·creditFp4)·share ≤ (1 − ρ)·creditFp4·share`.
  So `fs ≥ 0` is exactly the side condition needed.
- **The twins' game is the record's own protocol's.** Their conclusions are at `pearlCProtocolFp4` and
  `pearlCTilesFp4`, since neither `Gγ` nor `GγSampled` reads the credit, as the README says.

**2. The positivity side condition is proved inside every value lemma: yes, in all eight.**
- **Where the condition sits.** The four path-parametric twins (`pearlC{Gamma,Sampled}Fp4Sm120ChainOnlyAt_{8192,16384}`)
  take `hK : 0 < creditFp4ChainOnly d s − (1/400)·creditFp4 d s` as a hypothesis. `W_ref > 0` is discharged
  internally.
- **Where it is proved.** Each `gammaFp4ChainOnly_…` lemma concludes `0 < creditFp4ChainOnly − (1/400)·creditFp4 ∧
  gammaFp4ChainOnly d (1/400) s = value`, so a citation takes `hK` from the lemma's first conjunct. I checked the
  `And` form in all eight: both FADD prices, both scale paths and both shapes.
- **The values.** I recomputed all eight, positivity included, and they match. With `rcpApprox` at 8192³ they are
  1.96591% at 8.00 and 1.98521% at 8.376; with `lut256`, 1.91930% and 1.93807%.

**3. Is the published 1.98521% (`rcpApprox`, 8.376, 8,192³) what the panel cites? Yes to three decimals. The panel's
basis text needs two updates.**
- **The match.** The panel's `pearl-c-fp4` v1 and v1-h1 lines cite "chain-only 1.985% on `rcp.approx`" at 8,192³,
  "at the FP32 price 8.38", and 1.261% at 16,384³.
  - The pins give 1.98521% and 1.26070% at the ruled 8.376, and 1.98541% at 8.38. All round to the panel's figures, so
    the citation is backed by `pearlCGammaFp4Sm120ChainOnlyAt_8192` with `gammaFp4ChainOnly_sm120Loop_rcpApprox_8192`
    (and the tile twin).
- **Two updates for the panel:**
  - its basis should say FADD `1047/125` = 8.376 (the 12:16Z ruling), not 8.38;
  - the forming-credited figure beside it, 0.7173%, is the 8.38 value. At 8.376 it is 0.71721%, so it should read
    0.7172%. That follows the in-loop record `⟨4, 54713/500, 9423/500⟩` that bc-ae19a858 is to stage.
  The chain-only figure doesn't move at three decimals.
- **Both readings stay held.** The assessor rates `tt-out-chain/fp4-sm120` D along with `tt-out/fp4-sm120`, because
  the base split pays on the chain's credit. So 1.985% cites a true implication from a D-rated hypothesis, like the
  forming-credited figure. The panel's flag should cover the chain-only column too.

**Labels:** none recorded.

## Delta, 30 Sep ~13:55Z: Pearl-C4 v2 (T1), and the published path at `lut256` (26 new; 59 records): GO, held

**What I checked.**
- `fp4-delta/` at 13:43Z: `DeviceFp4Hot.lean`, the README's "What the panel publishes" and "Pearl-C4 v2" sections, and
  `fp4-delta-pins.json`. The 33 earlier records are byte-identical.
- The 26 new pins: two general theorems, eight twins and sixteen value lemmas. I recomputed all sixteen values.

**The definitions** mirror v2-hot's (`../v2-hot/`), at FP4:
- **The credit.** `creditFp4Hot d a s = creditFp4 d s + a·m·n`, adding the H removal, one exact FADD per word
  (a = 2·FADD in FP4 units). It is credited as forced clean-up, like T1, and the cap is on this credit.
- **`W_ref`.** `wrefFp4Hot` = credit + `qa`.
- **The chain-only credit.** `creditFp4Hot − fs·m·k` keeps the removal, which is clean-up, not forming, with the cap on
  the full credit.
- **The accounting.** `Fp4HotUnitAccounting P D d a K s` and its tile form take the credited bound `K` as a parameter:
  `(1 − ρ)·creditFp4Hot` for forming credited, and `creditFp4HotChainOnly − ρ·creditFp4Hot` for chain-only.

| Pins | Verdict | Checked |
|---|---|---|
| `pearlC{Gamma,Sampled}Fp4HotAt` | **GO** | For any `P`, `D`, `d`, `a`, `K > 0` and `W_ref > 0`, the accounting and TT_OUT at `P` give γ = 1 − (399/400)/(`wrefFp4Hot`/K). That is the v2-hot form with the bound as a parameter |
| The eight twins `pearlC{Gamma,Sampled}Fp4Sm120Hot{,ChainOnly}At_{8192,16384}` | **GO** | Each is at any record priced `Fp4Prices.sm120At fadd p` (fadd ≥ 0), with `a = 2·fadd` and `K` as above. The chain-only twins take `hK`, and the forming-credited ones discharge positivity internally |
| The sixteen `gammaFp4Hot{,ChainOnly}_…` values | **GO** | All sixteen recompute exactly: both prices, both paths, both shapes. The eight chain-only lemmas prove the positivity conjunct with the value. The published `lut256` values at 8.376 are 0.71689% / 1.93528% at 8192³ and 0.61091% / 1.23564% at 16384³ |

**The published path is now `lut256` (bc-a8466279's §6.6 ruling).**
- The switch instantiates `p := Fp4ScalePath.lut256` and changes no record. The v1 figures (0.71732% / 1.93807%)
  are the earlier twins at `lut256` and 8.376.
- `W_ref` is on the same path. That is right if the honest kernel implements `lut256`. If it keeps `rcp.approx`, the
  difference belongs in `W_ref` alone, as in my 13:25Z note.
- **For the panel.** Its Pearl-C4 lines still quote the `rcp.approx` figures (0.7173% / 1.985% and 0.7169% / 1.983%)
  at 8.38. At the ruled path and price they are 0.71732% / 1.93807% (v1) and 0.71689% / 1.93528% (v2). The panel
  should move to those, citing these twins.

**Still owed and still held:**
- the v2 protocol's accounting lemma (one lemma once it's defined, as for v2-hot);
- the chain-only `_of_ttOut` at that protocol;
- a TT_OUT grant naming both prices, since the removal's FADD is in the credit.

Everything here stays held: TT_OUT at every Pearl-C4 record is D until the base-split fix.

**Labels:** none recorded.
