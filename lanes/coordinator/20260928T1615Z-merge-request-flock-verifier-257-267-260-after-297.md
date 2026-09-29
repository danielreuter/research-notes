---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: merge-request · from: flock-verifier (bc-8e519ca0) · to: research coordinator (bc-8ece7cde) · cc:
red-team-flock-3 · created: 2026-09-28T16:15Z · repo: danielreuter/verity

# Merge request: #257, #267 and #260 in the train after #297, one `check` on the combined head

**16:50Z: #282 joins this train.**
- [#282](https://github.com/danielreuter/verity/pull/282), branch `cursor/flock-verifier-region-free-bits-7ab3`, head
  `f8405b4f`: `main` `432edb3b` merged cleanly into the head the red team granted, `db55d87c`, at 13:13Z
  (`private/red-team-reviews/m0-statement/pr282-pr268-refusals.md`). Its `check` `r20260928-125233-755d` passed at
  `db55d87c`.
- It builds, and the audit passes with 14 pins, `Flock.mkRegion_ok` among them. `test_lean_verifier.py`: 19 passed.
- **Order:** after #260. Refinement R9c ([#291](https://github.com/danielreuter/verity/pull/291)) stacks on it.
- **The combined head, #267, #260 and #282 on `main`:** it merges cleanly and builds. The audit passes with 15 pins,
  `checkInRange_ok` and `mkRegion_ok` both. The three test files give 34 passed, 1 skipped. #282 also merges cleanly with
  #297's head.
- **Push:** `f8405b4f` is on origin (17:00Z).

| PR | branch | head | what | review |
|---|---|---|---|---|
| [#257](https://github.com/danielreuter/verity/pull/257) | `cursor/flock-verifier-region-words-7ab3` | `83beb9b2` | the region-word check, verifier side | granted (08:50Z) |
| [#267](https://github.com/danielreuter/verity/pull/267) | `cursor/flock-verifier-stmt-in-range-7ab3` | `cb4b987e` | `Stmt.InRange` at parse time, on #257 | granted at `3023daaa` (pin `Flock.checkInRange_ok`) |
| [#260](https://github.com/danielreuter/verity/pull/260) | `cursor/flock-verifier-coin-tree-v2-7ab3` | `e50a2f46` | coin-tree v2, verifier side | granted (08:50Z) |

- **Order:** #257, then #267, then #260, after #297.
  - Their prerequisites are on `main` with train H: #252 for #257, and #258 for #260.
  - #267 contains #257. You can take #267's head alone for both, or drop #267 from this train.
- **What changed since the grants:** only a merge of `main` `432edb3b` (train H), clean on each. #267 also merges #257's
  new head. No commit of mine moved.
- **Nothing to re-record:**
  - The executable's Lean audit passes on each head with its pins unchanged: 13 on #257 and #260, 14 on #267.
  - #257's fixture (`art:3104c2f9`, the GEMM k1024 stage) doesn't move with H.
  - #260's test vectors are the spec's. They are the same key `53d43b82…` and root `468d899b…` that #258's Rust
    `v2_reproduces_the_specs_vectors` holds, now on `main`.
- **Checked here, per head:**
  - #257: `lake build`, the audit, and `test_lean_region_words.py` with `test_lean_verifier.py`: 18 passed, 1 skipped.
  - #267: 19 passed.
  - #260: `test_lean_coin_tree.py` with `test_lean_verifier.py`: 28 passed, 1 skipped.
- **Checked on the combined tree** (#267's head with #260 merged): it builds, the audit passes, and the three test files
  give 31 passed, 1 skipped.
  - Each head also merges cleanly with #297's head `81fd1414`.
  - As you asked, there's no separate recorded `check`. The train's `check` on the combined head is the one.
- **The earlier recorded checks** were on `3ba4d8b3`, before H: #257 `r20260928-095343-7005`, #260
  `r20260928-110003-76d1`, #267 `r20260928-135640-08ae`. All passed and are preserved. The heads have moved since, so
  they don't satisfy the gate.

**Not in this train:**
- [#282](https://github.com/danielreuter/verity/pull/282): the three statement-adjacent refusals. Its `check` passed and it
  awaits the red team.
- [#226](https://github.com/danielreuter/verity/pull/226): Rust `table/v2`, `a99f5dd3` with H merged. Its re-check is
  running. It can join any train once that passes.
