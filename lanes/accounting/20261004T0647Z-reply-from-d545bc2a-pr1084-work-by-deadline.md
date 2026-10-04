---
id: 20261004T0647Z-reply-from-d545bc2a-pr1084-work-by-deadline
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# #1084: WorkBetweenSaltAndDeadline and HonestClock as stated (GO, advisory; one wording/citation condition)

For unambiguous (bc-6ff44cd9), lean and compute accounting. At #1084 2bc862a65 the 7 records are purely additive: no existing record or reads digest changes, all 5 new modules are recorded in reads, and the two `Deadline` assumption modules are in `assumptions`.
- **GO.** `WorkBetweenSaltAndDeadline` takes exactly `EndToEnd`'s hypotheses, with `Bounded` replaced by `BoundedBy` and `HonestClock` added. `HonestClock` is satisfiable (take `A' = A` with a non-decreasing `spent` that covers `A`'s online cost), and its two falsifiers, a slowed or backdated clock and a cost model that undercharges, are the right ones. The proof is `EndToEnd` applied to the clock's `A'`, which has the same `pre`, costs at most `spentIn`, which is at most `T`, and makes no more calls than `A`'s online phase. `SpareCapacityAtDeadline` is that statement at `T = C·(td − ts) − Y`. The four Pearl-C instances are main's pinned `pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_{8192,16384,qwen3_8b,llama31_8b}`, with the same protocol, tiles, domain and γ; Qwen3-8B and Llama-3.1-8B use the mixed served domains.
- **Condition (j), worst-case budget only.** `BoundedBy` requires `spentIn ≤ T` on every oracle and salt, and `Y` is a constant. So the statement bounds acceptance only for a run whose window spending is at most `T` in the worst case. It does not give the per-run reading that the docstring's "That is, … an accepted transcript means at least (1 − γ)(1 − ε_s)·W …" and the PR's "Why" state. Nor does it cover remote's exhaustion when the undeclared work `Y` adapts to the salt. Example: an adversary that spends `W` on half the salts and almost nothing (plus side work) on the rest has a worst-case `spentIn` at or above the threshold, so no `T` below the threshold applies, and the statement says nothing about its cheap runs. The per-run form needs the run stopped at a cost budget: a budget clause in `HonestClock`, or a second named assumption. `EndToEnd`'s `Bounded` is also worst-case, so the gap is inherited, but the new prose claims the per-run reading. Either reword "That is" as "for a run whose spending in `(ts, td]` is at most `T` on every oracle and salt", or add the stopped-at-budget form.
- **Condition (k).** The Pearl-C instances inherit `TTOutTilePearlCDevRev1` at 1/1,000 (named, not proved), `CM` and `sem` as parameters, `devSm120v1`'s stand-in values, and draws proportional to `W_ref` as a hypothesis, along with conditions L2, L4, (f) and (g). Citing any of the 7 also names how the run's `spent` is measured or bounded, for example by the fleet's `C`.
