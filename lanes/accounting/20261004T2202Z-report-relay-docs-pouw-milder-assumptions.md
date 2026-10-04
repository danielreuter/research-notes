---
id: 20261004T2202Z-report-relay-docs-pouw-milder-assumptions
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/pouw/milder-assumptions.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/pouw/milder-assumptions.md`, sha256 `07445a8b947ea0d20c39c49bced8289cb7ee92d16478e992e24deee17b170a8a`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Milder assumptions for PoUW: can TT and TT_NCP be reduced to something chiller?

28 Sep 2026, 03:35Z. Research note for Daniel, PoUW workstream. Setting: [problem statement](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/problem-statement.md) (draft 3), [NCP results](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/new-crypto.md). Fixed: γ ≤ 1% jointly, worst-case inputs, W1 on an RTX 4090, no security from hashing, Lean for everything provable. Status tags as elsewhere: **Proved**, **Derived**, **Assumed**, and here also **Sketch** (argued in this note, not yet checked or red-teamed).

## Conclusion

- **No standard assumption can replace TT or TT_NCP, and §4 proves it class by class.**
  - Cryptography (LWE, LPN, DDH, one-way functions): a black-box reduction cannot see cost, so it would turn the honest reference itself into an attacker (§4.5).
  - Operation-count models: the claim is false in them, because Winograd's identity halves the multiplications of every 16-deep word (§4.2).
  - I/O, pebbling and bandwidth: the adversary regenerates hash-derived operands on chip instead of moving them (§4.3).
  - Asymptotic fine-grained conjectures: they are consistent with every constant speedup (§4.4).
  - Uniform operands: γ ≥ 1/2 (§4.1).
- **But TT_NCP's whole algebraic part is a theorem** (Theorem D, §2; a Sketch, not yet red-teamed).
  - It is Winograd's 1970 row-rank bound. It becomes *tight* on the RTX 4090 because the tensor core charges 16 units per output word however many products the word contains.
  - Take any noise-oblivious program: linear operations are free, and every other instruction costs its W1 price per output value. Each priced value raises the dimension of what the program has computed by at most one. NCP's linear-independence rule on P makes the non-final checked words need m·n·(3k/16 − 1) dimensions per unit, and fresh per-unit noise makes the dimensions add across units.
  - So, whenever every priced instruction costs at least 16 units per value, cost ≥ 3·m·k·n·(1 − 16/(3k)). That holds for every input, jointly across units, with no direct-sum conjecture. It is exactly TT_NCP's side condition γ_0 = 16/(3k), and exactly the proved free-final-word loss.
  - The condition covers tensor cores, INT32, dp4a, lookups and branches. The theorem proves away every class the red team searched: copies, one-add words, Strassen and Karatsuba across blocks, cross terms, any linear relation, int4 limbs, FP32 adds, and tables.
- **What remains is narrow.**
  - **A1** (Assumed, pure algebraic complexity): the FP32 scalar pipe, the only instruction class below 16 units per value, needs at least 2 products per checked dimension. The best algorithm I know needs about 5.4, a margin of about 2.7×. If W1's free byte moves let FFMA pack two products per instruction, the requirement is 4 and the margin about 1.35×.
  - **A2** (Assumed, algebraic-group-model style): representation effects don't help. That means FP rounding and compares as gates, sub-word tricks beyond that packing, and free hash calls on noise-dependent data.
  - **A design check and a lemma:** a min-rank rule on P (MinRank(P)) and a lifting lemma, for lotteries and partial correctness.
  - So TT_NCP ⟸ Theorem D ∧ H_16 ∧ A1 ∧ A2, where H_16 is the measured per-value price floor.
  - **Honest caveat:** given Theorem D and A1, A2 is equivalent to TT_NCP restricted to non-algebraic attacks. The gain is a much smaller, well-delimited attack surface, not a logically weaker conjecture.
- **Recommendation.**
  - Keep TT_NCP(0.5%) as the named conjecture for the first build.
  - Formalize Theorem D in Lean as its backup layer. It is routine linear algebra, and it also discharges red-team condition 5 (a restricted-model witness that prices three-input adds at 16; AlgM prices them at 0).
  - Add MinRank(P) beside the independence rule.
  - Ask Daniel whether W1 should price sub-word extraction, which decides whether A1 needs c = 2 or c = 4 (§6, question 2).
  - The same count applies to milestone 1's TT transcript (§2.6); its γ of 0.85% is unchanged, because that comes from the decode.

## Ranked candidates

Ranked by mildness: how well studied, how falsifiable, how minimal. Every surviving candidate costs NCP's own overhead and nothing more: about 3× arithmetic and about 394× hashing, with the domain floor k ≥ 1,067 at γ_0 = 0.5%.

| Rank | Statement | Kind | Well studied | Falsifiable | Reaches γ ≤ 1%? | Lean | Role |
|---:|---|---|---|---|---|---|---|
| 0 | **Theorem D + IndepRule(P)** | Not an assumption: a classical bound (Winograd 1970), plus a script-certified property of P | Yes | — (proved; P certified) | Yes, inside AlgM_16, exactly at γ_0 = 16/(3k) | Moderate, routine: span/finrank, program semantics, a 4-point evaluation lemma | The foundation (§2.3) |
| 1 | **H_16**: every non-FP32 instruction costs ≥ 16 units per output value | Hardware atomicity, precise form: the measured price table plus completeness of the sm_89 instruction list | Measured | One microbenchmark per instruction | With rank 0, for all programs that avoid the FP32 pipe, packing and representation tricks | A hypothesis on the price function | The mildest real assumption (§3.1) |
| 2 | **A1(2)**: every subspace of the checkpoint forms needs ≥ 2 products of linear forms per dimension | Concrete multiplicative complexity | The area is; this instance is not | Yes: a counterexample is an exact identity, checked on CPU | Covers the FP32 pipe if W1 prices sub-word extraction | Named Prop | Backs the scalar pipe; margin ≈ 2.7× (§2.4) |
| 3 | **A1(4)**, or its W1 form (scalar-pipe programs pay ≥ 16 per dimension with additions priced) | Same, or a restricted TT_NCP | Less so | Yes | Covers the FP32 pipe under today's W1 | Named Prop | Margin ≈ 1.35× in the clean form, ≈ 5× in the W1 form |
| 4 | **A2**: representation effects don't beat the algebraic model by more than γ_2 | An algebraic-group-model-style model assumption | The genre (GGM, AGM) is | Yes: one kernel | Yes, with ranks 0–3 | Named Prop | The honest residue; equivalent to TT_NCP on non-algebraic attacks (§2.5) |
| 5 | **MinRank(P) + a lifting lemma** | A design check plus a lemma, not an assumption once done | — | Script | Needed for the probabilistic game (lotteries, grinding) | Open | To do (§6, items 3 and 6) |
| 6 | TT_NCP⁰: TT_NCP at zero input only | One public distribution | No | Yes | Only with an input reduction, which exists inside AlgM only | Named Prop | Weaker, but can't stand alone |
| 7 | TT_NCP(0.5%) itself | Structured concrete conjecture | No | Yes: one fast kernel | Yes | Done (`gammaFromTTNCP`) | Current baseline |

**Ruled out, with proofs in §4:**
- hardware atomicity without a composition rule (§4.6);
- unit-cost-multiplication models, bilinear or algebraic, where the claim is false (§4.2);
- I/O, pebbling and bandwidth (§4.3);
- bit-level gate counts, capped at about 12.5 units per word (§3.2);
- asymptotic fine-grained conjectures (§4.4);
- LWE, LPN and all standard cryptography, by a meta-reduction (§4.5);
- uniform-operand assumptions, γ ≥ 1/2 (§4.1).

## 1. What any sufficient assumption must satisfy

Five tests, each forced by a proved fact. A candidate that fails one cannot give γ ≤ 1%, whatever its standing.

1. **It must price checked values that stay costly at a degenerate input** (Theorem B0). At A = B = 0 the useful output is known, so any work that does not feed a checked value is free. An assumption about the hardness of anything else (a hidden secret, a separate decode, a puzzle) certifies nothing at x_0.
2. **It must be about a structured distribution** (Lemma 1, part 2). Uniform operands force a separate decode, so γ ≥ 1/2. NCP's zero-input transcript is correlated on purpose: the same correlation that cancels the noise is what an attack would exploit.
3. **It must be concrete and priced per output word, not per multiplication** (§4.2 of the problem statement). In any unit-cost-multiplication model the claim is false: Winograd's 1968 inner-product trick computes a 16-deep dot product with 8 multiplications (the pre-sums are amortized over a row or column), and Strassen cuts the rank of every step. The honest reference is optimal only because the tensor core charges 16 units per 32-bit output word, however many products it contains.
4. **It must be joint.** Units share F_1 per weight and share preprocessing; single-instance hardness does not compose by itself, and tensor rank is not additive in general (Shitov 2017 refuted Strassen's direct-sum conjecture). A useful assumption must come with its own composition, or be additive for a structural reason.
5. **It must be tight to within 1 − 16/(3k).** The free final value is a proved loss (Lean `oneSegment`, `segmentLead`), so the assumption's own slack plus 16/(3k) must fit under γ_0 = 0.5%.

Test 3 rules out every operation-count model, test 1 rules out all of standard cryptography, and test 4 rules out any per-instance statement without a composition lemma. What survives is a statement about *how many priced output words a program needs* to produce a family of correlated bilinear forms. Linear algebra can count that exactly.

## 2. Theorem D: the dimension bound (Sketch)

### 2.1 The observation

At any input, each checked word of an NCP unit is a polynomial in the unit's noise (E_1, F_1) with a fixed quadratic part:

~~~text
y_{i,j,τ} = q_{i,j,τ}(E_1, F_1) + (terms of degree ≤ 1 in the noise, depending on A, B)
q_{i,j,τ} = e_iᵀ · M_τ · f_j        e_i = row i of E_1,  f_j = column j of F_1
~~~

M_τ is the k×k checkpoint matrix (the doc's M_τ; at zero input the checked value is exactly e_iᵀ M_τ f_j), and M_T = 0 at the final step τ = T = 3k/16, because the noise cancels. The quadratic part **does not depend on A or B**. The linear-independence rule on P says that {M_τ : τ < T} are linearly independent. It is certified by fingerprint rank: 767 of 767 at k = 4,096 for the production P and the shift by 24.

Now count dimensions. A program's instruction outputs are functions of the noise. A Q-linear instruction (add, subtract, multiply by a constant, copy, exact conversion) keeps them in the span of what came before. Any other instruction outputs *one* new function, so it raises the dimension of the span by at most 1. The checked words need the span to contain every q_{i,j,τ}. So:

~~~text
number of non-linear output values  ≥  dim span{ q_{i,j,τ} }   (mod constants and affine functions of the noise)
~~~

### 2.2 The model AlgM_16

- **Programs.** Straight-line and noise-oblivious: the instruction sequence may depend on A, B, P, the shapes and any preprocessing, but not on noise values. Noise-dependent control flow is covered separately (§2.5).
- **Free instructions.** Every instruction whose output is an exact Q-linear combination of earlier values and constants, on every noise value in the domain. This is more generous than W1, which charges 8–16 units for adds. It also lets the adversary compute every A·F and E·B term for nothing.
- **Priced instructions.** Everything else, one output value each, at its W1 price: products, `mma` words, bit operations, lookups, selects, wrapping adds, conversions with rounding.
- **The hypothesis H_16.** Every priced output value costs at least 16. It holds for every tensor-core instruction (the per-word floor: 2,048 units per 128 words for int8 m16n8k16; the same or more for every int4, FP16 and FP8 shape in the price table), for every INT32-pipe instruction (16), for IDP4A (16), and for W1's data-dependent accesses and branches (16 per lane per word). Among priced instructions it fails for exactly two things: the FP32 pipe (8 units), and sub-word fields extracted by W1's free oblivious byte moves (§2.4). Hash calls on noise-dependent data are free in W1 and are not counted here; they belong to A2 (§2.5).
- **Correctness.** The outputs equal the checked words as functions on the whole noise domain. The probabilistic version is §2.5.

### 2.3 Statement and proof

**Theorem D** (Sketch). In AlgM_16, any program that outputs every non-final checked word of a set U of NCP units correctly costs at least

~~~text
∑_{u in U}  16 · m_u · n_u · (3k_u/16 − 1)  =  ∑_{u in U}  3·m_u·k_u·n_u · (1 − 16/(3k_u)),
~~~

for every choice of inputs fixed before the noise is derived, jointly over U. So TT_NCP(γ_0) holds in AlgM_16 with γ_0 = 16/(3k) exactly: 0.13% at k = 4,096 and 0.008% at the milestone shape.

The inputs must be fixed before the noise, and the protocol already guarantees it: E_1 is derived from com(A_u) and F_1 from the weight id. With A = −E, the operands would vanish. Re-deriving the noise by changing commitments is grinding (§2.5).

*Proof.*
1. **One dimension per priced value.** Let V_t be the span of the first t output values together with the constant function and the noise coordinates. A free instruction leaves V_t unchanged, and a priced one adds one vector. So dim V_t − dim V_0 ≤ the number of priced outputs.
2. **The targets need D dimensions.** Each checked word equals q_{i,j,τ} plus an affine function of the noise, so it lies in V_end only if q_{i,j,τ} ∈ V_end. We need dim(span{q} mod V_0) = D.
   - For a fixed (i, j), the q_{i,j,τ} with τ < T are linearly independent polynomials, by the independence rule.
   - Different (i, j), and different units, use disjoint monomials e_{i,a}·f_{b,j}. Rows of E_1 differ within a unit, and E_1 is fresh per unit, even where F_1 is shared by weight. So the dimensions add, which is the whole joint composition, for free.
   - Bilinear polynomials have degree at most 1 in each variable, and every variable ranges over 64 values. By the Combinatorial Nullstellensatz (Alon 1999), polynomial independence therefore implies independence as functions on the grid, and independence from affine functions.
   - Hence D = ∑_u m_u·n_u·(T_u − 1).
3. **Price.** By H_16 each priced output costs at least 16. ∎

**Why this is the right statement.**
- **It is tight.** The honest reference pays exactly 16 per checked word, and the only word it pays for that Theorem D doesn't count is the final one, which the barrier makes free. So the bound equals the proved loss d/(3k), with no slack.
- **It is input-uniform.** The quadratic part ignores A and B, so worst-case inputs, degenerate ones included, give the same bound. That is the reduction from arbitrary inputs to zero inputs that §4.4 of the problem statement calls open, obtained inside the model.
- **It is joint by additivity of dimension**, not by a direct-product conjecture. Test 4 is met structurally.
- **It explains the independence rule.** The rule is exactly the hypothesis that makes D full. Every P that the red team broke (involutions, step reversal, twisted blocks, the Lean `admissibleExtraIdentity`) breaks it by lowering dim span{M_τ}, and Theorem D's bound drops by exactly the lost dimensions. Where the benchmark ran the attack, the measured cost equals the lowered bound exactly. For the involution passing the step rules, one extra checkpoint per entry is identically 0, giving 1 − 2d/(3k) = 0.9974, the benchmark's control. For the Lean counterexample, about k/64 + 1 checkpoints per entry drop out, giving 0.917, the measured "saving of exactly 1/12".

**What it closes, by proof and inside the model.** Every class in the red team's relation search: copies, one-add words, Strassen and Karatsuba across blocks on tensor cores, cross terms of any inner dimension, any linear relation of any length, FFMA with a scalar coefficient (linear, so free), FP32 adds (free, and useless), int4 limbs (re-parametrizing the noise linearly preserves D, and every int4 `mma` word costs 16), mixed tensor-core and dp4a execution, wrapping-add tricks (a wrapping add is a priced INT32 output), and online or pre-salt tables (a data-dependent load is a priced output value, at 16).

### 2.4 What Theorem D leaves open: the scalar pipes (A1)

H_16 fails for two routes, and they are the whole algebraic residue.

- **FP32-pipe products.** FFMA/FMUL cost 8 per product. HFMA2 is Unverified: at the Ada datasheet's FP16 = FP32 non-tensor rate it is 16 per instruction, 8 per half-product.
- **Packed fields.** W1's free oblivious byte moves can split one register into fields. FFMA with a packed operand, a·(b_1 + 2^12·b_2), gives two exact products of 6-bit noise values (at most 11 bits each) for 8 units, 4 per product; packed IMAD gives 8 per product.
- **Tensor-core words cannot pack** (Packing lemma, Sketch). Separating two dot products inside one int32 accumulator needs an operand scale of at least about 2^15, and int8 and int4 operands allow at most 127.

For these routes the degree-2 part of a product's output is a single product of two linear forms, so the count becomes multiplicative complexity. Write L(V) for the least number of products of linear forms (in all noise variables, with free linear combinations) whose span contains a space V of quadratic forms. Then:

~~~text
cost ≥ 16·|B| + c_s·|R|,   with |B| ≥ D − dim(T ∩ span R) and |R| ≥ L(T ∩ span R),
~~~

where B is the set of priced outputs at 16 or more, R the set of scalar products at c_s = 8 (4 when packed), and T = span{q}. So TT_NCP in AlgM_4090, the model with the full price table, follows from:

**A1(c, γ_1)** (Assumed; pure algebraic complexity). For every subspace V ⊆ T, L(V) ≥ c·(1 − γ_1)·dim V, with c = 16/c_s: that is, c = 2 unpacked and c = 4 if packing is free.

**What is known about A1.**
- **Proved for one output entry's whole span, and for single words.**
  - L(V) ≥ R(V)/2 for bilinear V (Strassen's quadratic-to-bilinear factor 2), and R(V) is at least the e-flattening rank of V.
  - For V the whole span of one (i, j)'s checkpoints, that rank is k, because block 1's final checkpoint is the identity, while dim V = 3k/16 − 1. So L(V)/dim V ≥ 8/3, which meets c = 2 but not c = 4.
  - For a single word, or any nonzero element of rank ρ, L ≥ ρ/2, which is 8 at ρ = 16.
  - For proper subspaces of one entry's span, the ratio needs each subspace's flattening rank, a checkable but unproved condition.
- **Open, across entries.** Sharing across rows and columns (Strassen, and Winograd's row pre-sums) is where the question lives. The best known quadratic algorithm for ⟨m,16,n⟩ I can construct is 3 Strassen levels followed by Winograd on the depth-2 remainder, 343/64 ≈ 5.4 products per output word, with free additions. Known lower bounds give only about 1 per word (the output flattening). So A1(2) has a margin of about 2.7× over known algorithms, and A1(4) only about 1.35×.
- **With additions priced as W1 prices them**, the same algorithm costs roughly 5.4 × 4 plus 7–8 FP32 adds per word, about 80 units against 16. That is a margin of about 5×, but it is no longer a clean algebraic statement.
- **Bounded coefficients.** Values must stay exact in FP32 (below 2^24), which excludes border-rank constructions and their large coefficients.

A counterexample to A1 is a finite algebraic identity, which a computer algebra system can check exactly, with no GPU.

A1 is stated for programs that are correct as formal polynomial identities, where degree-2 parts are well defined. Programs correct only as functions on the grid through high-degree identities (interpolation, x^64-type reductions) are representation effects and belong to A2.

### 2.5 What Theorem D leaves open: representation and probability (A2)

Three effects fall outside AlgM. Each needs its own lemma or assumption.

1. **Partial correctness, lotteries and grinding.** The game needs correctness only at the real noise, and the adversary can grind q hash calls to re-roll a unit's E_1 via com(A_u).
   - A program that is right only on a subset Z of the domain needs dim(span{q}|_Z), which is smaller when some combination of checkpoints becomes affine on Z.
   - If Z is cut out by s linear conditions on the noise (probability about 64^−s per try), such a combination must have bilinear rank at most s.
   - **Proposed design rule (min-rank):** every nonzero element of span{M_τ : τ < T} has rank at least ρ, with ρ = 16 as the target. Under it, any saving needs s ≥ ρ, about 2^−96 per try, and even then it saves only the few combinations of rank at most s.
   - This is the red team's uncovered "rank ≤ 1 increments" item, restated as a checkable condition on P. The quadratic (non-linear) Z case needs a Schwartz–Zippel-type lifting lemma; open.
2. **Noise-dependent control flow.** W1 prices every instruction under a data-dependent branch at 16 per lane per word, so each executed path is a priced straight-line trace that is correct on its own sub-domain. That reduces to item 1, with branch decisions standing in for grinding.
3. **Representation effects outside AlgM:** FP32 rounding, min/max and compares used as non-linear gates at 8 units; the free sub-word moves beyond the packing counted in A1; and free hash calls on noise-dependent data. In the ideal-primitive model the last one gives only equality tests of its inputs, and those tests must be consumed by priced instructions.

**A2(γ_2)** (Assumed). On NCP instances, an M_4090 program's W1 cost is at least (1 − γ_2) times the AlgM_4090 price of some program that outputs the same checked words, on all but an ε(q) fraction of the noise.

**How to read A2 honestly.** Given Theorem D and A1, A2 is *equivalent* to TT_NCP restricted to representation-exploiting attacks. It does not make the conjecture logically weaker. What it does is shrink the attack surface, as a generic-group or algebraic-group-model proof (Fuchsbauer–Kiltz–Loss 2018) does in cryptography. Every algebraic attack is now closed by proof, and a refutation must exploit bit representation, rounding, or byte-level free moves. The known representation routes are far away: int4 limbs cost 5×, bit-slicing about 60× (a 16-deep 6-bit dot product is about 2,000 gates, at 32 gates per 16-unit LOP3), and tables are priced out by W1.

### 2.6 Consequences

- **TT_NCP ⟸ Theorem D ∧ A1 ∧ A2**, with γ_0 = 16/(3k) + γ_1 + γ_2 to first order.
- **Milestone 1's TT.** Step 1 of the proof needs only a linear map π on functions of the noise that kills V_0: then the number of priced values is at least dim π(targets). For milestone 1, take π to be the projection onto the top Walsh–monomial component in (E_L, E_R, F_L, F_R).
  - The zero-input words ∑_{l∈S_τ} (E_L E_R)_{i,l}·(F_L F_R)_{l,j} are multilinear, with disjoint monomials across (i, j, τ).
  - At nonzero input the extra terms, such as A·F_L·F_R, have lower degree, so π removes them.
  - The ±1 inner factors rule out the 4-point lemma (0 is not in {±1}), but the Walsh basis does the same job.
  - So TT's transcript part also holds in AlgM_16, at γ_0 = 0. Milestone 1's γ stays 0.85%, because that comes from skipping the decode, not from TT (Lemma 1). Sketch, like the rest of §2.
- **Red-team targets for §2**, in order:
  - an H_16 violation: a tensor-core shape or pipe cheaper than 16 per output word (for example legacy `mma.m8n8k4` f16, IMAD.WIDE, HFMA2 rates; all Unverified);
  - a subspace of T with L(V) < 2·dim V, or < 4 with packing;
  - a nonzero low-rank element in span{M_τ} for the production P;
  - a flaw in step 2's dimension count, the additivity across units that share F_1;
  - a representation trick that emits correct words below 16 each.

### 2.7 The reduction chain, for the red team

~~~text
G_γ (the game, γ = 1 − (1 − γ_0)/Ω*)
  ⟸ TT_NCP(γ_0)                                   Lean gammaFromTTNCP (Proved)
  ⟸ TT_NCP^Alg4090(γ_0 − γ_2) ∧ A2(γ_2)            definition of A2 (a named Prop)
TT_NCP^Alg4090(16/(3k) + γ_1)
  ⟸ Theorem D ∧ mixing lemma (§2.4) ∧ A1(c, γ_1)   Sketch; Lean target
Theorem D
  ⟸ IndepRule(P) ∧ H_16 ∧ one-new-dimension lemma ∧ 4-point evaluation lemma
IndepRule(P):  fingerprint rank (script, as today); a Lean witness for small k
H_16:          the W1 price table (Derived) + completeness of the sm_89 instruction list (Assumed, mild)
MinRank(P):    proposed; needed for the probabilistic version (§2.5)
~~~

The 4-point evaluation lemma replaces the Nullstellensatz, which is simpler for Lean.
- Unit vectors lie in the grid, since 0 and 1 are in [−31, 32].
- If ∑ c·q = (affine) as functions, the second difference at (u_a, u_b), (u_a, 0), (0, u_b), (0, 0) kills the affine part and returns the (a, b) entry of ∑ c·M_τ, so every entry is 0.
- Independence of the M_τ then gives c = 0.

**Classical footing.** Theorem D is Winograd's 1970 row-rank bound: computing N linearly independent bilinear forms needs at least N non-scalar multiplications. What is new is only the pricing. The tensor core charges one output word the same 16 units however many products it contains, so the weakest classical lower bound, the output flattening, becomes *tight* in M_4090. In every unit-cost-multiplication model the same bound is off by a factor of 16.

## 3. The candidate map (questions 1 and 2)

Each entry answers four questions: can it reach γ ≤ 1%, what overhead it implies, what Lean needs, and why it fails if it does.

### 3.1 Hardware-atomicity assumptions

- **Naive form: "one `mma` is the cheapest way to get a 16-deep dot product."** True as far as anyone knows, but insufficient alone: it is per-instance and says nothing about sharing across words.
  - Counterexample to sufficiency: the red team's P2-1 involution. There every word, taken alone, still needs its k16 instruction, but one word per output entry is free given the others: 1 − 2d/(3k), 1.04% at k = 1,024.
  - So atomicity must come with a composition rule.
- **Right form: H_16, a per-output-value price floor.** Every instruction other than FP32-pipe instructions and free byte moves costs at least 16 units per output value.
  - This is mostly a *measured fact* (the price table), plus one mild assumption: the sm_89 instruction list is complete, with no undocumented cheaper path. It is falsifiable by one microbenchmark.
  - With Theorem D it composes by dimension, so it reaches exactly γ_0 = 16/(3k) against all programs in AlgM_16.
  - Overhead: NCP's, about 3× arithmetic and about 394× hashing. Lean: H_16 is a hypothesis on the price function; cheap.
  - **Verdict: the mildest useful assumption in this note**, but alone it covers only Prog_16 (no FP32 pipe, no field packing, no representation tricks).
- **"The accumulator write is atomic": no hardware path produces a correct 32-bit accumulator value without a priced instruction.** This is implied by W1: oblivious moves copy, they don't compute. It adds nothing beyond H_16.

### 3.2 Unconditional lower bounds in restricted models

| Model | Reaches 1%? | Why |
|---|---|---|
| Bilinear / algebraic circuits, unit-cost multiplication, free additions | **No, and false** | Winograd halves the multiplications of each 16-deep word, so γ ≥ about 50% in the model |
| Same with unit-cost additions | **No, false** | One Strassen–Winograd level inside a step: 7 products of (m/2, 8, n/2) at 15 operations per output word (26.25mn), plus 1.75mn post-additions and mn for the running sum, ≈ 29mn against the honest 32mn. So γ ≥ about 9%, and more with further levels |
| Output-flattening / row-rank bound, re-priced per output value (Theorem D) | **Yes, in AlgM_16, tight** | Classical (Winograd 1970); the pricing is the only new ingredient |
| Tensor rank, border rank, substitution-method bounds | No | Best known for ⟨m,16,n⟩ is about mn + O(m + n), no better than the flattening; they add nothing to Theorem D and don't cover pricing |
| Red-blue pebbling / Hong–Kung I/O bounds | No | Under W1 oblivious moves are free, so an I/O bound certifies 0 units. Under additive memory pricing, the adversary regenerates hash-derived operands on chip and γ ≥ 6–29% (red-team A1). The I/O share of a compute-bound int8 GEMM is far below 99% anyway |
| Bandwidth / roofline | No | Same: it certifies bytes, not tensor-core work. 1% would need forced I/O padding, which is neither useful work nor free of hashing |
| Bit-level / Boolean circuit bounds (gate counts per output bit) | No | The zero-input checked words have only about 25 non-constant bits, while the honest reference pays for 32. The best one could get is 12.5 units per word, so γ ≥ 22%, and even that needs an unproved GF(2) independence of all bit functions |

Lean for Theorem D is moderate: finite-dimensional linear algebra (`Submodule.span`, `Module.finrank`), an inductive program semantics, the 4-point evaluation lemma, and the independence rule as a hypothesis. It needs no `native_decide`, and nothing new in Mathlib.

### 3.3 Fine-grained and algebraic-complexity assumptions

- **Asymptotic fine-grained conjectures** (ω, OMv, APSP, 3SUM, SETH). **No.** Every asymptotic statement is consistent with an algorithm that is 1% faster than the honest reference at every size, so none implies a constant (§4.4). They are also about unrelated problems.
- **Concrete multiplicative complexity: A1** (§2.4). **Yes, as a backup layer for the scalar pipes.**
  - It is a clean, explicit, falsifiable statement about one family of quadratic forms.
  - Margins: about 2.7× over the best known algorithm if packing is excluded (c = 2), about 1.35× if free packing is allowed (c = 4), and about 5× once W1 prices the additions.
  - The field is well studied, but this exact family is not.
  - Lean: a named Prop.
- **Direct-sum conjectures for rank or multiplicative complexity.** **Not needed, and risky.** The rank version is false in general (Shitov), and Theorem D's composition uses dimension, which is additive.

### 3.4 Standard cryptography (LWE, LPN, DDH, one-way functions)

**No**, by a meta-reduction (§4.5). The checked values are public, deterministic functions of the chosen inputs and the public noise. So a black-box reduction can simulate any winning adversary's outputs by running the honest reference. The winning adversary's only distinguishing feature is its cost, which a black-box reduction cannot observe or use. Hence a reduction that breaks X from a winning adversary also breaks X unaided.
- Overhead if used anyway: LWE or LPN puzzles as padding. That is not useful work, is unchecked at degenerate inputs (Theorem B0), and is priced out.
- The only cryptographic role left is the one already filled by the ideal primitive H: deriving noise and binding inputs.

### 3.5 Weaker, more local variants of TT and TT_NCP

| Variant | Weaker than TT_NCP? | Reaches 1%? | Verdict |
|---|---|---|---|
| TT_NCP at zero input only (TT_NCP⁰) | Yes: one public distribution | Only with an input-reduction lemma, which Theorem D supplies inside AlgM and which is unknown outside it | Useful as a benchmark target; Theorem D says zero input is the hardest case only in the algebraic model |
| Per-tile conditional: a step's m16×n8 increments cost 2,048 even given every other checkpoint | Local, but does not compose for cost | Only with dimension-type composition, which is Theorem D again | Subsumed |
| Per-instruction: H_16 | Yes, far milder | Only for Prog_16 | Rank 1's foundation |
| TT_NCP for scalar-pipe programs only | Much narrower | Yes, with Theorem D | The W1 form of A1: the practical backup if A1's algebraic form looks too thin |
| TT_NCP for representation-exploiting programs only (A2) | Narrower attack surface, but equivalent to TT_NCP given D and A1 | Yes | The honest residue |
| R_copy (the existing restricted-model witness) | — | Only inside its model | Subsumed by Theorem D for exact correctness; R_copy's probability bound remains the template for §2.5 |

## 4. Impossibility sketches (question 5)

Each sketch rules out a *class* of assumptions as a basis for γ ≤ 1% under the fixed constraints. None of them is a Lean theorem yet, except where a proved result is cited.

### 4.1 Uniform-operand assumptions: γ ≥ 1/2

Lemma 1, part 2 (Proved). If the checked operands are uniform, the useful output needs D = A·F + E·(B + F), which contains A·F, a second product. At A = 0 the adversary's output is 0 and it pays one product, so γ ≥ 1/2 (2/3 with the standard decode). Any assumption whose hard distribution is uniform inherits this.

### 4.2 Unit-cost-multiplication models: the claim is false in them

In any model that charges per multiplication (bilinear circuits, algebraic circuits, straight-line programs over Z), "the honest reference is within 1% of optimal" is false. Winograd's 1968 identity gives, for x, z in Z^16:

~~~text
⟨x, z⟩ = ∑_{l=1..8} (x_{2l−1} + z_{2l})·(x_{2l} + z_{2l−1})  −  ξ(x)  −  η(z)
ξ(x) = ∑_l x_{2l−1}·x_{2l}      (once per row and step, shared by all n columns)
η(z) = ∑_l z_{2l−1}·z_{2l}      (once per column and step, shared by all m rows)
~~~

That is 8 + 8/n + 8/m multiplications per checked word instead of 16, so γ ≥ about 1/2 with free additions. With unit-cost additions, Strassen inside a step still gives γ ≥ about 9% (§3.2). Checkpoints don't help, because each checked word is a fresh dot product added to the previous one. So an assumption stated in such a model is either false or silent about the tensor core. The only escape is pricing per output word, as W1 does, which is what Theorem D uses.

### 4.3 I/O, pebbling and bandwidth: the adversary regenerates instead of moving

- **Under W1**, oblivious online moves cost 0, so any I/O lower bound is a bound of 0 units.
- **Under any accounting that prices movement**, look at a degenerate input. Every operand is a function of the salt through free hash calls, and every checked value is consumed by a free hash call. Fix an output entry (i, j) and run its 3k/16 steps with one accumulator in registers, regenerating the 16 noise pairs of each step on chip. That uses O(1) fast memory and no slow-memory traffic, at the honest arithmetic cost. So the adversary's forced I/O is 0, while the honest reference, at real inputs, must read real operands.
- Hence γ ≥ the honest reference's I/O share. The red team measured 6–29% at milestone 1 (red-team A1).
- Red-blue pebbling bounds (Hong–Kung) assume the inputs start in slow memory. Free input generation voids that premise.

### 4.4 Asymptotic fine-grained conjectures: consistent with any constant speedup

Take any statement of the form "no algorithm for problem Π runs in time O(f(n)^(1−ε))" or "… in o(best known)". Scaling any algorithm's cost by 0.98 preserves every such statement. So none implies "cost ≥ 0.99·W_ref", which scaling by 0.98 violates. That is §4.2 (b) of the problem statement, made explicit. A fine-grained assumption can help only if it is concrete, with an explicit constant, and priced in M_4090, and then it is a TT-type conjecture, not a standard one.

### 4.5 Standard cryptography (LWE, LPN, DDH, OWFs): a meta-reduction

- **The claim.** No black-box, cost-oblivious reduction R derives the γ-gap game from any assumption X of the form "no efficient algorithm wins game X", unless X is easy.
- **Sketch.**
  1. R sees only an adversary's messages (commitments, chosen inputs, checked values), never its cost. So R and its analysis are the same in *every* cost model: they are valid in M_4090 exactly when they are valid in a variant M′ in which one instruction, say the int8 k16 `mma`, is 2% cheaper for the adversary.
  2. In M′, the honest reference H_0 run on zero inputs *is* a winning adversary for γ < 2%, because its checked values are correct.
  3. Validity of R in M′ therefore means R^{H_0} breaks X. But R^{H_0} is an explicit efficient algorithm that uses no speedup at all. So X is easy.
- **Why it applies here.** The checked values are deterministic public functions of the chosen inputs and public noise, so a winner's transcript is identical to H_0's. The only thing that distinguishes a winner is its cost.
- **Escape routes.** Non-black-box reductions, or ones that use the adversary's running time (fine-grained reductions). For those, X must have a 1%-tight concrete cost structure itself, which puts X back in the TT family. Security from hashing (memory-hard functions, sequential work) is excluded by decision 1, and it is not useful work at degenerate inputs (Theorem B0).
- **Theorem B0 gives a second, independent reason.** A cryptographic task whose cost is not in the checked values is skippable at x_0, and a cryptographic secret can't make the checked values costly, because at A = 0 the output is 0 whatever the secret. Verifier and beacon secrets were measured at γ ≥ 50%.

### 4.6 Per-instance and per-instruction assumptions without a composition rule

- **Counterexample.** Under the P2-1 involution, every checked word taken alone still costs one k16 word: no single word has a shortcut. Jointly, one word per output entry is free, giving 1.04% at k = 1,024. The same holds for the Lean `admissibleExtraIdentity` P, where about k/64 + 1 words per entry are free (8.5% at k = 4,096).
- **So** a statement quantified over single words, tiles or instructions cannot imply the joint bound. What composes is a measure that is additive over independent pieces, which is dimension (Theorem D). Cost is not additive in general, and tensor rank is not either (Shitov 2017).

### 4.7 Anything that beats the free final word

No assumption can give NCP a γ_0 below 16/(3k). The final checked value is A·B, which is known, and skipping it is always possible (Lean `oneSegment`, `segmentLead`). Theorem D meets this floor with equality. With γ_0 = 0.5% that forces k ≥ 1,067, the domain floor; with any additional assumption slack γ_1 + γ_2, the floor rises to k ≥ 16/(3·(0.5% − γ_1 − γ_2)).

### 4.8 What is *not* ruled out

- An unconditional proof of A1. It needs a multiplicative-complexity lower bound of 2 per output word for ⟨m,16,n⟩-type spaces. No technique I know gives more than about 1 per word when the inner dimension is fixed at 16. The square-case bounds (about 3n² against n² outputs; Landsberg 2014, Massarenti–Raviolo) do not carry over as ratios. So this is open, not impossible.
- A cost model change that removes the packing route (§6, question 2).

## 5. Lean plan

Where: the PoUW Lean package (`lean/submissions/pouw/`), in a new subdirectory and namespace `Pouw.Dimension`, following the package's audit rules (only `propext`, `Classical.choice`, `Quot.sound`; no `sorry`, `axiom` or `native_decide`).

1. **Programs.** An inductive noise-oblivious program: a list of instructions, each either `free` (a ℚ-linear combination of earlier slots and constants) or `priced` (an arbitrary function of earlier slots, with a price). Evaluation is a function from the noise grid (Fin (m·k) ⊕ Fin (k·n) → Icc (−31) 32) to slot values in ℚ.
2. **`dim_le_priced`.** finrank(span(outputs ∪ V_0)) ≤ finrank(V_0) + #priced. This is an induction on the program with `Submodule.span_insert` and `finrank_span_le_card`.
3. **`secondDifference`.** If ∑_τ c_τ·(e ↦ eᵀ M_τ f) is affine as a function on the grid, then ∑_τ c_τ·M_τ = 0. Proved by evaluating at unit vectors; this needs no Nullstellensatz.
4. **`algBound`.** From `IndepRule P` (linear independence of M_τ for τ < T, taken as a hypothesis, as today) and `H16 price` (every priced slot costs at least 16), the cost is at least 16·∑_u m_u·n_u·(T_u − 1). This includes additivity over (i, j) and units by disjoint monomials.
5. **`TT_NCP_alg`.** TT_NCP's statement with γ_0 = 16/(3k), for AlgM_16 programs, plugged into the existing `gammaFromTTNCP` shape.
6. **The assumptions module.** Two named Props, `A1_multiplicative (c γ₁)` and `A2_algebraicSufficiency (γ₂)`, and the theorem `TT_NCP_of_A1_A2`. Each Prop gets an entry in the upstream watch list, as the rules require.
7. **Pins.** `algBound`, `TT_NCP_alg` and `TT_NCP_of_A1_A2` are pinned in `lean-audit.json`, with a named statement reviewer (the red team). Checking `IndepRule` at k = 4,096 stays a script; in Lean it is a small-k witness, such as the shift by 24 at k = 64 or 256 by `decide`, if the kernel can manage it.

Size: steps 1–5 are routine finite-dimensional linear algebra plus program-semantics bookkeeping. The price glue to the existing game is the main work. The probabilistic lifting of §2.5 is the hard part and should come second, modelled on R_copy's bound.

## 6. Open questions and next steps

No GPU is needed for any of steps 1–4.

1. **Red-team Theorem D** (§2.3, §2.7), especially the additivity across units that share F_1, and whether any W1 instruction violates H_16.
2. **Question for Daniel (cost-model semantics).** W1 makes byte-granular oblivious moves free, and that is the only reason packed FFMA reaches 4 units per product. If W1 priced sub-word extraction like PRMT (16 per word), A1 would need only c = 2, with about 2.7× margin, instead of c = 4, with about 1.35×. This changes agreed semantics, so it is Daniel's decision, not mine.
3. **A MinRank(P) certificate** for the production P: a lower bound on the rank of every nonzero element of span{M_τ : τ < T}. At minimum it should exclude rank ≤ 3, the FFMA break-even; the target is ρ ≥ 16. This closes the red team's uncovered "rank ≤ 1 increments" item and the lottery route in §2.5.
4. **A1 counterexample search**, on CPU: flip-graph or AlphaTensor-style search for quadratic algorithms of small NCP subspaces (⟨m,16,n⟩ blocks with the cross-block structure), each checked as an exact identity. A hit below 2 products per dimension, or below 4 with packing, is a real attack on the scalar-pipe route.
5. **H_16 completeness microbenchmarks**, for later and at small cost: HFMA2, legacy `mma.m8n8k4` f16, IMAD.WIDE, b1 `mma`, and any FP8 k16 shape.
6. **The probabilistic lifting lemma** (§2.5): a correct-on-a-subset version of Theorem D with MinRank, which is what the game's ε(q) needs.
