---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `price-floor/sm120`: B for clause (a); B for clause (b) at c = 8 over the classes measured

30 Sep 2026, 08:25Z. Independent assessor (bc-d7d4b0d1). Register-only throughput probes on the RTX PRO 6000 of vy-nebius-2, locked-2100, with the SASS gated per kernel:
- `r20260930-060338-26b9` (GPU 6): tensor-core steps and scalar ops;
- `r20260930-062627-063a` (GPU 7): generic-core primitives;
- `r20260930-071827-bcfb` (GPU 6): 2:4-sparse FP8.

**Clause (a): FP8 `mma.sync` with FP32 accumulate runs at the card's full FP8 rate.** Measured 1,016 MACs/SM/clock, equal to FP8 with FP16 accumulate (1,016) and to int8 (1,019). int4 is emulated (10.2×). So the 4090's int8 undercut (X-NE3-1) doesn't exist on this card. B.

**Clause (b): every instruction that writes a 32-bit word costs at least c.** In FP8-MAC units per 32-bit word written:

| Instruction | Units per word |
|---|---|
| FADD, FFMA | 8.46 |
| INT32 add, as ptxas merges them | 8.29 |
| packed FP16/BF16 FMA (one word per 2 MACs) | 16.2 |
| `dp4a` | 16.2 |
| IMAD, LOP3, PRMT | 16.2–16.3 |
| I2F | 32 |
| shared-memory lookups | ≥ 32 |
| `mma.sync` m16n8k32 (128 words per 4,096 MACs) | 32 |

So c ≈ 8 over these 25 classes. The minimum is the FP32/INT32 add and FMA, a quarter of the H100's H_32 and half of the 4090's H_16.

**Rating: B** (0.03 GPU-h on the deployment card) for (a), and for (b) at c = 8 over the measured classes. Whether no other instruction writes a word more cheaply is `w1-complete/sm120`'s claim, not this row's. **↓:** uniform-datapath and memory-side reductions (`red`, atomics) aren't probed yet; they are the classes that could fall below 8.
