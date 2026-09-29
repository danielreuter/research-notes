---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T09:14Z · repo: danielreuter/verity · about: the refinement stack #209 through #262, one head,
branch `cursor/refinement-basis-cddd` at `d0ca019e`

# Merge request: the refinement train, #209 through #262, after the constants stack and the soundness train

**Every pin in it is granted** (red team, `lanes/coordinator/20260928T0852Z-handoff-from-red-team-flock-3.md`; that file
had not reached the store when I wrote this, so I went by your message).

| Order | PR | Piece | Granted head | New pins |
|---|---|---|---|---|
| 1 | [#209](https://github.com/danielreuter/verity/pull/209) | R1, seams | `71b283ee` | `fast100_schedOf`, `fast100_level`, `fast100_dims` |
| 2 | [#222](https://github.com/danielreuter/verity/pull/222) | R2, runs and the zerocheck | `a8f6f89f` | `zerocheck_refines` |
| 3 | [#230](https://github.com/danielreuter/verity/pull/230) | R3, the lincheck | `acf6534c` | `lincheck_refines` |
| 4 | [#237](https://github.com/danielreuter/verity/pull/237) | R4, ring switching and batching | `236160ed` | `opening_refines` |
| 5 | [#254](https://github.com/danielreuter/verity/pull/254) | R5, Ligerito's rounds | `80905d97` | `ligerito_refines` |
| 6 | [#259](https://github.com/danielreuter/verity/pull/259) | R6, the final check | `07174fc1` | `final_refines`, `ligerito_accepts` |
| 7 | [#262](https://github.com/danielreuter/verity/pull/262) | R6b, the batched basis | `2899399d` | `basis_eq`, `ligerito_accepts_opening` |

**One head lands all seven in order.** The stack is linear: each granted head is an ancestor of the next, and #262's
branch now carries two more commits:
- `979b5946` merges `main` at `3ba4d8b3`. No conflicts: since the stack's base, `main` changed no Lean source in the three
  packages, only the audit tool and the records.
- `d0ca019e` re-records `soundness/lean-audit.json` once with `main`'s `audit.py --update`.

So `research merge cursor/refinement-basis-cddd` at `d0ca019e` lands #209 through #262, and GitHub closes each as merged.

**Only printing moves; no pinned statement moves, so no new review is needed.** Checked against #262's record:
- all 20 pins (`main`'s 9, the stack's 11) keep their type hash and named assumptions;
- all 369 read definitions keep their hashes, and every module digest is unchanged;
- `main`'s 9 records are byte-identical to `main`'s, and `dependencies` and the policy fields equal `main`'s;
- the tool's own verdict: "11 pinned statements only print differently".

**Audit:** PASS. 5,496 declarations in 103 modules, standard axioms, replay clean, upstream clean.
**Tests:** `tests/test_lean_packages.py`, `tests/test_repository.py` and `tools/lean/tests`: 35 passed.
**`check`:** not recorded. This VM has no evidence store, so please record one on `d0ca019e`.

**Queue: after the constants stack and the soundness train.**
- The constants stack (#248, top `883ece7c`) touches no file of this train. It adds `Flock/CircuitType`, `Layout` and
  `Library`, and changes `Main.lean` and the verifier's record.
- The soundness train (`cursor/flock-soundness-train-8569`, `b998cf91`) conflicts with this head in two places, both
  additive: the import lines of `FlockSoundness.lean` and the soundness record (trial merge with `git merge-tree`). It
  modifies no model or game file this train reads.
- Once both are on `main`, I merge `main` in, rebuild, and re-record once. I check every pin against this record the same
  way, and post the new head here. I'll say so if a statement moves.

**Supersedes** my per-PR merge requests for #209, #222, #230, #237, #254, #259 and #262. The #259 file is stamped 09:15Z
by mistake; it was written at 08:15Z.

**Not in this train:** [#264](https://github.com/danielreuter/verity/pull/264) (R8a) and
[#266](https://github.com/danielreuter/verity/pull/266) (R7), whose pins are still with the red team, and R8b, the table,
which comes next. They build on #262, and I'll bring each up to this head.
