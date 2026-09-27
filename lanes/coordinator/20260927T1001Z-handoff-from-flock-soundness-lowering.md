---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity

# flock-soundness → coordinator: option 1 is #144; one question on M1's level 0

- **[PR #144](https://github.com/danielreuter/verity/pull/144)** is a draft: branch `cursor/flock-lowering-8569` at
  `084f8478`, stacked on #141.
  - It defines the audit's circuit as the rows the verifier parses (`Op.row`, `Rows`, `IsRowsUnit`, `Prog.circuit`).
  - It proves the lowering for every template (`lowering_sound`, `UnitPlace.correct`).
  - It names L1 in ASSUMPTIONS.md §1.5: each template's rows compute its gates. The IR comparison tests are its
    evidence, and a verified lowering is the path to discharge it.
  - There is no `sorry`, and all 159 axiom checks are standard.
  - It adds one test, `test_pinned_rows_read_earlier_columns`.
  - It edits #122's `Audit/Circuit.lean`, adding the `row` constructor.
  - A local merge with #133 at `6d4e28c0` builds, with all 171 axiom checks standard. It conflicts only in two
    append-only lists.
- **Documents.**
  - New: `internal/lanes/audit-lean/20260927T0957Z-handoff-from-flock-soundness-rows-circuit.md`. It gives C's
    definition and a tested patch for #133, making the decoder per drawn unit.
  - Edited: `internal/lanes/flock-soundness/20260927T0925Z-draft-rope-lowering-scope.md`. It now says "rows" rather
    than "netlist", and records that option 1 was decided.
  - No directories were created or moved. My `internal/red-team-m1-zk/` handoff is already in `private/`, and nothing
    else of mine under `internal/` is sensitive.
- **Question.** flock-zk (09:45Z) says M1's level 0 has settled at #123 `8d621454`: `t_pad = 2 q_0`, with 277, 242 and
  229 queries at m = 25–27. Should I now state the padded level-0 `Level` (`RS[2L, L + 2 q_0]`) in the table theorem?
  Or wait for the red team's verdict on the fix?
