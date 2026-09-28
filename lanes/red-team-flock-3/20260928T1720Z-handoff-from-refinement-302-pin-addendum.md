---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: red-team-flock-3 · kind: handoff · from: refinement lane (bc-159ce83b) · to: red team (bc-f0bc7e75) · created:
2026-09-28T17:20Z · repo: danielreuter/verity · about: #302 at `ec807b18`, one more pin

# #302: one more pin, `live_le_tableC`

**What's new.** #302 now also pins `FlockSoundness.Refine.live_le_tableC`, the transfer for `tableC` itself. Its one
hypothesis is `Decodes`.

~~~text
live_le_tableC … (hdec : Decodes (tableOut H E) pL (·.accepted = true) opn dec one fin capOf
    (fun pts r => Model.repC A r.val S sch hm (Model.extraClaims S ptLocal mPts pts))) (Pr : Strategy (liveTable dg mPts N)) :
  prob pL (liveTable dg mPts N) Pr ≤
    prob (·.accepted = true) (Model.tableC A H E S sch hm ptLocal mPts) ((simTable … hdec).strategy Pr)
~~~

**Its proof** is `live_le` at `tableOut H E`, which is `tableC`'s verdict written as `modelTable`'s output. `live_le`'s
`AllInh` hypothesis is discharged by `allInh_repC`: every message a compiled rep receives has an inhabited type, from
`AllInh` of each game the reps are built from.

**What to check:** `tableOut H E cap pend o` is `tableC`'s own output:
- `pend.1.verdict o && pend.2.verdict o && decide (OpensOK H E cap 0 pend.1 o ∧ OpensOK H E cap 1 pend.2 o)`;
- then `cap`, `pend` and `o`.

**Audit:** PASS. 6494 declarations in 113 modules; standard axioms; 35 pinned theorems. `Refine/LiveCompiled.lean` has no
compile-time code (no `macro`): the `do`-walking tactic is written out at each use.
