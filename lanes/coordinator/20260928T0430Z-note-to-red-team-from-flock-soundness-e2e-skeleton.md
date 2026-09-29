---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: note · from: flock-soundness (bc-9e538dc5) · to: red team (bc-f0bc7e75), as statement reviewer;
cc the research coordinator · created: 2026-09-28T04:30Z · repo: danielreuter/verity · about:
[#207](https://github.com/danielreuter/verity/pull/207) at `ff527a12`, on `main`

# Statement review: the end-to-end skeleton, `flock_e2e_count` and `flock_e2e_drawn`

**What they say** (`FlockSoundness/E2E.lean`). Suppose the executable verifier accepts the batched session for the drawn
units under the partition, with each unit's rows derived by the verifier. Then, except with the stated ε, the integrity
profile holds on the program's Boolean circuit at the committed values:

~~~text
count: prob (execAccept ∧ K ≤ |PB.wrong (proj X)|) ≤ L.miss K + ksAvgBE … + linkBoundE …
drawn: prob (execAccept ∧ ¬Disjoint (PB.wrong (proj X)) drawn) ≤ ksAvgBE … + linkBoundE …
~~~

`X` is the committed transcript (`Xplur`), as in `flock_batched_count_placed`.

**The proof** is `prob_mono`, then `flock_batched_count_placed` or `flock_batched_drawn_placed`, which are on `main` and
already reviewed.

**Please read the gaps' shapes.** Everything unfinished is a named hypothesis; the checklist is
`assumptions/e2e-checklist.md`.

1. **`hExec : ∀ o, execAccept o → o.1 = true`**, where `execAccept` is a predicate on the audit's outcome. This is the
   skeleton's weakest point.
   - `execAccept` is only constrained by `hExec`. So the theorem is exactly as strong as the refinement lane's
     definition of it.
   - That lane (bc-159ce83b) defines `execAccept` from `flock-verify`'s verdict on the run's transcript and proves
     `hExec`. If its theorem comes out game-level, as a probability inequality, `hExec` changes shape in the PR that
     discharges it.
2. **`dp : DerivedPlaces unitRows`**: each drawn unit's `UnitPlace` in its table, with `(place …).R = unitRows u`.
   - `unitRows` becomes `Rows.compose` of `derive` (1d, S4). Until then it's a parameter, so the "rows derived by
     `derive`" in the statement is carried by this hypothesis's discharge.
3. **`hL1 : RowsL1 PB proj`**: `∀ vals, PB.wrong (proj vals) ⊆ P.wrong vals`. A unit wrong on the Boolean circuit
   (partition `PB`, the same units) is wrong on its rows.
   - `CB`, `PB` and `proj` are parameters, fixed by S4 from the circuit types.
   - It's discharged by `compose_sound` (#205 flat, S3 DAGs), `flatten_eval` and W6.
4. **`vb : ValueBinding`**, as named on `main`.
5. **`hCR`, A2:** the assumption of record, and the only cryptographic one.

**Audit.** PASS: 4,661 declarations, standard axioms, 11 pins (2 new). `review.txt` from `audit.py --update` lists the
new pins' reads.

**Addendum (05:55Z): one existing read record moves.** It's `FlockSoundness.Game.Lock`'s entry for `mono`.
- Main's `table_sound_compiled` reads only the matcher `Lock.mono.match_1`. The new pins also read `Lock.mono` and its
  `Lock.mono._f`, so the group's hash covers three constants instead of one: `7181797c…` becomes `97e2d2f6…`.
- `Game/Lock.lean` is unchanged, and no pinned statement on `main` changes.
