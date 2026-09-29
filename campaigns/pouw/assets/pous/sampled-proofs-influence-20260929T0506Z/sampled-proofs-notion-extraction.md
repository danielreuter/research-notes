---
cursor:
  subagentId: "bc-e7e2bf3a-f0d8-5b5a-9714-9de87eb030a8"
---

# What Daniel's Draft 2 still offers the sampled-proofs Lean

## Headline

- **The influence-cap theorem is Draft 2's Lemma 4.7:** "Fix E ⊆ G and a downstream cut K for E. Among the transcripts
  defining 𝒪_C(E), the values at K determine the delivered output. Consequently, |𝒪_C(E)| ≤ 2^(w(K))."
  - A downstream cut meets every path from E to a designated output (Definition 4.6), and w(K) = Σ_(i∈K) log₂|D_i|.
  - "RU" is a **replay unit**. The "RU outputs" are the delivered outputs of the request's replay unit, the served
    tokens. The draft's §6.2 applies the lemma to replay units: a replay unit's exports cut every unit inside it.
- **`main` had none of it.** The closest statement is `compose_cone` in `Audit/Circuit.lean`.
  - I proved the lemma and its uses on `main`'s audit model: Theorem 4.8 on the one-stage audit, Theorem 5.4 over replay
    units, Corollary 3.3, and a link from harm bounds to influence.
  - That is 15 theorems, with no `sorry` and only the three standard axioms, in the store draft
    [`lean/submissions/sampled-proofs-influence/`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/lean/submissions/sampled-proofs-influence/NOTES.md).
    Verity's Lean audit passes with 12 of them pinned in the package's `lean-audit.json`; no statement reviewer yet.
- **PoUW's decision 4 applies the lemma correctly** (§1).
- **Three flags** (§4):
  - the input-linkage lemma's proof is wrong for s < 1;
  - §6.3 and Appendix A still count input units, which contradicts the page's own §5;
  - the repo's exfiltration bound counts value bits but not fault locations.

## Sources and status legend

- **Draft 2** (main page, last edited 2026-09-10): §1–§10 and Appendices A–B. This is the source quoted unless marked
  otherwise.
- **"Section 4 — working draft"** (child page, 2026-09-05): an older §4 with inputs fixed rather than faultable. It fits the
  current ruling better than the main page's §4.
- **"[Draft] Sift"** (child page, 2026-09-06, with its "Revision notes"): a rewrite that samples every gate equation,
  inputs included, following Daniel's instruction at the time. The main page's later §5–§8 and the repo anchor inputs
  instead. Items found only in Sift are in group J.
- **The repo** at `main` b4fd93e9, which was `origin/main` at 04:40Z:
  - the soundness package's `Audit/` (`Law`, `Stratified`, `OneStage`, `TwoStage`, `Circuit`, `Examples`);
  - `Flock/Draw.lean` and `Flock/Partition.lean`;
  - `verity.ir.partition` and `verity.ir.cut`, and `verity.proofs.profile`;
  - `protocols/one_stage` and `protocols/sampled_proofs`.
- **The store:**
  - [`pouw-accountable-compute`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/lean/submissions/pouw-accountable-compute/NOTES.md):
    21 pins, awaiting review;
  - the [PoUW design](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/sampled-proofs-circuit.md),
    §12.5 and decision 4.

**Status legend:**
- **Proved:** a Lean theorem on `main` proves it, or an equivalent or stronger form.
- **Proved (store draft):** proved only in the new, unreviewed package.
- **Stated only:** Python code, a named hypothesis or a document says it, with no Lean proof.
- **Missing:** nothing states it.
- **Superseded:** a ruling or the repo's model replaces it, so it should not be ported.

The draft's "verification unit (VU)" is the Glossary's **proof unit**.

## 1. The influence-cap theorem

**As written:**
- *Definition 4.6 (downstream cut):* "A set K⊆G is a downstream cut for E if every directed path from a gate in E to a
  designated output contains a gate in K. The cut may include fault locations and output gates themselves. Paths of
  length zero are included, so a faulty output gate must itself be covered. The cut's width is w(K)=Σ_(i∈K) log₂|D_i|."
- *Lemma 4.7 (a cut determines the output):* "Fix E⊆G and a downstream cut K for E. Among the transcripts defining
  𝒪_C(E), the values at K determine the delivered output. Consequently, |𝒪_C(E)| ≤ 2^(w(K))."
  - 𝒪_C(E) is "the outputs of well-typed transcripts for the prescribed circuit and input with E(τ)⊆E".
- *Uses in the draft:*
  - Theorem 4.8 takes the union over the likely fault sets.
  - Lemma 5.1 applies the lemma to the unit (coarsened) circuit.
  - Theorem 5.4 does the same in the two-stage protocol.
  - §6.2 cuts at replay-unit exits: "For each replay unit, all its exported scalars form a downstream cut for every
    verification unit it contains … This can be much smaller than the sum of all internal unit-output widths."
  - Lemma 6.2 describes heavily corrupted replay units by their exits.

**What "RU" means.**
- A replay unit (§5.2) is "a subcomputation together with its incoming and outgoing boundary values: once the incoming
  boundary values are fixed, correct evaluation determines its interior and outgoing boundary values".
- It groups whole proof units, and the prover supplies its interior only when the first draw selects it.
- Its outputs are its outgoing boundary values. In the draft's request-local baseline (one request per replay unit,
  prefix caching off, §5.2 and §8.2) and in Daniel's 04:35Z remark, the delivered ones are the served tokens.
- The repo's Glossary uses the same term, and the PoUW design (§12.5) reads it the same way.

**Precisely, on `main`'s model.**
- The model: a Boolean circuit, one bit per gate, with a partition into units and an input unit anchored on every audit.
- Let D be the delivered wires, K a set of committed wires, and B a set of units.
- K **separates** B from D if every gate path from a gate of a unit of B to a wire of D passes through K.
- **Then:** two transcripts whose inputs equal the anchors, whose wrong units all lie in B, and that agree on K, agree on
  D.
- **So** those transcripts deliver at most 2^|K| distinct values on D.
- Two points differ from the draft:
  - the draft's "designated outputs" become D, the delivered wires, which can be fewer than the circuit's outputs;
  - the width is |K| bits.

**In the repo.**
- **On `main`, missing.**
  - `compose_cone` is the determination step with no faults allowed: a consumer's committed wires are right when its cone
    holds no wrong unit.
  - `correct_congr` says a unit's correctness reads only its committed inputs and outputs.
  - `verity.ir.cut` has the width rule but no cut-based bound.
- **Proved in the store draft** (`Influence/Separator.lean`):
  - `outputs_eq_of_separates` and `card_delivered_le`: the lemma and its count;
  - `separates_exits`: a replay unit's exits cut it;
  - `Separates.union` and `Separates.mono`.

**PoUW decision 4 applies it correctly, under these conditions:**
- **D must be the served tokens only.** The word leaves and commitments are circuit outputs, so they must stay out of D.
  The design names this condition, and the Lean statement makes D an explicit parameter.
- **Inputs must be anchored.** The salt, the forward index and the weights carry no influence only because the input unit
  is certified on every audit. That adds δ_in to the error; it is not the draft's input-linkage argument (§4, item 1).
- **U also counts fault locations:** U = log₂ Σ_E 2^(w(K_E)), not the widest cut. The design's conclusion still holds,
  because the served-output width caps U whatever the partition.
- **The draft's own baseline forbids it:** "a narrower downstream cut does not permit a wider baseline VU". That is a
  policy of the baseline instantiation, not a theorem. Theorem 5.4 supports decision 4, and Daniel's 04:35Z ruling
  overrides the policy.

## 2. Every item at a glance

| # | Item | Status | Where |
|---|---|---|---|
| A1 | Def 3.1 (U, ε)-integrity | Proved (store draft), soundness half | `influenceSet`, `audit_influence` |
| A2 | Remark 3.2 influence in bits | Proved (store draft) | `card_influenceSet_le` |
| A3 | Cor 3.3 exfiltration | Proved (store draft) | `audit_exfiltration`, `card_guess_le` |
| B1 | Protocol 1, the all-gate sampler | Superseded | `audit`, input unit |
| B2 | Lemma 4.2 acceptance (1−p)^\|E\| | Proved | `bernoulli_escape`, `audit_profile` |
| B3 | Lemma 4.3 normalization | Superseded | Boolean model |
| B4 | Lemma 4.4 transcript count | Missing as stated, role covered | `card_delivered_le`, `card_admissible_le` |
| B5 | Thm 4.1 one-stage integrity | Missing as one theorem, derivable | store draft pieces |
| B6 | Why output, argument and input checks matter | Superseded | Boolean model, anchors |
| C1 | Thm 4.5 exact matmul influence | Missing | none |
| D1 | Def 4.6 downstream cut | Proved (store draft) | `Separates` |
| D2 | Lemma 4.7 | Proved (store draft) | `outputs_eq_of_separates` |
| D3 | Union of cuts | Proved (store draft) | `Separates.union` |
| D4 | Thm 4.8 cut-based integrity | Proved (store draft) | `audit_influence`, `card_influenceSet_le` |
| D5 | U_k ≤ kb + log₂ C(N, k) | Proved (store draft), as ingredients | `card_influenceSet_le_harm`, `card_admissible_le` |
| E1 | Unit interfaces and unit check | Proved | `Partition.Correct`, `validate_unit_cut` |
| E2 | Acyclic quotient requirement | Superseded | gate-level induction |
| E3 | Lemma 5.1 coarsening | Proved (different form) | `correct_congr`, `compose` |
| E4 | Unit width, 32-bit baseline | Stated only | `Q_word` width rule, `validate_width` |
| E5 | No reuse of a cut inside a unit | Proved (by definition) | `Separates` |
| F1 | Replay units, boundary, disjoint interiors | Proved | `Refines`, `exists_wrong_fine` |
| F2 | Protocol 2 ordering (interiors before the second draw) | Proved | `twoStage`, `late_interior_insecure` |
| F3 | Early exemptions | Superseded | ruling: an abort rejects |
| F4 | Lemma 5.2 fixed-completion acceptance | Proved at B_ex = 0, one fault per RU | `effEscape_bernoulli_prod` |
| F5 | Lemma (input linkage) | Proved (different form); the draft's proof is wrong | `AnchorsSound`, `audit_cone` |
| F6 | ℓ* and Lemma 5.3 adaptive completion | Proved for ℓ* ≥ 1 | `Analysis₂.compose`, `twoStage_profile` |
| F7 | Malformed-boundary normalization | Superseded | Boolean model |
| F8 | Thm 5.4 two-stage integrity | Proved (store draft), over replay units | `Refines.twoStage_influence` |
| F9 | Rate endpoints and concentration | Proved for `main`'s laws | `effEscape_full`, `effEscape_bernoulli` |
| G1 | Separable survival bound, capped risk | Superseded | prices exemptions only |
| G2 | Lemma 6.2 two-level description | Missing (the all-heavy case is in the store draft) | `twoStage_influence` with `separates_exits` |
| G3 | Thm 6.3 summary certificate | Missing (a coarser form is in the store draft) | recommendation 6 |
| G4 | Zero-allowance identity | Superseded | exemptions |
| G5 | Appendix A endpoints and fallback | Endpoints proved, fallback missing | `stratified_escape_floor` |
| H1 | Law-generic miss probability | Proved | `Law.escape` and its laws |
| H2 | Gap sampler (§6.4, Appendix B) | Superseded; executable link stated only | `verity.randomness`, `Flock/Draw.lean` |
| H3 | Prop 6.1 descriptor correctness | Superseded | `verity.ir` |
| H4 | Resource counts (§5.5, Thm 6.4) | Count identity proved | `Law.avg_card` |
| I1 | Thm 7.1 committed-I/O integrity | Proved (different form) | compiled layer |
| I2 | Thms 7.2, 7.4 and Lemma 7.3 (privacy) | Missing, out of scope | none |
| J1 | Sift Thm 5.5 budget boundary | Missing (belongs in the planner) | none |
| J2 | Sift Prop C.1 | Superseded input policy | see C1 |
| J3 | Sift exact count for complete replays | Missing, derivable | `card_influenceSet_le` |
| J4 | Sift Freivalds check | Missing, unused | none |
| J5 | Sift Prop E.1 advice composition | Missing | none |
| J6 | Sift late-interior counterexample | Proved | `late_interior_insecure` |

## 3. The items

Each item gives the statement as written, a precise restatement, and what the repo has.

### A. Integrity and influence

**A1. Definition 3.1, (U, ε)-quantitative integrity.** *Soundness half proved in the store draft.*
- *Written:* "Completeness. … Pr_r[accept(V,x,r,P)=1]=1. Soundness. For every x∈X, there exists a set Y_x⊆Y with
  |Y_x|≤2^U such that, for every deterministic prover strategy P*, if P* provides some y∉Y_x at the start of the
  protocol, then Pr_r[accept(V,x,r,P*)=1]≤ε."
- *Precisely:*
  - for fixed C and x, one set Y_x, chosen before any prover, with |Y_x| ≤ 2^U;
  - every strategy has Pr[accept ∧ y ∉ Y_x] ≤ ε, a joint probability and not one conditioned on acceptance;
  - the honest prover is accepted with probability 1.
- *Repo:*
  - `main` has no notion of an output set; its profile bounds sets of wrong units.
  - In the store draft, `influenceSet D e a δ` is Y_x: it depends on the circuit, the partition, the anchors, the law and
    δ, never on the prover.
  - `audit_influence` is the soundness half, with ε = δ + ε_ks + δ_link + δ_in.
  - No audit in the repo formalizes completeness.

**A2. Remark 3.2, influence.** *Proved (store draft).*
- *Written:* "all outputs that can be accepted with probability greater than ε lie in a set Y_x of size at most 2^U … U
  bounds the prover's influence over the output, measured in bits … not their numerical distance".
- *Precisely:* the influence is log₂|Y_x|. When U = 0, completeness forces Y_x = {C(x)}, which is ordinary soundness.
- *Repo:* `card_influenceSet_le` bounds |Y|.

**A3. Corollary 3.3, exfiltration security.** *Proved (store draft), for deterministic provers and receivers.*
- *Written:* "Pr[V accepts ∧ M̂=M] ≤ 2^(U−ℓ)+ε", for M uniform on {0,1}^ℓ and independent of x, a prover strategy chosen
  from M, and a receiver that sees only x and y.
- *Repo:*
  - `main`'s `exfiltration_bound` (Python) and the store's `exfiltration` bound the output bits held by wrong units, not
    the messages a receiver can recover (§4, item 7).
  - The store draft's `card_guess_le` and `audit_exfiltration` prove
    avg_m Pr[accept ∧ g(out) = m] ≤ |influenceSet|/|M| + δ + ε_ks + δ_link + δ_in.
  - Randomized provers and receivers (by averaging) are not formalized.

### B. The one-stage sampler

**B1. Protocol 1.** *Superseded.*
- *Written:* "The prover supplies a claimed output y and an oracle string containing the values at all gates … forms a
  sample Q⊆G by including each gate independently with probability p … accepts exactly when out(τ)=y and every sampled
  gate is correct."
- *Precisely:* a Bernoulli(p) sampler over all gates, input gates included, with output typing and agreement checked on
  every run.
- *Repo:*
  - `Audit/OneStage.lean`'s `audit` draws proof units under any `Law`, with the stratified law as default.
  - Inputs are certified against their anchors on every audit, never sampled.
  - The draft's own §5 drops input sampling the same way.

**B2. Lemma 4.2, acceptance.** *Proved, as the upper bound that soundness needs.*
- *Written:* "If y is well-typed and out(τ)=y, the probability of acceptance is (1−p)^(|E(τ)|). Otherwise it is zero."
- *Repo:*
  - `Law.bernoulli_escape` gives the escape as ((den − num)/den)^|B|.
  - `audit_profile` gives Pr[accept ∧ wrong ∈ 𝓑] ≤ sup escape + ε_ks + δ_link.

**B3. Lemma 4.3, normalization.** *Superseded.*
- *Written:* "every transcript τ with well-typed output has a transcript τ′ with the same output, well-typed at every
  gate, and satisfying E(τ′)⊆E(τ)."
- *Repo:* vacuous. `main`'s transcripts are `Fin C.N → Bool`, so every value is well-typed and a width is a bit count.

**B4. Lemma 4.4, counting.** *Missing as stated; its role is covered.*
- *Written:* "the number of well-typed transcripts with at most k incorrect gates is at most C(N,k)·2^(k·w_max)."
- *Repo:* the store draft counts outputs rather than transcripts:
  - `card_delivered_le`: at most 2^|K| outputs per fault set;
  - `card_admissible_le`: at most Σ_(j≤K) C(n, j) likely fault sets.

**B5. Theorem 4.1, one-stage integrity.** *Missing as one theorem; derivable from the store draft.*
- *Written:* "For every 0<p<1 and integer 0≤k<N, Protocol 1 has (U,ε)-integrity … U = k·w_max + log₂ C(N,k),
  ε=(1−p)^(k+1)."
- *Repo:* it follows by combining four results, but nobody has stated it as one theorem:
  - `bernoulli_escape`;
  - `card_admissible_le`;
  - `card_influenceSet_le_harm` with every unit's harm equal to w_max;
  - `separates_exits`.

**B6. Why the checks matter.** *Superseded.*
- *Written:*
  - without output typing, "no finite influence bound suffices for error below 1−p";
  - argument typing is needed because one value of L·w bits can feed L readers;
  - "Input equations must also be included in the sampler."
- *Repo:*
  - output and argument typing are vacuous with one-bit gates;
  - inputs are anchored on every audit instead of sampled.

### C. Matrix multiplication

**C1. Theorem 4.5, exact influence for canonical matmul.** *Missing, low priority.*
- *Written:*
  - "min_(τ:out(τ)=Y′)|E(τ)| = ρ_(A,B)(Y′)", with ρ = min over Ã, B̃ of d_H(Ã,A) + d_H(B̃,B) + d_H(Y′,ÃB̃);
  - U_MM = log₂|{Y′ : ρ_(A,B)(Y′) ≤ k}|;
  - the count is at most min{ν^M, Σ_(j≤k) C(I+M,j)(ν−1)^j}.
- *Precisely:* over F_ν, with anchored inputs (the repo's policy), the exact count is the Hamming ball
  Σ_(j≤k) C(M,j)(ν−1)^j. The Section 4 working draft states this version.
- *Repo:* none. `main`'s GEMM units have tensor-core semantics, so this can only serve as a test oracle for a
  certificate, not as a statement to pin.

### D. Cuts

**D1 and D2. Definition 4.6 and Lemma 4.7.** See §1. *Proved (store draft).*

**D3. Union of cuts.** *Proved (store draft):* `Separates.union` and `Separates.mono`.
- *Written:* "if K_i is a downstream cut for each individual gate i∈E, then their union is a cut for E, with width at most
  Σ_(i∈E) w(K_i). Shared cut values are counted once."

**D4. Theorem 4.8, cut-based integrity.** *Proved (store draft):* `audit_influence` and `card_influenceSet_le`.
- *Written:* "let a(E) be the probability that the sample misses every gate in E, and choose a downstream cut K_E
  independently of the transcript values … U = log₂[Σ_(E⊆G: a(E)>ε) 2^(w(K_E))]."
- *Precisely:* it holds for any draw law. Y is the union of 𝒪(E) over the fault sets E with escape at least δ.
- *Repo convention:* the draft writes a(E) > ε. The Lean uses δ ≤ escape, as `IsHarmBound` does, and the error becomes
  δ + ε_ks + δ_link + δ_in.

**D5. The padded form, U_k ≤ k·b + log₂ C(N, k).** *Proved (store draft), as ingredients:* `card_admissible_le`, and
`card_influenceSet_le_harm` with every unit's harm equal to b.

### E. Proof units (the draft's verification units)

**E1. Unit interfaces and the unit check.** *Proved: this is `main`'s model.*
- *Written:* "The incoming interface of V_i consists of the distinct values produced outside V_i and used by its gates.
  Its outgoing interface consists of the distinct values produced in V_i that are either used outside it or designated
  as delivered outputs … claimed outgoing values of V_i = f_(V_i)(claimed incoming values of V_i)."
- *Repo:*
  - `Partition.committed`, `localEval` and `Correct` in `Audit/Circuit.lean`;
  - `validate_unit_cut` and `Flock.Partition.validate`, under which the committed set is the boundary set.

**E2. The acyclic quotient.** *Superseded.*
- *Written:* "contracting each V_i to one vertex must leave a directed acyclic graph."
- *Repo:*
  - not needed: `cone_induction`, `compose_cone` and the new separator lemma all induct over gates;
  - neither `verity.ir` nor `Flock.Partition` checks it.

**E3. Lemma 5.1, coarsening.** *Proved (different form).*
- *Written:* "The unit check at V_i is the local correctness predicate of its quotient gate. The counting, normalization,
  and downstream-cut arguments of Section 4 apply to this port-valued circuit."
- *Repo:*
  - `correct_congr` and `compose`;
  - the store draft's lemma works on gates with unit ownership, so no quotient circuit is needed.

**E4. Unit width and the 32-bit baseline.** *Stated only.*
- *Written:*
  - "a faulty unit can choose its entire outgoing tuple, of width w(V_i)=Σ_(j∈out(V_i)) log₂|D_j|";
  - "every ordinary VU has one scalar output of at most 32 bits … The full outgoing interface determines the width; a
    narrower downstream cut does not permit a wider baseline VU."
- *Precisely:* w(V_i) is the width of the unit's own exits, and those exits always separate the unit.
- *Repo:*
  - `Q_word` v1's width rule allows at most 16 bits, or one boundary value of at most 32 bits (`verity.ir.cut.fits`,
    code `unit-too-wide`). `validate_width` is a Python check too, and no theorem uses either.
  - In the store draft's terms, the rule bounds `(exits {u}).card`, the unit's trivial separator.
  - Decision 4 replaces that with the Z separator for the units behind Z.

**E5. "A cut inside a unit cannot be reused."** *Proved, by definition.*
- *Written:* "a cut inside a unit cannot be reused when it no longer separates the unit's outgoing fault-injection
  points."
- *Repo:* `Separates` quantifies over every gate of every unit in B.

### F. Replay units and the two-stage protocol

**F1. Replay units, the boundary and disjoint interiors.** *Proved.*
- *Written:* "fixing its incoming boundary values determines its correct interior and outgoing values … each unit check in
  R_r now depends only on b and z_r … the interiors have disjoint sets of free variables."
- *Repo:*
  - `Partition.Refines`, `Refines.localEval_eq` and `exists_wrong_fine`;
  - the Glossary's "replay unit (RU)".

**F2. Protocol 2's ordering.** *Proved, without exemptions.*
- *Written:* "The entire set F and all these strings are fixed before the next sample … Using fresh randomness generated
  after step 3".
- *Repo:*
  - the `twoStage` game runs: registration, the first draw, the interior, the second draw, then the session;
  - `late_interior_insecure`: an interior chosen after the second draw is accepted with probability 1;
  - `protocols/sampled_proofs`, pitfall 4.

**F3. Early exemptions.** *Superseded.*
- *Written:* "After learning which replay units were selected, the prover may decline to supply the interior of at most
  B_ex of them."
- *Repo:*
  - no protocol has them, and the PoUW ruling is that "an abort rejects the window";
  - only veritor's legacy wire codes `EXEMPTIONS_EXCEEDED` and `EXEMPTION_INVALID` remain, in `verity.proofs.codes`.
  - Take B_ex = 0 everywhere.

**F4. Lemma 5.2, fixed-completion acceptance.** *Proved at B_ex = 0, with one fault charged per replay unit.*
- *Written:* "a_(q,s,B_ex)(E) = E_J[max_(F⊆J,|F|≤B_ex) (1−s)^(Σ_(r∈J∖F)|E∩R_r|)]", and at B_ex = 0,
  "∏_r[1−q+q(1−s)^(|E∩R_r|)]".
- *Repo:*
  - `effEscape_bernoulli_prod` gives ∏_(u∈B)(1 − p + p·m_u), with m_u the largest miss probability of one proof unit
    in u (F6).
  - Under `protocols/sampled_proofs`' law (exactly k proof units per drawn replay unit), a wrong replay unit escapes with
    probability at most 1 − p·k/n_v.

**F5. Lemma (input linkage).** *Proved in a different form; the draft's proof has an error (§4, item 1).*
- *Written:* "A deviation from a prescribed input has no freedom of its own … Consequently prescribed inputs contribute no
  term to the bound".
- *Repo:*
  - the input unit is certified on every audit: `InputsAgree`, `AnchorsSound δ_in`, `InputsSound` and `audit_cone`;
  - a deviation costs δ_in in the error and nothing in U, and `audit_influence` has the same shape.

**F6. ℓ\* and Lemma 5.3, adaptive completion.** *Proved for ℓ\* ≥ 1; the general case is missing.*
- *Written:* "the greatest acceptance probability over all permitted early exemptions and adaptive interior choices is
  E_J[max_F (1−s)^(Σ_(r∈J∖F) ℓ*_r(b))]. It is attained by choosing one full well-typed completion before the first
  sample".
- *Repo:*
  - `Analysis₂.compose` (a wrong drawn replay unit has a wrong proof unit under every interior) with `twoStage_profile`;
  - tightness on chains: `two_stage_b_tight`.
  - Nothing counts several unavoidable faults per replay unit (ℓ\* > 1). That matters only for cuts inside a replay unit
    (F8).

**F7. Malformed-boundary normalization.** *Superseded:* the model is Boolean.

**F8. Theorem 5.4, two-stage integrity.** *Proved (store draft), over replay units.*
- *Written:* "For every possible faulty-unit set E⊆[N_V], choose a downstream cut K_E of the coarsened computation C̄ …
  U = log₂[Σ_(E : a_(q,s,B_ex)(E)>ε) 2^(w(K_E))]."
- *Repo:*
  - the store draft's `Refines.twoStage_influence` and `card_influenceSet_le` work on the coarse partition with
    `effEscape`;
  - the fault sets are sets of wrong replay units, and each cut separates replay units, for example `separates_exits`.
  - The draft's proof-unit-level E needs completions of undrawn replay units, which `main`'s analysis never builds.

**F9. Rate endpoints and fault concentration.** *Proved for `main`'s laws.*
- *Written:*
  - "setting q=1 gives one-stage sampling on the coarsened computation … Setting s=1 gives survival (1−q)^m";
  - "h faults concentrated in one replay unit survive with probability 1−q+q(1−s)^h, whereas h faults in distinct replay
    units survive with probability (1−qs)^h."
- *Repo:*
  - `effEscape_full` and `twoStage_full_profile`: proving every unit inside the drawn replay units gives the one-stage
    audit over replay units;
  - `two_stage_a_coarse`: committing everything before one draw gives the one-stage audit over proof units;
  - `effEscape_bernoulli`: with Bernoulli(p) replay units and k₂ of n_v proof units inside each, every chain escapes
    as under Bernoulli(p·k₂/n_v).
  - The binomial formula at s = 1 with exemptions, and the late-exemption comparison, go with the exemptions.

### G. Certificates

**G1. Separable survival bound and capped risk.** *Superseded: they exist only to price exemptions.*
- *Written:* "a ≤ 2^(λB_ex) ∏_r[1−q+q·max{(1−s)^(j_r), 2^(−λ)}]", with
  h_λ(j) = −log₂(1−q+q·max{(1−s)^j, 2^(−λ)}).
- *Repo:* at B_ex = 0 the product is exact (`effEscape_bernoulli_prod`).

**G2. Lemma 6.2, the two-level fault description.** *Missing; the all-heavy case is in the store draft.*
- *Written:* "a_(t,λ)|L| + b_(t,λ)|H| < σ + λB_ex. For fixed choices of L and H, the resulting outputs belong to a set of
  size at most 2^(Σ_(i∈L)w(i)+Σ_(r∈H)c(r))".
- *Precisely:* a lightly corrupted replay unit is described by its faulty units and their cuts. A heavily corrupted one,
  with more than t faults, is described by its identity and its exit width c(r).
- *Repo:*
  - t = 0 (every replay unit heavy) is `twoStage_influence` with `separates_exits`;
  - mixing the two descriptions needs ℓ\* (F6).

**G3. Theorem 6.3, the summary certificate.** *Missing; a coarser form is in the store draft.*
- *Written:* "U_(t,λ,B)(z) = z(σ+λB_ex) + Σ_k n_k log₂(1+2^(w_k − z·a_(t,λ))) + Σ_(a:v_a>t) B_a log₂(1+2^(c_a − z·b_(t,λ)))".
- *Precisely:* a Chernoff-style bound, with a multiplier z, on log₂ Σ_(likely E) 2^(width), computed from family and bank
  summaries.
- *Repo:*
  - Python's `Stratified.count_bound` (exact) and `harm_bound` (the largest total harm, a linear relaxation, not a
    log-sum);
  - the store's `stratified_isHarmBound`, a closed-form harm bound;
  - the store draft's `card_influenceSet_le_harm` with `card_admissible_le`, which gives
    U ≤ H + log₂ Σ_(j≤K) C(n, j), coarser than Theorem 6.3.
  - Recommendation 6 is the multiplier form for the stratified law.

**G4. The zero-allowance identity.** *Superseded, with the exemptions.*

**G5. Appendix A's endpoints and fallback.** *The endpoints are proved in analog; the fallback is missing.*
- *Written:*
  - "If q=s=1 and B_ex<N_R … U ≤ B_ex·c_max + log₂ C(N_R,B_ex) … This returns zero for zero allowance";
  - "h(j) ≥ qjs/(1+js)";
  - "U(z_*) < z_*Δ+1".
- *Repo:* `stratified_escape_floor` and `audit_whole_stratum` (a stratum proved whole never escapes). No numeric
  certificate exists in Lean.

### H. Draw laws, sampling and representation

**H1. A miss probability for any law.** *Proved, for more laws than the draft has.*
- *Written* (Theorem 4.8): "The distribution of that set is fixed by the statement and public protocol parameters."
- *Repo:*
  - `Law.escape`, `miss` and `incl`;
  - `subset_escape`, `subset_miss`, `subset_escape_le_prod`, and `subset_minimax` (the uniform subset is optimal);
  - `bernoulli_escape`, `stratified_escape`, `stratified_escape_floor` and `effEscape`;
  - in the store, `closureLaw_escape` and `both_escape_le`.

**H2. The gap sampler (§6.4, Appendix B).** *Superseded; the executable link is stated only.*
- *Written:* "return gap j∈{1,…,R} with probability p(1−p)^(j−1), and the terminal outcome … with probability (1−p)^R."
- *Repo:*
  - `verity.randomness` has exact samplers: rejection-sampled uniform, a partial Fisher–Yates subset, and a per-unit
    Bernoulli. `tests/randomness/vectors.json` pins them, and `Flock/Draw.lean` re-implements them.
  - No Lean theorem says that `Flock.Draw.subset` or `stratified` realizes `Law.subset` or `Law.stratified`.

**H3. Proposition 6.1, descriptor correctness.** *Superseded* by `verity.ir`: descriptor v1, queries, `CheckedTiling` and
`partition_object`, all tested in Python.

**H4. Resource counts (§5.5, Theorem 6.4).** *Only the count identity is proved.*
- *Written:* "E[L_supplied] ≤ L_∂+qΣL_r"; "E|Q| = sΣp_r|R_r| ≤ qsN_V".
- *Repo:* `Law.avg_card` (the mean draw size is the sum of the inclusion probabilities). Costs are accounted in Python.

### I. Cryptographic realization and privacy

**I1. Theorem 7.1, integrity for committed I/O.** *Proved in a different form, for C-Flock.*
- *Written:* "Pr[Acc₃ ∧ ValidOutputOpening(c_y,y) ∧ y∉Y_φ] ≤ ε+δ_base", given prefix recording and straight-line
  extraction.
- *Repo:*
  - `Analysis.committedOf` (the committed transcript is fixed at registration), `KnowledgeSound` and `LinkSound`;
  - `ExtractionAnalysis`, `extraction_audit_le` and `flock_batched_knowledgeSound`.
  - Extraction is per drawn unit rather than through one joint recorder.

**I2. Theorems 7.2 and 7.4 and Lemma 7.3 (I/O privacy, padding, circuit privacy).** *Missing, and out of scope for
sampled-proofs soundness.*

### J. Only in the Sift draft

**J1. Theorem 5.5, the budget-boundary reduction.** *Missing; it belongs in the Python planner, not in Lean.*
- *Written:* "q*(s)=min{1, (B_P−F_P)/(R_P+sL_P), (B_V−F_V)/(R_V+sL_V)} … inf U_cert(q,s) = inf_s U_cert(q*(s),s)".

**J2. Proposition C.1.** *Superseded:* it is C1 with sampled inputs.

**J3. The exact count for complete randomly selected replays,** "Σ_(j≤k) C(B,j)(D−1)^j". *Missing, but derivable:*
`card_influenceSet_le` with one unit per execution and its outputs as the separator, plus an attainment argument.

**J4. The Freivalds check,** "Pr[Er=0]=ν^(−rank E)". *Missing; no ruling uses it.*

**J5. Proposition E.1, advice composition,** "U_total ≤ log₂ Σ_a 2^(U_a) ≤ log₂|𝒜| + max_a U_a", with error at most
max_a ε_a. *Missing.* It is a short union lemma over `influenceSet`, needed only if serving advice (batching, reported
nondeterminism) is ever counted.

**J6. The late-interior counterexample** (a three-gate chain, where acceptance rises from 1/2 to 7/8). *Proved* by
`late_interior_insecure`.

## 4. What is wrong or conflicts with current rulings

1. **The input-linkage lemma's proof is wrong for s < 1.**
   - Its case (ii) reads: "the interior is honest, and the replayed outputs differ from the claimed outputs, which the
     linkage check detects with certainty".
   - Protocol 2's only unconditional value check compares the claimed output with the boundary.
   - A boundary value that disagrees with an honest interior makes its producing unit wrong, and that unit is caught only
     when sampled.
   - The conclusion holds in the repo for a different reason: inputs are certified on every audit (δ_in).
2. **Input units still appear in sums.**
   - §6.3 says "Omitting an input family or its contribution to an exit would invalidate the certificate". Appendix A
     says "Input-gate units appear in every applicable summary".
   - The main page's §4 and the whole Sift draft sample input equations.
   - The same page's §5–§8, and the repo, say that input gates are no units and are never drawn, and that the input unit is
     certified against its anchors on every audit (`INPUT_UNIT`, `AnchorsSound`, PoUW design §1).
   - The §6.3 and Appendix A sentences are leftovers from the sampled-input version and should be dropped.
3. **Early exemptions are superseded.** The PoUW ruling is that an abort rejects the window, and no protocol has
   exemptions.
4. **The draw laws changed.**
   - The draft draws Bernoulli(q) replay units and Bernoulli(s) proof units.
   - The repo has three laws: exactly k proof units per drawn replay unit in `protocols/sampled_proofs` (decision 43),
     stratified uniform k_s-subsets as the default (Daniel, Sep 27), and closure draws for PoUW.
   - Replace (1−s)^j with each law's escape. The influence theorems need only an escape function.
5. **Terminology.** "Verification unit" is now "proof unit" (Glossary). "Replay unit" is unchanged.
6. **The width baseline contradicts decision 4.** The draft says "a narrower downstream cut does not permit a wider
   baseline VU". Decision 4 (Daniel, 04:35Z) does exactly that for the PoUW units behind Z. Theorem 5.4 supports the
   ruling, which overrides the baseline policy.
7. **Harm is not influence.**
   - The repo's exfiltration bound is the largest number of output bits in a likely set of wrong units. That covers
     `verity_one_stage.consumers.exfiltration_bound`, the store's `exfiltration`, and H*_B in PoUW §12.5.
   - The draft's influence also counts which set is wrong: U ≤ H + log₂ #{likely sets}. This is the log₂ C(N,k) of
     Theorem 4.1. Sift says it plainly: "small values alone do not account for the choice of fault locations".
   - `exfiltration_bound`'s docstring mentions the n·H₂(b/n) term, but the function doesn't add it.
   - No design conclusion changes, since the served-output width caps U anyway. But H*_B is not an influence bound.
     `card_influenceSet_le_harm` states the corrected one.
8. **Randomness is consistent with the rulings.** The draft wants live verifier coins after the commitments.
   `protocols/sampled_proofs/PROTOCOL.md` still says beacon, which is already tracked as stale.
9. **Two-stage granularity.**
   - The draft's cuts at the proof-unit level presuppose completions of undrawn replay units.
   - The repo profiles wrong replay units instead. That is not a conflict, but two-stage influence has to be stated over
     replay units, as the store draft does, until ℓ\* is formalized.

## 5. What to add to the sampled-proofs Lean, in priority order

The first four items are proved in the store draft. Their intended home on `main` is
`backends/flock/verifier/lean/soundness/FlockSoundness/Audit/Influence.lean`, beside `Stratified.lean`. It needs only
Mathlib, and `IsHarmBound` if item 3 comes along. Each item needs a `lean-audit.json` pin and a named statement
reviewer.

**1. The influence cap: separators and Lemma 4.7.**
- *Why first:* decision 4 rests on it, and it is the one missing piece. Everything else composes with `main`'s existing
  profile theorems.
- *What the reviewer checks in `Separates`:*
  - it quantifies over every gate of every unit in B;
  - D is the delivered wires only;
  - K is committed.

~~~lean
inductive Circuit.FeedsAvoiding (K : Finset (Fin C.N)) : Fin C.N → Fin C.N → Prop
  | refl {t : Fin C.N} : t ∉ K → FeedsAvoiding K t t
  | step {g h t : Fin C.N} : g ∉ K → g ∈ (C.op h).args → FeedsAvoiding K h t → FeedsAvoiding K g t

def Partition.Separates (K : Finset (Fin C.N)) (B : Finset (Fin n)) (D : Finset (Fin C.N)) : Prop :=
  ∀ g t u, P.unit g = some u → u ∈ B → t ∈ D → ¬ C.FeedsAvoiding K g t

theorem outputs_eq_of_separates {K : Finset (Fin C.N)} {B : Finset (Fin n)} {D : Finset (Fin C.N)}
    (hK : K ⊆ P.committed) (hD : D ⊆ P.committed) (hsep : P.Separates K B D) {X Y a : Fin C.N → Bool}
    (hX : C.InputsAgree X a) (hY : C.InputsAgree Y a) (hwX : P.wrong X ⊆ B) (hwY : P.wrong Y ⊆ B)
    (hXY : ∀ g ∈ K, X g = Y g) : ∀ t ∈ D, X t = Y t

theorem card_delivered_le (hK : K ⊆ P.committed) (hD : D ⊆ P.committed) (hsep : P.Separates K B D)
    (a : Fin C.N → Bool) : (P.delivered D a B).card ≤ 2 ^ K.card

-- the exits of B: its committed wires
theorem separates_exits (B : Finset (Fin n)) (hD : D ⊆ P.committed) : P.Separates (P.exits B) B D
~~~

**2. (U, ε) soundness for `main`'s audits: Theorems 4.8 and 5.4.**
- This replaces "harm in bits" with a count of outputs.

~~~lean
-- influenceSet D e a δ := ⋃ over B with δ ≤ e B of delivered D a B
theorem card_influenceSet_le (hD : D ⊆ P.committed) (e : Finset (Fin n) → ℝ≥0∞) (a : Fin C.N → Bool) (δ : ℝ≥0∞)
    (K : Finset (Fin n) → Finset (Fin C.N)) (hK : ∀ B, K B ⊆ P.committed) (hsep : ∀ B, P.Separates (K B) B D) :
    (P.influenceSet D e a δ).card ≤ ∑ B ∈ univ.filter (fun B => δ ≤ e B), 2 ^ (K B).card

theorem audit_influence (hks : (P.analysis X ext).KnowledgeSound εks)
    (hlink : (P.analysis X ext).LinkSound δlink) (hin : AnchorsSound X a δin) (δ : ℝ≥0∞)
    (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ out D (X (reg σ) (cont σ)) ∉ P.influenceSet D L.escape a δ)
      (audit L Reg session) σ ≤ δ + εks + δlink + δin

-- the same on the two-stage audit, over replay units, with `effEscape L₁ L₂ r.parent`
theorem Refines.twoStage_influence : …
~~~

**3. From harm bounds to influence: the location term.**
- This makes `harm_bound`'s value, under its specification `IsHarmBound`, into an influence certificate.
- It needs `IsHarmBound` to land with the pouw-accountable-compute pins, or to move into `Audit/`.
- Afterwards, as a separate Python change, add the location term to `exfiltration_bound`, or rename it as a bits bound.

~~~lean
theorem card_influenceSet_le_harm (hD : D ⊆ P.committed) (hb : Fin n → ℕ)
    (K : Finset (Fin n) → Finset (Fin C.N)) (hK : ∀ B, K B ⊆ P.committed) (hsep : ∀ B, P.Separates (K B) B D)
    (hw : ∀ B, (K B).card ≤ ∑ u ∈ B, hb u) {H : ℕ} (hH : IsHarmBound L (fun u => (hb u : ℝ)) δ H) :
    (P.influenceSet D L.escape a δ).card ≤ 2 ^ H * (univ.filter fun B => δ ≤ L.escape B).card

theorem card_admissible_le {K : ℕ} (hK : L.miss (K + 1) < δ) :
    (univ.filter fun B : Finset (Fin n) => δ ≤ L.escape B).card ≤ ∑ j ∈ range (K + 1), n.choose j
~~~

**4. Exfiltration: Corollary 3.3 on the audit.**

~~~lean
theorem audit_exfiltration {M : Type} [Fintype M] [Nonempty M] [DecidableEq M]
    (hks : (P.analysis X ext).KnowledgeSound εks) (hlink : (P.analysis X ext).LinkSound δlink)
    (hin : AnchorsSound X a δin) (δ : ℝ≥0∞) (σ : M → Strategy (audit L Reg session)) (g : (D → Bool) → M) :
    avg (fun m => prob (fun o => o.1 = true ∧ g (out D (X (reg (σ m)) (cont (σ m)))) = m)
      (audit L Reg session) (σ m)) ≤
      ((P.influenceSet D L.escape a δ).card : ℝ≥0∞) / Fintype.card M + (δ + εks + δlink + δin)
~~~

**5. A separator check the verifier runs per program.**
- *First step:* a Python function beside `verity.ir.cut`, `separates(graph, owner, K, B, D)`, a reverse search from D
  that avoids K.
- *What it gives:* decision 4's claim that every PoUW unit reaches y only through Z becomes checked on the IR, not
  argued.
- *Later:* an executable Lean check with a soundness proof into `Separates`. That needs a link from the executable
  partition to the abstract one, which `main` lacks: nothing ties `Flock.Partition` to `Audit.Partition`.

**6. An influence certificate for the stratified law: Theorem 6.3 without heavy replay units.**
- It builds on the store's `stratified_escape_le_exp`.
- It is needed only when a consumer wants a count finer than the served-output cap, which PoUW doesn't.
- The statement elaborates; the proof is not written yet:

~~~lean
theorem sum_admissible_le (σ : Fin n → Fin m) (k : Fin m → ℕ) (hk : ∀ s, k s ≤ (Law.stratum σ s).card)
    (w : Fin n → ℕ) {δ : ℝ} (hδ : 0 < δ) {z : ℝ} (hz : 0 ≤ z) :
    ∑ B ∈ univ.filter (fun B => ENNReal.ofReal δ ≤ (Law.stratified σ k hk).escape B), (2 : ℝ) ^ (∑ u ∈ B, w u) ≤
      Real.exp (z * Real.log δ⁻¹) *
        ∏ u, (1 + 2 ^ w u * Real.exp (-(z * (k (σ u) : ℝ) / (Law.stratum σ (σ u)).card)))
~~~

**7. Low priority:**
- ℓ\* adaptive completion (Lemma 5.3 in full), for cuts at the proof-unit level inside replay units;
- the exact matmul count, as a test oracle for certificates, in Python;
- advice composition (Sift Proposition E.1), once serving advice is counted;
- the budget-boundary reduction (Sift Theorem 5.5), in the planner.

**Do not port:**
- exemptions, and everything priced by λ;
- the Bernoulli second-stage formulas;
- the normalization and typing lemmas;
- the acyclic quotient;
- the gap sampler and the bank descriptor;
- input units in any sum.
