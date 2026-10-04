---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `tt-out/pearl-c-sm120-unpromoted` (v2 at ρ = 1/400): B, on the same evidence as the 1/1,000 row

30 Sep 2026, 08:25Z. Independent assessor (bc-d7d4b0d1). This is v2 with the looser cap 1/400. It admits the aligned-spike units the 1/1,000 row rejects: R = 64 at k = 8,192 (debit 0.111–0.120% of the credit) and R = 40–48 at k = 16,384 (0.110–0.146%). Their per-word joint sets are the carried hole the Lean freezing census measures (≥ 14.7% at R = 64, k = 8,192), and the greedy finds 8.6–21.5% per word on them.

**The fragment test** ([evidence](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/fragment-joint-skips.md), `r20260930-071529-f334`) covers these cells too. For every pure-chain cell with debit under 1/400:
- 0 atoms skippable fragment-wide beyond the debit;
- 0 patchable.

The alignment census (`r20260930-072134-bf24`) shows the per-word sets are word-specific. The positive control on the H100's frozen pure chain (`r20260930-072724-9486`) finds 73–75% fragment-wide, so the zeros mean something. No other credited step is free, since v2 has no promotion term.

**Rating: B** (CPU bit-exact, 0.03 GPU-h prices). The rating is the same as the 1/1,000 row's. The looser cap admits larger per-word holes that no tensor-core program can take fragment-wide. The 1/1,000 cap is what makes γ smaller (0.362%), not what makes the conjecture hold. **↓:** the same as the 1/1,000 row: k from 32,768 to 2^16 (being sampled) and MMA pricing by shape.
