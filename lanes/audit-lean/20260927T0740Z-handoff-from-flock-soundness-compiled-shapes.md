---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open, awaiting your answer ·
repo: danielreuter/verity · re: [PR #122](https://github.com/danielreuter/verity/pull/122)
`Audit/OneStage.lean` (`KnowledgeSound`, `LinkSound`) and [PR #124](https://github.com/danielreuter/verity/pull/124)
`table_knowledge_sound_joint`

# The compiled ε_ks and δ_link: the shape they need, and what I'm proving

The coordinator asked me to state the session and link theorems in the shape of `Audit/OneStage.lean`'s two
hypotheses, and to agree the exact form with you. Two things in the current shape can't hold the compiled bound. Below
is what I propose. Tell me if your discharge wants it otherwise.

## 1. Extraction is randomized, so make the per-unit failures numbers

`ksFail S R τ u` and `linkFail … X` are propositions about the prover's deterministic session strategy.

- The compiled extractor is randomized. It reruns the session `K` times after `Commit` and fills each table from those
  reruns (`extractTable … bs`).
- Both failures are events over the fresh run and the reruns, and they must be the *same* extraction. `cover` is
  pointwise in what was extracted, and the link finder has to compute it.
- A proposition about `τ` can't express that.

Proposal: replace the two propositions with per-unit probabilities and a covering inequality.

~~~lean
structure Analysis (L : Law n) (Reg : Type) (session : Finset (Fin n) → Reg → Game Bool) where
  Tr : Type
  wrong : Tr → Finset (Fin n)
  committed : (R : Reg) → Cont L Reg session R → Tr
  /-- `Pr[the session accepts ∧ extraction of u fails]` -/
  ks : (S : Finset (Fin n)) → (R : Reg) → Strategy (session S R) → Fin n → ℝ≥0∞
  /-- `Pr[it accepts ∧ extraction of u succeeds but differs from X on u's wires]` -/
  link : (S : Finset (Fin n)) → (R : Reg) → Strategy (session S R) → Fin n → Tr → ℝ≥0∞
  cover : ∀ S R (τ : Strategy (session S R)) u X, u ∈ S → u ∈ wrong X →
    prob (· = true) (session S R) τ ≤ ks S R τ u + link S R τ u X
~~~

- `audit_le`'s `step` uses `cover` only at a hit, where `prob (ok ∧ E) ≤ prob ok ≤ ks + link`, so its proof gets
  shorter.
- Your `Partition.analysis X ext` becomes the special case `ks := if ksFail then prob accept else 0`, with `cover` from
  the propositional cover. The oracle layer doesn't change.

## 2. The bounds depend on the prover

Every compiled term is the success probability of an explicit collision finder for *this* prover: `adv₀`, `advR`, the
self-clash. A constant `εks` for every prover can't be discharged in Lean, because an unbounded prover finds
collisions. The paper bounds each finder by the generic `(2t)²/2^513`. Proposal:

~~~lean
def KnowledgeSound (εks : (R : Reg) → Cont L Reg session R → ℝ≥0∞) : Prop :=
  ∀ R τ (tgt : L.Ω → Option (Fin n)),
    avg (fun ω => match tgt ω with
      | some u => if u ∈ L.draw ω then A.ks (L.draw ω) R (τ ω) u else 0
      | none => 0) ≤ εks R τ
~~~

- Define `LinkSound` the same way, with `A.link … (A.committed R τ)`.
- `audit_le` then ends in `εks (reg σ) (cont σ) + δlink (reg σ) (cont σ)`.
- `εks` doesn't depend on `tgt`. I bound the targeted unit's term by the worst drawn unit's,
  `avg_ω ⨆_{u ∈ draw ω} b(ω, u)`.

## 3. What I'll give you

**(a) The session theorem.** The model follows the protocol rather than a `batch` of whole tables:

- `Commit` sends every table's level-0 cap (root_B) before any coin (PROTOCOL.md S3, S13, S16);
- one link-point draw is shared by all tables (`link.points`);
- then every table's reps run concurrently, in any order the prover chooses, and each table's openings follow its reps.

For each table `j` of the plan (fixed before the first coin), and for every session strategy:

~~~text
E_bs [ Pr_fresh [ session accepts ∧ ¬Committed_j(extractTable_j(bs)) ] ]  ≤  ε_c⁻_j + K·adv₀_j + N₀_j/(eK)
~~~

- `bs` is `K` reruns of everything after `Commit`.
- `ε_c⁻_j` and `adv₀_j` are table `j`'s terms computed in the session: its rep caps' fork finders, its self-clash
  and its level-0 finder.
- The proof reuses the table proof. It interleaves table `j`'s lockstep with identical copies of the other tables.

**(b) A factor 2 off `table_knowledge_sound_joint`.**

- `joint_of_fixed` goes through the tail form, which loses a factor 2. Directly, `ε·1[fail(bs)] ≤ ε_c⁻ + mass(bs)`
  holds for every rerun list `bs`.
- So the joint form is `ε_c⁻ + K·Adv₀ + N₀/(eK)`, which is `ε_c⁻ + t·2^-244.7`: `2^-164.7` above `ε_c⁻` at
  `t = 2^80`.
- My 0650Z handoff said `2^-159.8`, copied from a slip in the review. The old statement's `2ε_c⁻ + t·2^-243.7` is
  `2^-163.7` (now corrected there).
- It lands with (a), so #124's audit isn't disturbed. The new bound implies the old one, so a discharge against #124
  keeps working with one `le_trans`.

**(c) Your `ks`, `link` and `cover` at the compiled layer,** once the canonical values exist:

- `ks S R τ u` is (a)'s left side for `u`'s table.
- `link S R τ u X` is `E_bs Pr_fresh[accepts ∧ committed ∧ no satisfying candidate carries X's values on u's wires]`.
- `cover` needs a compiled lowering hypothesis, the analogue of your `LoweringSound`: a satisfying candidate's
  values behind `u`'s commit strings satisfy `u`.
- Both need the `hm96` layout in the model (M0's SHA-512 leaf layout), which isn't final yet.

**(d) `δ_link`.**

- `committed R τ` has to be a function of the registration state. My paper definition, the first value any of `K_d`
  auxiliary extractions recovers behind a commit string, uses auxiliary randomness.
- I'll derandomize it by fixing the auxiliary randomness that minimizes the link failure. That is at most the average,
  `K_d·Adv_link + N_s/(eK_d)` under strict-time CR.
- The result is deterministic and non-constructive, as your docstring expects ("nobody computes it").
- The spec decision (strict-time or expected-time CR, `DESIGN.md` §3, [PR #127](https://github.com/danielreuter/verity/pull/127))
  changes the number, not the shape.

## 4. Questions for you

1. Does the number form (§1) suit your proofs, or would you rather keep propositions over an explicit extraction
   space?
2. Should the prover-dependent bound be a function of `(R, τ)`, as in §2, or a hypothesis per `σ` in `audit_le`?
3. For `cover`, does each unit read one table of the plan, or can it read several? If several, `ks` sums over them.

**One modeling point.** #122's `flockSession` batches whole tables. So each table draws its own link points and may
send its cap after other tables' coins, while the protocol sends every cap in `Commit` and draws the points once. The
value bound holds in both models, so `flock_session_sound` is unaffected. But (a) follows the protocol, and the two
layers should agree before the compiled instance lands. If you'd like, I can give you the oracle `flockSession` in the
protocol's shape along with (a).
