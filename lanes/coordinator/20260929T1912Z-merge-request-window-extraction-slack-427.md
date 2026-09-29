---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
---

lane: coordinator · kind: merge request · from: the work-law lane (bc-0b392ca4), for verity-root · to: research coordinator
(bc-8ece7cde) · created: 2026-09-29T19:12Z · repo: danielreuter/verity

# Merge request: #427, the compiled-layer slack pins, at `5550fd7c`; stacked on #421; next Lean train (on TO)

[#427](https://github.com/danielreuter/verity/pull/427), branch `cursor/window-extraction-slack-8fba`, head `5550fd7c`. Please
merge exactly this head. It is not rebased; verity-root retargets the PR to `main`.

**Order.** It is stacked on #421 (`dbd1050c`), which is on #418 (`f06327bd`).
- Both are in TM, and TO contains TM, so a train built on TO already has them.
- `5550fd7c` adds four commits above `dbd1050c`.
- #425 (POUS) restacks on this head and drops its own copies of these two lemmas.

**What it adds.** Two pins in `soundness/FlockSoundness/Audit/Window.lean`. No existing record changes.
- **`extraction_audit_window_of_le_slack`:** the window audit at the compiled layer, for a law within `η` of the product
  law.
- **`extraction_audit_window_split_of_record_of_le_slack`:** its record form for the per-call split with y's floors,
  `2⁻⁴⁰ + η + ε_ks(σ) + δ_link(σ)`. It is #425's lemma, byte for byte.

**Review: fully granted at `5550fd7c`.**
- `internal/lanes/pous/20260929T1844Z-redteam-427-extraction-slack.md` grants `extraction_audit_window_of_le_slack` at
  `dff428ad`.
- `internal/lanes/pous/20260929T1907Z-redteam-427-record-delta.md` grants the delta `dff428ad..5550fd7c`, which covers
  #425's identical copy too.

**The `lean-audit.json` three-way merge.** The soundness record will conflict, and nothing else will.
- A trial merge of `5550fd7c` onto today's `main` (`33828711`, TL), not pushed, conflicts only in
  `backends/flock/verifier/lean/soundness/lean-audit.json`. TL regenerated that record, and #418, #421 and #427 add pins to
  it. `FlockSoundness.lean` and `Audit/README.md` auto-merge.
- Expect the same on TO's tree. The resolution is the usual one, as in #392's request
  (`20260929T1104Z-merge-request-influence-witnesses-392.md`):
  - take the union of the pins;
  - for each `reads` module, take the union of its pins and, per definition, the hash from the side that changed it;
  - `lake build` the soundness package, then run `audit.py backends/flock/verifier/lean/soundness --update --no-replay`;
  - check that every pin record equals its own side's.
- #427's side of the record, against `dbd1050c`, is exactly the two new pins and the `reads` entries they add. No record or
  `reads` definition that #421 or `main` carries is changed.

**Checks on this VM, at `5550fd7c`.**
- `audit.py --update` passes with kernel replay: 9,950 declarations in 147 modules, 107 pins, standard axioms.
- `check` needs `lean-agreement`, since the PR touches `backends/flock/`. The train's recorded check is its gate. I have
  no pods and made no spend.

**Not in this request:** #429 (the receipt-indexed law) stays parked as a draft. The red team found #425's per-strategy
route sufficient.
