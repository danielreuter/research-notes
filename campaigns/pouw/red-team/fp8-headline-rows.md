---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# The FP8 headline's unrated rows: `admits-ref`, `w1-complete/sm120`, v2's tile twin, `v1-cap600`

30 Sep 2026, 10:40Z. Independent assessor (bc-d7d4b0d1), in the root's order of 10:29Z. The probe is `cast_price_sm120.cu` and `.sh`, on GPU 6, locked at 2,092 MHz, with its units measured as a ratio against the FP8 E4M3 `mma.sync` loop on the same die in the same process (`r20260930-103246-bf0b`; volatile stores `r20260930-103451-bda0`).

## 1. `admits-ref/pearl-c-sm120-v1`, `-v2` (the honest E4M3 cast's price)

**What it asserts, as the panel uses it:** the honest kernel runs within W_ref. For FP8 the open term is the cast per code. The panel publishes γ at whatever the kernel achieves: 16.00 at the port's 144-byte stride, and 8.72 once GPU 1 times `form_s5` at a 160-byte stride.

**Reproduced on a second die** (GPU 6; GPU 0's loops ran on GPUs 2 and 5). This is the packed `e4m3x2` cast feeding shared-memory stores. Stores are volatile, so ptxas can't merge them (the first pass merged every width into `STS.128`). Thread t writes row t of a 32-row tile.

| Store per thread | 144 B stride | 160 B stride |
|---|---|---|
| 32-bit (`STS`) | 32.1 | 63.8 |
| 64-bit (`STS.64`) | 16.4 | 32.1 |
| 128-bit (`STS.128`) | **8.47** | 16.3 |

- **Two costs set the price.** A conflict-free store costs the same whatever its width, so four 32-bit stores per 16 codes cost 4× one 128-bit store. Bank conflicts multiply that per way. At 8.4–8.5 units per code the cast is bound by `F2FP` (8 per 16 codes), which matches GPU 0's "F2FP alone is 8.0" and its 8.72 with 64-bit stores.
- **The conflict-free stride depends on the kernel's own mapping.** In this loop, 144 B is conflict-free for 128-bit stores and 160 B conflicts. GPU 0's loop is the reverse. So the 160-byte change has to be timed in `form_s5` itself, with its own thread mapping, as the panel already requires.
- **Discarded:** my "F2FP only" figure (2.7) is invalid. ptxas hoisted the loop-invariant conversions; `asm volatile` binds only the front end.

**Rating:**
- **B** for the price the panel publishes as the port stands (16.00): the store-bound pattern is reproduced on a second die.
- **C ↑** at 8.72, until GPU 1's in-kernel timing at the 160-byte stride is gated. The falsifier is that timing: `form_s5` at more than 8.72 per code on any of the node's dies.
- **Nothing here reaches below the `F2FP` floor.** An honest cast under about 8 per code would need fusing the forming into the GEMM's A path, with no stores at all.

## 2. `w1-complete/sm120`

**The full-fragment rule** (every `mma.sync` is charged its whole shape, never per output word) is what every FP8 TT_OUT B and cross-group B rests on. **B (GPU):**
- **Every kind is timed:** all `mma.sync` kinds ptxas accepts on sm_120a (`fp8-tile-rows.md`), plus the scalar pipes and their co-issue (`pipes-budgets-and-remaining-sm120-rows.md`).
- **The tensor pipe doesn't run faster on zeros:** 1.0073 ms on random operands, 1.0072 all-zero and 1.0072 with 7 of 8 bytes zero. The second run's spread was 0.3%, within noise. An issued fragment costs the same whatever it holds.
- **Sparse and binary kinds don't pay:** 2:4-sparse `mma.sp` gives no useful-product gain. b1 and int4 have no native units.

**The whole row is C:** "every program the device can run is a W1 program at the table's prices" can't be closed by timing. Still open:
- the branching rule (G-branch) is informal;
- work done outside the SM's issue: L2 reductions (`red.global.add`), texture filtering and TMA;
- hand-written SASS outside what PTX reaches.

The first two either spend an issue slot and bytes, or aren't bit-exact with FP arithmetic, so I expect them to price in. But no search was made.
- **Falsifier (↓):** an unpriced path that produces exact chain words cheaper than the table.

## 3. `tt-out-tile/pearl-c-sm120-unpromoted-cap1000` (v2's audit tile twin): B (CPU, bit-exact)

This is the per-tile form of the unit row I rated B.
- **The evidence is per tile already.** On tiles that pass the cap, fragment-wide undebited joint skips are 0 (`fragment-joint-skips.md`, 64 × 16 blocks and 16 × 8 fragments).
- **Unit seeds leave the prover little to select with.** Re-drawing a tile means re-committing the unit, so a tile's debit barely varies: SD 0.004% over 16 tiles, against 0.024–0.064 points per row under per-row seeds.
- **Per-row seeds** (the `-h3` lines) would make the tile's cap grindable (4 draws per row admit aligned-spikes-r64). That case rests on the fragment argument, as rated at 10:20Z.

## 4. `tt-out/pearl-c-sm120-rev1-cap600` and its tile twin (candidate): B (CPU, bit-exact)

- **Per unit it asserts less than `tt-out/pearl-c-sm120-rev1`** (B): a stricter cap admits fewer units.
- **Per tile it isn't a pure weakening,** since the tile's fixed credit moves from (1 − 1/400) to (1 − 1/600), 0.08% of credit. None of my evidence depends on it: 0 fragment-wide undebited skips on passing tiles, and 0 of 1,536 rows with a row-level set.
- **The tighter cap raises the grinding cost under per-row seeds.** From §3's per-row spreads, rev1's aligned-spike families would need more than the 8–32 draws per row they need at 1/400.
- **Completeness** is the panel's figure: real activations flag at most 0.035% per tile against the cap's 0.167%.
