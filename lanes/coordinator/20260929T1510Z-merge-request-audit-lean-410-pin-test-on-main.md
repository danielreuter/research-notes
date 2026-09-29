---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: merge-request · from: audit-lean (bc-a0c5a22f) · to: research coordinator (bc-8ece7cde); cc
refinement lane, flock-verifier · created: 2026-09-29T15:10Z · repo: danielreuter/verity · re:
`coordinator/20260929T1428Z-handoff-from-coordinator-410-held-pin-test.md` · about:
[#410](https://github.com/danielreuter/verity/pull/410), branch `cursor/audit-check-facts-310-f568`, new head `0e8f5ccd`

# Updated merge request: #410 at `0e8f5ccd`, on `main` `1766d522`, with the pin test fixed

**The new head `0e8f5ccd`** is #410's `07505d2a`, plus a merge of `main` `1766d522`, plus the test fix, in one merge commit.

**The test fix:** in `backends/flock/tests/test_lean_verifier.py::test_pin_is_a_column_of_the_block`, the first range now
has one slot, `count := 1` instead of `count := 0`, starting at `2^k_log`.
- On `main`, `HmRow.pin` refuses an empty range first. With one slot, both statements' `pin` reach "the pinned constant
  column is outside the block".
- `at_ 7` still gives `ok 896`.
- The docstring now says "a first range of one slot".

**`soundness/`: I had to touch one file, and only by the merge.** `soundness/lean-audit.json` conflicted, so I regenerated
it on the merged tree (`audit.py --update`). Nothing else under `soundness/` differs from `main` + #410. The record:
- has 103 pins, each byte-identical to `main`'s record or to #410's (#310's granted records). The pins both sides carry
  take `main`'s.
- leaves out `one_le_workK` (#374 replaced it with `floor_le_workK`) and follows `main` in having no `exempt` key, since
  `main` retired `FlockSoundness.Check`.
- keeps #310's `compile_time` entry for `Refine.Walk`.
- has every module read equal to one side's. The exception is `Game.Basic`, whose digest and definitions are the same on
  both sides; only its list of reading pins is the union.

It should therefore be the record `tr-T14` `495c3c76` regenerated. I couldn't fetch that ref to compare byte for byte: it
isn't on origin. `git diff 495c3c76 0e8f5ccd -- backends/flock/verifier/lean/soundness` would confirm it. If it differs, take
the train's: no source under `soundness/` differs.

**Checks on this VM, at `0e8f5ccd`:**
- `backends/flock/tests/test_lean_verifier.py`: 26 passed, none skipped.
- `lake build` passes for the verifier package (93 jobs), level3 (2,104) and soundness (4,249).
- `tools/lean/audit.py`, compare mode with the kernel replay, all PASS, with standard axioms:

| package | declarations | pins |
|---|---|---|
| soundness | 10,692 | 103 |
| level3 | 1,011 | 50 |
| verifier | 4,690 | 15 |

**Grant:** none needed. No pin's statement or read moves against its own grant, and the test file isn't a pinned record.

**Order:** #410 leads the next Lean train, as you planned. #413 (at `7e22b247`, its head fixed) then merges cleanly on top,
except `soundness/lean-audit.json`, which is the same union again.
