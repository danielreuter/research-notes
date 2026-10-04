---
id: 20261004T2202Z-report-relay-internal-pouw-fp8-redteam-h1
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/internal/pouw-fp8/redteam-h1.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/pouw-fp8/redteam-h1.md`, sha256 `997b1f63559b7775afdb446e68c1e09bf6dccd174e918ec4842965b419af6287`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# H-1: the consolidated red-team verdict

Coordinator, 28 Sep 2026. **Status: H-1 final (20:40Z); the H-1T verdict was added 29 Sep, 00:50Z (the last section).** Two independent reviews are running:

- **The main red team, Phase 19** (bc-89770364): Round 9 repricing, the registration check, worst-case activations,
  reuse and commitment order. Its post goes to `genuine-fp8-interface-red-team.md` and `new-crypto/red-team.md`.
- **An independent strike** (bc-8954d550), in `red-team-h1-strike.md`. It covers:
  - the γ accounting, counted instruction by instruction at Round 9 prices;
  - adversarial weights that still pass the registration check;
  - the two absorption attacks and their fixes;
  - the 4090 block-2 = −block-1 issue;
  - whether `DistinctLiveH1` is the only new assumption.

**The candidate:** `docs/pouw/hardness-shaped-matrices.md`, with its scripts in `internal/pouw/hardness/`, posted in
`genuine-fp8-interface.md` §2.1.H. It claims:
- γ 0.74–0.78% at 16,384³ (Round 9 prices), and 1.05–1.14% at 8,192³ (0.999% with the Y16 input);
- perplexity +0.03% to +0.36% against the model's own FP8.

**Compiled prices:** H-1's forming kernel is being added to the Round 10 spec (`internal/pouw/gpu-constants.md` §15,
ptxas 12.9). Track H will supply CPU-side SASS counts. Nothing runs on a GPU without the Verity root's approval.

**Target configuration (Daniel, 19:52Z):** the registration check adopted, B = 2, the hybrid floor, the X_q route; Y16 as
a secondary row.

## Verdict: NO-GO as specified; CONDITIONAL GO at 16,384³ and above once repaired

Both reviews reach this independently: the main red team's Phase 19 (bc-89770364), and the strike (bc-8954d550,
`red-team-h1-strike.md`). The strike glimpsed two coordinator log headlines at about 20:17Z. That was after its core
findings were computed and recorded, and its report says so.

### Why NO-GO: the registration check admits weights that break `DistinctLiveH1`

All of these are measured on the bit-exact atom, and they are found independently.

| Family | Finding | ε | Proposed fix |
|---|---|---:|---|
| One lane differs at the minimum separation | F19-2 (Phase 19) | about 12.5% | activation-side repair |
| Shared loud lanes plus per-column "tag" lanes: the 14-bit truncation swamps the tags | X-H1-S1 (strike) | **about 48%** of all words, every salt | **P2′, an L1-relative P2.** Borderline for real weights: sampled minimum 2^−4.6 against about 2^−4.8 needed; untested at full shape |
| A column pair b, −b at A = 0 | `barrier`, **confirmed** by Phase 19b on the exact atom | about 25% | a sign-separation clause (P2 against −B′). It rejects no Qwen2.5-0.5B weights |
| P4-legal slices absorbed by the FP32 running chain | `barrier` (up to 0.44), **confirmed** by Phase 19b (real on every salt); X-H1-S3 (12.5–25%) | 12.5–44% | the L1 form of P4, a full ulp (equivalently, P4 + 2 bits). Real weights pass at k = 16,384 (+0.66 bits); **32,768 is about −0.34 bits by trend, so Track H must measure it**; 65,536 is off the frontier |

### Forming is underpriced by about 73–79 units per element

- **Phase 19** puts it at 318.5 on X_q. The **strike** puts it at 312 on X_q with the hybrid floor, 274 on X_q with the
  row floor, and 264 and 226 on Y16.
- The shared causes:
  - the f16 → e4m3 cast costs 48–64 per code, not 32;
  - a lone LOP3 costs 32, not 17;
  - a second LOP3 is required.
- A compiled count is still needed; Round 11 carries H-1's forming kernel.

### γ if repaired (measured Round 9 prices, FADD 32.11, ε = 1/400)

| Route (2,048³ and 4,096³: not run; 4,096³ fails structurally) | 8,192³ | 16,384³ | 32,768³ | 65,536³ |
|---|---:|---:|---:|---:|
| **X_q, hybrid floor (adopted)** | 1.36–1.38% (fails) | **0.89–0.90%** (FADD* 32.17–32.18) | 0.66% | dropped (frontier) |
| X_q, hybrid, at ptxas 12.9 compiled prices (238.3 per element; Phase 19b; untimed) | 1.139% (fails) | **0.781%** | 0.602% | dropped |
| X_q, row floor | 1.25% | 0.84% | 0.63% | — |
| Y16, hybrid (comparison) | 1.22–1.24% | 0.82–0.83% | 0.62–0.63% | dropped |

These γ values hold only if ε really is 1/400. Under X-H1-S1 as it stands, γ ≈ 48%.

### Other findings

- **X-H1-S5:**
  - Y16 needs |y| < 464, or about 50% of words become free;
  - 𝒫 should require finite codes;
  - the f16 intermediate needs no widen.
- **X-H1-S6:**
  - Block 2 = −block 1 gives no gain on the H100 under additive W1, because the negated word is distinct and not free.
  - Under a time model it would matter, and it would need the H-1P permutation.
- **X-H1-S7:**
  - "any B′ that passes 𝒫" is a sound worst-case replacement only if 𝒫 implies `DistinctLiveH1`. **Today 𝒫 is a
    heuristic filter.**
  - The quality evidence is WikiText-2 only.

### Phase 19b (20:48Z)

- Both of `barrier`'s families are confirmed on the exact atom, with independent code.
- **D-3s and D-4 are not affected by absorption** at these sizes.
- **The cast and the X_q unpack at 32 per code under ptxas 12.9** (approved; untimed until Round 10) put the adopted cell
  at 238.3 per element.
- **Side finding:** P2 already rejects Qwen's tied LM head (1,970 real rows and 271 padding rows with duplicated slices).
  The class needs a rule for duplicated output columns, for example crediting each distinct column once.

### Conditions for GO

1. **Track H repairs the class against all four families.** That means P2′ (or F19-2's activation-side repair), a
   sign-separation clause against −b, and P4 raised by 2 bits (or an L1 form of P4).
2. **Re-run the adversarial constructions at full shape** (S1, F19-2, b/−b, absorption), and measure the pass rates of
   real weights at every k in the domain. If real weights fail at 65,536, restrict k or lower c1.
3. **Pin one bit-exact forming map** (F19-4), with F19-3's fix.
4. **Add legal-input clauses:** finite codes, and |y| < 464 on Y16. Both are checked at audit.
5. **Restate γ at the repaired forming price, with a compiled count** (Round 11).
6. **Re-measure quality under the repaired class,** on more than WikiText-2 and on a second model.
7. **Carry `DistinctLiveH1` as a named open assumption** until the Lean effort (`lean-atom-plan.md`) proves it for the
   repaired class. Proving it would also drop γ₀ = 1/400.

**Deployment requirement for Daniel** (the §0 rule): the registration check is itself a nonstandard deployment step.
It is adopted by Daniel. Its cost: a one-time pass over the weights of about one GEMM per matrix, and rejection of
non-passing layers, such as Qwen's `lm_head` duplicate rows.

## H-1T: the consolidated verdict (29 Sep, 00:50Z)

**The candidate:** Track H's H-1T, which puts 3 salted tag lanes with a fixed injective tuple per column in every k32 slice.
It is described in `docs/pouw/hardness-shaped-matrices.md` and posted in interface §2.1.H (21:41Z).

**The reviews:**
- the strike (bc-8954d550), in the "H-1T strike" section of `red-team-h1-strike.md`;
- the main red team's Phase 19c (bc-89770364), in `new-crypto/red-team.md` (Phase 19c) and
  `genuine-fp8-interface-red-team.md`.

The two ran independently: neither read the other's H-1T section.

### Verdict: NO-GO at 2,048³, 4,096³ and 8,192³; CONDITIONAL GO at 16,384³ and 32,768³

Both reviews agree on every size. γ is at FADD 32.00, credit 4T − 3, at γ₀ = 1/400 / γ₀ = 0:

| Size | γ | Verdict | Why |
|---|---|---|---|
| 2,048³ | 4.11% / 3.87% | NO-GO | price |
| 4,096³ | 2.21% / 1.96% | NO-GO | price |
| 8,192³ | 1.24% / 0.99–1.007% | NO-GO | See below |
| 16,384³ | 0.75% / 0.50% | **CONDITIONAL GO** | |
| 32,768³ | 0.50% / 0.25% | **CONDITIONAL GO** | |

**Why 8,192³ fails:** it clears only with γ₀ = 0 (a Lean proof) and FADD ≤ 32.006.
- Round 10's sweep predicts about 32.0075 for loops of the step's size (276–282 instructions, bank-clean): strike,
  X-H1T-S9.
- The uncounted IMAD.MOV, or HADD2 and HFMA2.MMA priced at 64, take the remaining 3.3 units of forming margin
  (Phase 19c).

**Function level holds.** Every construction, run through Track H's unchanged `h1_tagged.py`, gives 0 free or
duplicate credited words:
- the strike: S1, F19-2, b/−b, absorption, tag swamping and tuple collisions (X-H1T-S1 and S2);
- Phase 19c: 75 family runs, the targeted R check, a spiky Family B, R-pair probes and x = ±448 (X-H1T-1).

The weaknesses are in the arguments, the branching model and the deployment requirements, not in the simulations.

### Conditions for 16,384³ and 32,768³ (the union of both reviews)

1. **`DistinctLiveH1T` stays Assumed at ε = 1/400** until the Lean proof lands.
   - Phase 19c accepts the statement with 9 changes (X-H1T-8), including the unit id in the salt context and the full
     list of proof obligations.
   - Its "unequal on at least half the salts" is stronger than Target A, and `census` doesn't measure it (X-H1T-7).
2. **The proof covers every obligation both reviews found:**
   - cross-column R words for every tag lane, by an argument across several slices. A single flip moves adjacent
     columns (t₀ differing by 8) by 128, under ulp(R) = 512 (strike X-H1T-S5; the Lean worker's M2-1);
   - a "chain keeps moving" lemma for block-2 R words, and the pair (I_τ, R_τ) (X-H1T-5);
   - absorption via "an absorbed summand is at most half an ulp", which holds at ±2^k. The pinned `rnAddMoves` alone
     leaves [960, 1,024) open (X-H1T-3). So **R1's F6 is wrong**, and the Lean worker's L5 point is right. The fix is
     to pin M1's half-ulp movement lemma, or to raise the lowest lane-0 tag to 72.
3. **Branching stays a named gap**, and the β = 1% budget is not cited as bounding it:
   - the budget doesn't bound it (X-H1T-2: an 8-column dead-lane group passes P2′ yet collapses on 1/16 of salts);
   - at the frontier's n, the gap is larger than posted: the tag bits decide 92–98% of I words (strike X-H1T-S3).
   - Its size is bounded two ways:
     - the best branching prover loses at Round 10 prices, from +57% at 2,048³ to +1.1% at 32,768³ (strike X-H1T-S4);
     - branching saves at most 32·(2P − 1) per I word and nothing on R words, and nothing at all if predicated-off
       instructions still cost their issue slot (X-H1T-9).
   - **So the statement prices a salt-selected operand at 32 or more**, and **Round 11 times SEL, SHFL and LDS**, and
     predicated issue.
4. **The legal-input audit:** finite codes, and k ≤ 32,768 per unit.
   - The 416 headroom is **not** needed for security (X-H1T-4): saturation caps x1 at 448, so |R| < 2^33 for any
     finite code. Track H's decision 5 overstates it, and legal inputs can be all finite codes.
   - The headroom's quality role is unchanged.
5. **Units wider than 88,412 columns** get per-unit salts or unit-indexed tuples (strike X-H1T-S7; vocabulary heads).
   Phase 19c recommends a per-unit salted permutation of the tuples (X-H1T-13), which trades against the next item.
6. **B′'s tiling, decided by Daniel at 01:21Z: option (a), pre-tiled, only when FP8 PoUW is on.** The byte-realigning loader is dropped (X-H1T-12). The choice was: TMA can't place 29-byte runs, so the choice
   is between:
   - B′ stored pre-tiled with its tag rows: **+10.3% weight memory**, no latency cost, and a one-time re-layout;
   - a byte-realigning loader: +0.35 to 1.4 points of γ, which fails 16,384³.
7. **γ restated at measured prices** (Round 11): FADD for the 276–282-instruction step, HFMA2.MMA, HADD2, and the
   IMAD.MOV Phase 19c found uncounted (X-H1T-11).

### Not adopted

- **The budgeted P2′ as a registration gate.** Daniel did not adopt it (01:21Z). Both reviews advise against it (strike X-H1T-S8; Phase 19c X-H1T-2 and
  X-H1T-12).
  - It doesn't bound branching.
  - Its real-weight figures were computed on H-1R's layout.
  - β = 1% would reject Qwen2.5-0.5B's tied LM head, which is a liveness failure.
- **§6's claim that four tag lanes remove the cross-column obligation** is false (X-H1T-6).

### Confirmed

- The 4T − 3 credit is right, tight and conservative (strike X-H1T-S6; Phase 19c X-H1T-10).
- f_a = 297.6 and the step's SASS reproduce (X-H1T-11; the frontier strike's G.8).
- The branching prover and the tag tuples are not a function-level break.

### What happens next

- **Round 11 goes to root** now that the verdict is in, once its restage (bc-f2500633) lands. It adds SEL, SHFL, LDS
  and predicated-issue rows.
- **The Lean worker (bc-5382063c) starts M2** on `DistinctLiveH1T` with Phase 19c's 9 changes, the multi-slice argument
  and the half-ulp lemma. R1 (bc-1114588c) reviews the F6 correction together with the `check.sh` records.
- **Track H:** X-H1T-4 (decision 5), X-H1T-12 and X-H1T-13 (tiling and permutation, a ruling for Daniel), the tuple wrap
  past 88,412 columns, and the enlarged branching figure.
