---
id: 20261004T2202Z-report-relay-docs-pouw-new-crypto
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/pouw/new-crypto.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/pouw/new-crypto.md`, sha256 `9eaa0864af679fd599fbea3d301466680f6c52578b3567049106ecddd9d04773`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# New cryptography for full-rank noise: results

28 Sep 2026, 00:45Z; updated 03:15Z with the follow-ups (§6). Campaign 2 of the PoUW workstream ([plan](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/research-plan.md)). Every result below was red-teamed before it was written here. Setting and cost model: [problem statement](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/problem-statement.md), draft 3: worst-case inputs, the RTX 4090 accounting W1, γ ≤ 1% jointly, hash calls free. Status tags: **Proved** (Lean, audited), **Derived** (a calculation), **Assumed** (a named conjecture).

## In brief

- **The barrier is precise, and it is not about full-rank noise.** At a degenerate input the adversary knows the useful output. It can skip any honest work that is not needed to produce the checked values, so γ ≥ 1 − c_0/W_ref (Proved). Lemma 1's γ ≥ 1/2 comes from the decode being separate, unchecked work.
- **One construction gets around it with full-rank noise: noise-cancelling polarization (NCP).**
  - The honest reference runs one plain int8 GEMM of inner dimension 3k on three noised copies of A and B. The noise cancels inside the accumulator, so the output is exactly A·B, with no decode.
  - At zero input the adversary saves only the single checked step that the known output fixes: 0.13% at 4,096², 0.008% at the milestone shape.
  - Under its named conjecture TT_NCP(0.5%), γ ≈ 0.51% at the milestone and 0.69% at 4,096² (after Daniel's 03:35Z W1 decision to price sub-word extraction), the first design found that reaches γ ≤ 1% at a transformer shape under worst-case inputs. It needs k ≥ 1,067.
  - Daniel adopted it on 28 Sep (§5). Afterwards the rule on P was hardened to checkpoint independence, and the Lean chain was completed, with 104 signed pins. A GPU falsification benchmark found nothing below 0.995 of honest cost (§6).
  - The cost is about 3× arithmetic and about 394× hashing per useful MAC.
- **Everything else fails, or is dominated by NCP.** That covers non-linear encodings, checked decodes with fresh noise, verifier or beacon secrets, timed challenges, input commitment, and a noise-free transcript with a non-degeneracy check.

## 1. The barrier

**Theorem B0** (Proved: Lean `Pouw.Barrier.Proofs.generic`, with a satisfiability witness).
- **Statement.** Take any cost model, protocol and domain. Suppose that at one admissible input x_0 a program commits every unit's checked values and useful output correctly, for every oracle and salt, at cost c_0. Then the γ-gap game fails with probability 1 for every γ < 1 − c_0/W_ref.
- **Why:** W_ref reads only the layout, never input values.
- **Degenerate inputs:** an input is degenerate when the useful output there is a known constant or cheap. A = 0 or B = 0 is the canonical case.

**Classification** (Proved in an abstract model where a plain product costs m·k·n; each class has a protocol-side witness):

| Class of encoding | Lower bound on γ | What a way out must break |
|---|---|---|
| (a) One checked noised product, useful output by a separate decode. Covers additive, affine and any linear encoding | 1 − 1/p when W_ref ≥ p·W_mm: 1/2 for a decode by plain GEMMs, 2/3 for the standard decode | The decode lies outside the checked values |
| (a′) Lookup-table (S-box) encodings with a cheap separable correction | Reduce to (a): the tables must be affine on int7 (Lean `tablesAffine`) | Same as (a) |
| (b) t checked products whose final values give A·B through a known relation, checked only at their final values | 1/t | The relation fixes one whole checked value |
| (c) Running-sum transcripts at depth d of products whose total inner dimension is K, with A·B a free linear function of them | d/K (Lean `segment`, `oneSegment`) | The known output fixes the final segment; this is unavoidable |

Only class (c) is compatible with γ ≤ 1%. The classification is not exhaustive.

**Consequences for design:**
- Every unit of honest work must produce checked values that stay costly at degenerate inputs.
- The useful output must fall out of those values at no extra cost.
- Products checked only at their outputs are not enough, even with restricted inputs. The zero-input operands have headroom, so one Strassen level saves about 12% of an output-only product (red team).

## 2. The construction: noise-cancelling polarization (NCP)

~~~text
E_1 ∈ [−31, 32]^(m×k)    uniform, per unit, from H(s, index, com(A_u), w)
F_1 ∈ [−31, 32]^(k×n)    uniform, per (epoch, weight), from H(s, w)
P                        a fixed public word-granular permutation (it permutes aligned 4-entry words and keeps
                         the order inside each word), derived from a public seed (then repaired twice: v1.1,
                         see below), whose
                         non-final checkpoint matrices M_τ are linearly independent (at zero input each
                         checked value is e_iᵀ·M_τ·f_j). This implies the step rules π(S) ∩ S = ∅,
                         π(S) never a step, and P² ≠ ±I
E_2 = E_1·P,   F_2 = −P·F_1,   E_3 = E_1 + E_2,   F_3 = F_1 + F_2

A·B = [A + E_1 | A + E_2 | −(A + E_3)] · [B + F_1 ; B + F_2 ; B + F_3]
checked values: route U's accumulator (decided 28 Sep 07:40Z with the red team, Phase 10), mod 2^32,
                block-major, after every 16-deep step:
                C^U_t = c_0 + Σ_{l < 16t} (X + β)_{:,l} · Y_{l,:},   c_0 = −β·colsum(Y) = −3β·colsum(B),
                X, Y the stacked operands above, β = 128 (129 allowed; see below). C^U_T = A·B, and
                C^U_t = C_t − β·𝟙·(Σ_{l ≥ 16t} Y_l), where the shift is public per-weight data
~~~

**Why it is correct.**
- The A·F and E·B terms cancel because the noises sum to zero.
- The E·F terms cancel because E_1·F_2 + E_2·F_1 = −E_1·P·F_1 + E_1·P·F_1 = 0.
- With int7 A and B, every operand lies in int8: at most [−127, 126].
- Proved in Lean: `Pouw.NCP.cancel`, `stacked`, `wrap`, `range`.

**Why it escapes the barrier.**
- There is no decode: the useful output is the accumulator.
- At A = B = 0 the three blocks' running sums are different products of full-rank uniform matrices. Per step, the third block equals the first two plus a cross term of inner dimension 2d, so computing it directly is cheapest.
- The only saving is the final value, which the known output fixes: d/(3k). Lean `segmentLead` proves that this saving is available.
- The red team's relation search found nothing else below the per-word floor of 16 units per checked word. It covered copies, one-add words, rank-1 increments, Strassen and Karatsuba across the blocks, FP32 routes, tables, grinding and lotteries.

**The structure of P is the attack surface** (red team, findings N1 and NA1):
- A step-aligned involution saves 52%, and a step-preserving P in interleaved order 33%.
- A designer-chosen P can pass a weak rule and still lose: a step reversal saves 50%, and adjacent-step swaps 29%.
- An involution (P² = I) that passes the step rules still makes one extra checked value free: the end of block 2 is E_1·(I − P²)·F_1 = 0 at zero input. That doubles the floor to 2d/(3k), 1.04% at k = 1,024 (red-team P2-1).
- The step rules are not enough (Lean counterexample `admissibleExtraIdentity`, 28 Sep 02:10Z). Some P pass all three clauses (disjoint from every step, never mapping a step onto a step, P² ≠ ±I) yet map a union of 64-index blocks onto itself with P² = ±I there. At zero input that makes about k/64 + 1 checkpoints per output entry free, identically zero or the sum of two earlier checkpoints: about 8.5% at k = 4,096.
- A weaker fix is not enough either (red-team Phase 3). 'No checkpoint equals 0, ±M_a or ±M_a ± M_b' misses a twisted-block P with 189 longer linear relations, some sharing intermediates across output entries, which saves 8.1% under W1.
- The fix: block-major order, and a fixed public P whose **non-final checkpoint matrices are linearly independent**. That rules out every linear shortcut, whatever its length or coefficients. It is checkable by script: a fingerprint rank computed mod a prime can only undercount, so full rank certifies it. It takes about 7 s at k = 4,096. The production P for k = 4,096 (SHA-256 `42cea286…`) and the shift by 24 are certified full rank (767 of 767), with only the final value free: 0.13% = d/(3k). Formalizing the rule, and a satisfiability witness for it, is in progress. It costs the honest reference nothing, and it makes the permutation an oblivious, free data move under W1.

**Numbers** (Derived: `internal/pouw/new-crypto/ncp-accounting.md`, granted by the red team with its conditions applied):

| | Milestone shape (4096, 65536, 65536) | Transformer shape (4096, 4096, 4096) |
|---|---|---|
| γ under TT_NCP(0.5%) | 0.51% (route U) | 0.69% (route U, sub-word extraction priced; 0.66% before) |
| Free final value, inside γ_0 | 0.008% | 0.13% |
| Honest arithmetic Ω | ≈ 3.0 | ≈ 3.0 |
| Hashing per useful MAC | ≈ 394× | ≈ 394× |
| Real time of the honest kernel against the bare m·k·n GEMM (measured at 4,096²) | — | 3.74–3.97× in cycles, 4.2–4.9× in wall time (power-capped at 450 W) |

- **Route U** forms the operands as biased unsigned bytes and runs u8 × s8 tensor-core instructions, with the bias correction in the accumulator's initial value. Measured on an RTX 4090 (28 Sep, runs `r20260928-014051-da08` and `-014438-1d3e`): u8 × s8, s8 × u8 and u8 × u8 `mma` run at exactly the s8 × s8 rate, 1,024 MACs per SM per clock at k32 and 1,023.3 at k16, as native IMMA instructions. So route U stands.
- **Route S** needs only s8, but forms the operands with byte arithmetic packed into 32-bit registers, which costs more. It is the fallback, giving 0.53% and 0.92%.
- **The honest kernel measured:** a (4096, 12288, 4096) m16n8k16 GEMM with every accumulator read once per 16-deep step. It runs at 615–638 MACs per SM per clock, that is 3 × 1.25–1.32 in cycles against the bare 4,096² GEMM. In wall time it is 4.2–4.9×, because the reads push the card deeper into its power cap (about 2.0 GHz against 2.35 GHz). Hashing and operand forming are not included.

**The W1 change of 28 Sep 03:35Z: sub-word extraction priced like PRMT.** Daniel decided that any instruction or access that extracts, inserts or rearranges fields narrower than a 32-bit word costs 16 units per word it produces, on both sides.

- **The honest reference, route U** (units per activation position; the coordinator's recount in `internal/pouw/new-crypto/ncp-accounting.md`):
  - the two noise fields E_1 and its complement, taken from hash output by one LOP3 per 4 entries each: 8;
  - A's complement, by one LOP3: 4;
  - the three packed adds, with no carries: 12.

  That is 24 in total, against 20 before. The zero-input adversary pays 12, since the constant bias goes into the accumulator's initial value.
- **The permutation P must be word-granular.** It permutes aligned 4-entry words and keeps the order inside each word, so forming E_2 = E_1·P moves whole registers, which stays free. A byte-granular P needs PRMT byte assembly, adding 16–24 units per position (γ ≈ 0.83–0.89% at 4,096²).
- **A word-granular P passes the rule.** The coordinator's check, `internal/pouw/new-crypto/ncp-wordp-check.py` with the red team's fingerprint code, used the seed `pous-pouw-ncp-Pword-v1` and 3 repair swaps at k = 4,096. It passes the three step clauses and is certified independent: span rank 767 of 767, and T − 1 at k = 256 and 1,024 too, with only the final value free and no scaled-FFMA or rank-1 hits. The Lean witness, the shift by 24, is already word-granular. The red team is re-certifying.
- **γ, conservative reduction:** Ω* − 1 ≈ 24/(3n) = 8/n. That gives γ ≈ 0.69% at 4,096² (0.66% before) and 0.51% at the milestone shape (unchanged). If activations arrive unbiased, biasing them adds about 12 units per position, for γ ≈ 0.79% at 4,096².
- **The adversary side.** The packed-FFMA route (two products per FP32 instruction) now pays for its packing. So Theorem D's residue A1 needs only c = 2, about 2.7× below the best known algorithm.
- **The falsification benchmark is unaffected.** Its device kernel (`code/pouw-ncp-falsify/ncp.cu`, `k_ncp`) loads operands only as 128-bit vectors and packed 32-bit registers. Byte-level operand forming happens on the host, outside both sides' count, and is priced separately above. Pricing sub-word moves can only raise an adversary's cost, so its conclusions stand (coordinator check, 04:25Z; the red team flagged the question in Phase 6).

**The assumption TT_NCP(γ_0)** (Assumed; a new concrete conjecture).
- **Statement.** For the distribution above, in the γ-gap game with free unbounded preprocessing and q hash calls, the running sums of the correct units cost at least (1 − γ_0)·3·m·k·n, except with probability ε(q). This is TT's form with the credited work tripled. The Lean states it as `Pouw.NCP` `TT_NCP`, with the side condition γ_0 ≥ 16/(3k), and reduces the game to it (`gammaFromTTNCP`). At γ_0 = 0.5% the side condition means k ≥ 1,067, so the NCP domain uses k ≥ 1,088 with 64 ∣ k, or k ≥ 2,048 among powers of two. The benchmark confirms it: at k = 1,024 the free final value alone costs 0.52%.
- **Its class.** It is a structured conjecture, not a uniform one (red-team N2). At zero input the transcript has [KW]'s low-rank form, but the core rank is k, the full inner dimension of the useful product, not 16. Milestone 1's TT has rank 16 at depth 16; here the rank exceeds the depth by a factor of k/16.
- **Why it can't be uniform.** A uniform-operand assumption cannot give γ < 1/2 (Lemma 1, part 2).
- **The evidence:**
  - the per-word floor at depth 16: every INT32 or tensor-core instruction costs at least 16 units per word it outputs, exactly what the honest reference pays;
  - the red team's relation search;
  - the design conditions above.
- **Witnesses:**
  - consistency: `ttncpWitness`;
  - a restricted model where the bound depends on the noise: R_word-NCP under checkpoint independence (§6);
  - the full lead instance with independence: `leadIndWitness`.

## 3. What does not work

All of these were checked by the red team:

| Route | Outcome | Why |
|---|---|---|
| Multiplicative masks, mixed (A + E)·M, wraparound, prime-field CRT, S-boxes | γ ≥ 1/6 to ≈ 1 | int8 forces signed permutations, which map A = 0 to 0; every other variant leaves an unchecked recovery |
| Checked decode with full-rank fresh noise at every level | Padding only: 1% needs about 198 noise products | Each level doubles the products |
| Checked decode with rank-16 fresh noise at level 1 (CD1) | γ_0 + 0.17% at the milestone, γ_0 + 2.4% at 4,096² | It survives at the milestone on its own conjecture, but NCP dominates it at both shapes |
| Beacon or verifier secrets, masked outputs | ≥ 50% | At zero input the output is 0 whatever the secret |
| The verifier performing the decode online | ≈ 0.5%, but excluded | The verifier would compute a full product per unit online, which breaks sampled verification |
| Timed challenges, deadline pipelines | ≥ 50%, or dilution only | A deadline changes when work happens, not whether work with a known result is needed |
| Inputs committed or bound before the noise | ≥ 50% | Binding is not non-degeneracy |
| Input restriction (rank or entropy checks, chain consistency) with full-rank noise | ≥ 6.2% | The unchecked output product is open to Strassen |
| A noise-free transcript with a verifier-checked non-degeneracy predicate | Refuted | Rank-1 and two-term row structures pass the predicate and save 47–49% |

## 4. Comparison

| | Milestone 1 (D1, low-rank noise) | NCP (full-rank noise) |
|---|---|---|
| Noise | rank 16, outer {−3..3}, inner ±1 | full rank, uniform 6-bit |
| Named conjecture | TT(0.5%); zero-input core rank 16 at depth 16 | TT_NCP(0.5%); zero-input core rank k at depth 16 |
| γ at the milestone | 0.85% | 0.51% |
| γ at 4,096² | 4.6%, and at least 1.89% for any additive-noise decode | 0.69% (route U, measured at full rate) |
| Honest arithmetic | ≈ 1.004× | ≈ 3× |
| Hashing per useful MAC | 131× | 394× |
| Lean | 55 pins, granted | 104 pins in all, the barrier and NCP chain included, granted and signed; `check.sh` passes at 1,912 declarations |

## 5. Decisions (Daniel, 28 Sep 01:23Z: all three accepted at their defaults)

1. **Adopt NCP as the full-rank-noise construction, with TT_NCP(0.5%) as its named conjecture.** *Decided: yes.* NCP is the main candidate for transformer shapes, and milestone 1's low-rank design (D1) is kept as the baseline.
2. **Hashing for an NCP build.** At depth 16, NCP hashes about 394× per useful MAC, three times milestone 1's 131×, which was accepted for milestone 1 only. Depth 32 halves that, but loses the per-word tightness argument and brings Strassen with FP32 adds to break-even. *Decided: about 400× hashing at checked depth 16 is accepted for the first build. Hashing reduction (folds) stays a separate research item: nonlinear folds cost 0.5–2× the GEMM and need their own assumption.*
3. **The honest arithmetic of about 3×.** *Decided: accepted.* It is intrinsic: at least three products are needed for an exact cancellation with scalar coefficients (two are impossible). Whether a matrix-coefficient scheme can go lower is open.

## 6. Follow-ups after the decisions (28 Sep, 01:26–03:12Z)

All four items Daniel asked for are done, and each was red-teamed.

**1. The final NCP Lean pass and a stronger witness.**
- Verity's audit passes on 104 pins, with `leanchecker --fresh` and the three standard axioms, and the red team signed every pin as named statement reviewer.
- **The rule on P, pinned:**
  - three step clauses (no step overlaps its image, no step's image is a step, P² ≠ ±I), each shown to reject a permutation the others accept;
  - and the rule that carries the security: **checkpoint independence**, meaning the non-final checkpoint matrices M_τ are linearly independent.
- **Why independence, not the clauses.** Two red-team attacks break the weaker rules:
  - a Lean counterexample (`admissibleExtraIdentity`) passes all three clauses, yet makes 1 in 12 checkpoints free: 8.3% under W1;
  - a twisted-block P also passes the rule that no checkpoint is 0, a copy or a two-term sum of earlier ones, and still saves 8.1% through longer relations.

  Independence excludes every linear shortcut.
- **The stronger witness.** In the restricted model R_word-NCP a checked word costs 16 fresh, 8 as an FP32 add of two words, 0 as a copy or a constant.
  - **Reduction.** A rule is an identity in the noise exactly when the coefficient matrices satisfy it (`reductionIf`, `reductionOnlyIf`).
  - **Floor.** Under independence the only identities are the final values, so TT_NCP holds in that model, except with probability N·2^−(m·n·(γ_0·3k/16 − 1)) (`ncpFinalOnlyInd`, `ncpWordFloorInd`).
  - **Witnesses.** Independence has a structural Lean witness: the shift by 24, for every k ≥ 1,024 with 16 ∣ k (`independentWitness`). The whole lead instance with independence is jointly satisfiable (`leadIndWitness`).
- **The chain reaches the protocol's actual checked values** (`Pouw.NCP.Chain`).
  - The checked values are the integer running sums wrapped mod 2^32, and identities transfer (`paramsYLink`, `wrapIdentity`, `wrapFinalOnlyInd`).
  - Every running sum fits in int32 for worst-case int7 inputs at k ≤ 2^16: at most 20,480·k (`int7Int32`).
- **The production P for k = 4,096.** It is seed-derived and deterministically repaired, with SHA-256 `42cea2860372d09d2241d82317b5176151ffd6043e1d8224c09d7050b013dd18`. It passes the three clauses, and independence is certified by script: its fingerprint rank is full, 767 of 767, and a rank mod a prime can only undercount. It is not proved in Lean.
  - **Superseded after the 03:35Z W1 change.** That P is byte-granular. Its replacement is word-granular, from seed `pous-pouw-ncp-Pword-v1` with 3 repair swaps, SHA-256 of its entries as 2-byte little-endian integers `24e68f30edbe538e2842266ac6b917a8a0ccf3ee0b4f8bf2cb1d8fe5c5943854`. It is certified independent the same way, 767 of 767. The red team is re-certifying it.

**2. The u8 × s8 measurement** (RTX 4090, USD 0.15). u8 × s8 runs at the full s8 rate, so route U stands. γ at 4,096² is 0.66% under the earlier W1, and 0.69% once sub-word extraction is priced (below). The honest kernel costs 3.74–3.97× the bare GEMM in cycles, and 4.2–4.9× in wall time under the 450 W cap.

**3. The falsification benchmark** (RTX 4090, USD 0.23; `internal/pouw/new-crypto/ncp-falsify.md`, code in `code/pouw-ncp-falsify/`).
- **Result.** For independent P, including the production P, nothing reaches below 0.995 of honest cost at 4,096². Every route matches the honest digest, 171 of 171 plus the reruns.
- **The routes and their W1 cost against honest:**
  - skipping the known final value: exactly 1 − d/(3k);
  - block 3 through the cross term: 1.66–2.05;
  - Strassen within steps: 3.3;
  - int4 limbs: 5;
  - mixed dp4a: 1.19, at 0.85× the wall time, which is capacity rather than cost.
- **The positive controls all fire:**
  - step reversal: 0.50;
  - a step involution: 0.67;
  - an involution passing the step rules: 1 − 2d/(3k);
  - the Lean counterexample: 0.917.
- **Domain.** TT_NCP(0.5%) needs k ≥ 1,067 (k ≥ 1,088 with 64 ∣ k, 2,048 among powers of two). At k = 1,024 the free final value alone costs 0.52%.

**4. GPU spend.** USD 0.38 across these follow-ups, and USD 0.89 across all PoUW rounds this session. Every `vy-pous-pouw-*` pod is terminated.

**Still open** (from the red team's final verdict table):
- TT_NCP itself is Assumed.
- In the restricted model, the noise hypothesis for the actual checked values must be stated with targets mod 2^32 (red-team P5-1).
- The step from oracle answers to uniform noise is not formalized.
- The restricted model's caveats: it is non-adaptive, and it has no tables, rank ≤ 1 increments, FFMA with a scalar, or cross-unit rules. The benchmark and scripts found no instance of the missing routes.
- The production P: a Lean proof of independence at k = 4,096, and a certified P for every production shape.
- Route U's checked values in Lean (decided 07:40Z; being built in `internal/pouw/new-crypto/route-u/`, with re-pinning to follow and the red team as named statement reviewer).
- A general lower bound for class (a) decodes.
- Research:
  - fewer than three products using matrix coefficients;
  - folds that cut NCP's hashing without an extra assumption.

**Planned next step: Theorem D as TT_NCP's backup** (from [milder-assumptions.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/milder-assumptions.md), started 03:40Z).
- **The survey's finding.** None of the milder assumption classes can replace TT_NCP. But Winograd's row-rank bound becomes tight on the 4090, because every priced instruction other than the FP32 pipe costs at least 16 units per output value.
- **Theorem D.** Under checkpoint independence it proves TT_NCP's bound, γ_0 = 16/(3k), for every attack that avoids the FP32 pipe and representation tricks.
- **The residue.** Two named assumptions remain:
  - A1, multiplicative complexity for the FP32 pipe;
  - A2, an AGM-style statement that representation effects don't help.
- **The survey's recommendation:** keep TT_NCP(0.5%) as the named conjecture, with Theorem D as its Lean backup.
- **Running now:** the red team attacks Theorem D's reduction chain, and the Lean worker formalizes it in `Pouw.Dimension`, with A1's constant c as a parameter.
- **Decided by Daniel (03:35Z):** W1 prices sub-word extraction like PRMT, so A1 needs c = 2, a margin of about 2.7× over known algorithms (c = 4 would have left about 1.35×).

## Sources

Working reports in `internal/pouw/new-crypto/`:
- `barrier.md`: the barrier and its Lean;
- `ncp-accounting.md`: NCP's W1 schedule;
- `escapes-encodings.md`: encodings and checked decodes;
- `escapes-protocol.md`: secrets, timing and input commitment;
- `red-team.md`: every verdict, with its scripts `red-team-ncp.py`, `red-team-fixedp.py` and `red-team-nd.py`.

Lean: `lean/submissions/pouw/Pouw/Barrier/` and `Pouw/NCP/`.

## Decided 28 Sep 07:40Z: route U's checked values and P v1.1 (the MVP's questions; with the red team, Phase 10)

- **The checked values are route U's accumulator**, C^U above, not the unbiased running sums.
  - *Why:* the signed accounting (`ncp-accounting.md`, γ ≈ 0.694% at 4,096²) always assumed it. Honestly producing the
    unbiased sums costs 36 units per position, not 24, which puts γ at 1.08% at n = 2,048.
  - *What transfers:* C^U differs from C by public per-weight data (in V₀), so every bound proved mod V₀ transfers
    exactly: independence, MinRank, Theorem D, `algBoundCausal`, the mixing lemma and `LiftMinRank`.
  - *The conjecture:* TT_NCP(0.5%) is restated over C^U, since neither form implies the other in W1 cost. No known
    attack helps against C^U more than against C, and the step involution is harder against C^U.
  - *The honest schedule:* 6 instructions per 4 positions from int7 A, 24 units per position, checked byte for byte by
    the red team.
- **β is a parameter.** The first build uses β = 128. β = 129 costs 20 units and gives γ 0.823% at n = 2,048, but only
  if the kernel's SASS issues the IADD3 with two negated sources as one instruction. β ∈ {127, 128, 129} keep block 3
  in u8.
- **P is v1.1:** v1 plus a second repair (`internal/pouw/new-crypto/pword-repair2.py`) that enforces MinRank's
  hypothesis (c): no cycle of π² inside a step, so no 2-cycle.
  - It fires only on a violation, so P is unchanged at k = 4,096 (`24e68f30…3854`) and 11,008 (`a57ea054…40eb8`).
  - v1 violates (c) at 385 of the MVP's 1,008 values of k, among them 1,088 (now `536757a2…546f`) and 2,048 (now
    `7f00a9b7…9732`).
  - Script-certified at all four k: hypotheses (a), (b) and (c); λ₃ = 32 exactly; MinRank = 16; full independence
    rank.
- **Details:** `internal/pouw/new-crypto/route-u-checkpoints.md`.

## Overnight, 28 Sep to 09:55Z: the Theorem D chain in Lean, and what A2 turned out to be

Consolidated in `docs/pouw/overnight-report.md`.
- **Proved in Lean and signed by the red team** (220 pins):
  - Theorem D, with causal A;
  - the mixing lemma;
  - Theorem 1, the quadratic closed FP32 pipe at 16 per dimension;
  - the route-U transfer.
- **Staged:** the open pipe, where FP32 may read tensor-core words, still at 16·D.
- **Still open:** FP32 merges (`A1_nonquad`).
- **A2:** once restricted to the checked words, so that it can't be refuted (red-team P9B-1), A2 is equivalent to the
  per-word form of the conclusion (`a2WordsIff`).
  - So the chain is evidence that no algebraic attack in these classes helps; it is not a reduction of TT_NCP to a
    milder assumption.
  - TT_NCP_U(0.5%) remains the named conjecture.
  - An embedding theorem (W1 as a formal machine `M4090`) is being scoped as the route to a genuine reduction.
