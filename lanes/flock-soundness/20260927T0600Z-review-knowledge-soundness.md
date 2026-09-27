---
cursor:
  subagentId: "bc-397556e5-2c0d-5e48-9d01-51e08c726604"
---

lane: flock-soundness · kind: review · status: for the lane, before any Lean · repo: danielreuter/verity · reviews `20260927T0535Z-draft-knowledge-soundness-analysis` against [PR #110](https://github.com/danielreuter/verity/pull/110) (`cursor/flock-compiled-8569` at `806f719e`, merged: `ASSUMPTIONS.md`, `DESIGN.md`, `CompiledSound.lean`, `Rewinding.lean`, `Game/Lock.lean`, `Defs.lean`, `Accounting/Schedule.lean`) and the Project doc `docs/lifetime-soundness.md`

# Review: the knowledge-soundness extraction analysis

## Verdict

**The argument is correct in substance, but not yet ready to formalize as written.** One slip, one non-problem, one better form, one gap.

1. **The core is right.** PR #110 proves `compiled_le_bad` for an arbitrary level-0 table, so (A) holds. The Markov step of §3 is sound: on $G=\{\sum_{p\in U}q_p<\varepsilon-\varepsilon_c\}$, every completion of $T^*|_O$ is committed, all at once. This is the "missing queries" bound of Chiesa–Dall'Agnol–Guan–Spooner (CDGS23). The old "coverage must be 99%" concern does go away.
2. **The numbers check, with one slip.** $K=2^{21.56}/(\varepsilon-\varepsilon_c)$ at $m=33$ is right. The hash term is $t\cdot2^{-233.4}/(\varepsilon-\varepsilon_c)$, not $2^{-232.9}$: the draft's value counts both reps twice. That is 0.5 bit on the safe side.
3. **§5 is not open.** The extractor chooses the completion itself, so it can decode the *completed* word at radius $\delta+\zeta'$, for every $u$. Puncturing to $O$ was an optimization nobody needs. Recommend neither route (i) nor (ii).
4. **A tighter form is available.** Compare fresh runs with the extractor's own table rather than $T^*$. The failure bound becomes $(K\,\mathrm{Adv}_0+N_0/(eK))/(\varepsilon-\varepsilon_c^-)$, the hash term is squared, and §4 (the $W$ analysis, $\zeta'$, `expect_offmass_le`) disappears.
5. **The audit needs a different form of the theorem, plus $\delta_{\rm link}$.** The product form $\Pr[\text{accept}\wedge\text{extraction fails}]$ comes out at $\approx2\varepsilon_c$. But $\delta_{\rm link}$, whose collision finder runs the extractor, is not addressed. A first estimate is $\approx2^{-65}$ at $t=2^{80}$ (audit B), which would dominate. Don't update the lifetime numbers until it is bounded.

Notation below is the draft's: $N_0$, $2Q_0=436$ level-0 openings per table, $q_p$, $T^*$, $\varepsilon$, $\varepsilon_c$, $\mathrm{Adv}_0$ (Lean `adv₀`, two continuations after the level-0 cap), $\rho=\tfrac12$, $\eta=\tfrac1{50}$, $\delta=1-\sqrt\rho-\eta=0.2729$.

## 1. Is the argument correct?

### 1.1 (A), checked against the Lean

- **What's proved.** `compiled_le_bad` bounds $\Pr[\mathsf{acc}\wedge\neg\mathrm{Committed}(C_0)]$ by `tableError` plus the bad-run mass, for any `C₀`. `bad_pointwise` splits a bad run three ways: a self-clash, a level-0 opening off `C₀`, or an opening off `plurC` at a later cap. Only the level-0 piece depends on `C₀`. So, for every level-0 table $T$:

  $$\Pr[\mathsf{acc}\wedge\neg\mathrm{Committed}(T)]\;\le\;\varepsilon_c^-+\Pr_\omega[\mathrm{Off}_0(T,\omega)]\qquad\text{(A}'\text{)}$$

  $$\varepsilon_c^-:=\mathrm{tableError}+\Pr[\mathrm{SelfClash}]+\sum_{r<2,\;\ell\ge1}\sqrt{N_\ell Q_\ell\,\mathrm{Adv}_{r,\ell}}$$

  Here $\mathrm{Off}_0(T,\omega)$ means run $\omega$ opens some level-0 position, with a verifying path, to a row other than $T$'s.
- **The draft's (A) follows.** Use $\mathrm{Off}_0(T)\subseteq\mathrm{Off}_0(T^*)\cup\bigcup_{p:\,T(p)\ne T^*(p)}\{\text{opens }p\}$, then `Rewinding.expect_bad_le` for $T^*$. At $q_p=0$ every opening count is zero, so any row is a plurality (`IsPlurality`).
- **A Lean gap to note.** `advR` is defined through `lockTable … (C0star …)`. For $T\ne T^*$, the refactor needs `advR` on `lockTable … T` to be the same number. It is, because `forkE` reads only compiled-side nodes and `plurC`, but that is a structural-induction lemma to write. The alternative is to state the bound with `advR` at $T$.
- **Row-level distance.** `Close` counts positions where every lane agrees, so the draft's "disagreement" is row-level, as `Committed` needs.

### 1.2 The run count and the Markov step

- **One Markov step covers every completion.** $\mathrm{Committed}(T_z)$ is a fixed fact once $U$ is fixed. By (A), failing it forces $\sum_{p\in U}q_p\ge\varepsilon-\varepsilon_c$. So a single Markov step bounds $\Pr[\exists z:\neg\mathrm{Committed}(T_z)]$, with no union bound over $z$.
- **The expectation.** $\mathbb E\sum_{p\in U}q_p=\sum_pq_p(1-q_p)^K\le N_0/(eK)$, since $q(1-q)^K\le qe^{-qK}\le1/(eK)$. CDGS23 state the same bound as $(1-\delta_j)^T\delta_j\le1/T$.
- **The run count.** $K=N_0/(e\tau(\varepsilon-\varepsilon_c))$ is $2^{21.56}/(\varepsilon-\varepsilon_c)$ at $m=33$ ($N_0=2^{21}$, $\tau=\tfrac14$) and $2^{23.56}/(\varepsilon-\varepsilon_c)$ at $m=35$.
- **It is larger than the old estimate.** This $K$ is about $2^6$ above the old coverage estimate ($N_0/Q_0$ times a log), because it pays for provers that open positions rarely. That is harmless for the table theorem. It does feed $\delta_{\rm link}$ (§4d), where it enters under a square root.
  - Optional refinement: accepted runs query $\ge Q_0$ positions, so rarely opened positions make up at most a $\ln(2/\varepsilon)/(2Q_0)$ fraction. That recovers most of the $2^6$.

### 1.3 The hash term and the success probability

- **The ingredients.** $\sum_pb_p\le\sqrt{N_0\cdot2Q_0\cdot\mathrm{Adv}_0}$ is the intermediate step of `bad_sq_le`, and $\Pr[p\in W]\le Kb_p$.
- **The arithmetic.** With $2Q_0=436$, $\mathrm{Adv}_0\le(2t)^2/2^{513}$, $\tau=\tfrac14$ and $\zeta'=\tfrac1{100}$:

  $$\frac{K}{\zeta'}\sqrt{\frac{2Q_0\,\mathrm{Adv}_0}{N_0}}=\frac{t\cdot2^{-233.4}}{\varepsilon-\varepsilon_c}\;(m=33),\qquad\frac{t\cdot2^{-232.4}}{\varepsilon-\varepsilon_c}\;(m=35)$$

  The draft's $2^{-232.9}$ is what $2Q_0=872$ gives.
- **The success probability** is $\ge1-\tau-t\cdot2^{-233.4}/(\varepsilon-\varepsilon_c)$, once decoding uses the completed word (§2).
- **The knowledge error.** "The knowledge error is $\varepsilon_c$ itself" overstates it. Success $\ge\tfrac12$ needs $\varepsilon-\varepsilon_c\ge t\cdot2^{-231.4}$, so state $\kappa=\varepsilon_c+t\cdot2^{-231.4}$.
- **The collision branch is optional.** $W$ already covers conflicting openings, since a conflict needs an off-plurality run. If the branch stays, the theorem must add the straight-line term $\binom K2\mathrm{Adv}_0$. Dropping it is simpler.

### 1.4 What the extractor must know

$K$ depends on $\varepsilon-\varepsilon_c$, which the extractor doesn't know.

- **For the audit (§4),** the extractor is an analysis device and may depend on $\varepsilon$.
- **For an efficient extractor,** as recursion's proof of knowledge needs, use either a fixed budget with the theorem stated for $\varepsilon\ge\varepsilon_0$, or doubling with the decidable stop "a satisfying witness is found".
- **Doubling needs an exponential tail,** because Markov tails fall only as $1/K$. Split the runs into $r$ disjoint blocks. Since $U=\bigcap_bU_b$, we get $\sum_{p\in U}q_p\le\min_b\sum_{p\in U_b}q_p$. So $r$ blocks of $K_1=2N_0/(e(\varepsilon-\varepsilon_c))$ runs fail with probability at most $2^{-r}$.

### 1.5 A tighter form: compare fresh runs with the extractor's own table

$T^*$ is the right reference for soundness, where no extractor exists. For extraction, it costs the rewinding square root.

- **The construction.** Take $T_E$: at each observed position, the first verifying opening the extractor saw, and a fixed row $z_0$ on $U$. A fresh run $\omega$ with $\mathrm{Off}_0(T_E,\omega)$ does one of two things:
  - it conflicts, at some $p\in O$, with the extractor run that supplied $T_E(p)$;
  - or it opens some $p\in U$.
- **The bound.** Each (fresh run, extractor run) pair is an independent pair of runs, which is one `adv₀` experiment. So:

  $$\mathbb E_E\Pr_\omega[\mathrm{Off}_0(T_E,\omega)]\le K\,\mathrm{Adv}_0+\frac{N_0}{eK},\qquad\Pr_E[E\text{ fails}]=\Pr_E[\neg\mathrm{Committed}(T_E)]\le\frac{K\,\mathrm{Adv}_0+N_0/(eK)}{\varepsilon-\varepsilon_c^-}$$

  The second step is (A′) with §3's own argument: a fixed fact, then Markov. At the draft's $K$, the failure probability is $\le\tau+\big(t\cdot2^{-244.7}/(\varepsilon-\varepsilon_c^-)\big)^2$ at $m=33$ ($2^{-243.7}$ at $m=35$).
- **The hash term is squared.** At $t/(\varepsilon-\varepsilon_c)=2^{120}$ it is $2^{-249}$ instead of $2^{-113}$. The effective $\kappa$ becomes $\varepsilon_c^-+t\cdot2^{-243.7}$.
- **$\varepsilon_c^-$ drops the level-0 rewinding term,** the largest single hash term in $\varepsilon_c$ ($\sqrt{N_0\cdot2Q_0}=2^{14.9}$ out of $S_{33}=2^{15.8}$). The hash part falls from $t\cdot2^{-239.7}$ to $t\cdot2^{-240.9}$.
- **§4 disappears.** So do $\zeta'$, $W$ and `expect_offmass_le`. The extractor decodes $T_E$ at radius $\delta$ exactly, and the list has at most $L_0=50$ entries by `closeMsgs_card_le`, which is already proved.
- **Where the square root goes.** This is CDGS23's reductor: recovered answers overwrite an all-$\alpha$ string, and unfilled queries are charged $\ell/T$. The difference is the binding step. CDGS23's position-binding adversary runs the whole reductor, at cost $\approx Kt$. Here it is replaced by a union over the $K$ fresh–extractor pairs, each a two-run finder of cost $2t$.

## 2. "Unseen positions as disagreements, compiled soundness for every completion"

- **"Compiled soundness for every completion" is sound, and it is the key idea.** On $G$, $\mathrm{Committed}(T^*|_O\oplus z)$ holds for all $z$ simultaneously. It is standard in both models.
  - CDGS23, as restated in CDDGS25 §4, initializes the extracted message to $\alpha^{\ell}$ for an arbitrary symbol $\alpha$.
  - In the random-oracle model, BCS16 and Chiesa–Yogev read the tree off the query trace. A leaf that was never queried can't later be opened without inverting the oracle, so its value is immaterial.
- **"As disagreements" is valid only through the avoidance step, and isn't needed.**
  - Avoidance needs, at each $p\in U$, a row outside $\{c(p):c\in M\}$, so $|M|<|\Sigma|$ suffices. The draft's $/N_0$ comes from a random-completion union bound.
  - The small-list regime holds while $\delta/(1-x)<1-\sqrt{\rho/(1-x)}$, which is up to $x=u/N_0\approx3.1\%$, not 1%.
  - Beyond that, a covering count still gives the draft's conclusion up to $x\le1-\rho-\delta\approx22.7\%$. If every $z$ is covered, some satisfying $c$ has $d_O(c,T^*)\le\lfloor\delta N_0\rfloor-u+a-1$, with $a=\lfloor N_0/\log_2|\Sigma|\rfloor+1$. Otherwise $|\Sigma|^a\le\binom ua\binom{N_0-u}{k}\le2^{N_0}$, which fails. Here $a/N_0=1/(128\cdot2^{k_0})\le2^{-11}$.
- **Why it's moot.** The extractor picks the completion, so it can decode $\hat T=T_{\rm obs}|_O\oplus z_0|_U$ directly.
  - On $G$, a satisfying codeword lies within $\delta N_0$ of $T^*|_O\oplus z_0$. Hence it lies within $(\delta+\zeta')N_0$ of $\hat T$ whenever $|W|<\zeta'N_0$.
  - $\delta+\zeta'=1-\sqrt\rho-(\eta-\zeta')$ is below the Johnson radius with margin $\tfrac1{100}$, for every $u$.
  - That is the draft's own $u=0$ case. Puncturing only ever improved the radius for $u>0$.

## 3. The open case: which route

**Neither (i) nor (ii).** Fill and decode (route 0), preferably in the extractor-table form of §1.5.

| Route | Tightness | Lean effort | Literature |
|---|---|---|---|
| **0. Fill with a fixed row, decode the full word** (recommended) | Radius $\delta+\zeta'$ for every $u$, or exactly $\delta$ in the §1.5 form. No extra runs, no condition on $u$ or $\varepsilon$. | Nothing new at the oracle layer. Decoding is full-length, so the puncturing bridge goes away. | CDGS23 and CDDGS25 in the standard model; BCS16 and Chiesa–Yogev in the ROM. FRI-Binius extracts straight-line by decoding the full word, then compiles with BCS. |
| (i) Oracle with $\bot$ | Erasure-aware radius, better only for large $u$; same $K$ | Re-prove the level-0 half of `table_sound` over $\Sigma\cup\{\bot\}$ (MCA on punctured domains, the list size, the phase lemmas) | Not a standard IOP notion; the literature pushes $\bot$ into the compiler |
| (ii) Threshold | Loses $\ln(N_0/\beta)\approx2^4$ in $K$; brings a coverage event back | Accounting, plus a coverage lemma | Barak–Goldreich universal arguments (frequent answers; conflicting positions become collisions) |

**Route (i) is sound, just not worth it.**

- A1 (BCHKS25 Theorem 4.6) holds for Reed–Solomon codes on any evaluation set.
- Puncturing only widens the margin. With the punctured radius $\delta'=(\delta-x)/(1-x)$: $1-\sqrt{\rho/(1-x)}-\delta'=\big(1-\delta-\sqrt{\rho(1-x)}\big)/(1-x)\ge\eta/(1-x)$.
- But it reopens proved code for no gain at the parameters that matter.

**Route (ii) is the older, looser style.**

- The literature lineage is Barak–Goldreich's universal-argument extractor.
- Between the two, (i) is better. Route 0 dominates both.

## 4. What the audit composition still needs

**(a) The product form.** The audit bound consumes $\Pr[\text{accept}\wedge\text{extraction fails}]$ (lifetime doc §3, step 2(b)). A success probability $\ge1-\tau$ at fixed $\tau$ doesn't work: with $\tau=\tfrac14$ the product is $\varepsilon/4$.

Acceptance and the extractor's runs are independent given the prover's state. So, per state:

$$\varepsilon\cdot\Pr_E[\text{fail}]\le2\varepsilon_c^-+2\Big(K\,\mathrm{Adv}_0+\frac{N_0}{eK}\Big)$$

This takes the case $\varepsilon\le2\varepsilon_c^-$ and the case $\varepsilon/(\varepsilon-\varepsilon_c^-)<2$ together. For this term no reduction runs the extractor, so $K$ may be chosen freely. With Jensen over states:

$$\Pr[\mathsf{acc}\wedge E\text{ fails}]\le2\varepsilon_c^-+4\sqrt{N_0\,\mathrm{Adv}_0/e}\le2\varepsilon_c^-+t\cdot2^{-243.7}\qquad(m=33;\ 2^{-242.7}\text{ at }m=35)$$

- At $t=2^{80}$ that is $2^{-159.8}$, against the lifetime doc's rough $\sqrt{t\cdot2^{-227}}=2^{-73.5}$.
- With the draft's §4 instead, block amplification gives $\approx2\varepsilon_c+2^{-r}+r\,t\cdot2^{-233.4}$. That is also linear in $t$: $2^{-146}$ at $r=128$.

**(b) The session.** State the theorem for one table inside a session strategy.

- The extractor reruns the session after all $J$ level-0 caps, and the rest of the session is part of $P^*$.
- $\varepsilon:=\Pr[u^*\text{'s table accepts}\mid\text{state}]$, with $u^*$ fixed before the first session coin, as the lifetime doc does for soundness.
- Only $u^*$'s extraction is needed for the first-hit charge.
- If every sampled table must be extracted (to define $X$, say), add a union over the $J$ tables: $J$ times the conflict term, and $r\ge128+\log_2J$.

**(c) Canonical values.** The extractor should output the `hm96` values, not "one satisfying witness".

- Two satisfying list members that differ behind a commit string are an `hm96` collision the extractor can output.
- $X$ ("the value the extractor recovers most often") needs this, and so does `registered_weights`.

**(d) $\delta_{\rm link}$ is not addressed, and it probably dominates.** Its collision finder runs the extractor on two independent draws. So the extractor's run count, $K\propto N_0/\varepsilon$, enters the collision-resistance bound. Under strict-time CR, truncate at acceptance $\varepsilon_{\min}$ and optimize.

A first estimate, with $X$ defined by the draw-level analogue of §1.5:

- $K_d$ independent draws, each extracted;
- a missing term $N_s/(eK_d)$;
- a conflict term $K_d\,\mathrm{Adv}_{\rm link}$, with $\mathrm{Adv}_{\rm link}\le(2Kt)^2/2^{513}$.

$$\delta_{\rm link}\lesssim\min_{\varepsilon_{\min}}\Big[\varepsilon_{\min}+2\sqrt{N_s/e}\cdot\frac{2K(\varepsilon_{\min})\,t}{2^{256.5}}\Big],\qquad K(\varepsilon_{\min})\approx\frac{128\cdot4N_0}{e\,\varepsilon_{\min}}$$

- **The numbers.** For audit B at $m=33$ ($N_s=2^{28.3}$) this is $2\sqrt{t\cdot2^{-212.5}}$: $2^{-73.3}$, $2^{-65.3}$ and $2^{-50.3}$ at $t=2^{64}$, $2^{80}$ and $2^{110}$.
- **What that means.** It sits above the lifetime doc's rough knowledge row ($2^{-73.5}$ at $2^{80}$). So sharpening the table term alone doesn't sharpen the audit.
- **Where the square root comes from.** It is the strict-time phenomenon CDGSY24 discuss. Their expected-time reduction would remove the $\varepsilon_{\min}$ trade-off, at the price of an expected-time CR assumption that isn't in Table 1.
- **Recommendation.** Bound $\delta_{\rm link}$ in the same paper note, from the same lemmas, before formalizing it or changing the lifetime numbers.

**(e) Expose the extractor's hash count.**

- $\delta_{\rm link}$ and `registered_weights` are reductions that run the extractor. So `table_knowledge_sound` should output the extractor's cost ($K$ session reruns, $Kt$ hash evaluations) next to its error.
- Efficient decoding (Guruswami–Sudan plus the pruned interleaved search) is needed only by those reductions. The table theorem itself can decode non-constructively, through `closeMsgs`.

## 5. Changes to the Lean plan (draft §6)

1. **`table_sound_compiled_of_table`.** State (A′) with the deviation term $\Pr[\mathrm{Off}_0(T)]$. That is `bad_le` without its level-0 `expect_bad_le` step. Add the lemma that `advR` doesn't depend on the level-0 table.
2. **`expect_offmass_le`.** Drop it; the §1.5 form doesn't need it.
3. **The $K$-run experiment.**
   - $K+1$ independent runs.
   - A union over the $K$ fresh–extractor pairs, each distributed as `adv₀`'s `expect₂`.
   - $\sum_pq_p(1-q_p)^K\le N_0/(eK)$, then one Markov step.
   - Disjoint blocks where an exponential tail is needed.
4. **Decoding.** Full length, radius $\delta$. The table theorem decodes non-constructively via `closeMsgs`. Guruswami–Sudan and the pruning move to `registered_weights`.
5. **`table_knowledge_sound`, in two forms,** with the extractor's cost as an output. Then $\delta_{\rm link}$.

~~~lean
-- deterministic prover, K runs, T_E = first verifying opening per observed position, z₀ elsewhere
theorem table_knowledge_sound (hε : εc⁻ < ε) :
    Pr[¬ Committed (T_E K)] ≤ (K * adv₀ + N₀ / (exp 1 * K)) / (ε - εc⁻)
-- the form the audit consumes (acceptance and the extractor's runs independent given the prover)
theorem table_knowledge_sound_joint :
    Pr[accepted ∧ ¬ Committed (T_E K)] ≤ 2 * εc⁻ + 2 * (K * adv₀ + N₀ / (exp 1 * K))
~~~

## Sources

- **Repository:** [PR #110](https://github.com/danielreuter/verity/pull/110) at `806f719e`: `ASSUMPTIONS.md` §1.2, §1.3, §7; `DESIGN.md` §2, §3; `CompiledSound.lean` (`compiled_le_bad`, `bad_pointwise`, `bad_le`, `adv₀`, `advR`, `opOf_conflict_collision`); `Rewinding.lean` (`bad_sq_le`); `Game/Lock.lean` (`forkE`, `leafE_off_le`); `Defs.lean` and `Model/Statement.lean` (`Committed`, `Close`, `closeMsgs`); `ListSize.lean` (`closeMsgs_card_le`); `Accounting/Schedule.lean` (`fast100`: level 0 is $2^{20}$ columns at rate $\tfrac12$, 218 queries, $2^{k_0}$ lanes).
- **Project:** `docs/lifetime-soundness.md` §2–§3 and §9; `note:20260926T2330Z-finding-knowledge-soundness`.
- **External:**
  - A. Chiesa, M. Dall'Agnol, Z. Guan, N. Spooner, "On the Security of Succinct Interactive Arguments from Vector Commitments", [ePrint 2023/1737](https://eprint.iacr.org/2023/1737), plus Guan's [slides](https://ziyiguan.github.io/slides/kilian-pcp-iop.pdf): rewinding reductor, "missing queries" $\ell/T$.
  - A. Chiesa, M. Dall'Agnol, Z. Di, Z. Guan, N. Spooner, "Quantum Rewinding for IOP-Based Succinct Arguments", [ePrint 2025/947](https://eprint.iacr.org/2025/947): §4 reductor ("initialize $\tilde\pi_i:=\alpha^{\ell_i}$, $\alpha$ an arbitrary symbol"), Lemma 5.4 (the IOP extractor run on the filled oracle).
  - A. Chiesa, M. Dall'Agnol, Z. Guan, N. Spooner, E. Yogev, "Untangling the Security of Kilian's Protocol", [ePrint 2024/1434](https://eprint.iacr.org/2024/1434): strict-time versus expected-time rewinding.
  - E. Ben-Sasson, A. Chiesa, N. Spooner, "Interactive Oracle Proofs", TCC 2016-B, [ePrint 2016/116](https://eprint.iacr.org/2016/116); A. Chiesa, E. Yogev, *Building Cryptographic Proofs from Hash Functions* ([snargsbook.org](http://snargsbook.org/)).
  - B. Barak, O. Goldreich, "Universal Arguments and their Applications", SICOMP 2008 ([ECCC TR01-093](https://eccc.weizmann.ac.il/eccc-reports/2001/TR01-093/)).
  - B. Diamond, J. Posen, "Polylogarithmic Proofs for Multilinears over Binary Towers" (FRI-Binius), [ePrint 2024/504](https://eprint.iacr.org/2024/504) §2: polynomial commitment defined in the IOP model, straight-line extraction by decoding, BCS for compilation.
  - A. Novakovic, G. Angeris, "Ligerito", [ePrint 2025/1187](https://eprint.iacr.org/2025/1187): guarantees stated with the Merkle layer abstract.
  - A. Block, A. Garreta, J. Katz, J. Thaler, P. Tiwari, M. Zając, "Fiat–Shamir Security of FRI and Related SNARKs", [ePrint 2023/1071](https://eprint.iacr.org/2023/1071): round-by-round knowledge soundness at the IOP layer, then BCS in the ROM.
  - BCHKS25, [ePrint 2025/2055](https://eprint.iacr.org/2025/2055), Theorem 4.6 (A1).

## Summary

1. **Verdict:** correct in substance. (A) and the Markov step check against PR #110, and $K\approx2^{21.6}/(\varepsilon-\varepsilon_c)$ checks. The hash term is $t\cdot2^{-233.4}/(\varepsilon-\varepsilon_c)$; the draft's $-232.9$ counts both reps twice.
2. **The open case is an artifact.** The extractor picks the completion, so it can decode the completed full word at radius $\delta+\zeta'$ for every $u$. This is the standard arbitrary-symbol fill of CDGS23 and BCS16.
3. **Route:** neither (i) nor (ii). Fill and decode, preferably comparing fresh runs with the extractor's own table. That removes §4 and the square root: failure $\le(K\,\mathrm{Adv}_0+N_0/(eK))/(\varepsilon-\varepsilon_c^-)$.
4. **Required fixes:** decode the completed word; fix the constant and state $\kappa$ honestly; say how the extractor learns $\varepsilon$; add the product form $\Pr[\mathsf{acc}\wedge E\text{ fails}]\le2\varepsilon_c^-+t\cdot2^{-243.7}$, with canonical `hm96` values and the extractor's hash count as outputs.
5. **Audit:** the table term becomes $\approx2\varepsilon_c$. But $\delta_{\rm link}$, whose finder runs the extractor with $K\propto1/\varepsilon$, is unaddressed and probably dominates at $\approx2^{-65}$ ($t=2^{80}$, audit B). Bound it before changing the lifetime numbers.
