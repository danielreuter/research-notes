---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

# flock-zk (M1): the masked protocol works on CPU for RoPE

**Lane** flock-zk. **Agent** bc-2a9978cc-cafd-5d88-a4de-888a71d85659. **PR** [#123](https://github.com/danielreuter/verity/pull/123), a draft stacked on #83.
**Branch** `cursor/flock-zk-m1-5659`, tip `fc6cfe99`. **Cost** CPU only, no pods, $0. Written Sep 27, about 1:05 AM PT.

The full layout is in the repo: `backends/flock/live/PROTOCOL.md` (private repo). This page is the summary, plus the items
that are soundness-relevant and so stay out of the public notes.

## What works

- **Coverage.** `flock-circuit --zk` masks every message a repetition sends. The CPU audit (`zkaudit`) attributes every
  byte the verifier keeps and every opened proof value, and finds none in the clear (`complete: true`).
- **The zerocheck and lincheck.** These follow VEIL's §4.1 and Remark 4.4:
  - Each value is sent plus a pad, and the pads are committed before the first coin (Reed–Solomon with 192 uniform
    padding symbols, hm96-sha512 leaves).
  - The verifier replays upstream's checks as affine forms in the pads.
  - A sacrificed multiplication triple covers `final_a · final_b`.
  - One inner dot-product proof checks all 10 constraints.
- **Ring switching.** The masked claims' `s_hat_v` are hidden by uniform words in the mask slot. The prover checks the
  rank condition (512 of 1024) before sending, and the region claims' `s_hat_v` are recomputed from public data.
- **Ligerito.** Level 0 follows VEIL Figs. 8–9, in a new upstream patch (`flock-zk-b684b12.patch`):
  - Every lane is padded by `(X_L + c)·μ` with `t_pad = 500` uniform coefficients.
  - Two padded uniform lanes are folded in after the lane rounds.
  - Level 0's OOD value, lane messages and the extra lanes' sums are padded, and their chain becomes two constraints.
  - Every later Ligerito message is then a function of a uniform table.
- **The simulator.** `simulate_full` builds a whole proof from the public statement, the verifier's coins and a
  dummy-witness opening, and the verifier accepts it (128 of 128).
- **Statistics.** At N = 64 (128 transcripts per kind), real and simulated transcripts are indistinguishable on all 11
  classes (smallest of 55 p-values: 0.013). The unmasked control is distinguished (p ≈ 0).
- **Selftests.** RoPE CPU: M0 mode 30 of 30, `--zk` 28 of 28, with 5 new negatives. One of them, an extra lane's sum
  forged with an honest `T'`, is caught only by the inner proof.

## Measured prover overhead

On the 4-core VM, per repetition, median of three loopback runs:

| | M0 | M1 | |
|---|---|---|---|
| RoPE, m = 25 | 0.25–0.29 s | 0.31–0.32 s | +12–24% |
| RoPE, m = 27 | 0.38 s | 0.46 s | +20% |

- Upstream's prover under masking costs +7% at m = 27, mostly level 0's padding NTTs.
- The fixed part is 0.05 s: the replay and the pads commitment.
- End to end: +14% at m = 25, +17% at m = 27.
- Proofs grow by +32–36%, mostly the inner proof's Merkle paths.

## Findings (private)

- **Binary fields: high-coefficient padding leaks.** In the additive NTT's novel basis `X_L = Ŵ_n` vanishes on half the
  codeword, which I checked on upstream's NTT. So VEIL's RS padding placed in the high coefficients alone would leave
  about half of level 0's opened positions unmasked. `(X_L + c)·μ` with `c` outside GF(2) vanishes nowhere, and that is
  what the patch uses. This belongs in the Lean ZK proof's statement and in DESIGN.md §11's "binary-specific" list.
- **Fixed before any merge: `e` must precede `ρ`.** The extra lanes' sums `e` must be absorbed before the verifier draws
  `ρ_0, ρ_1`. Commit `74a197d9` had it the other way, which let a prover choose `e` to fit any lane-phase claim.
  `652357eb` fixed it; it is VEIL Fig. 9 step 1.
- **Open soundness item: the level-0 query count.** Level 0's code now has message length `L + t_pad` in `2L` positions.
  Its relative distance drops from 1/2 to 0.439 at m = 25 (below `2^-9` of change at production lane lengths). The level
  still uses Fast100's 218 queries for rate 1/2. The soundness lane should recompute that count; it sets `t_pad = 2q + 64`
  in turn.
- **For M0, via the coordinator: upstream `flock-core`'s unit tests don't compile on #83.** After
  `flock-sha512-b684b12.patch` there are 14 errors: `verify_level_opens` misses the salts argument, the 64-byte `Hash`,
  and non-exhaustive `HashKind` matches. They are identical with and without M1's patch. M1's upstream changes are covered
  by the integration selftests instead.

## What M1 still needs, and what M2 needs

- **M1:** the level-0 query recount above; a red-team review of `PROTOCOL.md` §4–§7; and, optionally, one interleaved
  padded NTT and a shared cap for the inner paths.
- **M2 (`PROTOCOL.md` §9):**
  - the per-session coin commitment (a SHA-512 root over HM96 coin commitments, per (table, rep, round));
  - the single-rewind simulator, which M1's dummy-witness opening and `simulate_full` are built for;
  - C1's level-0 root check, which M0 has and M1 keeps (padding and extra lanes are drawn once per session);
  - the GPU path.

## Evidence

- In the notes: `lanes/flock-zk/evidence/20260927T0750Z-zkstat64-rope.json` and the `20260927T0805Z-*` files (selftests,
  audit, bench, N = 16 statistics).
- In the repo: `backends/flock/tests/zk_stats.py`, and the commands `flock-circuit zkstat | zkaudit | selftest --zk`.
