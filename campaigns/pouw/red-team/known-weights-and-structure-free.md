---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `known-weights/*` and `structure-free/rot-*`: B for E4M3, C for NVFP4

30 Sep 2026, 08:50Z. Independent assessor (bc-d7d4b0d1). These are the two new rows behind the approved-weights fork. The weights are fixed and public before any salt, so a prover preprocesses freely against the codes the chain multiplies. The defence is a beacon-keyed randomized Hadamard rotation of each linear's residual-stream side, folded into the weights, then per-row round-to-nearest (`rot`) or stochastic rounding (`rot-sr`). The verifier uncredits near-duplicate rows and blocks.

**The attack** (`known_weights_sm120.py`, `r20260930-084114-ee9d`, CPU on node 2). It reuses the lane's own transform and chains (`relation-attack.py`) for faithfulness and adds three tests the lane's single-key run didn't make. Setup:
- 128 weight rows, two masters:
  - a trained-weight stand-in (Gaussian rows, 30% with outlier spikes);
  - a crafted master with row₃ = row₁ + row₂ on the E4M3 grid and row₄ = row₁ planted among real-like rows;
- both roundings, 8 keys at k = 2,048 and 4 at k = 8,192.

| Test | As registered | After the rotation (every key) |
|---|---|---|
| Derived words of the planted relation correct (the lane's attack, reproduced) | 94% (k = 2,048), 100% (8,192) | **0%**, `rot` and `rot-sr` |
| Exact two-row sums e4m3(row_i + row_j) matching a registered 128-group | on every group of the planted triple | **0** in 48 keyed cells |
| 2:4-compatible 64-slices; all-zero atoms | 0 | **0** |
| Worst near-duplicate among distinct rows (d* = 112 of 128, 29 of 32) | — | 12 of 128, 6 of 32 |
| The planted duplicate | exact | survives `rot` in every key, **caught by the verifier's rule**; broken under `rot-sr` |
| Key transfer: the decoy key's 20 closest pairs, under the real key | — | at most 7 of 128 codes shared |
| Energy outside rank 32 of the rotated real-like codes | — | ≥ 79% |

**What a prover could do with known weights, priced on the measured rates:**
- **Lookup tables over the fixed weights.** Even one-code tables are 256·n·k entries (68 GB at 8,192²). Each lookup feeds an n-wide exact add at 8.46 units, so the route is bandwidth-bound at about 1,000× the GEMM. Tables over pairs are 256× larger again.
- **Strassen with the weight-side pre-adds precomputed free.** The activation side still leaves E4M3, so sub-products stay FP16 at 2.00: the best is 1.80× the chain, as in `no-exact-rewrite` (B).
- **A low-rank or structured master.** The rotation preserves the master's rank before rounding, but the rounding residual is dense and wide, as for the noise core (`noise-core/pearl-c`, FP8 B).
- **Exact structure** (relations, duplicates, 2:4, zeros, spikes): removed by the rotation or caught by the rule, over every key tried. The lane's real-checkpoint census agrees: 0 duplicate rows or blocks, 0 2:4 slices and max/RMS ≤ 6.1 after rotation; 0.0% skippable on real Qwen2.5-7B (`r20260930-073807-c5c8`).

**Ratings:**
- **`structure-free/rot-e4m3`: B** (CPU bit-exact, about 0.3 CPU-h). It is an open lemma about one fixed randomized function, so CPU simulation of that function counts. Clauses (a)–(c) hold on every key tried (ε_T ≤ 1/48 by this sample, 0 observed). Clause (a)'s duplicate case is the rule's under `rot` and the lemma's under `rot-sr`, and both behave as claimed.
- **`known-weights/sm120-e4m3`: B.** Every exploit class priced above needs exact structure the lemma removes, or a route that costs more than the chain at the measured prices. **↓:** unknown structure in pseudo-random codes is the row's residual content by construction; the sample here is 12 keys.
- **`structure-free/rot-nvfp4` and `known-weights/sm120-nvfp4`: C.** Only the lane's single-key relation test covers them (100% to 0%). The multi-key census and key transfer weren't run on NVFP4, and the FP4 rows wait on a Pearl-C4 replay. NVFP4's zero codes (7–8% on real weights, the lane's stats) are the class to watch there.
