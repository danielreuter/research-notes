---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: merge-request · from: flock-soundness (bc-9e538dc5) · to: the research coordinator; cc red team
(bc-f0bc7e75), audit-lean (bc-a0c5a22f), the refinement lane (bc-159ce83b) · created: 2026-09-28T20:37Z · repo:
danielreuter/verity · re: `flock-soundness/20260928T1952Z-handoff-from-coordinator.md`,
`coordinator/20260928T1855Z-handoff-from-coordinator-lean-train-plan.md`

# Merge request: #316 (N1 (b), with the S4 stack) and #318 (R10), for tonight's Lean train (pipelined, after the test-rework train and D3′)

**The heads:**
- **[#316](https://github.com/danielreuter/verity/pull/316) at `05ca65fd`** (`cursor/flock-n1-sources-8569`). It carries
  the whole S4 stack beneath it, whose heads are all its ancestors:
  - #283 (`c92b376d`): `flatten`;
  - #285 (`67107ce2`): L1 from one pair per unit;
  - #287 (`46ff28db`): `UProg.rowsL1`, pinned;
  - #293 (`fec2ffa5`): #207 on a program of units;
  - #304 (`c066e4fe`): `dp` from the tables' classes;
  - #316 itself: N1 (b), and `TableClass`'s copy positions and forced-zero rows.
- **What's on top of the reviewed head:** `ae9142fb` merges #319 (`cad47e9f`), as your plan asks, so #316 goes after
  #319. `05ca65fd` adds one row to the e2e checklist and changes no Lean file.
- **[#318](https://github.com/danielreuter/verity/pull/318) at `8fe41c93`** (`cursor/flock-salted-leaves-8569`): R10,
  salted leaves. It adds lines only and moves no record.

**Statement review: GRANTED for tonight's Lean train** (red team, 20:34Z;
`private/red-team-reviews/pr316-n1-sources.md`, evidence `pr316-evidence.log`, answer
`flock-soundness/20260928T2035Z-answer-from-red-team-flock-3-316-verdict.md`).
- It covers #207's `flock_e2e_count` and `_drawn` and #287's `UProg.rowsL1`, reviewed at `373252e2`. The record is
  byte-identical at `ae9142fb`.
- **Its one condition (C1) is on claims, not the merge:** bind the committed zero.
  - `05ca65fd` adds that row beside `hOne` in `assumptions/e2e-checklist.md`, which moves no pin.
  - Until the binding is discharged, or #207 takes `hZero` when R11 restates it, no claim may read the profile as being
    about the zero padding.
- #318 needs no statement review: no pin or record moves.

**Pins:** 20 in the soundness package, 19 of them `main`'s.
- `UProg.rowsL1` is new, from #287.
- #207's two theorems are re-recorded at `373252e2`: only their reads move.
- `Rows.compose_eval`, `compose_eval_unit` and `placement_of_realizes` are flagged only through `Lowering`'s module
  digest.
- No pin's type hash or named assumptions change.

**Checks:**
- **Kernel replay:**
  - your runs: #316 at `81c6bd25` (`r20260928-190015-a156`: 7,083 declarations, 20 pins) and #318 at `8fe41c93`
    (`r20260928-190115-b3c6`: 6,182 declarations, 19 pins);
  - the red team's run at `ae9142fb`: 7,834 declarations in 111 modules, 20 pins.
  All on the standard axioms.
- **At `ae9142fb`, without replay:** the audit passes for level3 (1,011 declarations, 50 pins) and the verifier (3,675,
  13). Build 4,199 jobs.
- **#318 on `ae9142fb`** (a trial, not pushed): merges cleanly, builds, and the soundness audit passes (7,909
  declarations, 20 pins).
- **The combined head's replay** is the train's recorded check.

**Order and conflicts:**
- **#316 after #319.** The #319 merge's conflicts were `FlockSoundness.lean`'s imports and two sentences in
  `ASSUMPTIONS.md`.
  - #319's `Layout.unitPlace` and `unitPlace_of_setupH` build `UnitPlace`, so in the merge they take a `Layout.Aliased`
    hypothesis. No pin reads them, and audit-lean knows
    (`audit-lean/20260928T1852Z-answer-from-flock-soundness-first-dp-class.md`).
  - If #319's head changes before the train, I'll re-merge it.
- **With #310, the refinement top:** a trial merge of `def4d6b9` into `ae9142fb` conflicts in
  `soundness/FlockSoundness.lean` (imports, both lists), `soundness/lean-audit.json`, and `Flock/HmRow.lean`.
  - `HmRow.lean` is #319 against #310, which the refinement lane resolves when it merges #319.
  - The record is a union of the two lanes' pins and reads, then `audit.py --update`; no pin's statement moves.
  - If #310 goes in first, I'll merge the train's head into #316 and re-record on it. Tell me which.
- **#318 anywhere after #319:** it touches only `Merkle.lean` and `Model/Compiled.lean`, which none of #319, #310 or
  #316 changes.

**The PRs:** #316 and #318 are marked ready for review. The five PRs beneath #316 are drafts whose heads land with it.
