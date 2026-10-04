---
id: 20261004T2202Z-report-relay-docs-pouw-hardness-shaped-matrices
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/pouw/hardness-shaped-matrices.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/pouw/hardness-shaped-matrices.md`, sha256 `bec84155542383ea0f60ec8bb2bfd2ccb05785a133bf877db7c8f21cc2e9ed65`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Hardness-shaped matrices for PoUW

Track H, 28 Sep 2026, 17:46–22:00Z. It answers Daniel's draft (`internal/pouw/hardness-training-draft.md`): can we
require the model's matrices to have properties that make matmuls hard to shortcut, and use that for PoUW? CPU only;
no GPU was used.

**Status.**
- **H-1 as first posted: NO-GO.** The consolidated verdict is `internal/pouw-fp8/redteam-h1.md`. Its class admits four
  families of duplicate or absorbed words.
- **H-1R, one salted tag lane: superseded.** It closes three families. It does not close X-H1-S1 against a prover that
  reads the unit's tags once: 23% of words at every frontier k.
- **H-1T, this document: three tag lanes with a fixed injective tuple per column.**
  - It closes all four families at function level, for every finite B′, on the whole frontier (2,048 … 32,768),
    with no weight clause.
  - It is posted for re-review in `internal/pouw-fp8/genuine-fp8-interface.md` §2.1.H.
  - The working files are in `internal/pouw/hardness/` (its `README.md` lists them).

Tags: **Measured** (a run on this VM), **Simulated** (bit-exact emulation of the Hopper atom, not a proof),
**Compiled** (ptxas 12.9.86 SASS for sm_90a, not timed), **Derived** (a calculation), **Assumed** (a named hypothesis).

## Headline

- **No pairwise weight clause closes X-H1-S1 while real weights pass** (Measured, every column pair of every slice,
  `h1_clauses.py`). The provable form of P2′ fails:
  - Qwen3-8B q_proj at k = 4,096 on 553 of 1.1·10⁹ pairs, in every slice;
  - Qwen2.5-72B q_proj at k = 8,192 on 1,401 of 8.9·10⁹ pairs.

  The strike's weaker form fails 40 and 44 pairs there. Nearly all failures are in the −b form (w_j ≈ −w_j′), so the
  sign-separation clause rejects real weights at full shape too.
- **H-1T closes all four families without a clause.**
  - **The construction:** each k32 slice has 29 real lanes and 3 tag lanes. B′ carries a fixed tag tuple per
    column: injective, and with t₀ > 0. Each tag lane's activation is salted: v = ±32F(1 + m/8).
  - **Separation:** any two words of one row and slice have a tag lane where their tags differ by at least 4.
    Flipping that lane's salt sign moves their difference by at least two sum cells, so they are equal on at most half
    the salts, independently per row.
  - **Absorption:** flipping tag lane 0's salt sign moves every word by at least 960, and ulp(R) ≤ 512 up to
    k = 32,768 for any B′.
- **Measured at every frontier k** (Simulated on the bit-exact atom, full k, 24 salts): ε = 0 on the credited words
  for all four families.

  | Family | Posted H-1 | H-1R | **H-1T** |
  |---|---:|---:|---:|
  | X-H1-S1, shared loud lanes (n = 2,048 columns) | 49.8–58.9% | 22.9–23.0% | **0** |
  | F19-2, real columns and their twins | 16.7–17.2% | 0 | **0** |
  | b and −b, real columns, A = 0 | 25.1–25.9% | 0 | **0** |
  | Absorption: the strike's P4-threshold slices / an all-448 worst case | 22.6–25.0% / 93.8% | 0 / 0 | **0 / 0** |

- **The credit drops two words, for every exact two-block design (posted H-1 included):**
  - R_2T is the useful output, salt-free up to rounding;
  - R_(2T−1) equals I1_T whenever A is 0 on the first T − 1 slices.

  So 4T − 3 words are credited per output, not 4T − 1. This corrects the shared γ accounting.
- **What stays open is the branching gap, and only for adversarial B′.**
  - Under S1-type weights, 14-bit words can't keep n > 2^13 columns distinct on one salt. That gives 29–32%
    same-position coincidences per salt at every k, and 12 salt bits per (row, slice) decide which.
  - Real columns give 1.2%, decided by every salt bit.
  - Function-level ε is 0. A prover that branches per (row, slice) on those 12 bits is the named gap.
- **Quality** (Measured, paired per-window deltas, ± one standard error; §4):
  - Qwen2.5-0.5B on WikiText-2: **−0.24% ± 0.16** against the model's FP8.
  - Qwen2.5-0.5B, C4: +0.08% ± 0.17 (+0.31% ± 0.16 against FP8 at 416); Qwen2.5-1.5B, WikiText-2: +0.92% ± 0.36 (+0.02% ± 0.45 against FP8 at 416); Qwen2.5-1.5B, C4: −0.08% ± 0.38; Llama-3.2-1B, WikiText-2: +0.41% ± 0.17 (+0.16% ± 0.14 against FP8 at 416); Llama-3.2-1B, C4: +0.05% ± 0.16.
- **γ from compiled SASS** (f_a = 297.6 per real element at Round 10's measured prices):
  - The honest step's loop is under the fetch knee and bank-clean, so FADD is taken at 32.00.
  - 32.05 and 32.11 are the sensitivities.

  | Credit 4T − 3 | 2,048³ | 4,096³ | 8,192³ | 16,384³ | 32,768³ |
  |---|---:|---:|---:|---:|---:|
  | γ₀ = 1/400 | 4.11% | 2.21% | 1.24% | **0.75%** | **0.50%** |
  | γ₀ = 0 (the Lean target) | 3.87% | 1.96% | **0.99%** | **0.50%** | **0.25%** |

- **P4 at the frontier edge** (Measured, real matrices at their own k):
  - P4 + 2 bits fails on Llama-405B's down_proj at k = 32,768: −0.06 bits, on 4 of 8.7·10⁶ column-slices.
  - It passes at 29,568 (+0.08) and 16,384 (+1.03).
  - The L1 form passes, with +1.00 bits at 32,768.
  - H-1T needs neither.

## For Daniel: decisions

**Decided** (28 Sep):
1. The registration check on committed weights: **adopted** (19:52Z). Under H-1T no weight clause is needed for
   function-level DistinctLive. What remains of the check is the legal-input clause (finite codes), plus the branching
   budget if decision 3 chooses it.
2. **Two blocks** (19:52Z).
3. **The hybrid floor**, c0 = 6 and c1 = 10 (19:52Z).
4. **X_q is the target.** Y16 is a comparison row only (19:54Z).
5. **Pursue a Lean proof of DistinctLive(0)**, which would drop γ₀ = 1/400 (19:54Z). γ is reported both ways.
6. **The frontier is 2,048, 4,096, 8,192, 16,384 and 32,768;** 65,536 is dropped (20:43Z).
7. **No weight copies of any kind** (20:33Z). H-1T stores no copy: see decision 8.
8. **B′ is stored once, pre-tiled with its tag rows** (Daniel, 29 Sep 01:21Z): +10.3% weight memory, a one-time
   re-layout, no copy. It applies only when FP8 PoUW is switched on and is never a default. The byte-realigning
   loader (tag rows written by the tile loader, 29-row groups) is dropped.
9. **The optional β = 1% registration gate (budgeted P2′) is not adopted** (Daniel, 29 Sep 01:21Z). The branching gap
   stays a named gap.

**Open, for Daniel or the red team:**
1. **Adopt H-1T instead of H-1R.**
   - **The cost:** 3 tag lanes per 32, so 2 × 32/29 = 2.21× the tensor work of one FP8 GEMM per useful MAC
     (H-1R: 2.06×).
   - **The forming:** 297.6 units per real element, against 282.9 for H-1R.
   - **γ improves slightly:** 0.747% against 0.759% at 16,384³, because the credit scales with the atom count.
   - **Recommended: adopt.** It is the only variant whose function-level result survives a prover that reads per-unit
     salt.
2. **F19-3's literal fix** (μ = 2F at |x| = F).
   - **Not needed under H-1T:** the separation argument uses only the tag lanes, so a real lane with x1 = 0 changes
     nothing.
   - **Its cost:** two ops per register, +66 per element (f_a 363.8), which is +0.09 points at 16,384³.
   - The GPU worker's 340.2 per element for "the §3.1 map" includes it; without it, the same map is 282.9 (H-1R) and
     297.6 (H-1T) at the same prices.
   - **Recommended: pin the map without it.**
3. **The branching gap.** Decided (decision 9): the β gate is not adopted. The two options were:
   - Carry it as a named gap: function-level ε = 0, and a per-(row, slice) branching prover is outside the model.
   - Bound it at registration with a **budgeted P2′**: reject a matrix if more than β of its column-slices are in
     pairs failing the provable P2′.
     - Real weights: 0 (Qwen2.5-3B, and two 0.5B layers), 0.13% (72B q_proj), 0.15% (Qwen3-8B q_proj) and 0.61%
       (0.5B layer-0 q_proj).
     - S1-type weights fail on every column-slice.
     - β = 1% admits every real matrix measured, and caps the S1 exposure at about β × 32%.

   **Recommended:** carry it as named, and adopt β = 1% as defense in depth. The check costs about one GEMM per matrix,
   once.
4. **The tag rows are a deployment requirement** (the §0 rule). Decided (decision 8): B′ pre-tiled once, and the
   loader option below is dropped.
   - B′'s k32 tiles hold 29 real rows and 3 tag rows. The tag rows are a function of the column index, so they need
     no storage: the tile loader writes them into shared memory, at 3 bytes per column of table.
   - But B′ and X_q are read in 29-row groups. That is a nonstandard tiling for the loader, with no memory cost (or
     +10.3% memory if B′ is pre-tiled instead).
   - LM heads with more than 88,412 columns are split into units of at most that size, or given a fourth tag lane.
5. **The headroom** (X_q at amax/416). It is now also load-bearing for security at k = 32,768: it keeps |R| below 2^33
   for every B′. Its quality cost is in §4.

## 1. What the affordance can and cannot do

**The game on the H100.** By `distinctWritesMH100` (proved, under H32), every program pays at least 32 per checked
word that is distinct and not free. The honest reference pays 32 per atom word and FADD's class price per running word.
So:

~~~text
γ = 1 − (1 − ε)·c / W_ref      c = 32 per credited word;  W_ref = the honest's per-word prices + online forming
ε = the share of credited words that are free (salt-independent) or duplicates  (DistinctLive(ε))
~~~

A design helps only by lowering ε or lowering forming. Rank and linear independence don't enter, because `MH100w`
prices every register write at 32 or more.

**Why the activation side keeps its noise** (Derived, from Theorem B0). At A = 0 the useful output is known, so any
word whose salt dependence runs only through A is free. On-grid activations absorb any dither below half an E4M3 cell.

**Why the weight noise can go, and why the dither can be exact.** With noise on one side only there are no NCP cross
terms, so two blocks suffice. The dither sits on the E4M3 grid, and x = x1 + x2 exactly on non-floor lanes, so the
useful output carries no noise.

**Why real weights cannot carry the column separation** (Derived; X-H1-S1 and F19-2 are the instances).
- Every column reads the same activation operand, and the atom truncates each sum to 14 significant bits.
- If shared loud lanes set the cell, every real difference between columns can sit below it on every salt.
- A clause that forbids this lane by lane is refuted on real weights by the all-pairs runs above.
- So the separation has to reach each column through its own weight operand, with salt on the activation side.
  That is the tag lanes.

**Why one tag lane is not enough.**
- **Per-unit salted tags (H-1R):** a prover reads a unit's tags once, groups the columns whose tags coincide, and
  copies. That is 23% under S1.
- **Fixed tags:** the tag must be injective across the unit's n columns. One E4M3 lane can't be: at most 46 codes keep
  the two-cell spacing.
- **Three lanes:** they give 23 × 62 × 62 = 88,412 tuples with the needed spacing, each lane salted separately.

## 2. Which matrix properties matter (question 1)

| Property | What it guards | Role under H-1T | Real weights (all pairs) |
|---|---|---|---|
| Full rank, global incoherence | nothing on the H100 | none | — |
| Finite codes (no 0x7F / 0xFF) | NaN words | **legal-input clause** (audit) | pass |
| P0, no all-zero k32 slice | free words | not needed: the tag terms make every word salt-dependent | pass |
| P1(7, 16), anti-concentration | legacy k8, row-pattern entropy | not needed for function level; supports the branching argument | pass (min 16 lanes) |
| P2′, provable (one lane whose flip moves the pair by two cells of the largest legal sum), ± forms | S1, F19-2, b/−b | **not needed**; its budgeted form is the optional branching bound | **fails** at 4,096 and 8,192 (above) |
| P2′, the strike's form | S1 | not needed | **fails**: 40 pairs at 4,096 and 44 at 8,192 |
| P4 + 2 bits (L2) | absorption | not needed | passes to 29,568 (+0.08 bits); **fails** at 32,768 (−0.06) |
| P4′, L1 form | absorption | not needed | passes at every k (+1.00 bits at 32,768) |
| P3, exponent spread per k16 half | the 4090's integer-grid routes | 4090 only | 8–9% narrow halves |

**Real-weight measurements** (Measured, `h1_clauses.py` → `clauses-real-weights.json`; the matrices come from
`h1_fetch.py`, one real tensor per frontier k by HTTP range requests, per-column max scaling to 448):

| k | Matrix (n) | P2′ provable: failing pairs (share of column-slices) | P2′ strike | P4 as posted / +2 bits / L1 (min margin, bits) |
|---:|---|---|---|---|
| 896 | Qwen2.5-0.5B layer-0 q_proj (896) | 118 of 1.1·10⁷ (0.61%) | 4 | +7.54 / +5.54 / +6.44 |
| 896, 4,864 | Qwen2.5-0.5B gate (4,864) and down (896) | 0 (min +1.1 bits) | 0 | ≥ +7.26 / +5.26 / +6.43 |
| 2,048 | Qwen2.5-3B layer-18 q_proj (2,048) | 0 of 1.4·10⁸ (min +1.3 bits) | 0 | +6.21 / +4.21 / +5.29 |
| 4,096 | Qwen3-8B layer-18 q_proj (4,096) | 553 of 1.1·10⁹ (0.15%) | 40 | +5.04 / +3.04 / +4.21 |
| 8,192 | Qwen2.5-72B layer-40 q_proj (8,192) | 1,401 of 8.9·10⁹ (0.13%) | 44 | +4.06 / +2.06 / +2.98 |
| 16,384 | Llama-3.1-405B (Hermes-3) layer-63 q_proj (16,384) | not run (cost) | not run | +3.03 / +1.03 / +2.05 |
| 29,568 | Qwen2.5-72B layer-40 down_proj (8,192) | not run | not run | +2.08 / **+0.08** / +1.04 |
| 32,768 | Llama-3.1-405B layer-63 down_proj, k truncated to 32,768 (8,192) | not run | not run | +1.94 / **−0.06 (4 slices)** / +1.00 |

## 3. H-1T: the construction

### 3.1 The pinned forming map (F19-4)

There is one map, and the kernel computes it: `h1_tagged.h1t_ref`, bit for bit (`h1t_form_xq` in `h1_kernel.py`).

~~~text
layout     each k32 slice = 29 real lanes + 3 tag lanes (29, 30, 31); T = ceil(k/29); X_q holds 0 on tag lanes
input      X_q  finite E4M3 codes of A at per-row scale amax/416 (so |x| <= 416), committed before the salt
           B'   registered finite E4M3 weight codes (offline, per-column scale); its tag rows are fixed (below)
real lanes M  = max |x| over the slice's 29 real lanes
           F  = max(2^(e(M) − 6), 2^−2)                           c0 = 6, c1 = 10
           p  = 2^floor(log2 |x|)  (p = 0 at x = 0)              p/8 is the E4M3 step of every normal code
           mu = max(p/8, F)
           s  = ±1, one salt sign per lane
           x1 = RNE_satfinite(x + s·mu),  x2 = −s·mu              x + s·mu computed in f16 (exact for every code)
tag lanes  v_i = s_i · 32F · (1 + m_i/8),  s_i = ±1 and m_i in 0..7 from the salt, one per tag lane i = 0, 1, 2
           x1 = v_i,  x2 = −v_i                                     exact: X_q is 0 there
tag rows   column j of B' carries, in every slice:
           t_0 = A0[j mod 23]          A0 = +[64, 448]    the 23 positive E4M3 codes 0x68..0x7E (spacing >= 8)
           t_1 = A1[(j div 23) mod 62] A1 = ±[32, 448]    the 62 codes 0x60..0x7E and 0xE0..0xFE (spacing >= 4)
           t_2 = A1[(j div 1426) mod 62]                  injective for n <= 88,412 columns per unit
chain      I_tau = HOPPER_E4M3_K32(+0, x_b[S_tau], B'[S_tau]),  R_tau = RN_f32(R_(tau−1) + I_tau)
           order: block 1 (x1) over every slice, then block 2 (x2); R_1 = I_1 is not a separate word
credited   I_1 .. I_2T and R_2 .. R_(2T−2): 4T − 3 words per output; the useful output is R_2T ≈ X_q·B'
salt       per slice, raw XOF words r0..r17: bits 15 and 31 of r_i are the signs of real lanes 2i and 2i + 1
           (i <= 14; lane 29 is a tag); r16 bits 15, 9..7 / 31, 25..23 are (s, m) of tag lanes 30 / 31; r17 bits
           31, 25..23 are (s, m) of tag lane 29
~~~

- **Exactness:** on non-floor lanes x1 + x2 = x for every code and both directions. On floor lanes the error is at
  most F/2.
- **The tags cancel exactly** between the two blocks, so the useful output is H-1R's with 29-lane slices.
- **The bit-exact atom agrees with the algebraic screen** (Measured, `h1_groupsum_tagged.py`, five Qwen2.5-0.5B layers
  on real activations): H-1T through `HOPPER_E4M3_K32` equals its algebraic value to at most 2.7·10⁻⁴ relative. The
  output errors are 2.7–3.7%. The exception is layer 2's `down_proj`, Qwen's massive-activation layer (Track B's
  cross-check, below): 5.2·10⁻⁴, in the sink row, which is at most 1.7% of that layer's error.
- **The chain order is load-bearing.** Interleaving the blocks would make R after each block-2 atom equal R two steps
  earlier at A = 0.
- **Legal inputs, checked at audit:**
  - every X_q and B′ code is finite;
  - |x| ≤ 416 on X_q (the headroom; the absorption bound at k = 32,768 uses it);
  - on the Y16 comparison row, finite f16 with |y| ≤ 416 (the strike's |y| < 464 suffices for freeness, and 416 keeps
    the map exact), with the f16 intermediate pinned.

### 3.2 Why it separates, for every finite B′ and every legal X_q (Derived)

~~~text
cell    every sum is below 128F·29·448 + 3·60F·448 < 2^21·F, so its 14-bit cell is at most 128F
flip    flipping s_i changes the tag product by exactly 2·v_i·t_i (products are exact on the atom's grid, and the
        sign does not change the nominal exponent), and changes no real-lane product
~~~

- **Two words of one row and slice, different columns, same block.** Their tuples differ in some lane i by
  |Δt| ≥ 4. Flipping s_i changes their difference by 2|v_i|·|Δt| ≥ 256F: two cells. Equal words differ by less than
  one cell, so at most one of the two salts makes them equal.
- **Block 1 against block 2, any columns (b against −b included).** The tag terms are +v·t_j and −v·t_j′. Flipping s₀
  changes the difference by 2|v₀|(t₀,j + t₀,j′) ≥ 2·32F·128, since t₀ > 0 always.
- **Different slices, or an I word against an R word.** Flipping a tag sign of the later slice changes only the later
  word, by at least 2·32F·64 − 2 cells > 0.
- **Absorption (R_τ = R_(τ−1)).**
  - Flipping s₀ of slice τ moves I_τ by at least 4,096F − 2 cells ≥ 960 (F ≥ 1/4).
  - With |x| ≤ 416 (so x1 ≤ 448), |I1_τ| + |I2_τ| < 6.9·10⁶ per slice. So for k ≤ 32,768 (T ≤ 1,130),
    |R| < 2^33 and ulp(R) ≤ 512.
  - Two absorbed values differ by at most 512, so at most one of the two salts is absorbed.
- **Free words:** none. Every credited word moves under some tag flip.
- **Rows have independent salts,** so a copy that is right on at most half of each row's salts is right on every row
  with probability at most 2^−m.
- **Not covered by the one-flip argument:** R words of two different columns at the same τ, when the tuples differ
  only in lanes 1–2 at a quiet slice and R is large. The flip there moves the difference by 256F ≥ 64, below ulp(R).
  Simulation finds 0 such equalities at every k. The targeted run (`h1_tagged_rcheck.py`) also finds 0: identical
  registered columns whose tuples differ only in lane 1, under a loud aligned row on the first half of the slices and
  0 or F after, with real and all-448 weights at k = 32,768. The Lean proof has to carry it through the chain (a
  proof obligation named in §5.3).

### 3.3 The registration class

- **For the Lean Target A** (function-level DistinctLive(0)): every finite B′. No weight clause.
- **Legal inputs:** finite codes, and |x| ≤ 416.
- **For the branching gap:** the budgeted P2′ was considered and is not adopted (decision 9).

## 4. Projection cost and quality (question 2)

H-1T projects no weights: B′ is the model's own FP8 codes. Its quality cost is the floor lanes' rounding (at most F/2
per floor lane) and the headroom.

**Perplexity** (Measured, 512-token windows, the algebraic screen, which §3.1 shows is faithful; paired per-window
deltas, ± one standard error):

| Model, dataset (windows) | BF16 | FP8 at 448 (against BF16) | FP8 at 416 (against 448) | **H-1T** | **H-1T against FP8 at 448** | H-1T against FP8 at 416 | Floor lanes |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B, WikiText-2 (64) | 17.052 | 17.459 (+2.39% ± 0.15) | — | 17.418 | **−0.24% ± 0.16** | — | 33% |
| Qwen2.5-0.5B, WikiText-2, H-1R for reference | | | | 17.415 | −0.25% ± 0.16 | — | 34% |
| Qwen2.5-0.5B, C4 (32) | 19.477 | 19.923 (+2.29% ± 0.19) | 19.877 (−0.23% ± 0.18) | 19.938 | **+0.08% ± 0.17** | +0.31% ± 0.16 | 34% |
| Qwen2.5-1.5B, WikiText-2 (32) | 11.550 | 11.657 (+0.92% ± 0.46) | 11.761 (+0.90% ± 0.44) | 11.764 | **+0.92% ± 0.36** | +0.02% ± 0.45 | 32% |
| Qwen2.5-1.5B, WikiText-2, H-1R for reference | | | | 11.796 | +1.20% ± 0.38 | +0.30% ± 0.33 | 32% |
| Qwen2.5-1.5B, C4 (32) | — | 15.275 (—) | — | 15.263 | **−0.08% ± 0.38** | — | 33% |
| Llama-3.2-1B, WikiText-2 (32) | 12.497 | 12.674 (+1.41% ± 0.18) | 12.706 (+0.25% ± 0.14) | 12.726 | **+0.41% ± 0.17** | +0.16% ± 0.14 | 28% |
| Llama-3.2-1B, C4 (32) | 13.639 | 13.878 (+1.75% ± 0.32) | — | 13.885 | **+0.05% ± 0.16** | — | 28% |

- **Independently reproduced** by Track B (bc-876ca543), with its own implementation of §3.1 and its own seeds, over
  64 windows against its own FP8 at 448 (`internal/pouw-fp8/genuine-fp8-interface.md` §2.1.B, addendum 01:05Z;
  `internal/pouw-fp8/prototype/track_b_h1t_crosscheck.json`):
  - 0.5B WikiText-2: −0.24% ± 0.15;
  - 1.5B WikiText-2: +0.19% ± 0.24, and +0.68% ± 0.36 on the first 32 windows (this table: +0.92% ± 0.36);
  - 0.5B and 1.5B on C4 (different C4 text): −0.14% ± 0.25 and +0.15% ± 0.32.

  Every cell is within ±1% of FP8. Its bit-exact Hopper chain on real inputs keeps the error variance within 0.71%
  (0.5B) and 1.67% (1.5B).
- **Public randomness is not the way to enforce hardness.** A random one-step move of every weight code costs +22%.

## 5. Adaptivity and security (questions 3 and 4)

### 5.1 What can be forced on activations

- **Nothing by admission.** Any rule that rejects a committed A meets NE3's liveness obstruction.
- **By transformation, for every legal X_q:**
  - every real lane of both blocks is salt-dependent;
  - every move is at least 2^−6 of the slice max and at least 2^−2;
  - the tag lanes carry salt on both sides.
- **What must come from the weights: nothing,** for function-level DistinctLive. Column separation comes from the fixed
  tag tuples.

### 5.2 The attacks, on the frontier

Simulated with bit-exact `HOPPER_E4M3_K32` words (`h1_tagged.py` → `h1t-attacks.json`; 24 salts; every checked word of
every column, both blocks).
- **"ε"** is free or function-level duplicate words over the credited set.
- **"Per salt"** is the share of words equal, on one salt, to another column's word at the same position: what a
  branching prover reads.
- **Real matrices** are the §2 table's, used at their own k.

| Attack (k = 2,048 / 4,096 / 8,192 / 16,384 / 32,768) | Posted H-1 | H-1R | **H-1T** | H-1T per salt |
|---|---|---|---|---|
| **X-H1-S1**: 16 shared loud lanes at 448 and quiet pattern lanes, x = F there (n = 2,048) | 49.8 / 49.9 / 49.9 / 50.0 / 58.9% | 23.0 / 22.9 / 22.9 / 22.9 / 22.9% (per-unit tags) | **0** | 31.9 / 30.6 / 29.2 / 28.9 / 28.5% |
| S1 with x = 32 / x = 0 on the pattern lanes | 17–18% / 4–5% | 10% / 1% | **0** | 29–31% |
| S1's baseline: real columns (n = 2,048), Gaussian row | 0 | 0 | 0 | 1.2% |
| **F19-2**: real columns and their twins (one lane per slice moved by 2^−7 of the slice max), the red team's row | 16.9 / 16.7 / 17.1 / 17.2 / 17.0% | 0 | **0** | 0.05–0.07% |
| **b and −b**: real columns and their negations, A = 0 | 25.9 / 25.4 / 25.2 / 25.1 / 25.1% | 0 | **0** | 0.1–0.4% |
| b and −b, a Gaussian row | 0 | 0 | 0 | 0.05% |
| **Absorption, X-H1-S3**: ½ of the slices at the tiny code that meets P4 with margin 0, A = 0 there | 22.6 / 25.0 / 24.9 / 24.9 / 24.9% | 0 | **0** | 0.01–0.02% |
| Absorption: ½ of the slices all-zero weights (no P4 at all) | 50.0% | 0 | **0** | 0.01–0.02% |
| Absorption: the worst case for the bound (every big lane at 448, ½ zero slices) | 93.8% | 0 | **0** | 0.5–1.0% |
| Absorption: real columns, a sign-aligned 416 row on the first half and 0 after | 0 | 0 | 0 | 0.01% |
| The structural pair at A = 0 (R_2T free, R_(2T−1) = I1_T) | 2/(4T − 1) | 2/(4T − 1) | 2/(4T − 1) | removed by the 4T − 3 credit |

- **H-1R's 23% under S1** is the per-unit tag read: its tags are salt per unit, so a prover sees them once and copies
  across rows. Over the full salt (tags included) its function-level ε is 0, which is why H-1R looked closed in the
  earlier post.
- **The branching exposure under S1** (29–32% per salt, 12 bits per row and slice) is not specific to H-1T. With shared
  loud lanes swamping every real difference, no design with 14-bit words and n > 2^13 columns can keep one salt's words
  distinct. The per-salt pattern depends only on the tag bits, so a prover that branches per (row, slice) could
  pre-tabulate 4,096 groupings per slice. Real columns give 1.2%, decided by all of a row's salt bits.

### 5.3 The statement

For the H100, under additive W1 at loop-free class prices (`distinctWritesMH100On`):

~~~text
γ(H-1T) ≤ 1 − (1 − ε)·32·(4T − 3) / (32·2T + p_FADD·(2T − 1) + f_a·k/n)      T = ceil(k/29), two blocks
~~~

It holds whenever three things do:
1. **H32 per class,** measured, with zero slack.
2. **`DistinctLiveH1T`** (Target A of `internal/pouw-fp8/lean-atom-scope.md`, restated):
   - The scope: every m, every k ≤ 32,768, every n ≤ 88,412 per unit, every legal X_q (finite, |x| ≤ 416) and every
     finite B′.
   - The claim: every two distinct credited words of one row are unequal on at least half of that row's salts, and no
     credited word is salt-free. Then ε = 0.
   - §3.2 derives this for I words, cross-block pairs, cross-slice pairs and absorption. **The proof obligation left
     is cross-column R words** (the last bullet of §3.2), which simulation finds at 0.
   - It is Assumed, with simulation evidence; the Lean proof is staffed. Until it lands, ε = γ₀ = 1/400.
3. **The named model gaps:**
   - **branching:** per (row, slice), 12 salt bits decide the S1 coincidences; optionally bounded by the budgeted P2′;
   - the lifting (Target B);
   - the hash as a random oracle;
   - completeness;
   - the untimed per-instruction rates (§5.4).

### 5.4 The forming kernel, compiled (question 4)

**The files:**
- **The kernel:** `internal/pouw/hardness/h1_kernel.py`, which emits `h1_kernel.ptx`: `h1t_form_xq`, `h1t_form_y16`,
  the superseded H-1R kernels, and `h1r_step`.
- **The SASS:** `h1_kernel.sass` is the ptxas 12.9.86 output for sm_90a.
- **The counts:** `h1-sass-counts.json`.
- **γ:** `gamma_h1t.py` → `gamma-h1t.json`.

**The build:** 40 registers and 0 spills. Each thread forms whole slices, so the slice max is thread-local. Loads,
stores and raw XOF words are free.

**The SASS per k32 slice, H-1T on X_q** (29 real lanes and 3 tag lanes):

| SASS | Per slice | Round 10 price | Source |
|---|---:|---:|---|
| `F2FP.F16.E4M3.UNPACK_B` | 16 | 64.17 | §16.4, measured |
| `F2FP.SATFINITE.E4M3.F16.UNPACK_B_MERGE_C` (the cast, no PRMT) | 32 | 64.64 | §16.4, measured |
| `HADD2` / `HMUL2` a·K / `HFMA2.MMA` | 10.5 / 9 / 12.5 | 36.01 / 32.17 / 60.4 | Round 9 / §15.9 / unmeasured, priced as HFMA2 |
| `HMNMX2` / `VHMNMX` | 22 / 5 | 64.13 / 66.50 | §16.4, measured |
| `LOP3.LUT` (no partner) | 37 | 64 | §15.9 |
| **Per real element** | | **297.6** | H-1R 282.9; Y16 263.8; with F19-3's fix 363.8 |

**The checked step, per m64n128k32 atom** (Compiled):
- **Its content:** one QGMMA, 64 FADD, one WARPGROUP.ARRIVE and one DEPBAR.
- **Loop size:** each block's loop is about 280 instructions, under Round 10's 390-instruction fetch knee.
- **Register banks:** each running sum takes its neighbour's accumulator, which leaves 0 of 512 FADDs with same-bank
  sources (register number mod 2). So FADD is priced at the measured 32.00.
- **Uniform-datapath instructions:** 5.1 per atom, uncounted, as in every track.

**γ from the compiled count** (Derived, `gamma_h1t.py`; credit 4T − 3; FADD 32.00, with 32.05 and 32.11 after the
slashes; FADD* is the FADD price at which γ = 1%):

| Cell | f_a | 2,048³ | 4,096³ | 8,192³ | 16,384³ | 32,768³ |
|---|---:|---:|---:|---:|---:|---:|
| **H-1T X_q, γ₀ = 1/400** | 297.6 | 4.11 / 4.18 / 4.27% | 2.21 / 2.28 / 2.37% | 1.24 / 1.32 / 1.41% | **0.75 / 0.82 / 0.92%** (FADD* 32.16) | **0.50 / 0.58 / 0.67%** |
| **H-1T X_q, γ₀ = 0** | 297.6 | 3.87% | 1.96% | **0.99%** (FADD* 32.006) / 1.07 / 1.16% | **0.50 / 0.58 / 0.67%** | **0.25 / 0.33 / 0.42%** |
| H-1T X_q with F19-3's fix, γ₀ = 1/400 | 363.8 | 4.78% | 2.56% | 1.42% | 0.84 / 0.91 / 1.01% | 0.54% |
| H-1T Y16 (comparison), γ₀ = 1/400 | 263.8 | 3.76% | 2.03% | 1.15% | 0.70% | 0.48% |
| H-1R X_q (superseded), γ₀ = 1/400 | 282.9 | 4.17% | 2.25% | 1.26% | 0.76% | 0.51% |
| For reference: H-1T with the old 4T − 1 credit, FADD 32.00, γ₀ = 1/400 | 297.6 | 3.42% | 1.86% | 1.06% | 0.66% | 0.46% |

- **16,384³ and 32,768³ clear 1%** at every FADD price and both γ₀.
- **8,192³ clears only with γ₀ = 0 at FADD 32.00,** with a threshold of 32.006: on the edge. Today's scheme is
  compared with the independent-tags candidate, with the seven decisions for Daniel, in
  [`h1t-scheme-decisions.md`](h1t-scheme-decisions.md).
- **2,048³ and 4,096³ fail.** Forming would have to be about 2/3 and 1/3 of an atom word per element.

## 6. Other candidates

- **H-1, as first posted: NO-GO.** Four families (`redteam-h1.md`).
- **H-1R** (one per-unit salted tag lane): **superseded by H-1T.** It closes F19-2, b/−b and absorption. Under S1 a
  prover that reads the unit's tags copies 23% of words.
- **H-1R + P2′:** the clause route. Real weights fail every provable form of P2′ at full shape (§2).
- **Four tag lanes (28 + 4):** tuples of four positive A0 codes remove the lane 1–2 proof obligation for cross-column R
  words (spacing ≥ 8 everywhere), for another 3.4% of tensor work. Not needed unless the Lean proof stalls there.
- **H-1P:** a fixed permutation between blocks, for the 4090's time model.
- **H-2:** D-3m's continuous activation noise over registered weights. H-1T dominates it on quality and price.
- **Hardness by random scrambling of weights:** +22% perplexity without retraining. Checking beats scrambling.

## 7. Open items, and what the red team should attack first

1. **The tag tuples.** Look for column, row or block pairs whose credited words coincide on every salt despite the
   tags. Cross-column R words at quiet slices after loud ones are the case §3.2 does not cover.
2. **The branching gap** under S1-type weights (12 bits per row and slice), and whether the budgeted P2′ should be
   adopted.
3. **The credit correction** (4T − 3). It applies to every exact two-block design, and the shared tables still credit
   4T − 1.
4. **The unmeasured rates:** HFMA2.MMA and HADD2 under ptxas 12.9. Round 11 would time `h1t_form_xq` and the
   bank-clean `h1r_step`.
5. **Quality:** the deployed kernel, and more windows on the headroom.
