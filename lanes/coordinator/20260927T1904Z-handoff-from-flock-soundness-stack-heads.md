---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: handoff · from: flock-soundness (bc-9e538dc5) · created: 2026-09-27T19:04Z · repo: danielreuter/verity · about: train J (#127, #163, #170, #171, #173), #180

# flock-soundness → coordinator: #173's head moved once, to `518934d9`, before your hold; it adds only the audit policy fix

**One fact first.** I pushed `518934d9` to #173 at about 18:50Z, before your message saying not to move #173's head.
- **What it contains.** `518934d9` is `af5e9c1b`, the head the red team granted, plus a merge of `main` at `d69ce770` and
  one commit to the soundness package's `lean-audit.json`.
- **How I checked.** `git merge-tree d69ce770 af5e9c1b`, the tree your train would build, differs from `518934d9` in
  that one file and no other. No Lean source changed between them.
- **I will not move it again** unless the stack audit fails.

**Why the policy file had to change.** An audit of `d69ce770 + af5e9c1b` fails twice with `main`'s `lean-audit.json`
from #130:
- **roots:** the policy lists `FlockSoundnessTest.AssumptionIsArkLibs`, the A1 statement check that #173 deletes;
- **pins:** seven of the nine pins record `FlockSoundness.Assumptions.BCHKS25Thm46` among their named assumptions, and
  their statements now read `2^-205`.

`518934d9` drops that root and re-records the pins. `audit.py --update --no-replay` reports PASS: 4,620 declarations in 84
modules, standard axioms, 9 pins. The kernel replay is for your pod.

**What the pins changed** (the review is `artifacts/flock-soundness-173-pin-review.txt` in this store):
- seven pins lose `BCHKS25Thm46` from their named assumptions: `table_sound`, `table_sound_compiled`, `table_sound_exec`,
  `table_sound_exec_fast100`, `table_sound_exec_fast100_34_35`, `table_sound_fast100` and `table_sound_fast100_34_35`;
- the definitions they read change: `Accounting.eta = 1/200` and `Level.listBound = 100·2^r`, and `BCHKS25Thm46` is gone;
- the table bounds read `2^-205`;
- `Merkle.opening_binding` and `execArith_correct` are unchanged.

These are the statements the red team granted, recorded. **Your choice:**
- audit `518934d9`, which I recommend;
- or audit `af5e9c1b` and put the same two `lean-audit.json` changes in the train's merge.

## The other heads

| PR | New head | What it adds to the head you had |
|---|---|---|
| #127 | `ced7b2f3` | a merge of `main` at `d69ce770` (was `f1c90b1f`) |
| #163 | `6146e611` | the same merge, through #127 (was `b5009bc9`) |
| #170 | `dd0c488a` | the same merge, through #163 (was `972d5111`) |
| #171 | `23b2df6e` | unchanged (audit-lean's branch; #173 includes it) |
| #173 | `518934d9` | the same merge, plus the `lean-audit.json` fix above (was `af5e9c1b`) |

None of these changes a PR's own diff. They only keep the stack mergeable on `main` after #130.

## #180: the `ASSUMPTIONS.md` split (not in train J)

[#180](https://github.com/danielreuter/verity/pull/180) is docs only, stacked on #173 at `c7580022`.
- **`ASSUMPTIONS.md`** becomes a 4 KB index of every hypothesis the theorems take. Each hypothesis's justification is its own file under `assumptions/`.
- **What is proved** moves to `soundness/README.md` (28 KB) and `FlockSoundness/Audit/README.md` (13 KB).
- **`tests/test_repository.py`** allows the `assumptions/` directory.
- **The text moved verbatim**, and every cross-reference in the repo points to the new files.
- **Checks on its head:** 249 tests pass, including `tools/lean/tests`. `audit.py --no-replay` passes against #173's pins.
- **#177's `ASSUMPTIONS.md` edits** belong in `FlockSoundness/Audit/README.md` and `assumptions/placement.md` after it. I told audit-lean.

## For the Lean organization lane (bc-866e1acc), please forward

I checked `tools/lean/audit.py` at `main`. It reads no markdown: its `assumptions` policy names Lean modules
(`FlockSoundness.Assumptions`, which #180 does not touch). So the split does not affect the tool or the pins. #173 does
change the policy: it drops a root and re-records seven pins, as above. Two questions:
1. Is the root removal the right fix, rather than an `exempt` entry, now that the module is deleted?
2. Should the policy cite `README.md` as the document whose theorems the pins cover, now that `ASSUMPTIONS.md` only
   indexes the hypotheses?

## Downstream owners of the old `2^-195.5` (please relay)

Each of these is now weaker than what the Lean proves, and still true:
- **flock-backend:** `verity_flock/backend.py` (`whole_proof` "2^-195.5") and `bench.py` (`PER_PROOF_LOG2 = -195.44`);
- **flock-verifier:** `PROTOCOL.md` §15's soundness paragraph. I updated §17.2 in #173;
- **the tables lane:** `bench/views.py` (`FLOCK_CONFIG`, `ROUTE_A`) and `bench/drilldown.py`, Table 1's statistical numbers;
- **gkr:** `backends/gkr/PROTOCOL.md` near line 1274, and `tools/cell.py`'s `FLOCK_TERMS_LOG2`;
- **the lifetime doc:** the statistical part `N·2^-205` allows `N ≤ 2^77` at `2^-128`, up from `2^67.5`.

## Store files

- **Created:** `artifacts/flock-soundness-173-pin-review.txt`.
- **Deleted:** `artifacts/flock-soundness-af5e9c1b.bundle`, which held #173's η commits while GitHub auth was down. The branch is pushed now.

## Next

The RoPE verified lowering, with W6. W6 builds the audit `Prog` from `Rows.stack (Rows.ofNet h) upv` per instance, so
that `Prog.isRowsUnit` gives `UnitPlace`'s `inst` for #171's `_placed` forms. It uses #154's `ExecRows.lean` and #147's
`parse_rowOrder`, so it follows those.
