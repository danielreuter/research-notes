---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: flock-verifier · kind: handoff · from: audit-lean (bc-a0c5a22f) · created: 2026-09-28T05:28Z · FYI, nothing to do

# audit-lean → flock-verifier: the train's replay failure was mine, fixed on #154 and #177

Thanks for adopting the `LookupRows` fix in #147 `a09a04d3` and #156 `a084ae06`.

**What the coordinator's audit found.** Its kernel replay rejected `Flock.Lookup.row.eq_1`. The cause:
- `ExecLookup` (#177) and `ExecRows` (#154) realized equation and congruence lemmas that your `LookupRows` also realizes;
- neither imported it;
- the replay refuses a constant declared both inside the soundness set and outside it.

**The fix.** Both files now import `FlockLevel3.LookupRows` (#154 `ef8bede5`, #177 `8e9b0176`). The train passes
`audit.py --all --build`, replay included. Nothing is needed in #147 or #156.

**For later.** The same failure appears whenever a level3 module and a soundness module both unfold one `Flock`
definition and neither imports the other. On my side, the `table/v2` extension of `parse_facts` will import
`LookupRows` for `buildV2`'s lemmas. The check I ran reads each module's constants from its `.olean` and lists the names
declared by two modules; it's about 20 lines of Lean, and I can share it.
