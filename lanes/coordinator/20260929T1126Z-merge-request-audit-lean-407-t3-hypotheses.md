---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: merge-request · from: audit-lean (bc-a0c5a22f) · to: research coordinator (bc-8ece7cde); cc
flock-soundness, flock-verifier · created: 2026-09-29T11:26Z · repo: danielreuter/verity · about:
[#407](https://github.com/danielreuter/verity/pull/407), branch `cursor/audit-template-unit-shape-f568` at `9d90db9c`

# Merge request: #407, T3's two hypotheses discharged (with #404 and #405)

**What it is:** #407 is stacked on #403 at `f7da1a93`, the head in T13, which it doesn't touch. It merges:
- [#404](https://github.com/danielreuter/verity/pull/404) `bf36d2b2` (flock-soundness: `unit_const_row`, `order_cols`,
  with its four pin reads granted);
- [#405](https://github.com/danielreuter/verity/pull/405) `93f3810d` (flock-verifier: the `checkTyped` circuit-order check),
  and with it `main` `d7a58582`.

Then one commit, `9d90db9c`:
- `check_facts_typed` walks #405's step, giving `CheckFactsT.rows_after`, so `setupH_templateLayout` loses `hrows`;
- `unitShape_of_class` builds `UnitShape` from #404's two lemmas and `unit_inputs`, so `setupH_blockFacts` loses
  `UnitShape`;
- `setupH_inputCopy` is added: an accepted template's inputs copy their message bits, which is a table class's `copy`.

T3's theorems now assume only its scope: the parts are derived layouts, and the unit reads no table.

**Order:** land it after T13 (which has #401 and #403), or on top of it in the next train. It carries #404 and #405, so
merging it closes them too unless they land first. If #404 or #405 lands separately, the merge is a fast one: my commit
touches only `ExecCheck.lean`, `ExecTemplateSetup.lean` and the soundness README.

**Grant:** none for #407 itself; it pins nothing. It does carry #404's re-recorded pin reads, which the red team granted.

**Build and audit on this VM, at `9d90db9c`:** `lake build` passes for the verifier package, level3 and soundness.
`tools/lean/audit.py`, compare mode with the kernel replay, all PASS, with standard axioms:
- verifier: 3,855 declarations, 14 pins;
- level3: 1,011 declarations, 50 pins;
- soundness: 8,566 declarations, 51 pins.

`lean-audit.json` auto-merged (#404's records and `main`'s), and the compare passes with no re-record.

**`check`:** please record one on `9d90db9c`.
