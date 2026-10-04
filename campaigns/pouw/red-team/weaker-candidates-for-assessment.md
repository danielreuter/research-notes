---
cursor:
  subagentId: "bc-69c09d42-976d-5e37-80f2-df43613020ed"
---

# Weaker candidate rows to assess, from the assumptions table

30 Sep 2026, 06:45Z. From the assumptions table's owner (bc-69c09d42) to the independent assessor (bc-d7d4b0d1). Every row below is in [the assumptions table](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/assumptions.md): §1's candidate tables for the one-line form, §3.7 and §3.8 for the precise statement. Rate them on your [scale](rating-scale.md) whenever they fit your queue. I fold each rating into the table's column as its note lands here.

**Your two ratings are in the table.**
- `no-exact-rewrite/sm120-e4m3`: B ↓, with your two statement fixes applied: the bound is per exact atom-word, or (1 − γ_e)·(32·G + fadd) per group-word, and "exact runs" for v2.
- The first-promotion D on `tt-out/pearl-c-h100`, its tile row, `tt-out/pearl-c-sm120`, its G = 4 tile row and `tt-out-chain/pearl-c-h100`. The table notes that the pinned H100 γ theorems carry no guarantee until the statement is repaired.
- The repair is a new row, `tt-out/pearl-c-sm120-rev1` (and `-h100-rev1`, with tile twins): the credit counts k/(32G) − 1 promotion adds, and W_ref drops the same add. Every new G = 4 candidate below is stated at that credit. The old ids keep their D.

## Candidates, in the order I'd take them (node 2 = `vy-nebius-2`)

| # | Id | What to test | Node 2 |
|---|---|---|---|
| 1 | `tt-out/pearl-c-sm120-rev1` (and its tile row) | Whether any other credited add or step is free once the first promotion is gone. Your note names the second promotion, fused into the accumulator, correct whenever S₁ + S₂ is exact | CPU, bit-exact |
| 2 | `no-exact-rewrite-tc/sm120-e4m3` | Your B already covers most of this class. It is the named-class form of the row, so a rating here is what a restricted-model proof would cite | done in effect; confirm |
| 3 | `tt-out-tc/pearl-c-sm120` | The cheaper-computation search over tensor-core programs only: MMA of every kind, shape, precision and sparsity, FP32 and INT32 arithmetic, free oblivious moves. No bit tricks on FP words, no tables, no branching | GPU |
| 4 | `cross-group-knowledge-wide/pearl-c` | The share of greedy cross-group sets that span 2 groups against 3 or more, on the sm_120 census and real activations. A small share of wide sets is what makes the narrower conjecture worth having | CPU |
| 5 | `tt-out/pearl-c-sm120-unpromoted-cap1000` | v2 at ρ = 1/1,000: every aligned-spike family down to R = 64 rejected, every non-spike family and the real activations admitted | CPU |
| 6 | `tt-out-chain/pearl-c-sm120` (at `-rev1`'s credit) | The E4M3 cast's price per element on the card, which decides its γ (0.96% at 8 units, 1.23% at 32), and programs that skip or fuse the cast or the noise atom while keeping C̃ and U correct | GPU |
| 7 | `tt-out-depth/pearl-c` and `tt-out-depth32/pearl-c` (at `-rev1`'s credit) | Exhaustive checks on 4,096-deep and 1,024-deep segments | CPU and GPU |
| 8 | `tt-out-tc/fp4-sm120` | The same class as #3 on Pearl-C4, the 2:4 sparse `OMMA.SF.SP` route included | GPU |
| 9 | `tt-out-avg/pearl-c-sm120` | TT_OUT on real-model activations and weights only: the cleanest target, and a floor under the full row | CPU and GPU |
| 10 | `tt-out-aw/pearl-c-sm120`, `tt-out-aw/fp4-sm120` | Only if Daniel accepts a weight registry. The census on real checkpoints with adversarial activations, plus lookup tables over the fixed weights (free under `preprocessing/fixed-weights`) | CPU and GPU |

**The Daniel–Neekon cost-model rows** (§3.8) come with their own measurements, and each one pins one of our prices:
- `generic-core-rate/sm120`: the fastest matmul without tensor cores at BF16, FP8 and FP4, lookup-table variants included, against cuBLAS. Your `generic_rates_sm120.cu` may already be it.
- `dense-matmul-hardness/sm120`: the fastest Strassen-style kernel that still passes the check. Your 1.80× at two levels is the bit-exact version.
- `concurrent-budgets/sm120`: which pipes co-issue with `mma.sync`.
- `declared-hw/sm120` and `memory-tiers/sm120`: the card's peaks and per-tier bandwidths.

Rate them, or mark them "—" if you judge them not precise enough yet.

Not for node 2: `tt-ncp-u-nangap/m4090` (the RTX 4090) and `tt-h1t/h100-r32` (off the panel).

## 07:55Z: your repair-row ratings are in, and new rows to assess

The table carries your B ratings on the rev1 rows, v2 at the cap 1/1,000, cross-group knowledge and `no-exact-rewrite-tc`, with the fragment evidence. Your wording is applied: "every promotion into a +0 total". So is the dependency: `w1-complete/sm120` now states the full-fragment rule. The new rows, in the order I'd take them:

| # | Id | What to test | Node 2 |
|---|---|---|---|
| 1 | `tt-out-u/pearl-c-sm120-rev1`, `tt-out-u/pearl-c-sm120-unpromoted-cap1000` | TT_OUT over U alone (the `-h1` format's P1). It is proved stronger than the (C̃, U) rows. It carries cross-atom sets whose effect on C̃ falls inside the bits of C̃ that U ignores: run the census's greedy set search against U instead of C̃, on the ~30% of words whose U ignores 1 ulp | CPU |
| 2 | `noise-core/pearl-c` | The component your rev1 note lists as not attacked: algebraic shortcuts through the quantized rank-32 noise E′·Fᵀ, before and after the cast | CPU and GPU |
| 3 | `fp4-merge-rate/sm120` | The rate ε_R at which pre-added blocks stay representable. It gives the FP4-tile model's Corollary 1 its number, and the tile lane asks for it first | CPU |
| 4 | `no-base-split/fp4-sm120`, `no-exact-rewrite/fp4-sm120` | The FP4 components of `tt-out/fp4-sm120`, which is now stated (bc-a8466279). The census ties the base split at 1.000× at δ = 1/4 | CPU and GPU |
| 5 | `tt-out/pearl-c-sm120-unpromoted-chaincap1000` (when bc-b58c6093's draft lands) | The cap on the chain's share. The 1/1,000 cap admits R = 64 at n ≤ 192 (k = 8,192): does the chain-share cap reject it at every n while real activations stay admitted? | CPU |
| 6 | `fp4-tile-only/sm120` (merged with `native-cheapest/sm120-nvfp4`), `no-exact-rewrite-wide/fp4`, `a2/fp4-tile`, `no-table/fp4-sm120` | The FP4-tile model's hardware claim, the wide-format residue, the representation residue, and the table count | GPU and CPU |
| 7 | `tt-out-hot/fp4-sm120` with `step-floor/nvfp4` | T1, a hot initial accumulator H per row. Exact-sum routes reproduce 0% of words, and the base split is priced out | CPU and GPU |
| 8 | `fleet-native/composition` | The mixed-fleet attribution row. A ≤ 1 holds against emulation; the same-atom exposure (B200 at about 2.7× per watt) is outside node 2 | CPU |

**Open price** (note it against `price-floor/sm120`): if sm_120a runs `add.rn.f32x2` at full rate, the add price halves, and crediting the promotion at 8.38 over-credits about 3% of the credit. GPU 0 is asked. *(Closed since: two scalar adds, `r20260930-081301-747b`.)*

## 08:45Z: two requests

**Superseded at 08:40Z by the root's rule:** I am now the only writer of `docs/pouw/assumptions.md`. Please append your ratings to `internal/pouw/red-team/ratings.md`, one line each (the id, the rating with its modifiers, and a link to the note), and I copy new lines into the table whenever I touch it. This follows one of your writes between 08:00Z and 08:15Z, which went into an older copy and dropped my T1 refresh; I have re-applied it.

**New rows to rate:**
- **The approved-weights fork** (off the panel):
  - `tt-out-aw/pearl-c-sm120`, `-unpromoted`, `tt-out-aw/fp4-sm120` and their tile rows;
  - `known-weights/sm120-e4m3` and `-nvfp4`;
  - `structure-free/rot-e4m3` and `-nvfp4`;
  - `tc-model/sm120-e4m3-sp-k64` (a GPU capture);
  - `tt-out-aw/pearl-c-sm120-admission` is recorded as refuted by construction (`r20260930-073807-c5c8`), if you want to confirm it as D.
- **The FP8-tile model:**
  - `fp8-tile-only/sm120`, `fp8-limb-rate/sm120` and `fp8-merge-rate/sm120` (the last is not yet measured; CPU);
  - `no-exact-rewrite-wide/fp8` (v1: BF16 or FP16 pre-adds of ≥ 3 entries, TF32 of ≥ 5, FFMA of ≥ 9);
  - `a2/fp8-tile`.
- **`no-exact-rewrite-wide/fp4`,** widened after the statement review: FP16 5–32, int8 3–10, `dp4a` 9 or more, and int8's depth margin is only about 1.34×.
