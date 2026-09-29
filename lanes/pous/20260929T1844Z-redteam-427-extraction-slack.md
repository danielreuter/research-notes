---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75) · to: verity-root / the research coordinator
(bc-8ece7cde); cc the work-law lane (bc-0b392ca4) and POUS (Lean lane) · created: 2026-09-29T18:44Z

# #427 at `dff428ad`: `extraction_audit_window_of_le_slack` GRANTED

Re: `internal/lanes/red-team-flock-3/20260929T1818Z-handoff-from-work-law-427-extraction-slack-grant.md`. I fetched the
PR head directly; it sits two commits above #421's granted `dbd1050c`. Evidence is in the store's
`private/red-team-reviews/pr427-evidence.log`. CPU only, $0.

## Checks

- **Build:** the soundness package builds, with no warnings in `Audit/Window.lean`.
- **Axioms:** `#print axioms` over all 106 pins gives only the standard three.
- **Audit:** `audit.py` passes with kernel replay: 9,949 declarations in 147 modules, 106 pins.
- **One repo test fails at the branch head, only because of its base, as on #421.**
  - `tests/test_repository.py` refuses `lean-audit.json` at 267,236 bytes, over the 262,144-byte limit on #418's base.
  - Train TL's allowlist on `main` (512 KiB) fixes it at the rebase.
  - The other 14 repo tests pass.

## The statement combines two lemmas already granted, and nothing else

I word-diffed it against both.
- **Against #418's `extraction_audit_window`,** the only changes are:
  - adding `{L : Law n} {η}` and `hL : ∀ B, L.escape B ≤ (stratified σ k hk).escape B + η`;
  - `L.closure cl` in the stratified law's four places;
  - `η +` in the bound.
- **Against #421's `audit_window_of_le_slack`,** the only changes are `ExtractionAnalysis` for `Analysis`, and the
  per-state `εks` and `δlink` applied at `(reg σ') (cont σ')`.
- **The proof** is `extraction_audit_window`'s: `extraction_audit_le`, then the case split on the committed set. The bad
  case goes through #421's `closure_escape_le_window_slack` and the other through `prCoin_false`.

## Records

- All 105 of #421's pin records are byte-identical.
- The single removed line is a comma-only change. No definition was added or moved; nine modules' pin lists just gain
  the new pin.
- The new pin carries no named assumption.

## Notes

- **No record-sizing form at the compiled layer.** POUS's claim of record is compiled and at the record sizing, so the
  chain will want one to cite. It follows from this pin with `covers_window`, `covers_of_floor` and `pow_record_le`.
- **#429 has the same gap in its indexed forms.** Its record form, `audit_indexed_window_split_of_record_of_le_slack`,
  is oracle-layer only. So the compiled record form the chain cites is best added once, in its indexed form. My #429
  verdict says the same.
