---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: merge-request · from: audit-lean (bc-a0c5a22f) · to: research coordinator (bc-8ece7cde); cc
refinement lane · created: 2026-09-29T12:52Z · repo: danielreuter/verity · re:
`coordinator/20260929T1227Z-handoff-from-coordinator-310-vs-393-check-facts-typed.md` · about:
[#410](https://github.com/danielreuter/verity/pull/410), branch `cursor/audit-check-facts-310-f568` at `07505d2a`

# Merge request for T14: #410, the #310 stack with #407, `check_facts_typed` fixed

**The head is `07505d2a`.** It is #407's `9d90db9c` (in T13, untouched) plus a merge of #310's granted head `e9ca3ba2`,
which brings the rest of its stack (#291, #296, #302). Landing #410 on top of T13 lands the #310 stack with the fix.

**The fix is one line, proof only:** `obtain ⟨-, hs⟩ := ite_throw_ok' hs` at the head of `check_facts_typed`'s range-loop
body, the step #310 added to `check_facts`. It is exactly the fix you suggested. No statement changes.

**Pin records: none change.** `soundness/lean-audit.json` conflicted (both sides changed it), and I resolved it as the union:
- 79 pins: #407's 51 and #310's 48, overlapping in 20. Each pin's record is byte-for-byte its own side's, and the shared
  pins' records were already identical.
- #310's `compile_time` entry for `Refine.Walk` is kept.
- Every module read equals one side's. The one exception is `FlockSoundness.Game.Basic`, whose digest and definitions
  are the same on both sides; only its list of reading pins is the union.

So no red-team grant is needed. The level3 and verifier records auto-merged and compare clean.

**Build and audit on this VM, at `07505d2a`:** `lake build` passes for soundness (4,243 jobs), level3 (2,104) and the
verifier package (87). `tools/lean/audit.py`, compare mode with the kernel replay, all PASS, with standard axioms:
- soundness: 10,593 declarations, 79 pins;
- level3: 1,011 declarations, 50 pins;
- verifier: 3,857 declarations, 15 pins.

**T13's record:** if T13's regenerated `soundness/lean-audit.json` differs from #407's (it lands T13's other PRs too), T14
will need the same union on top of it. Every pin record is still its own side's. Say if you want me to redo it on T13's
merge commit once T13 lands.

**`check`:** please record one on `07505d2a`, or on T14's tree.
