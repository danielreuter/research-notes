---
lane: coordinator
kind: handoff
from: flock-128
created: 2026-09-25T10:55Z
---

# flock-128 PARAMETERS: profile flock-128-r2 = two sequential runs of Flock b684b12 `Fast100`, each with its own live-verifier coins, with no grinding credit. That gives 2^-195.5 for the CPU union (about 2^-194.5 for the GPU pair). Today's `Fast` is 2^-110.0 with live coins and 2^-50 under Fiat-Shamir.

Report (in progress): `lanes/flock-128/20260925T1018Z-report-flock-128.md`. Evidence: `lanes/flock-128/evidence/`.
Cost numbers follow in a separate handoff. The CPU cost run has already finished: proofs verify, negatives reject,
art:4cc099364d00a0255b44f83a29e25c207228c0ca3f5eedcc9572211c561ebe71. The H100 run is next.

## How the bound is counted (TABLES accounting)
- The bound is for the whole proof. Every Fiat-Shamir challenge the prover and verifier actually squeeze was logged by a
  wrapper around the `Challenger` trait (`evidence/pod-scripts/site_census.rs` gives `evidence/census/*.tsv`, with 8 shapes:
  hopper BF16/E4M3 x 1024/4096 VUs x Fast/Fast100). Each site gets its Schwartz-Zippel degree
  (`evidence/accounting.py`), so a site with degree D contributes D/2^128 or D/2^256.
- **No credit for PoW or grinding anywhere.** Grinding nonces stay in the proof, but they add 0 bits.
- Ligerito's proximity terms come from the embedded TOML schedules (`evidence/configs/m3{0..3}_{fast,fast100}.toml`).
  The query term uses the Johnson regime (eta 0.02) with BCH+25 list decoding, which is proven. Split-commit folds use
  the F256 MCA term.
- Under Fiat-Shamir, every statistical term is multiplied by 2^60 (state restoration, B-Ligero PROTOCOL §8c). Neither
  profile reaches 2^-128 under FS: repeating the run twice under FS still gives only (2^60 x 2^-97.8)^2 = 2^-75.6. The
  2^-128 profile therefore **requires live, interactive verifier coins**, drawn per round and fresh for each repetition.

## Accounting table (m=33, hopper BF16 at 4096 VUs; other shapes are within 0.6 bit)
| term | today: params | today: log2 eps, no credit | 2^-128: params | 2^-128: log2 eps |
|---|---|---|---|---|
| F128 PIOP and opening: zerocheck (skip and eq points, 28 rounds), lincheck, ring switch F128^7, merged opening, multipoint, Frobenius anchor (about 150 F128 challenges) | GF(2^128), grinding credited up to 128 | -118.4 | unchanged, 2 runs | -236.8 |
| Ligerito claim batching beta (17 draws, list-unioned) | F128, grinding credited | -115.1 | Fast100 schedule, 2 runs | -234.2 |
| Ligerito consistency batching alpha (6 draws) | F128, grinding credited | -114.5 | Fast100, 2 runs | -232.2 |
| Ligerito proximity queries (Johnson regime, eta 0.02) | Fast: [244,79,48,35,29,25] queries per level, plus 16-bit PoW per level | -110.1 | Fast100: [218,106,71,53,43,36] queries, no PoW, 2 runs | -195.6 |
| Ligerito F256 MCA and proximity gaps | 6 folds | -207.8 | 2 runs | -415.8 |
| F256 quadratic fold sumcheck | 6 | -243.9 | 2 runs | -491.6 |
| two-point OOD binding | 6 | -229.6 | 2 runs | -467.0 |
| FS challenges | FS x 2^60 | total -50.0 | live verifier coins | no 2^60 factor |
| grinding | credited | 0 counted | 0 counted | 0 |
| **whole proof** | 1 run | **-110.0 live coins / -50.0 FS** | 2 runs, live coins | **-195.5** (m30: -196.1) |

The GPU line (two Flock-CUDA proofs, unit and BLAKE3) is the union of both proofs: about 2^-109 today and about 2^-194.5
under r2. The F128 PIOP union alone is 2^-118.4, so no single-run F128 profile can reach 2^-128. The profile needs either
F256 or repetition.

## Parameter set (implemented): flock-128-r2
- Flock b684b12, crates **unmodified**. `PcsParams { profile: LigeritoProfile::Fast100, log_inv_rate: 1,
  log_batch_size: embedded initial_k (= 6 for m30-m33), num_lanes: union.commit_lanes(batch), merkle_hash: Default }`.
- `reps = 2`. Each rep is a full independent proof with its own transcript domain (`flock-128/fast100x2/rep{0,1}`), and
  the verifier accepts only if both reps verify. The verifier fixes the profile itself: a proof made under another profile
  is rejected.
- Coins: the cost runs use FsChallenger, with a distinct domain per rep, as a stand-in; the prover's work is identical
  under live coins. The 2^-195.5 figure holds only when the verifier supplies each squeeze live. Flock implements that
  as a `Challenger` that forwards every squeeze to the verifier; it is not built yet (audit item 1).
- Flock-CUDA: the same parameters, with `profile: Fast100` and `reps: 2` passed through the prove FFI. The GPU patch
  will be `evidence/flock-128-r2-gpu.patch`.
- A fallback that passed the same checks is `fastx2` (2 x Fast): 2^-220.1, with proof size and CPU prover time within 1-6% of fast100x2.

## Paper-only alternative: flock-128-f256
One run with every F128 PIOP and Ligerito batching site moved to GF(2^256). Queries rise about 1.17x, to at least 131.6
raw bits per level, with PoW set to 0. This is still interactive-only, since under FS each term would need at least
188 raw bits. It changes the protocol field, so it needs code in the PIOP, the challenger and the CUDA kernels. From the
phase trace I estimate 1.5-1.7x prover cost. It is not implemented.

## Patch files
- `lanes/flock-128/evidence/flock-128-r2-cpu-harness.patch`: a diff of flock-bench-80gb's `unit_shape.rs` against
  `evidence/pod-scripts/unit_shape128.rs`. It adds profile and rep selection, per-rep domains and 4 tamper negatives.
  It needs no change to Flock's own code.
- `lanes/flock-128/evidence/flock-128-r2-gpu.patch`: coming next, a patch to `gpu_roundtrip.rs` and the prove FFI.

## What a Flock red team must audit
1. **Live-coin protocol.** The sequential-repetition lemma (the error multiplies across reps under independent live
   coins, and does not under FS), independence of the two reps, and the forwarding Challenger that the live verifier
   would need.
2. The **7 fixed inner zerocheck coordinates** (N_INNER, univariate skip K_SKIP=6). The eq point uses a
   protocol-fixed prefix, and this needs a cited lemma that the fixed prefix loses no soundness.
3. The **degree for each site** (`evidence/accounting.py`): multipoint gamma of degree K-1, the univariate-skip
   degrees, lincheck degree 63, the jagged degree-255 site, and the Merkle-shift degree-3 rounds.
4. **Ligerito proximity:** BCH+25 Johnson-regime list decoding at eta 0.02, the subfield descent used by split
   commitments, F256 MCA a/2^256, and the union over claim and consistency lists (L_max).
5. **Two-point OOD binding** in the list regime.
6. **The Fast100 schedules:** the embedded m30-m33 TOMLs are frozen and their raw `expected_eps_*` values match the
   ledger, and the verifier derives the profile itself, so a downgraded proof is rejected (negative tested).
7. **Transcript hash.** Flock uses a custom chained BLAKE3 challenger. Under live coins soundness doesn't depend on
   it, but binding does. Table 1 must name the hash used for the Merkle trees (PcsParams default; the TOML says blake3).
8. **GPU and CPU transcript equality:** Flock-CUDA's device transcript must match the CPU verifier's squeeze for squeeze.
9. **The union registry and padding contract** (how the unit and BLAKE3 tables are padded and bound in one proof).
10. **Out of scope for this profile:** link conditions C1 and C2, and the chain glue C4 (red-team-link).
