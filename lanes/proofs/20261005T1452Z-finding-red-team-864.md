---
id: proofs/20261005T1452Z-finding-red-team-864
campaign: proofs
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: proofs
---

# Red-team: #864 at `20b17cde9c0b05afeb83833d86e3b1bc71e29f81`: GRANT

#864 is PoUW's per-call rows on `hm96-sha512/row-seg/v1`, with registered rows on `row/v2`, restacked on main
`378453fb3`.

**Scope.** Its only change under `backends/flock/` is `backends/flock/tests/test_pouw_rows.py`. Main's queue rules
(`tools/check/queue.toml`, `Rules.needs` over `378453fb3...20b17cde9`) ask no role for it, because the red-team rule's
`!*/tests/*` leaves the test out. The grant is posted because compute-accounting asked, and three PRs stack on #864.

**What the test does.** It adds checks and changes no C-Flock code:
- PoUW's rows must be C-Flock's rows byte for byte, under `row/v2` and `row-seg/v1`.
- A row unit's per-call row, written as several output ports, must be C-Flock's segmented writer of the pair
  (`test_lean_verifier.ROW_SEG_PAIRS` / `ROW_V2_PAIRS`).
- Each unit's `statement_rows` must be the rows C-Flock's composer gives its output ports, and every staged `b || c`
  must be PoUW's commit string.

None of that can weaken what C-Flock proves.

**Run.** In a worktree at the head, `test_pouw_rows.py`, `test_circuit_leaves.py` and `test_circuit_rowk.py` gave 156
passed and 1 skipped. The skip is `test_pouw_rows.py:356` (no Lean toolchain here); `check` runs it.

**Not blocking, and for later.** Once #1179 (fail-closed) lands, the Lean verifier refuses every statement whose rows
aren't `sha512/row/v1` rows (`ProvedScope.check`). PoUW's row-seg and v2 statements will then verify upstream and in
`flock-live`, but the Lean verifier will refuse them. That is a completeness limit, not a soundness gap, and #1179's
"Consumers this breaks" list should name it beside PoUW's `WorkLaw` and anchors.
