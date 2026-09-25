---
lane: red-team-link
kind: report
created: 2026-09-25T09:57Z
status: final
---

CHECKPOINT 2c704b0 (10:15Z) [final] CLEARED WITH CONDITIONS: link parity argument holds; GAPs C1 GF(2^128) claim reduction ~2^-122 (use GF(2^256)), C3 Flock not 2^-128, C4 no chain glue; traps: Flock FS from root_B, B-Ligero r1 reuse; art:beeefd44; pod terminated 10:11Z ~$0.01; handoffs 1025Z
CHECKPOINT 82adc8a7 (10:11Z) [open] toy harness art:beeefd44 (16 spec/flawed negatives OK; batched 2-point miss 5.3x independent in GF(2^8)); pod vy-red-team-link terminated 10:11Z; writing report + handoffs
CHECKPOINT 5483d13b (10:05Z) [open] paper review: link math (sec 4) holds; found GAPs: binary-side GF(2^128) claim reduction ~2^-122 defeats 2-point squaring; Flock eps_B<2^-128 impossible today; A-GKR single-tableau (no root_F2), B-Ligero 2-coin HM96. Next: toy negatives harness on cheap CPU pod
CHECKPOINT none (09:57Z) [open] started: read contract; reading flock-link-protocol, survey 3.8, census, flock-bench/agkr-bound reports; paper review first, no pod yet

# red-team-link: audit of Link L (the GF(2) to prime-field bit link)

**Overall: CLEARED WITH CONDITIONS.** The link's core argument (protocol §4 steps 1-4) is correct. No attack on the protocol as written
succeeds. Builders may build it. But route (a) produces **no 2^-128 Table 2 cell** until conditions C1-C4 below hold:
- C1, C2 are protocol fixes to the link itself;
- C3 is Flock's own 2^-128 profile, outside the link;
- C4 is the missing hash-chain glue, also outside the link.

Until then a route (a) result is at most an unfiltered, provisional drill-down entry (reason L, below the bound filter). The
class is granted per implementation: a red-team pass of the built statement against the checklist in §4.

Inputs: the Project store's `docs/flock-link-protocol.md` (the link doc, read-only), `hash-proving-survey.md` §3.8 and
`binary-backend-census.md`; flock-bench FINAL; `kb/flock-prover.md`; the agkr-bound report (hash spike, 0858Z-0955Z link
numbers). Code read only (no edits): A-GKR `backends/gkr/PROTOCOL.md` §2, §3, §5.1, §9 and §16 at agkr-bound 86f86084; B-Ligero
`backends/direct/ligero/PROTOCOL.md` §8c at b-ligero-standard-hash. Handoffs received: none (inbox empty at 09:57Z and at every checkpoint).

Evidence: toy harness `evidence/pod-scripts/link_toy.py`, run rtl-toy-1 on vy-red-team-link (cpu3c, 2 vCPU),
**art:beeefd44** (same content also stored as art:53255bc7 under a non-vocabulary kind; cite beeefd44).
- It uses the real link arithmetic: GF(2^128), the BabyBear prime, m = 12, and 2 points.
- The two sub-proofs are idealised: the binary side is an ideal PCS, and the prime side checks constraints (i)-(iii) directly.
- 16 of 16 expectations hold: honest ACCEPT; each spec-verifier negative REJECT; each flawed variant ACCEPT.

## 1. Soundness of the link as specified: HOLDS (with implementation conditions); GAP on Λ provenance

**What holds.** Both steps of the core argument are correct.
- *Integer identity.* Each side of (iii) lies in [0, p-1]:
  - the left side is in [0, N] with N ≤ p-1;
  - the right side is bit + 2u ≤ 2^(w_u+1) - 1 ≤ p-2.
  So equality mod p is equality over the integers.
- *Parity to y.* bit_t is GF(2)-linear and b is boolean, so the parity checks force y^k = b̂(r^k).

Toy scenarios:
- A (honest) accepts.
- B (b ≠ z in one bit, with y taken from either side) rejects.

**Every numbered attack in the link doc's §9 is either defended or correctly listed as an obligation.** Confirmed by construction:

| scenario (toy) | spec verifier | flawed variant | flaw |
|---|---|---|---|
| C: u = (σ - bit)/2 mod p | REJECT | ACCEPT | no range check on u (A6) |
| D: b_i = z_i + 2 (every parity kept; the recomposed word becomes 4262 instead of the hashed 3238) | REJECT | ACCEPT | no booleanity on a linked cell (A4) |
| F: two prime cells on one position, both 1, z = 0 there | REJECT (setup) | ACCEPT | Λ_F not injective (A17) |
| G: two VU rows swapped on the prime side | REJECT | ACCEPT | verifier uses a prover-supplied Λ (R1 pattern) |
| H: u range 32 bits over BabyBear, sparse data, one bit flipped | REJECT (w_u = 12) | ACCEPT | 2^(w_u+1) > p-1: bit' + 2u wraps |
| I: σ sent in clear, forged σ + p | REJECT | ACCEPT | verifier doesn't require canonical σ ≤ N |

**New or sharpened findings.**

*F1 (GAP): Λ provenance.*
- The doc says Λ is "public and pinned in Σ". A digest in Σ binds the challenges to Λ; it doesn't make Λ correct. This is exactly
  R1 of red-team-standard-hash: the (vu, x, W) triple was absorbed but prover-chosen.
- Condition: the verifier *derives* the map from `leaf_layout`, the batch layout and the instance range itself, on both sides.
  - Binary side: slot → (leaf, chunk, block).
  - Prime side: cell → position.
  It rejects any statement-supplied map, and it derives D's slot → leaf-id assignment the same way.
- Two maps are involved: Λ_B (hashed bit → trace position) and Λ_F (prime cell → position). **Both** must be injective, and every
  prime cell that the relation consumes must be in Λ_F's domain.

*F2 (GAP): SHA-256 bit order.*
- The doc's "same bit order" argument (§1, and census §3) holds for BLAKE3 only, whose words are little-endian.
- SHA-256 reads big-endian words, so message bit j of word w is byte 4w + 3 - ⌊j/8⌋, bit j mod 8. For `sha256/row/v1`, Λ is a
  fixed permutation inside each 512-bit block. That still preserves the sub-cube, so the cost is unchanged.
- The same applies to `vllm-v1`, whose operand-domain mapping is still PROVISIONAL (integration owns it). **No `+vllm-v1` link
  can be pinned before that spec is final.**
- Conformance vectors are needed per scheme and per format: BF16 is value 2w + ⌊j/16⌋; FP8 is value 4w + ⌊j/8⌋.

*F3 (condition): what the linked region contains.*
- The linked sub-cube must be the message *inputs* that the compression constraints consume, or copy slots whose copy rows are
  enforced.
- Any linked position with no prime cell (spare slots in the 2^19-slot A-GKR trace, a partial last chunk) must hold zero message
  bits in honest proofs. The admissibility rule already makes a nonzero bit there a detected difference; the toy doesn't need a separate case for it.

*F4 (condition): BabyBear size limits, which A-GKR hits in its sweep.*
- A-GKR's GPU cells run over **BabyBear with a degree-6 extension**, not Goldilocks as the link doc's §6.2 says (A-GKR
  `PROTOCOL.md` §16.3: |F| = p^6).
- The binding condition is 2^(w_u+1) ≤ p-1, so w_u ≤ 29, which means N ≤ 2^30 - 2. That is at most **21,845 BF16 VUs** (43,690
  FP8) per linked proof with the u form.
- The σ form (§2, S1) needs only N ≤ p-1: at most 40,959 BF16 VUs.
- Beyond that, split the parity sums into chunks.
- The trap: range-checking u as two 16-bit limbs, which is natural given A-GKR's `T_range16` table, makes w = 32 over BabyBear.
  That is the scenario-H forgery.

*F5 (outside L, blocks (H)): the hash statement.*
- flock-bench and agkr-bound proved **independent compressions**. Chaining, public endpoints, counters, flags and block_len were
  not modelled.
- Without chain glue, every block is forgeable: the prover proves block j with message m' and the honest cv_in(j), then block
  j+1 with the honest cv_in(j+1) ≠ out(j). Every compression is individually correct and the published chunk CV still matches.
- The link binds b to z; this binds z to nothing.
- What P_B must pin:
  - cv_in(0) = key or IV (BLAKE3), or the verifier-computed midstate (SHA-256's 64-byte prefix);
  - cv_in(j+1) = cv_out(j);
  - counter = chunk index, and block_len = 64 (or the partial length);
  - flags per position;
  - the SHA-256 padding block as constants;
  - the published chunk CV (or digest) at a verifier-derived slot;
  - that the chunk CVs are the same values the native parent and tree check consumes.

## 2. Challenge derivation: HOLDS on paper; GAP on the field bound; two implementation traps

**Ordering (paper): HOLDS.** The doc's order is correct: roots, then points, then y, then root_F2, then P_F's test coins, with
P_B's batching after y.

**Field bound: GAP.** Two GF(2^128) points do **not** give 2^-246 end to end.
- Schwartz–Zippel alone gives (m/2^128)^2 = 2^-246.4 at m = 28.
- But the binary side must still verify the two claims y^k = ẑ(r^k), and the doc folds them into Flock's opening over GF(2^128).
  - A batched check Σ λ_k (ẑ(r^k) - y^k) = 0 fails to catch a false pair with probability 1/2^128.
  - The multi-point reduction sumcheck, or ring-switching, adds about 2m/2^128 on the full trace.
- With m = 33 (BLAKE3 for the 4,096-VU BF16 batch, 2^19 slots), that is about 67/2^128 = **2^-121.9**. The squaring is lost.
- Toy scenario E (GF(2^8), m = 8, 200k trials, extremal δ): miss rates were
  - one point: 3.07% (Schwartz–Zippel bound 3.08%);
  - two points checked independently: 0.097% (bound 0.095%);
  - two points batched into one random combination: **0.52%**, 5.3 times the independent rate, about 1/|K| plus the independent rate.
- Fix, either:
  - (a) verify the two claims by independent reductions with independent coins, each sized so their product and the shared
    proximity term reach 2^-128; or
  - (b) better: run the binary side's link claim at **one point over GF(2^256)**, with the reduction over GF(2^256), for a bound of
    m/2^256 = 2^-251. Flock needs GF(2^256) for its own terms anyway (C3).

  The doc lists (b) as an alternative. It should be the default.

**Trap 1, P_B's coins (a BREAK if violated).**
- If Flock's Fiat–Shamir transcript is seeded from root_B alone, as its code does today, its batching coefficients λ are known
  before root_F and y.
- The prover then chooses b ≠ z after seeing λ. The false pair survives when λ1·δ̂(r^1) + λ2·δ̂(r^2) = 0, and the two-point
  squaring is gone.
- Worse, any P_B challenge that comes before y and isn't bound to y lets the prover compensate between claims.
- Condition: P_B's coins after root_B are the live verifier's (interactive), or come from a transcript that has absorbed Σ,
  root_F, r^1, r^2, y^1 and y^2. The same applies to Flock's zerocheck point, if the link claims share its reduction.
- The link points must be uniform in K^m, not Flock's partially deterministic (GF(2^8)-pinned) coordinates.

**Trap 2, B-Ligero's HM96 coins (a BREAK if violated).**
- B-Ligero's interactive mode has exactly two coin openings:
  - r1, after root, gives r, ρ_lin and ρ_quad;
  - r2 gives the columns.
- The link doc's §6.1 needs a **third** coin slot: points opened after root_F and root_B, *before* root_F2, and r1 opened after
  root_F2.
- Deriving the link points from r1, "as its other challenges are", reveals ρ_lin and ρ_quad before u is committed. A Ligero
  tableau committed with its test coins known satisfies the combined linear and quadratic tests without satisfying (ii) and (iii)
  individually.
- Condition: a separate coin slot, plus the sequential-depth increase (3 → 4).
- Also, B-Ligero is single-tableau. root_F2 needs a two-tableau Ligero, with a joint linear test across both tableaux and its own
  proximity accounting. That is a protocol change needing red-team review.

**A-GKR has no second commitment.** Its §5.1 commits everything in W_1 before any challenge ("no challenge-dependent value is
ever committed"). So the doc's root_F2 (u) doesn't fit. It is also unnecessary for A-GKR's class.

**S1, a simplification for NON_ZK_PROOF only.**
- Send σ(k,t) in the clear after the points: 256 integers of up to 28 bits.
- Prove Σ_i C(k,t,i)·b_i = σ(k,t) as 256 dense linear constraints on committed x, with public coefficients and a public
  right-hand side. They fold into A-GKR's deferred Ligero linear test like its input-layer claims.
- The verifier requires canonical 0 ≤ σ ≤ N_cells and σ mod 2 = bit_t(y).
- Soundness: both sides lie in [0, p-1], so the identity holds over the integers.
- Toy I: honest ACCEPT; σ + p forged REJECT (spec) and ACCEPT (flawed).
- This removes u, its range checks and the second commitment. It leaks σ, which a NON_ZK_PROOF class allows; B-Ligero (ZK)
  must keep u.

## 3. Composition: GAP. Today's whole-proof bound is about 2^-100, set by Flock

Whole proof = ε_F + ε_B + ε_red + ε_SZ + ε_ρ + hash terms, each over the whole batch:

| term | A-GKR route (a), 4,096 BF16 VUs | status |
|---|---|---|
| ε_F (A-GKR, interactive, BabyBear^6 or Goldilocks^3, t = 192) | 2^-130.2 (§9.1; the README says 2^-127.7 "with the chain functional's terms / default hash budget": the accountant must settle which applies) | proven |
| ε_B (Flock b684b12) | 2^-100 (paper: Johnson regime, round-by-round). The repo's "strict 128" needs 16-bit PoW credit, which our accounting doesn't give | not 2^-128 |
| ε_red (binary-side link-claim reduction over GF(2^128)) | about 2^-122 | fix C1 |
| ε_SZ (link, 2 points, L list factor) | L·2^-246.4 (negligible for any L ≤ 2^100) | proven |
| ε_ρ (combining 256 prime-side constraints over BabyBear^6) | ≤ 2^-177 | proven |

**The Fiat–Shamir factor.** By the campaign's rule (B-Ligero `PROTOCOL.md` §8c), a Fiat–Shamir sub-proof pays ×2^60 on every
statistical term. A Flock proof made with Fiat–Shamir therefore needs per-term 2^-188, which puts even GF(2^256) sumchecks at the
limit. So P_B must run **interactively**, on the live verifier's coins, as A-GKR's cells do, or be sized for the ×2^60 factor.

**Slack.** Keeping everything within 2^-128:
- with A-GKR at 2^-130.2, the rest must total at most 2^-128.35, for example Flock at or below 2^-129 and the link at or below 2^-140;
- B-Ligero's interactive union is 2^-128.05 over 25 × 170, which leaves no room: any ε_B term forces B-Ligero's t up, around 200+.

**Variant T** (§8 of the link doc): GAP too.
- The rank-1 term is 2^-132.8, and the binary sumcheck over GF(2^128) adds 2m/2^128, about 2^-122.5. Two independent sumchecks,
  or GF(2^256), are needed.
- The 2^-132.8 term alone becomes 2^-72.8 under the ×2^60 factor, so Variant T needs an interactive run.
- Its pad-rank rate is still unsimulated.

**Zero knowledge:** B-Ligero's declared class (COMPLETE_ZK_BACKEND) is unreachable until Flock has ZK (A20). A-GKR's
NON_ZK_PROOF is unaffected.

## 4. What must be true to grant the class (the builders' checklist), and the negatives the harness must include

**Conditions:**
- **C1:** the binary-side link claims are verified at one uniform point over GF(2^256), with a GF(2^256) reduction, or at two
  points with independent reductions sized to 2^-128. Not in one GF(2^128) batch.
- **C2:** transcript order is enforced mechanically:
  - P_B's coins after root_B come from the live verifier, or absorb Σ, root_F, r and y;
  - the link points are a coin slot of their own, after both roots;
  - (B-Ligero) r1 is opened after root_F2, and u's tableau is covered by a joint linear and proximity test;
  - (A-GKR) the σ form S1, or a second tableau with the same property.
- **C3:** Flock has a 2^-128 profile under campaign accounting:
  - proven bounds only (list decoding cited: BCH+25);
  - no PoW credit;
  - GF(2^256) for every term near m/2^128 (zerocheck with univariate skip, lincheck, shift glue, ring-switching, MCA);
  - interactive coins;
  - its partially deterministic zerocheck coordinates covered by a cited lemma.
  Flock itself needs its own red-team pass; none has run.
- **C4:** P_B proves the full leaf statement (F5): chain glue, endpoints, counters, flags, padding, and slot → leaf ids derived
  by the verifier, with its public outputs being the values the native tree check consumes.
- **C5:** the verifier derives Λ_B and Λ_F itself (F1). Both are injective. Every relation-consumed operand bit is linked, all 16
  (or 8) bits of each word, including bits the relation ignores (A16).
- **C6:** admissibility is checked at setup and in Σ: N_cells ≤ p-1 and 2^(w_u+1) ≤ p-1, with w_u = ⌈log₂(⌊N/2⌋+1)⌉ exactly and
  not rounded up to limb widths (F4). The σ form uses canonical σ ≤ N_cells.
- **C7:** booleanity is constrained on *every* linked cell and pad cell, and not "range-checked elsewhere". Every u bit is boolean.
- **C8:** the accountant prints the whole-proof sum of the table in §3 at the cell's batching, over all sub-proofs, with the
  ×2^60 factor applied to any Fiat–Shamir component.

**Negatives the harness must include.** Each must be rejected by the independent verifier. Tag S means rejected at setup.
1. bit flip in b only;
2. bit flip in z only;
3. **alt_alt_bits**: an altered operand carrying its own bits, with honest hashes. A-GKR's scaffold ACCEPTS this today, and the
   link must close it;
4. b_i = z_i + 2 (a non-boolean cell);
5. u computed mod p (unranged), and u with a 32-bit range (S over BabyBear);
6. σ + p forged (σ form);
7. a VU swap through a remapped Λ, or through statement-supplied slot and leaf indices;
8. a duplicated prime cell (S);
9. a nonzero message bit in a spare Flock slot or a partial chunk inside the linked sub-cube;
10. y^1 tampered; y^1 and y^2 tampered with λ-compensation;
11. link points recomputed with root_F or root_B changed, which must change them, and an acceptance test that refuses a transcript
    whose points don't hash both roots;
12. (B-Ligero) link points derived from r1;
13. a forged middle block with honest chunk endpoints (unwired chain);
14. a wrong counter, flag, block_len or padding block;
15. a cross-session replay of the Flock proof or the link messages;
16. BLAKE3's Λ applied to a SHA-256 leaf (it must fail completeness; this is the conformance vector);
17. the honest control, with its proof bytes, and the same honest proof accepted twice by independent verifier builds.

**Answer for agkr-bound's route (a).** Build the prime side now:
- in-unit bits (86f86084), plus the S1 σ-form link constraints in the deferred linear test;
- the dense ℓ coefficient vector (0.066-0.88 s on A100, per agkr-bound's 09:34Z and 09:55Z checkpoints);
- the negatives above.

Results are drill-down only (L) until C1, C3 and C4 land. Price C3 (Flock at 2^-128 over GF(2^256), interactive) before
promising a Table 2 cell; it is the long pole, not the link.

## FINAL

~~~text
tip: none (no repo commits; notes only)        merge-with: none
known-failures: none    pod: terminated 10:11Z (vy-red-team-link, 9bkz4idcq7fsg6, cpu3c 2 vCPU, about 5 min); about $0.01
artifacts: art:beeefd44
~~~

Handoffs written: `lanes/coordinator/20260925T1025Z-handoff-from-red-team-link.md`, with copies in `lanes/agkr-bound/` and
`lanes/b-ligero-standard-hash/`. Handoffs received: none. The link doc wasn't edited. Its errata for the author are §6.2 (A-GKR
is BabyBear^6 on GPU), §4's numbers (the binary-side reduction), §6.1's coin slot, and the SHA-256 Λ.
kb: `kb/flock-prover.md` gains a "Link L red-team" note (C1-C4, F4).
