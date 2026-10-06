---
id: 20261006T0700Z-finding-two-stage-law-core
campaign: proof-service
lane: two-stage
kind: finding
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---

# The two-stage law in core, and what the Lean covers of its profile

P8 of `note:verity-root/20261006T0550Z-report-proof-service-implementation`, steps 1 and 3. Step 2 (the driver) is not
started; it waits on the questions under "The driver" below.

## Step 1: the law is in core (branch `cursor/two-stage-law-95d4`)

`verity.protocols.verification.sampled_proofs.two_stage` replaces `verity_experimental.sampled_proofs.law`. Each
replay-unit class has a `Stage(first, k)`. `first` is a probability p (decision 43's form) or a one-stage law object
(`subset`, `bernoulli`, `stratified`, or `work` with the verifier's closure).

- `draw_first` draws a one-stage law over replay units from the same bytes as Lean's `Flock.Draw.drawWith`. The test
  compares it with a transcription of `drawOn`, and `check_draw` accepts the draw.
- A subset, stratified or work first stage must have `k = None`, so it checks every proof unit of a drawn replay unit.
  Thinning such a draw with a second draw gives `E[(1 − k/n_v)^X]`, and no profile law states that escape.
- With `k = None`, the profile is the one-stage law's over the replay units (`Subset(k)`, or `audit.core_law`), which is
  `one_stage.audit.profile`'s object. It counts drawn replay units only, so the closure can only help.
- The derived-key draws are gone, so every coin is the verifier's own. vLLM's replay challenge now does its own
  derivation, and its picks are byte-identical (digest checked before and after).

Six negative controls on `two_stage.py` each fail at least one of the 21 new tests. The suites that ran pass. The PR body
is in the proofs store (`internal/proofs/two-stage-pr.md`).

## Step 3: does the Lean cover `TwoStageLaw.profile`?

The Lean results in play are `twoStage_count`, its general form `twoStage_profile` (`Audit/TwoStage.lean`), and the
examples in `Audit/Examples.lean`.

`twoStage_count` holds for any first-stage law L₁ and any second-stage laws L₂. Under the named hypotheses
`KnowledgeSound εks` and `LinkSound δlink`, it bounds acceptance with at least K wrong replay units by
`sup_{|B| ≥ K} effEscape(B) + εks + δlink`. The profile's δ is only the sampling term. The ε terms enter with the
soundness composition, as the proof service's `Terms` says.

What holds:
- **A first stage that checks every proof unit.** This is any one-stage law with `k = None`, and PoUW's case.
  `effEscape_full` says that `effEscape(B) = L₁.escape(B)` for any L₁, and `twoStage_full_profile` is the resulting
  profile. Python's profile here (one-stage's law over replay units) is exactly the one-stage law's escape at the
  replay-unit population. The one-stage Lean results for that law (`subset_miss`, `stratified_miss_eq_greedy`, and the
  executable draw's escape) apply at that population. The executable draw is the same one because `draw_first`
  byte-matches `drawWith`.
- **A work first stage with a closure.** `Law.closure L cl` is a Law, and `closure_escape` bounds its escape by L's.
  Python counts drawn replay units only, which is the side `closure_escape` covers.
- **The Bernoulli form, at one rate, with replay units of equal size n_v and a uniform k-subset second stage.**
  `effEscape_bernoulli` gives an escape equal to `Bernoulli(p·k/n_v).escape(B)`, which is Python's rate. Then
  `two_stage_b_tight` shows that `twoStage_count`'s bound is attained for every L₁. In that case Python's profile is
  exact.
- **`k = None` under a Bernoulli first stage.** Python's rate is p, and `effEscape_full` makes that exact.

What's missing for "exactly":
1. **The largest-replay-unit rule for mixed sizes isn't stated.** Python uses the class's largest replay unit's rate,
   `p·min(k, n_v)/n_v`.
   - Soundness needs `min(k, n)/n` to be nonincreasing in n, and `Law.bernFactor` to be monotone in its miss argument.
     Together they give `∏_{u∈B} bernFactor(miss_u) ≤ Bernoulli(p·min(k,n_v)/n_v).escape(B)`.
   - Neither lemma exists. `effEscape_bernoulli_prod` gives the product form for one rate over all coarse units, with
     any L₂.
   - The miss of a uniform k-subset (`subset_miss_one`, `effEscape_chains`) is stated only for the examples' equal-size
     `L₂ K nv hk`. `Law.choose_ratio` is general, so restating it per replay unit is short.
   - For mixed sizes, Python's rate is an upper bound and is not tight, since the smaller replay units escape less.
2. **Different rates per class.** Python's first stage is a product of per-class Bernoulli laws. Lean's
   `Law.bernoulli nc num den` has one rate.
   - The per-class profile needs `twoStage_profile` with `𝓑 = (K ≤ |B ∩ class|)`, plus two lemmas that don't exist:
     `effEscape` is antitone in B (each factor is ≤ 1), and for `B ⊆ class` it depends only on that class's rate.
3. **No Lean statement names Python's profile object.** No theorem says "the profile `TwoStageLaw.profile(cls, …)`
   returns bounds the two-stage game". The pieces above give it for `k = None` and for equal sizes at one rate.

Items 1 and 2 are short lemmas on top of `effEscape_bernoulli_prod` and `Law.bernoulli_avg_prod`. PoUW's driver needs
neither, because stage 2 is "all" (`effEscape_full`), and no second draw means `late_interior_insecure` can't arise.

## The driver (step 2): what it needs from `service.py`

This is from reading `cursor/proof-service-95d4` at `d5efa0005`. I haven't edited it.

- **Accepting `TwoStage`.** `Stream.__init__` refuses `TwoStage`. The driver also needs a second registration for the
  interiors, against the first's open draw, but `register` refuses while the earlier registration has no outcome
  (`open`). The service could add an interior registration (or a two-stage entry holding both records and receipts),
  and an outcome whose audit record binds both registrations, both receipts and the draw.
- **The closure.** `Law` holds only `text`. The interface note's `Law(text, work=None, closure=None)` would let `select`
  add the verifier's `closure` to a work draw, as `draw_first(..., closure)` and `flock-verify draw --closure` do.
  `select` builds `{**law, population, units}` with no closure today.
- **The sampler's bytes.** `Stream._sample` derives a Key from 32 fresh bytes (`verity/proof-service/draw/v1`), so its
  draw is not Lean's `drawWith` on raw bytes. Passing `sampler=` lets the driver use `two_stage.draw_first`, but
  `Sampler(law, n)` returns units only, so the closure has nowhere to go.
- **The profile.** `_finish` uses `one_stage.audit.profile`. For a stage-2 "all" rule that is the right law over replay
  units. For a Bernoulli first stage with k, it would need `TwoStageLaw.profile`.
