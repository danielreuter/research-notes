---
id: 20260929T0612Z-handoff-from-pous-362-redteam
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: red team on #362 at `fb1ab521`: GO as the tile law; closure law and K still open

Our layout-A red team read `Audit/Work.lean`, the 13 pin records and the verifier guard. It couldn't build the soundness package, because ArkLib has to be built from source. Findings X-SPC-78 to X-SPC-81:

- **X-SPC-79 (info): C1 is met.** `Stmt.setupTables` (HmRow.lean:932–942) refuses a work draw unless `--partition`, `--program` and `--work-table` are all present. It requires `law == workLaw obj prog k table`, and every `verify` path goes through it. The inputs come from the verifier's own flags, or from a SHA-512 named with `--archive`. `test_verify_takes_a_work_draw_only_from_its_own_table` passes.
- **X-SPC-80 (medium, C1's class): K is still the draw's own.** The guard derives the law at the draw's k, and `verify` has no K flag. A draw at k = 1 passes U2 and draws about one unit per stratum, while `audit_work_of_record` needs K = 27,713. Fix: take K from the verifier itself, either a `--work K` on `verify` or the registration's value, and refuse a draw at any other K. The stratified law needs the same fix. This is moot only if the verifier of record is the only thing that ever writes `unit_draw`.
- **X-SPC-78 (medium): the closure seam doesn't yet meet §12's condition.** `escape_widen_le` (Work.lean:260, 266) is true, and it's the right hook for #372's `widen`. But it bounds B by the base law's own escape, which is 1 for a node unit that's never drawn and 1 for any zero-work B. So a wrong node is never charged to the tiles beneath it. Suggested pins, with cl as the verifier's own closure map, built from its Program:
  - `Law.closure L cl := L.widen (fun S => S ∪ S.biUnion cl)`;
  - `closure_escape : (L.closure cl).escape B = L.escape (B ∪ unsoundTiles cl B)`, where `unsoundTiles cl B = {t | ¬ Disjoint (cl t) B}`;
  - `audit_work_closure : Pr[accept ∧ T ≤ workOf (unsoundTiles cl wrong)] ≤ ((W − T)/W)^K + ε_ks + δ_link`, with `harm_le_unsoundWork` charging each wrong node the work of its unsound tiles.
  - This is the content of Phase 19e's `closureLaw_escape` and `audit_closure` in our accountable-compute submission. The executable also needs to accept a widened draw, because U3 counts only drawn units. #372 says the same under "Not yet".
- **X-SPC-81 (low): what the f_s follow-up must contain.** The head's `max 1` meets X-SPC-35's minimum. The follow-up needs:
  1. k_s = min(n_s, max(f_s, ⌈K·w_s·n_s/W⌉)), with f_s ≥ 1 on every non-empty stratum; U2 refuses f_s = 0.
  2. f_s taken from the verifier's own table, next to w_s, and re-derived by U2, never taken from the draw.
  3. Floors set per stratum by what y needs: dequantization and quantizer strata get their own, f_s ≈ ln(1/δ)/ε_s.
  4. Pins: `floor_le_workK : min n_s f_s ≤ k_s` (replacing `one_le_workK`); `workK_ge` unchanged; `sum_workK_le : Σ k_s ≤ K + Σ f_s`; and a per-stratum floor escape ((n_s − b_s)/n_s)^(f_s), with its audit.

**Net:** #362 is GO as the tile-draw law. Closure draws, and #372 of record, wait on `closure_escape` / `audit_work_closure` and U3 accepting widened draws. X-SPC-80's K fix belongs in #362 or a follow-up; your call.
