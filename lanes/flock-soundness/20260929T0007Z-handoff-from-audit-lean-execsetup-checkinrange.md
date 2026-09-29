---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: flock-soundness · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: flock-soundness (bc-9e538dc5); cc the research
coordinator · created: 2026-09-29T00:07Z · repo: danielreuter/verity · re:
`audit-lean/20260928T2240Z-handoff-from-coordinator-319.md` (D3′'s `ExecSetup` break)

# The `ExecSetup` break on D3′: #267 adds one step to `Stmt.setupH`, so `setupH_spec` needs one more bind

**The cause.** #267 (`cursor/flock-verifier-stmt-in-range-7ab3` at `cb4b987e`) adds a throwing step to `Stmt.setupH`, right
after #257's region-word check:

~~~lean
  let regions ← HmRow.regions c pub
  HmRow.checkRegionWords c da db regions
  checkInRange c.kLog regions.size (PT_LOCAL + nbl)        -- new in #267
  let mut h := tags.statement.toUTF8 ++ c.sha ++ (← canon tags.identity).toUTF8
~~~

`setupH_spec`'s walk steps over `setupH`'s binds one by one, then extracts `h0` (`let mut h`). With the extra bind, that
extraction fails. It is the "`extract_lets` failed: made no progress" at `ExecSetup.lean`'s `lets h0` line. #260 doesn't
touch `setupH`. The other steps (`k_log > 26 || m > 35`, the pin, Δ, the regions) are unchanged in #267.

**The fix** is one more bind step before `h0`, in `setupH_spec`, and nothing else. After the pin the walk reads:

~~~lean
  bindok pin hpin
  bindok _ -     -- HmRow.regions
  bindok _ -     -- HmRow.checkRegionWords (#257)
  bindok _ -     -- checkInRange (#267): add this line
  bindok _ -     -- canon tags.identity
  lets h0
~~~

That is the form on a head with #177's tactic macros. On #319's line, where #284 wrote the macros out, each `bindok _ -` is
`(have hh := except_bind_ok h; clear h; obtain ⟨_, -, h⟩ := hh)`, so there the fix adds a fourth such line after
`obtain ⟨pin, hpin, h⟩`. Without #257, which D3′ may not have, the region-word line isn't there either. Count the binds
between the pin and `let mut h`.

**Checked here:** #319 `cad47e9f` with #267 `cb4b987e` and #260 `e50a2f46` merged on a scratch tree, with that one line
added. The soundness package builds (4,195 jobs). Nothing was pushed, and I haven't touched `ExecSetup` on any branch.

**Next:** send me your fix's head. I'll rebase #319 on it, re-run the audit and hand the new head to the research
coordinator.
