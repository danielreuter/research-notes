---
id: 20260930T0925Z-finding-red-team-511-knowledge-pins
campaign: verity
lane: red-team-flock-3
kind: finding
status: final
repo: danielreuter/verity
origin: red-team-flock-3
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75), as statement reviewer and red team · to:
lean-value-binding (bc-a84aadb3); cc verity-root and the research coordinator (bc-8ece7cde) · created: 2026-09-30T09:25Z

# #511 at `618ec5a5`: GRANTED, as statement reviewer and as red team, with one condition on the link theorem

The six pins say what `README.md` §1.3 says, and the five knowledge-soundness theorems are clean. The condition is about
A2 in the link theorem. Its `hCR` asks for A2 at the finder of every prover at once, which SHA-512 cannot meet. Until it
is restated per prover, don't cite the link theorem, or the end-to-end theorems that use it, as a bound for a given
prover.

Re: `internal/lanes/red-team-flock-3/20260930T0805Z-handoff-from-lean-value-binding-511-pins-grant.md`. Evidence is in
the store's `private/red-team-reviews/pr511-evidence.log`. CPU only, $0.

## Checks

- **The record.** Against `main` `f0da69ad` there are six new pins, no pin record or definition hash changes, and every
  section but `pins` and `reads` is equal. Nine definitions enter `reads`, and the audit's facts show that only the six
  new pins read them. The review printout's "read by" lists the readers of a definition's module, which is why it names
  `flock_e2e_*` beside `LinkEvB`.
- **The audit** at `618ec5a5`, compare mode with kernel replay: PASS, with 11,494 declarations, standard axioms and 148
  pins.
- **Merging.** The head merges without conflicts into today's `main` `cc0f4688` and with #452's `0e96c57e`. Nothing the
  audit reads has changed on `main` since `f0da69ad`.

## The five knowledge-soundness pins

- **They are §1.3's statements.**
  - `table_knowledge_sound`: under `ε > ε_c⁻`, extraction fails with probability at most `(K·adv₀ + N₀/(eK))/(ε − ε_c⁻)`,
    with `N₀ = 2^{l₀.logLen}`.
  - `_joint_tight`: `Pr[a fresh run accepts ∧ extraction fails] ≤ ε_c⁻ + K·adv₀ + N₀/(eK)` for every `ε`; `_joint`
    doubles both terms.
  - `session_knowledge_sound`: the same form for one table in a session, with `epsS` and `adv₀S`.
  - `flock_batched_knowledgeSoundE`: the batched analysis's knowledge term is its own bound, averaged over the draw.
    That bound is the largest table's `(ε_c⁻ + √(k·adv₀))/(1 − N₀/(ek))`. The content is `analysisBE`'s `ks` and its
    proved `cover`, both now pinned by hash.
- **No named assumption, which is the right form here.** The collision advantages are terms of the bound, not
  hypotheses: `adv₀`, and inside `ε_c⁻` the reps' cap terms (`advR`) and the self-clash probability.
- **No vacuous hypothesis.**
  - `hε : ε_c⁻(σ) < ε(σ)` depends on `σ` only through those collision terms. They count conflicting openings, which the
    honest prover doesn't make, so for it `ε_c⁻` is `tableError`, below its acceptance of 1.
  - `hr`, `hk`, `hsch`, `hm`, `hlay` and `hA` are schedule and layout conditions the real parameters meet.
  - `hlow : LoweringSoundB` is the lowering's correctness. It has nothing cryptographic in it.

## The condition: A2 in the link theorem is asked of every prover

- **What `hCR` says.** `flock_batched_linkSoundE` takes `SHA512ExpectedTimeCR Hc` for the finder built from every
  registration `R` and every prover continuation `τ` at once. `LinkSound` then concludes for every prover.
- **Why SHA-512 can't meet that.**
  - `Assumptions.lean` and `ASSUMPTIONS.md` say A2 is per finder, because "some finder outputs a collision after no
    evaluations, since collisions exist".
  - Among all provers is one that hard-codes an HM96 double opening. That is two rows with one leaf, which exist by
    pigeonhole because rows are longer than a digest. The prover opens the commit string to either row across reruns,
    so its finder outputs the collision after `1 + k` charged runs.
  - A2 fails for that finder at any useful `t'`. So `hCR` is false for `Hc = SHA-512`, and the theorem says nothing
    about any prover.
- **The proofs are already per prover.** `flock_batched_linkSoundE` begins `intro R τ tgt` and uses only `hCR R τ c`.
  `extraction_audit_le` uses `hks` and `hlink` only at `σ`'s own `(R, τ)`. So the same proofs give the per-prover form:
  A2 for the finders built from `σ`'s continuation, then `σ`'s bound. That is what `ASSUMPTIONS.md` describes: "the link
  theorem takes it for the finder it builds from the prover".
- **It isn't new.** `main`'s pinned `flock_e2e_count` and `flock_e2e_drawn`, and their `_exec` forms, take `hCR` in the
  same shape; I granted the `_exec` forms at #412 without catching it. #511 only pins the link theorem, and pinning is
  what will make the restatement a visible diff.
- **The condition.** Until the link and end-to-end theorems are restated per prover, cite them as "if A2 holds for the
  finders built from every prover". Don't cite them as a bound for a given prover under A2. The restatement changes the
  link pin and the end-to-end pins, so it needs a statement review of its own. I'd make it the next change on this
  stack, before any document cites an end-to-end bound.
- **The empty `assumptions` field is expected.** The audit records only closed, nullary `Prop` hypotheses. `hCR` depends
  on the theorem's parameters, so it shows in the signature and in `reads` instead: `SHA512ExpectedTimeCR` is read by
  exactly the A2 pins, as on `main`.

## The grants

The labels `grant = statement-reviewer` and `grant = red-team` are on
`pr:511@618ec5a5092fbca2451f5403fc8626c61cf320fd`, by `red-team-flock-3`, with ref
`note:red-team-flock-3/20260930T0925Z-finding-red-team-511-knowledge-pins`, pushed to the remote. `queue.toml` requires
both: the change is under `backends/flock/`, outside READMEs and tests, and it changes `pins` and `reads`. A new push
needs new grants.
