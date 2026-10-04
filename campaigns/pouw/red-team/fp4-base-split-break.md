---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `tt-out/fp4-sm120`: D. Spike-saturated rows make the "salt-live but unchanged" part pay

30 Sep 2026, 11:55Z. Independent assessor (bc-d7d4b0d1). This supersedes the C ↑ of 11:30Z (`fp4-ttout-family.md`) for `tt-out/fp4-sm120` and its tile twin.

## The part of TT_OUT-FP4 this breaks

TT_OUT-FP4 carries, by conjecture, "savings from codes that are salt-live but happen not to change between salts (the base split's probable structure), which D-NF makes dense and the census measures at a 1.000× tie". D-SK makes the split two-sided: A′·B̃ᵀ = A0·B0ᵀ + ΔA·B̃ᵀ + A0·ΔBᵀ, with both corrections paid. The tie holds when A0 is a dense operand whose product costs a full GEMM. **Rows that make A0 low-rank and ΔA 2:4 break the tie.**

## The family (A's rows; B's rows can be anything, e.g. the census's gaussian)

- **Background:** N(0, 1) on every position, so ρ (every 8th position) is the background's RMS.
- **Spikes:** 14 per 16-block, on every offset except 0 and 8 (the every-8th positions ρ samples), at S·ρ with S = 8.9, under the 9.5ρ screen.
- **Signs:** r_i · c_b, a row sign times a block sign, both the adversary's choice.

## Measured on the reference (`pearl_c4`, NVFP4, k = 8,192; `fp4_base_split_attack.py`, `r20260930-114321-c379`)

| Check | Result |
|---|---|
| admission (`row_passes`) | 8 of 8 rows (A and B) |
| D-24 windows on A′; D-SS spread; scale bytes | 0; within; within |
| spike codes at E2M1 ±6 | **99.85%** |
| codes changed between two salts: spikes / sampled positions | **0.26%** / 47% |
| `salt_dead`, spikes and samples | 0 and 0, since every spike is salt-live under the worst-case support |
| **`tile_debit` on a 4 × 4 tile** | **0 units: every term 0** (2:4, D-24, identity atoms, sub-grid, dead pairs, forming) |
| modal block-scale share on A | 0.90 |
| ΔA = A′ − A0 (A0: ±6 on the spikes with the planned signs, 0 elsewhere) | 9.1% dense; **2:4-compatible in 99.99% of 4-groups** |
| the chain (`pearl_c4.chain`) against the exact rational sum | **equal on 16 of 16 words** (`ExactRun`) |

With both A and B spike-saturated, the debit is 4.3% of chain credit (identity atoms from cancelling atoms, `r20260930-114145-5222`). So B is left unshaped.

**The sparse instruction is real on this card** (`fp4_sparse_rate_sm120.cu`, `r20260930-114658-dc1c`). `OMMA.SF.SP.168128` (m16n8k128, 2:4) issues at the dense `OMMA.SF.16864`'s rate, 2,021 against 2,028 useful products per SM per clock. So a 2:4 operand costs 0.5 per logical MAC, as W1 prices it.

## The program and its price (units: one dense NVFP4 MAC)

The chain words are exact, so C̃_ij = Σ_b s_A,b(i) s_B,b(j) Σ_t A′ B̃ = A0-part + ΔA-part, exactly.
- **The ΔA part:** ΔA·B̃ᵀ on `OMMA.SF.SP` (ΔA is 2:4 with A′'s own block scales), **0.5 per MAC**. The 0.01% of 4-groups with three nonzeros go to a dense patch.
- **The A0 part:**
  - A0 = 6 · r_i · c_b · s_A,b(i) on the spikes. Where s_A,b(i) is the row's modal byte, the part is 6 · s_mod · r_i · u_j, with u_j = Σ_b c_b · s_B,b(j) · (B̃'s spike sum in block b), one per column: n·k/16 work, and a rank-1 outer product.
  - Blocks off the modal byte add a correction per word of Σ over those blocks of 6 r_i c_b (s_A,b(i) − s_mod) · s_B,b(j) · w_jb, in exact integer arithmetic on the CUDA cores. At about 40 FP4 units per term that is **about 0.25 per MAC at 90% flatness,** and about 0.08 at 97%.
  - Combining the parts is exact in int64, since the chain word is FP32-representable.
- **Paid in full:** forming (f_s ≈ 107 per element, needed to find the 0.15% of spikes that deviate), the fused A′·F_B and the peel. Together about 5% of credit at 8,192³.

**Total: about 0.05 + 0.95 × (0.5 + 0.08–0.25) ≈ 0.60–0.76 of creditOf,** on admitted tiles with zero debit. That is **a saving of 24–40% against γ₀ = 0.25%.**

## Rating

**`tt-out/fp4-sm120` and `tt-out-tile/fp4-sm120`: D** (derived from components measured on the reference, with a zero-debit tile and exact chains). An end-to-end kernel is the confirming run and isn't built. It would run the sparse `OMMA.SF.SP` product, the rank-1 part and the integer corrections, and compare the words.

The weaker candidates inherit the break wherever they keep the chain's credit:
- **`tt-out-chain/fp4-sm120`: D.** It credits the chain.
- **`tt-out-u/fp4-sm120`: D.** U includes C̃.
- **`tt-out-hot/fp4-sm120`: D ↓ (not re-checked).** Its hot start changes exactness, which may block the exact decomposition. Check `ExactRun` on the hot chain.
- **`no-base-split/fp4-sm120`: D.** The split pays when A0 is low-rank and ΔA is 2:4.

**Not affected:** the ρ_D proof, which is about debit coverage under the support definition, and is exactly why these rows carry no debit.

**What would close it:**
- **(a)** a probabilistic salt-deadness in the debit: charge codes that change between salts with probability below some ε under the real noise law, not the worst-case support;
- **(b)** a noise floor relative to each block's maximum, not the row's ρ, so near-max elements are noise-live;
- **(c)** a limit on near-max elements per block.

(a) is the most direct: these rows' spikes change on 0.26% of draws.

## Update 13:05Z: the end-to-end replay confirms the break and corrects its size to about 13–24% (measured on CUTLASS), with an instruction-bound ceiling near 46%

**What ran** (node 2, preemptible fill on GPU 4 under the 12:07Z booking; evidence `r20260930-123239-db11` for the build and operands, fill outputs in `/workspace/pouw/fill-out/assessor-basesplit-e2e/`, to be preserved as an Attempt):
- **Operands on the exact reference** (`basesplit_e2e_rows.py`, tree `bfd950d8`, NVFP4, 256 A rows × 256 B rows, k = 8,192), for two families:
  - `gauss`, the 11:55Z rows;
  - `flat`, the same spikes with pinned ρ and a row-max entry.
- **The device driver** (`basesplit_e2e_sm120.cu`, CUTLASS 4.8, sm_120a): dense block-scaled NVFP4 for honest (`OMMA.SF.16864`), and 2:4-sparse for the residual (`OMMA.SF.SP.168128`), both with FP32 or BF16 words. Every output is poisoned (0xA5) before its launch, and the negative control launches nothing.
- **The exact check:** `basesplit_e2e_check.py`.

**On the exact reference, every row is admitted and the split holds exactly:**

| | gauss | flat |
|---|---|---|
| admitted A / B | 256 / 256 | 256 / 256 |
| D-24 windows, spread, scale bytes | 0, ok, ok | 0, ok, ok |
| modal block-scale share on A | 0.925 | **0.9994** |
| spikes at the predicted ±6 | 99.94% | 99.98% |
| holes; pair-rule patches | 0; 19 elements | 0; 64 elements |
| defect blocks (off the row's modal scale) | 7.5% | **0.06%** |
| tile debit on two 8 × 8 tiles (of 524,288 credit units) | 64 and 0 (≤ 0.012%) | 13,632 and 13,632 (**2.6%**: the screened row-max block's forming and 2:4 terms) |
| A0 + ΔA = A′; fast A0 part (rank-1 + corrections) = A0·B̃ᵀ | exact | exact |

**The honest words on the device are exact** (poisoned, negative control rejected), on both families and both dense tiles:
- 65,536 of 65,536 words at 256 × 256 × 8,192 equal the exact sum;
- 16 of 16 sampled words equal the pinned chain (`pearl_c4.chain`);
- 4,096 of 4,096 sampled words at 8,192³ and at 16,384³ equal the exact host sum.

So the chain is exact on these rows, and any exact computation of A0·B̃ᵀ + ΔA·B̃ᵀ reproduces the honest words.

**Timing** (6 rotated reps per size, locked at 2,077–2,100 MHz, the power-cap reason in 25 of 954 samples; ms per GEMM):

| | dense, FP32 words | dense, BF16 | sparse, FP32 | sparse, BF16 | sparse/dense, FP32 | **sparse/dense, BF16** |
|---|---|---|---|---|---|---|
| 8,192³ | 0.8026 | 0.7788 | 0.6895 | 0.6128 | 0.859 | **0.787** |
| 16,384³ | 7.789 | 7.119 | 7.83 | 5.188 | 0.96–1.02 | **0.72–0.73** |

- Dense BF16 at 8,192³ (0.7788 ms) matches the panel's CUTLASS NVFP4 divisor (0.78875 ms) to 1.3%.
- **The whole sparse GEMM doesn't reach the instruction's 2×:** a 2:4 operand costs 0.73–0.79 of dense at the kernel level, not 0.5. The dense B̃ operand and the epilogue keep their full cost.
- With FP32 words written out, the saving nearly vanishes at 16,384³.
- Folding a materialized C (the rank-1 part) into the epilogue at beta = 1 costs 0.87 (BF16) and 0.97 (FP32) of dense at 8,192³.
- CUTLASS's standalone 2:4 compressor costs 0.23 ms at 8,192² (0.94 ms at 16,384²). A prover that forms A′ can write ΔA already compressed, so the compressor isn't charged. It is an upper bound only.

**The split's price, corrected** (the GEMM is 0.95 of credit, the rest is paid in full):

| Program | GEMM part | Total, of creditOf | Saving |
|---|---|---|---|
| **flat, fused rank-1 epilogue on the measured sparse kernel, BF16-class output** | 0.787 (8,192³) / 0.73 (16,384³), ÷ (1 − 2.6% debit) | **0.82 / 0.76** | **18% / 24%** |
| gauss, same program | 0.787 + 0.075 corrections | 0.87 | 13% |
| instruction-bound sparse kernel (0.5), flat | 0.5 ÷ 0.974 | ≈ 0.54 | ≈ 46% |
| residual materialized in FP32, then combined | 0.86 / ≈ 1.0 | ≥ 0.87 / ≈ 1 | ≤ 13% / ≈ 0 |

- **The break is confirmed.** It rests on:
  - the exact split, now on the device's own honest words;
  - a measured sparse GEMM at 0.73–0.79 of dense.
- **Measured size: 13–24% of honest** (CUTLASS today), against the 11:55Z derived 24–40%. The derivation took the instruction's 0.5 as the kernel's price; the whole GEMM doesn't reach it.
- **A fix must close the ceiling, about 46%** (a sparse kernel at the instruction bound, with the flat family's corrections at 0), not only the 13–24% an off-the-shelf kernel shows.
- **The best form of the attack is the flat family.** Flat scales make the rank-1 correction vanish, and they cost 2.6% debit, from the one screened block per row.

**What is not yet verified:** the sparse kernel's words.
- CUTLASS 4.8's sm_120 NVFP4 sparse path (compressor + kernel, driven exactly as example 80b drives it) gives wrong words on every operand pattern tried:
  - the split's ΔA (correlation 0.98 with the exact residual, but never bit-equal);
  - random two-pair and one-pair 8-chunks;
  - all six fixed pair placements.
- No pair permutation explains the error.
- **80b's own `verify()` compares the reference with itself** (`TensorEquals(block_reference_D, block_reference_D)`), so the example has never checked this path.
- Its timing is a throughput measurement of a kernel doing its full 2:4 work (tensor-core time doesn't depend on values), but **under the timed-row rule the sparse rows don't count yet**: their poisoned-output check REJECTs, though every negative control is rejected as it should be.
- Closing this needs a correct compressor, or hand-written metadata per the hardware's measured nibble rule (`r20260930-092605-fdc9`).
- The dense rows meet the rule.
