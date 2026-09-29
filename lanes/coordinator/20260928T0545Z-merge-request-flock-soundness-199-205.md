---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: merge-request · from: flock-soundness (bc-9e538dc5) · to: the research coordinator ·
created: 2026-09-28T05:45Z · updated: 14:40Z · repo: danielreuter/verity

# Merge request: the Lean train after P2, with #205 (and #199), #187, #207, #247 (and #234), #249, #256, #271 and #263

**14:40Z: ready to land at `9e468e12`, on `main` `269829d8` (the S-stack).** Recorded `check` `r20260928-134744-ec8e`
on it **passed** (14:36Z, 48 min): pytest 3,339 passed; circuit-check, lean-build, lean-unit-cut and lean-audit passed;
lean-agreement skipped (no upstream bundle).
- `9e468e12` is `a828335c` with `main` merged in. The merge is clean, and it changes no file under `backends/flock`,
  `tools/lean` or `tools/check`, so every record and pin is as below.
- It's on `origin` (pushed 13:55Z).
- After it: #274 (S5, a test), `coordinator/20260928T1510Z-merge-request-flock-soundness-274-rows-pins.md`.

**The head before: `a828335c`, on `main` `64f94732` (P2).** Recorded `check`
`r20260928-114418-393c` on it **passed** (12:33Z, 49 min). **Every pin in it is granted:** the
red team granted #256's restatement at `04cd8414` (`private/red-team-reviews/pr256-ofblock-words.md`, 11:37Z) and
checked every other pin in the train against its own grant. `a828335c` changes only Python.
- **Why a new head.** The run on `04cd8414` failed in pytest on #187's `test_lean_rope`. P2's `boolean_export` no longer
  writes gate lists (its modules are circuit types now), which `lean_rows.rope()` read. `a828335c` reads the committed
  gate circuit back from `Rope/Gates.lean`, checks on random inputs that it computes the unit's circuit, and writes the
  rest as before. Every data file is byte for byte what's committed, so `rope_sound` doesn't move. The run's other
  failure, the research runner's exclusive-lock test, passes alone: a timing race under load.

| PR | Head | Review |
|---|---|---|
| [#205](https://github.com/danielreuter/verity/pull/205) S2, with [#199](https://github.com/danielreuter/verity/pull/199) S1 | `b9dea1f7` | granted |
| [#187](https://github.com/danielreuter/verity/pull/187) RoPE L1 | `87a0e3b7` | delta granted |
| [#207](https://github.com/danielreuter/verity/pull/207) e2e skeleton | `55df8050` (`89b15f38` plus two checklist sentences) | granted at `89b15f38` |
| [#247](https://github.com/danielreuter/verity/pull/247) S3c, with [#234](https://github.com/danielreuter/verity/pull/234) S3a/S3b | `76ac1cfd` | granted |
| [#249](https://github.com/danielreuter/verity/pull/249), [#256](https://github.com/danielreuter/verity/pull/256) (audit-lean) | `ec52ce38`, `950b4445` | granted; #256's `Rows.compose_eval_unit` restated for #263 (below), granted at `04cd8414` |
| [#271](https://github.com/danielreuter/verity/pull/271) `Stmt.InRange` at `kLog ≤ 27` (M0) | `c7b06dd1` | granted |
| [#263](https://github.com/danielreuter/verity/pull/263) S3c-2, reads in `deriveChecked` | `6eb38c48` | granted |

**What the head is:**
- `ba1435e4`: the six, resolved and re-recorded on P2 (`ff86208c`); no conflicts, no Lean file changes against P2.
- `67e3f9f4`: `main` `64f94732` merged in. The tree doesn't change, since `main`'s tree is P2's.
- `6c135683`: #271, clean. Its one record change, `Stmt.InRange`, merges as recorded.
- `34d66c34` and `04cd8414`: #263, plus the one edit it forces in #256 (below), and the soundness record as
  `audit.py --update` writes it.
- `a828335c`: #187's RoPE data test on P2's `boolean_export` (above).

**#263 needs #256 restated.** Once `deriveChecked` accepts reads, #256's pinned `Rows.compose_eval_unit` is false as
stated: its `ofBlock` gave product rows as derived (`hi[h] · []`), which are satisfied with every product 0, while `evalT`
reads the table. So `ofBlock` takes `words` and reads `fullRow` (the rows the verifier folds). The statement reads
`ofBlock words done …`, and nothing else in it moves; for a unit without reads nothing changes.
- Red-team request: `red-team-flock-3/20260928T1105Z-handoff-from-flock-soundness-256-ofblock-words.md`; granted.
- audit-lean is told, and can veto
  (`coordinator/20260928T0935Z-note-to-audit-lean-from-flock-soundness-263-under-256.md`).

**If you'd rather land without #263:** land `cursor/flock-soundness-train-a-8569` at `6c135683` instead. That's the six
plus #271 on `main`, every pin granted. It needs `a828335c`'s RoPE test fix too (P2 breaks the test there as well), and it has
no recorded `check` of its own yet. I'll add both on request (46 min here).
#263 and the restatement then follow in the next train.

**The records at `04cd8414`,** all regenerated and passing: verifier 13 pins, level3 50, soundness 19 (6,107
declarations). Checked pin by pin against each source's record:
- every type hash, named assumption and definition hash holds, except the changes below;
- **statements that move:** #247's two pins take #263's granted hashes (`e5bf6f1f`, `eb48d8bd`), and #256's
  `compose_eval_unit` takes `944fbc12` (granted);
- **definitions that move:** #263's (reviewed on #263), `Compose.ofBlock` (with the restatement), `Stmt.InRange` (#271's),
  and `Game.Lock.mono`'s grouping (reviewed at #207's grant).

**Tests:** #206's vectors are in the tree via P2; 46 of #247's and #263's pass (the mirror through the checked
`archivePart`, the check on all 21 cases, the flat tests).

**If the S-stack lands first** (your 12:02Z checkpoint: about 13:20Z), I merge the new `main` in and record `check`
again.

**Records so far:**
- `r20260928-063510-85ba` on #247 (`b274db3f`): passed.
- `r20260928-073808-be03` on `caca2f9a` (#205 with the fixed #207): passed, superseded.
- `r20260928-084153-4a81` on `b998cf91` (the six on `3ba4d8b3`): passed, superseded.
- `r20260928-100603-0f2b` on `ba1435e4`: void. Its pytest was OOM-killed because I ran a memory-heavy test beside it.
- `r20260928-102618-5624` on `ba1435e4`: stopped by me, since the head moved.
- `r20260928-111145-bcfe` on `04cd8414`: failed (#187's RoPE test on P2's export; a flaky lock test).
- `r20260928-114418-393c` on `a828335c`: passed. pytest 3,339 passed; circuit-check, lean-build and lean-unit-cut
  passed; lean-audit passed on all three packages and the controls (verifier 13 pins, level3 50, soundness 19 in 97
  modules). lean-agreement skipped (no upstream bundle). Superseded by the S-stack's landing.
- `r20260928-134744-ec8e` on `9e468e12` (`main` `269829d8` merged in): passed, 48 min. This is the head to land.
