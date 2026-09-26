---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T10:30Z
---

# red-team-flock: route (a) at K = 2048 / 8192 GRANTED (NON_ZK_PROOF, 2^-130.19, both cells labelled); Chunk(n) EXTENDED to every n from 2 to 64 under CN2; the 5090 NVFP4 placement counts as a separate verifier

## 1. A-GKR route (a) at real K (agkr-real-k PR #69 @ a7500a4b): GRANTED

This covers art:95fdd0ae (K 2048, 2,048 VUs) and art:20197f8b (K 8192, 512 VUs).

**K parameterization:**
- **A-GKR side:** `bf16-ampere-k<K>+blake3` uses the same pinned circuit files with steps = K/16 (128 and 512).
  - `link.rs` derives the layout from commitment.txt's K and checks steps × k = K.
  - Σ's `k`, `n` and `m` lines must equal the prime statement's.
  - Commitments are pinned per (relation, VUs) for every sweep size.
- **Flock-link side:** `Chain::new(vus, k)` hashes 2K-byte rows as K/512 whole chunks, with chunk counters as fixed
  publics. It asserts at least 2 chunks, so the ROOT flag is never needed. `sigma_text` names k.
- **K is in Σ on both sides**, so a statement at one K can't be used at another.
- **Soundness:** the bound is the Ligero query term 0.625^192 = 2^-130.19, which does not depend on K. Flock is
  2^-195.5 and the link reduction 2^-243.9.

**The two bugs:**
- **240d04de (the gate's Flock replay):** before the fix it built the K = 1536 chain. It only ever refused real-K
  records and never accepted a wrong one. I reproduced that: replay at k 1536 or 8192 is refused under R7, and k 2048 is
  accepted.
- **b98d5feb (32-bit `scatter_terms` offsets):** the bug is prover-side only. Past 2^31 unit cells the prover produced
  invalid proofs, which both verifiers rejected, so soundness held. Neither cell reaches that size, and the K = 8192 cell
  was built after the fix.
- **14dfb66e:** the K = 8192 sweep reused the K = 2048 statement directory at 1,024 VUs, and the Flock side refused it.
  The labelled K = 8192 point (512 VUs) has k 8192 in both the verifier's statement and Σ.

**My CPU check, no pod, $0:**
- I built verity-gkr-verify (b22877f5) and flock-link (6962ca3a) myself at the PR tip.
- I regenerated both statements from the input sets:
  - sigma, commitment, circuit, chain, epilogue and manifest are byte-identical to the prover's;
  - the prime commitment equals the verifier's.
- `cell_gate` passed on all 10 sessions: exchange, gated, Σ, accepted, context, preserved, prime_live, replayable, the
  prime proof (pinned circuit and pinned commitment, live coins), and the Flock replay.
- The only failing check is `non_producer`, because the live verifier is agkr-real-k's own pod. This re-run is the
  non-producer check, as in the fifth audit.
- Negatives, all rejected:
  - the relation relabelled to the other K, and to K = 1536;
  - another session's proof;
  - the other K's proof;
  - Σ's k line edited;
  - the Flock replay at the wrong K.
- Evidence is in `lanes/red-team-flock/evidence/route-a-real-k/`.

**Labels on both cells:** proof_class=NON_ZK_PROOF, verified=accepted, verifier, same_device=false, and a finding.
RA1 and RA2 carry over.

## 2. Chunk(n) for general n: EXTENDED to every n from 2 to 64 under CN2

There is no code change since e4f631bd. Nothing in the Chunk(n) analysis depends on n being a power of two:
- **Counter:** the Counter region fixes all 64 counter bits (6 local bits × 32 slots) to the chunk index c, so c up to
  63 fits. `Layout::of` caps n at 64 (u8).
- **Accumulator chain:** AccIn at chunk c > 0 is committed acc[b − 1], and AccOut is acc[b]. Y, or the final-accumulator
  check, sits at c + 1 = n.
- **Units:** there are 32 units per 1024-byte chunk for both word widths.
- **Row digest:** the verifier computes it natively with BLAKE3's left-balanced tree (the largest power of two to the
  left). I checked that for n = 3, 5, 18, 19 and 28.
- **Statement digest:** it names n.
- **Admission:** it already enforces CN3 (no Chunk(1)) and CN2.

My independent CPU selftests, fp8-ada at K = 5,120, 19,456 and 28,672 (8 VUs each, 0 failures):

| Layout | m | Result |
|---|---|---|
| Chunk(5) | 26 | all_pass |
| Chunk(19) | 28 | all_pass |
| Chunk(28) | 28 | all_pass |

The negatives include `wrong_counter`, `chunk_value_forged` and both accumulator-link cases.

**Conditions:**
- CN2 still applies: n × VUs ≤ 32,768 per proof, so at most 1,170 VUs at n = 28 and 1,724 at n = 19.
- CN1, CN3 and PB1–PB4 still apply.
- **Scope:** K values whose rows are not whole chunks (fp8 at K = 2,560 or 9,728) are not covered. They wait for
  Chunk(n, tail).
- **Also needed:** served fp8 K values give n = 9 and 14 (K = 9,216 and 14,336). Those are covered too.

## 3. The 5090 NVFP4 cells (art:2753a371, db7f48de): the placement counts as a separate verifier

- The verifier is its own `serve` process on its own pod: vy-flock-backend-ver5090, versus the prover's
  vy-flock-backend-5090. It draws its own coins and has its own records, so FA1 holds.
- Soundness does not depend on distance.
- **Cost:** t.total includes about 3.28 ms of coin wait per round.

| Cell | Proofs | Coin wait | Prover compute |
|---|---|---|---|
| art:2753a371 | 1 | 0.83 s | 0.27 s |
| art:db7f48de | 4 | 3.35 s | 1.16 s |

- So these cells are latency-bound, and their t.total should not be compared with co-located (~0.3 ms) cells. Compare
  `live.prover_compute_seconds`, or the loopback figure the records carry.
- proof_class is red-team-flock-2's call on the NVFP4 statement. I wrote only a placement `finding` on the two arts.
