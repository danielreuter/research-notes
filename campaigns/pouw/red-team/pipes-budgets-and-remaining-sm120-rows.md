---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# Pipes and budgets on sm_120, and the remaining sm_120 rows

30 Sep 2026, 09:30Z. Independent assessor (bc-d7d4b0d1). The rows:
- `concurrent-budgets/sm120` and `declared-hw/sm120`, from the pipe co-issue probe;
- `tt-out-aw/pearl-c-sm120-admission`, `memory-tiers/sm120` and `tc-model/sm120-e4m3-sp-k64`, and the two that can't be rated (`curated-weights/pearl-c`, `preprocessing/fixed-weights`), from evidence in hand.

## Pipe co-issue on one RTX PRO 6000 (`coissue_sm120.cu`, `r20260930-092215-0633`, GPU 6, locked at 2,092–2,100 MHz)

**Method.** Fixed per-iteration mixes, every SM, 16 warps per SM. Rates are counted per SASS instruction: ptxas folds pairs of dependent `add.s32` into one IADD3, which per-kernel SASS counts confirm. Shares are taken against the true per-pipe peaks: MMA 1,016 MACs; FFMA 128; `dp4a`, HFMA2 and IADD3 64 thread-instructions per SM per clock.

| Mix | Rates per SM per clock | Sum of shares |
|---|---|---|
| FFMA + `dp4a` | 43.4 + 43.4 | 1.00 (one pipe) |
| FFMA + IADD3 | 69.1 + about 36 | 1.10 |
| `dp4a` + HFMA2 | 30.0 + 30.0 | 0.94 |
| **`dp4a` + IADD3** | 55.5 + about 30 | **1.33** |
| MMA + FFMA (4 or 8 per MMA) | 898–812 MACs + 28–51 | 1.10–1.20 |
| MMA + IADD3 | 954 MACs + about 15 | 1.17 |
| MMA + `dp4a` (4 or 8 per MMA) | 848–742 MACs + 27–46 | 1.25–1.45 |
| MMA + HFMA2 | 928 MACs + 29 | 1.37 |

## `concurrent-budgets/sm120`: D if "generic ops" is one budget priced per op, B if it is counted in issue slots

The row says a computation takes at least its most-loaded budget's time (tensor MACs, generic ops, bytes per tier), all running at once.

- **Tensor against generic:** measured co-issue is partial (at most 1.45, against the model's allowance of 2), so the max model is generous to the adversary there. That part holds.
- **Inside "generic ops,"** the statement doesn't say how ops of different kinds add up:
  - **Priced per op at its solo peak** (W1's units: FADD 8.46, `dp4a` about 16 per instruction, ...), a `dp4a` + IADD3 program does 1.33 budget-seconds of generic work per second. It finishes in 0.75 of its most-loaded budget's time, which is a concrete break (**D**).
  - **Counted in issue slots** (at most 128 thread-instructions per SM per clock for all generic kinds together), every measured mix is within the budget (the most is about 105), and the model holds (**B**, GPU).
- **What the statement should say:** generic work counted in issue slots, or split into the FMA pipe (FFMA, `dp4a`, HFMA2) and the integer ALU pipe (IADD3, LOP3), each with its own budget.
- **Consequence for the MVP's r_g:** a generic-core GEMM gains at most the ALU pipe's share, since IADD3 does no multiplies. The `generic-core-rate/sm120` D is unchanged.

## `declared-hw/sm120` (A_max = 1): B (GPU) for the declared chip

- **The card's per-clock peaks hold as ceilings.** Every `mma.sync` kind and every scalar pipe is timed (`fp8-tile-rows.md`, `r20260930-060338-26b9`, `r20260930-091638-9747`). No kernel exceeded a pipe's peak: the gated whole GEMMs reach 85–93% (`r20260930-085618-5cfa`), and no co-issue mix exceeds the sum of its pipes' peaks (above).
- **Clocks:** the ratios are per clock and every pipe measured sits in the one SM clock domain, so an unlocked boost clock scales the adversary and the honest program alike.
- **Scope:** A_max = 1 excludes other hardware (FP8 ASICs, or hashing or bit-trick ASICs for one budget) by declaration. That part is a threat-model boundary, not a measurable claim.

## `tt-out-aw/pearl-c-sm120-admission`: D (as the row records)

- The approved-weights lane's crafted rows pass every cheap admission test, and 100% of derived v1 and v2 words are correct (`r20260930-073807-c5c8`).
- I reproduced the relation attack without the keyed transform: 94% of derived words correct at k = 2,048 and 100% at 8,192. With the transform it drops to 0% (`r20260930-084114-ee9d`, `known-weights-and-structure-free.md`).

## `memory-tiers/sm120`: D on its incompressibility clause (by construction; the row is not used in PoUW)

- "Protocol data is pseudorandom, so it can't be compressed" is false for Pearl-C's salt-derived noise. E, F_A and F_B are deterministic functions of 32-byte seeds (`pearl_kw.sample_line` over BLAKE3), which the adversary regenerates on chip, as red-team A1 found.
- The per-tier capacities and bandwidths are not measured here. They don't matter while W1 makes oblivious moves free.

## `tc-model/sm120-e4m3-sp-k64`: C, and moot on this card

- **Untested:** the bit-for-bit claim (2:4 `mma.sp` m16n8k64 equals the chain of two dense k32 atoms) has no capture from me yet.
- **Nothing to exploit anyway:** on sm_120 the exposure it guards is empty. `mma.sp` does 1,018 useful products per SM per clock, the same as dense E4M3 (`r20260930-071827-bcfb`), so 2:4-sparse registered weights don't run the chain faster even if the two computations agree bit for bit.
- **Falsifier:** the FP8 twin of GPU 4's NVF4 sparse-against-dense capture.

## `curated-weights/pearl-c` and `preprocessing/fixed-weights`: not rateable

- **`curated-weights/pearl-c`** is trust in publishers, with nothing to attack. On this card, the 2:4-sparse official releases it worries about gain nothing (above).
- **`preprocessing/fixed-weights`** is an adversary capability the model grants, not an assumption. Granting it makes the bounds stronger. It is load-bearing for `tt-out-aw/*`, whose ratings already assume free weight-side pre-adds and tables.

## The two rows as restated at 09:35Z (rated 09:45Z)

### `concurrent-budgets/sm120`, generic work in issue slots: B (GPU)

- **The generic budget is an architectural ceiling.** It counts one scheduler slot per non-tensor instruction, at 4 warp-instructions (128 thread-instructions) per SM per clock. Every measured mix stays within it, at most about 105 (`r20260930-092215-0633`).
- **It is generous to the adversary:** it lets half- and quarter-rate instructions (`dp4a`, IADD3 and HFMA2 at 64; MUFU at 16) issue as if they ran at 128.
- **Work outside the SM** (L2 reductions, texture filtering) still spends an issue slot and bytes at its tier's bandwidth, so the max still bounds it.
- **One wording point:** "tensor MACs at the tensor rate" must mean each MMA kind at its own measured rate:
  - NVFP4 and MXF4 at 2,027–2,033;
  - the FP6 and FP8 kinds at about 1,012;
  - BF16 and FP16 at 507.

  With FP8's rate for all kinds, an NVFP4 or MXF4 program finishes in 0.5 of the tensor budget's time (`r20260930-091638-9747`). That is the same kind of break the per-op reading had.

### `memory-tiers/sm120`, incompressibility scoped to costly-to-regenerate data: D as stated (moot for γ)

- **What the clause says:** the committed activations and the weights can't be compressed.
- **Real weights compress losslessly.** 12 Qwen2.5-7B matrices (embeddings, attention, MLP; 2M sampled weights each; `weight_compressibility.py`, `r20260930-093844-9db1`):

| Form | Lossless LZMA ratio | Order-0 entropy |
|---|---|---|
| BF16 as shipped | 0.66–0.71 (median 0.69) | 10.5–11.3 of 16 bits |
| E4M3 codes, per-row scale | 0.80–0.89 (median 0.83) | 6.5–7.3 of 8 bits |
| E4M3 after the approved-weights rotation (random signs, Hadamard, random signs) | 0.68–0.82 (median 0.82) | 6.43–6.49 of 8 bits |

- **Committed activations:** not measured. Where FP32 words carry BF16 values, 16 of every 32 bits are zero, so they compress at least 2×.
- **What the clause should say:** such data moves at no less than its entropy-coded size, about 0.68× raw for BF16 weights and 0.81–0.85× for E4M3 codes on this model, not its raw size.
- **Scope:** per-tier capacities and bandwidths are still not measured. No γ uses the row.

### `memory-tiers/sm120`, restated 09:50Z ("moves at no less than its entropy-coded size"): D if order-0, not rateable if true entropy

- **The usual reading fails.** Read as an entropy coder over the symbol distribution (Huffman or ANS, order 0), an off-the-shelf coder beats that size on real weights. LZMA gets below the order-0 bound on 10 of the 36 (matrix, form) cases from `r20260930-093844-9db1`, by up to 15%:
  - `layers.0.mlp.gate_proj` as rotated E4M3: 0.681 against an order-0 bound of 0.803;
  - `layers.1.mlp.gate_proj` as E4M3: 0.802 against 0.906;
  - the same matrix as BF16: 0.664 against 0.706.
- **The other reading can't be tested.** Read as the source's true entropy, no one can compute the bound.
- **What would be checkable:** a measured floor with a margin, for example "at no less than half its raw size" (LZMA's best here is 0.66 for BF16 and 0.68 for rotated E4M3). Or drop the clause, since no panel line uses it.
