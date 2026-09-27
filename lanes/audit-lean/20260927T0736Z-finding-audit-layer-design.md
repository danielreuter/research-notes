---
id: audit-lean/20260927T0736Z-finding-audit-layer-design
campaign: verity
lane: audit-lean
kind: finding
status: current
repo: danielreuter/verity
origin: audit-lean
---

# The audit layer's design notes (moved from soundness/DESIGN.md §12)

The full rationale behind `backends/flock/verifier/lean/soundness/FlockSoundness/Audit/`. The repo's `DESIGN.md` §12 keeps a summary and cites this note. The text is as of branch `cursor/audit-compiled-ks-f568`.

## The audit layer: the integrity profile

`docs/audit-protocols.md` §4 is the plan. This section records how the Lean follows it and where it departs.

### 1 Why strategies, not `value`

The plan states `SessionSound` with `value`, the optimal prover's success. `table_sound_exec` bounds `prob … σ` for every
strategy instead. The two differ: `value` can exceed every strategy's `prob` when some branch has no strategy at all (a
`send` of an empty type), so a strategy-level bound does not give a `value` bound. The audit theorems therefore take
per-strategy hypotheses and give per-strategy conclusions (`Game/Prob.lean`: `prob_mono`, `prob_or_le`, `prob_map`). A
randomized prover is a mixture of deterministic ones, so nothing is lost.

### 2 Knowledge soundness and the link term, not soundness

Halevi–Micali leaves open to essentially any value, so "the committed values" exist only through extraction (§3,
ASSUMPTIONS.md §7). The one-stage theorem is abstract over an `Analysis`:

- the committed transcript, a function of the prover's state at registration;
- for each drawn unit and session state, two failure events: extraction fails (`ksFail`), or it succeeds and disagrees with
  the committed transcript on the unit's wires (`linkFail`);
- `cover`: a wrong unit fails one way or the other.

For a partition, `cover` is proved (`Partition.analysis`): an extracted opening that satisfies the unit and agrees with
`X` on its committed inputs and outputs makes the unit correct in `X` (`correct_congr`).

**The proof** of `audit_le` has three cases. Fix the prover's registration `R` and state `τ`, and so `X`. For each draw
`S`:

- if `S` misses `wrong(X)`, bound by the indicator of the event;
- otherwise pick a wrong drawn unit, a function of `(R, τ, S)` fixed before the session's first coin, and apply `cover`.

Averaging over `S` gives the sampling term plus the two hypotheses' averages. This is lifetime-soundness §3's first-hit
charge. The hypotheses quantify over every such picking rule, the weakest uniform form that the composition uses.

**The oracle layer is a special case** (`Partition.oracle`): the registration is the transcript and extraction returns
it, so `ksFail` is "the unit is wrong", `SessionSound` gives `KnowledgeSound`, and the link term is zero.

### 3 Transcripts and partitions

- **Transcripts are total** (`Fin C.N → Bool`); only committed entries are read. The plan's subtype
  `P.committed → Bool` would need transport at every restriction. With total transcripts, a coarse transcript is the fine
  one, and variant (a)'s coarse bound is one inequality (`Refines.card_wrong_le`).
- **The committed set is derived:** inputs, outputs, and every gate a gate of another unit reads (`Partition.committed`).
- **One evaluator.** `Circuit.run` evaluates with some gates fixed. The circuit's evaluation fixes the inputs, and a
  unit's local evaluation fixes every gate outside the unit to the transcript. `compose`, `compose_cone`, `correct_congr`
  and `Refines.localEval_eq` are strong inductions over gate indices, using only `topo`.

### 4 Two-stage and the laws

- **The second-stage coins** are drawn for every coarse unit, `∀ u, (L₂ u).Ω`, and only the drawn units' coordinates are
  used. That has the same distribution on what matters as coins for the drawn units only, and it avoids types that
  depend on the draw.
- **The effective escape** takes, inside each drawn wrong coarse unit, the largest miss probability of a fine unit in it.
  The prover chooses the interior after the first draw, so it chooses which fine unit is wrong. The fine units' draws in
  different coarse units are independent (`prCoin_pi_forall`).
- **Minimax** (`subset_minimax`) follows the plan's argument. First, averaging `escape B` over uniform `K`-sets gives
  `E[C(n − |S|, K)]/C(n, K)` for any law (`avg_escape_subsets`). Second, Jensen's step uses the supporting line of
  `s ↦ C(n − s, K)` at `k`, in `ℕ` (`choose_support`, from falling drops by Pascal's rule), rather than convexity over
  `ℝ`, where `C(n − s, K)` is not convex.
- **Tightness and the counterexamples** (`Audit/Examples.lean`) hold for any first-stage law, not only the plan's
  Bernoulli. The dishonest prover registers every chain's output wrong and commits an honest interior. Each wrong
  chain's only wrong fine unit is then its last gate, which a uniform `k₂`-subset misses with probability
  `C(nv − 1, k₂)/C(nv, k₂)`. The dilution counterexample compares with `L₁.miss K`: the `m`-dependent reading at
  `m = nv` gives each wrong chain the escape `1 − p` for Bernoulli(`p`), which is `L₁`'s own escape. So that reading is
  one-stage over the coarse partition with `L₁`, and the prover beats it whenever the first stage draws something and
  the second leaves a gate undrawn.
- **(b2) thinned** (`effEscape_bernoulli`) is proved on NOT chains, where every chain has `nv` fine units. Each Bernoulli
  coordinate contributes the factor `(num·a + (den − num))/den` (`bernFactor`, `bernoulli_avg_prod`). A uniform
  `k₂`-subset misses one gate with `a = (nv − k₂)/nv` (`choose_ratio`, from `Nat.choose_mul_succ_eq`). That factor is
  exactly the Bernoulli(`num·k₂/(den·nv)`) factor at `a = 0` (`bernFactor_thin`).

### 5 The Flock instantiation

**Oracle layer, proved** (`Audit/Flock.lean`). `table_sound` is proved by bounding `value`, so the optimal prover's
form `table_value_sound` comes out of it by a one-line split. `value_interleave_le` then projects a batched session onto
any one table (`value_batch_le`): the other tables' coins are part of the prover's strategy, and their values are at most
1. A drawn wrong unit's table has no committed satisfying witness by the lowering hypothesis (`LoweringSound`), so the
session is `SessionSound` at `2^-195.4` (`flock_session_sound`). The plan's strategy-level projection turned out
unnecessary: the audit's hypothesis is per strategy, and `prob ≤ value` closes the gap.

- **The plan** (`plan S tr : List FlockTable`) is the verifier's own derivation of the session's tables from the draw and
  the transcript. Packing several units into one table is allowed: the lowering names, for each drawn wrong unit, some
  table of the plan that no committed table satisfies.
- **The lowering hypothesis** is level 3's lowering theorem, stated for the audit: at the oracle layer a unit's statement
  carries its committed inputs and outputs, and it is satisfiable only if the unit's gates map one to the other.

**Compiled layer.** §12.6 discharges `KnowledgeSound`. `LinkSound` is the link theorem (the knowledge-soundness review,
§4d), and `AnchorsSound` is `registered_weights`.

### 6 The compiled layer: `ε_ks` from `table_knowledge_sound_joint`

- **Why the one-stage analysis is restated.** Two things differ from `Analysis`:
  - The table's extractor is randomized: it succeeds or fails depending on its `K` reruns after the level-0 cap.
  - Its bound depends on the prover, through `epsCminus σ` and `adv₀ σ`.

  So `ExtractionAnalysis` carries failure probabilities, and `cover` asks that, for a drawn wrong unit, the extraction
  and link failure probabilities add up to at least 1. That holds outcome by outcome. The named bounds are functions of
  the prover's state. The proof of `extraction_audit_le` is `audit_le`'s, with
  `Pr[accept] ≤ Pr[accept]·(ksFail + linkFail)` at the first wrong drawn unit.
- **The product is the joint form.** Given the state, the session's fresh run and the extractor's reruns are
  independent. So `Pr[accept] · E_bs[1(fail bs)] = E_bs[Pr[accept ∧ fail bs]]` (`expect_ind_and_const`,
  `expectN_const_mul`), which is exactly `table_knowledge_sound_joint`'s left side (`FlockTableC.joint_le`). No Jensen
  step is needed: the audit keeps the bound per state and averages it over the draw.
- **The configuration.** One table per session, with the leaf layer registered: the demo's, audit-protocols §0.2.
  - The verifier derives the table's statement from the draw and the registration (`plan`), so no serving-tree term
    arises.
  - With several tables, the joint theorem is needed for one table inside a batched session strategy, where the other
    tables are part of the prover. That is flock-soundness's to state
    (`note:audit-lean/20260927T0735Z-handoff-from-audit-lean`, §4).
- **The link event is the weakest one** (`LinkEvent`): the extraction succeeds, but every close message packing a
  satisfying witness disagrees with the committed transcript on the unit's wires.
  - `cover` then needs only the lowering (`LoweringSoundC`) and `correct_congr`.
  - The link theorem needs only that some satisfying candidate agrees with `X`.
  - `X` and `decode` are parameters the link theorem supplies. If `X` depends on auxiliary randomness, the bound holds
    for each draw of it.
