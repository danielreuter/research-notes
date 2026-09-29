---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: draft · status: done (#163 at `7516258b`), the plan before the Lean · repo: danielreuter/verity · follows Daniel's decision (Sep 27, 14:34Z) and `DESIGN.md` §3 in [PR #127](https://github.com/danielreuter/verity/pull/127)

# The expected-time extractor and the link theorem in Lean: plan

*Update 16:44Z: all done, in [#163](https://github.com/danielreuter/verity/pull/163).*
- **The theorem** is `flock_batched_linkSoundE` (`Audit/FlockLink.lean`), with standard axioms only.
- **Changes from the plan below:**
  - **Per commit string.** The finder targets one commit string and draws only unit sets that read it. So the bound is $Q_s(2(1+k)t'/2^{256.5} + 1/(eM) + k/(eR_w))/(1-\rho)$, with $Q_s\le N_s$ the expected number of commit strings the drawn units read.
  - **Self-collisions** (two drawn units opening one string differently) are one of the finder's successes, not a separate term.
  - **The plurality** is over the finder's own trial, and the ideal law differs from it by at most $k/(eR_w)$ (`expectAcc_le_waits`).
  - **`ValueBinding`** is a structure argument (commit strings `Pos`, values `Val`, openings, `collide`), not a `Prop`, because the finder uses its functions.
  - **The generic finder** is `LinkFinder.lean`; `Game/Seq.lean` and `ExtractWait.lean` are its infrastructure.

**Goal.** Discharge `LinkSound δ_link` for the batched compiled audit under A2 (`Assumptions.SHA512ExpectedTimeCR`, in #127), with δ_link the record term $t\cdot N_s(8N_0/e)/2^{256.5}$ up to lower-order terms. audit-lean then composes it with `extraction_audit_count`, as it does with #145's `analysisB`. The paper argument is `DESIGN.md` §3. This note is the Lean shape and the order of work.

## 1. Why a new analysis, not `analysisB`

- `analysisB` fixes `Kr` reruns. Under A2 the link finder's cost must not trade against the missing term, so the extractor stops after `k` *accepted* reruns: `1 + k` runs in expectation, whatever ε.
- The bound is relative: the missing term is `ε/c`, absorbed into the acceptance probability. `ExtractionAnalysis.cover` (`Pr[accept] ≤ ks + link`) can't carry that with raw joint probabilities, so the new analysis scales both fields by `c/(c−1)` and proves `cover` from the relative inequality.

~~~lean
-- the extractor's law: k independent accepted reruns of everything after Commit
Ek k σ F := expectN g σ k (fun bs => (∏ b ∈ bs, acc b) * F bs) / ε σ ^ k   -- 0 when ε = 0

analysisBE (c k) (hMCA) (hlow) : ExtractionAnalysis L Reg (batchedSession H E plan) where
  ks  S R τ u   := c/(c−1) · ofReal (epsS + √(k · adv₀S))          -- u's table, in the session
  link S R τ u X := c/(c−1) · ε · Ek k σ (LinkEvB … u X ∘ extractTableS)
  cover := one_le_fail_add_B' pointwise, knowledge_sound_E, then ε(1 − 1/c) ≤ … ⇒ ε ≤ …
~~~

`KnowledgeSound` of `analysisBE` is then its own `ks`, averaged over the draw (as `ksAvgB`).

## 2. Stages

- **S1. Accepted-only deviation.** `session_sound_of_table` with `accepted ∧ Off₀` as its deviation. The coupling's bad event already requires acceptance, and only `bad_pointwise` (`CompiledSound.lean`) drops it: its level-0 disjunct becomes `b.accepted = true ∧ ∃ p, Off …`, proved by `if_pos ⟨hB.1, ho⟩`. I'll add it as a variant, so the existing users don't move.
- **S2. The expected-time knowledge bound**, per table in the session:
  `ε · Ek[¬Committed] ≤ ε_c⁻ + N₀ε/(ek) + (k/ε)·adv₀S`, then `≤ ε_c⁻ + ε/c + √(k·adv₀S)`, via `min(ε, ·)`.
  - The missing term: `Ek[p missed] = (1 − q_p/ε)^k` by `expectN_prod_map`. Then `Σ_p q_p(1 − q_p/ε)^k ≤ N₀ε/(ek)` is `mul_one_sub_pow_le`, scaled by ε.
  - The conflict term: `off_firstTable_le` unions over the `k` accepted reruns. Each costs `adv₀S/ε` under the conditional law.
- **S3. `analysisBE`,** with `flock_batched_knowledgeSoundE` and `flock_batched_countE`. The latter is the count curve with the new `ks` and δ_link still named. audit-lean can switch to it as soon as it lands.
  - *Found at 15:40Z:* in the batched session, the reruns must be conditioned on the **session's** acceptance (every table accepts), not table `j`'s. The relative term has to be `ε_S/c`, with `ε_S` the audit's acceptance probability. Conditioning on table `j` gives `ε_j/c`, and `ε_j` can be far above `ε_S`.
  - So S1–S2 generalize to any acceptance event that implies table `j`'s, which is all the coupling uses (`session_sound_of_table_of`). Their current forms are the special case.
  - `k` is a natural number, so the scaling is `1/(1 − r_j)` with `r_j = N₀_j/(ek) < 1`. That is `c/(c−1)` at `k = cN₀/e`, per table.
- **S4. The binding interface and the value layer.**
  - `ValueBinding` is named, like `LoweringSoundB`. A satisfying witness of a drawn unit's table gives, for each io wire `g`, an opening (value, salt) of `g`'s registered commit string. And `collide` turns two openings of one string with different values into a SHA-512 collision, with its proof. M0's `hm96-sha512` leaf layout discharges it; until then the model has no commit strings.
  - `Xplur R τ g` is the plurality over `v` of `p_{g,v} = Pr[Ext recovers g with value v]`. `Ext` runs the draw, a fresh session, and if it accepts the `k`-accepted extraction. It reads each table's first close satisfying message, and each wire from the first drawn unit that has it.
- **S5. The finder and its cost.**
  - `linkFinder` is a `Game` with a fixed strategy. It picks `g` uniformly from the committed wires `G` and runs `Ext`. If `Ext` recovered `g`, it runs up to `M` more `Ext` until one recovers `g`, and outputs `collide` if the two values differ.
  - Inside `Ext`, the reruns are `k` geometric waits of at most `R` runs each, so the finder is a finite game. Its cost per outcome is `t'` times the runs it played.
  - Lemmas: a finite Wald identity (`E[Σ_{i≤τ} X_i] = E[τ]·E[X]` for a stopping time), and `E[min(R, Geom ε)] ≤ 1/ε`. Together they give `E[cost Ext] ≤ (1+k)t'` and `E[cost linkFinder] ≤ 2(1+k)t'`.
  - Tails: the truncated waits against `Ek` cost at most `k/(eR)` per extraction, from `ε·k(1−ε)^R ≤ k/(eR)`. The truncated aux loop costs `Σ_g r_g(1−r_g)^M ≤ |G|/(eM)`. At `R = M = 2^300` both are below `2^-280`.
- **S6. The link theorem.**
  - (a) `Pr[acc ∧ LinkEvB at u*]` is at most `Pr[∃ g, Ext recovers g with v ≠ Xplur g]`, plus a self-collision term: two drawn units in one extraction that read `g` differently, which is one `Ext`'s worth under A2.
  - (b) The plurality step: `Σ_g (r_g − p_{g,max}) ≤ Σ_g (r_g − Σ_v p_{g,v}²/r_g)`, where the right side sums the per-string collision probabilities.
  - (c) That sum is `|G|·Pr[linkFinder succeeds]`, plus the tails.
  - (d) A2 for `linkFinder`.
  - (e) The bound doesn't depend on the target unit: the link at `u` is at most the any-unit event. So one `Xplur` serves every rule `tgt`, which `LinkSound` needs.
- **S7. Numbers.** δ_link at `c = 2`, `k = ⌈2N₀/e⌉` is at most `t'·N_s(8N₀/e)/2^256.5·(1 + 2^-18)`: an `Accounting` lemma, with `decide +kernel` on the rational parts.

## 3. What audit-lean receives

~~~lean
theorem flock_batched_linkSoundE (hMCA) (hbind : P.ValueBinding …) (hlow : P.LoweringSoundB …)
    (hCR : ∀ R τ, Assumptions.SHA512ExpectedTimeCR H (linkFinder … R τ) … out cost) :
    (P.analysisBE H E plan tab decode (Xplur …) c k hMCA hlow).LinkSound (δlinkE …)
~~~

`analysisBE` takes the place of `analysisB` in their composition. `ValueBinding` is theirs to discharge from the leaf layout, or ours, whoever is first once M0 pins it. Their composed theorem inherits `hCR`.

## 4. Tractability and order

- **Done at 15:45Z (#163, head `62cd2abd`):** S1–S3.
  - The acceptance event is any event that implies the table's (`bad_pointwise_of`, `session_sound_of_table_acc`, `session_knowledge_sound_acc`).
  - The batch conditions on the session accepting (`SessionBatchAcc.lean`: `joint_le_accB`, `one_le_fail_add_accB`).
  - `Audit/FlockBatchedAcc.lean` has `analysisBE hMCA decode Xc k hk hr hlow`, whose `cover` is `ε(1 − r) ≤ a + ε·Pr[link]`, plus `flock_batched_knowledgeSoundE`, `flock_batched_countE` and `flock_batched_drawnE`.
  - Standard axioms only. It reused `Session.lean`, `SessionBatch.lean`, `Extract.lean` and `Knowledge.lean` with no new infrastructure.
- **Next:** S4–S6, the bulk. S4's interface is small.
- **Riskiest:** S5. It needs `prob`/`expect` of `Game.bind` with composed strategies; `Strategy.ofBind` exists, but there is no `expect_bind` lemma yet. It also needs the finder as one game that plays the prover inside it.
- **Blocked on M0** for discharging `ValueBinding` only, not for stating or proving the link theorem against it.

## 5. If the record moves

- `c`, `k`, `R` and `M` are parameters. The record's constant lives only in S7.
- **A first-recovery value layer** (`4N₀/e`, one bit better) keeps S1–S3 and S5's lemmas. It replaces S4's plurality and S6(b) with an averaging step (some aux outcome is at most the mean, which fixes `X`), and needs a finder that waits for every recovered string.

## 6. Risks

- The `ε^k` division at `ε = 0`: define `Ek` as 0 there, harmless since both fields carry a factor ε.
- Real `√` and powers inside `ENNReal`: follow `ksBoundB`'s `ofReal` pattern.
- `G` stands for the committed wires, and `|G| = N_s` in the numbers. Until `ValueBinding`, it is the set of io wires.
