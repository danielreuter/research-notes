---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T10:20Z · repo: danielreuter/verity · about: #264, #266 and #270, one head, branch
`cursor/refinement-table-cddd` at `13fda652`

# Merge request: #264, #266 and #270 (refinement R8a, R7, R8b), after the refinement train

**Every pin in it is granted** (red team; #270's review is
`private/red-team-reviews/refinement/pr270-verify-refines.md`).

| Order | PR | Piece | Granted at | Head | New pins |
|---|---|---|---|---|---|
| 1 | [#264](https://github.com/danielreuter/verity/pull/264) | R8a, one rep | `f34c5b6d` | `f34c5b6d` | `rep_refines` |
| 2 | [#266](https://github.com/danielreuter/verity/pull/266) | R7, the SHA-512 Merkle paths | `d3e503d0` | `d3e503d0` | `merkleCheck_verifies`, `opensOK_of` |
| 3 | [#270](https://github.com/danielreuter/verity/pull/270) | R8b, the table | `4f7f822a` | `13fda652` | `verify_refines`, `verify_tableAfter` |

**The order is #264, #266, #270, which is the stack's.** #266's branch contains #264's head, so merging #266 lands #264 as
well. The grant's order, #266 before #264, can't be done as separate merges.

**One head lands all three.** Each head is an ancestor of the next, and `cursor/refinement-table-cddd` at `13fda652`
contains the train head `d0ca019e`. So after the train, `research merge cursor/refinement-table-cddd` lands #264, #266
and #270 in order. Merged instead of the train, it would land all ten PRs at once.

**`13fda652` changes only docstrings,** for the red team's note N1 on #270, which is not a condition:
`verify_tableAfter`'s docstring now says its message list is existential and rep 0 goes first. The audit passes in
compare mode against the record granted at `4f7f822a`, so no pin or read hash moved.

**Audit:** PASS at `13fda652`. 5,627 declarations in 106 modules, 25 pins, standard axioms, replay clean.
**Tests:** `tests/test_lean_packages.py`, `tests/test_repository.py` and `tools/lean/tests`: 35 passed.
**`check`:** not recorded. This VM has no evidence store, so please record one on `13fda652`.

**Queue:** after the refinement train, which is after the constants stack and the soundness train
(`20260928T0914Z-merge-request-refinement-train-209-262.md`). Once those are on `main`, I merge `main` into the train
head, then carry it up through #264, #266 and #270. I re-record each once, check each pin's hashes against its granted
record, and post the new heads here.

**Supersedes** my merge requests for #264 (`0835Z`), #266 (`0842Z`) and #270 (`0932Z`).
