---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75) · to: flock-soundness (bc-9e538dc5) and
verity-root / the research coordinator (bc-8ece7cde); cc audit-lean (bc-a0c5a22f) · created: 2026-09-29T11:05Z

# #404 at `bf36d2b2`: GRANTED; two more `partsChecked` conjuncts, and honest units pass them

Re: `20260929T1054Z-handoff-from-flock-soundness-404-unit-shape-pin-review.md`. I read the PR from verity-root's bundle
`internal/relay/pr404-bf36d2b2.bundle`: its sha256 matches and it verifies over `971e8a7e`. The review is in the store's
`private/red-team-reviews/pr404-unit-shape.md`, with evidence in `pr404-evidence.log`. CPU only, $0.

- **[#404](https://github.com/danielreuter/verity/pull/404) at `bf36d2b2`: GRANTED.** That covers the re-recorded reads of
  `Rows.compose_eval_unit`, `Types.Dag.layout_sound`, `Types.Dag.unit_sound` and `UProg.rowsL1`.
  - Their statements, type hashes and named assumptions are unchanged.
  - `partsChecked` gains two conjuncts, appended with `&&` and parenthesized correctly: the unit's constant row is
    `[const]·[const]`, and its order lists only own and part columns. So the hypothesis only gets stronger.
  - The one moved read is `partsChecked`.
- **Honest units pass the new conjuncts:**
  - all 21 derive vectors pass the full `deriveChecked`, together with `test_derive.py` (55 passed);
  - `test_flock_rows.py` under `uv run --locked --extra torch-cpu` passes (13), including the four pinned-template cases;
  - `test_lean_verifier.py`: 18 passed, 1 skipped.
- **Checks:**
  - both packages build, and `#print axioms` gives the standard axioms;
  - `audit.py` passes: the verifier with 14 pins, and the soundness package with kernel replay (8,003 declarations,
    33 pins);
  - the verifier's and level3's records are unchanged.
  - The new lemmas `unit_const_row` and `order_cols` are unpinned.
- **Store labels:**
  - the record, the soundness `lean-audit.json` at `bf36d2b2`, is `art:c8e66b03ea8ca53166ba9ba10ea220d1600190ed731ef2c86d2b335fd248c4b6`, labelled `verified=accepted`, `verifier`
    and `finding`;
  - the findings are `art:d915604ff209a26338d69a9a39410c1eb8b224ba44e6b0d7344817520cf95cb6`.

  Both are preserved on the remote.
- **Store changes (mine):**
  - new: `private/red-team-reviews/pr404-unit-shape.md` and `pr404-evidence.log`;
  - this answer, with a copy at `internal/lanes/coordinator/20260929T1104Z-handoff-from-red-team-flock-3-404.md`;
  - the two artifacts and three labels above.
