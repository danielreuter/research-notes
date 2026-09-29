---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: note · from: flock-soundness (bc-9e538dc5) · created: 2026-09-28T05:15Z · updated: 09:05Z Sep 29 ·
repo: danielreuter/verity · about: where phase 1 and the end-to-end skeleton stand, for the morning

# flock-soundness: overnight state (phase 1 and the end-to-end skeleton)

**The train has landed on `main`** (`ac412eb8` includes it). It was `cursor/flock-soundness-train-8569` at `9e468e12` on `main` `269829d8` (the S-stack): #205 (with
#199), #187, #207, #247 (with #234), audit-lean's #249 and #256, #271 and #263. Every pin is granted, #256's restated
`Rows.compose_eval_unit` included (red team, 11:37Z). Recorded `check` `r20260928-114418-393c` passed on `a828335c`
(12:33Z). The S-stack landed at 13:27Z, and `check` `r20260928-134744-ec8e` on `9e468e12` passed at 14:36Z. Merge request:
`coordinator/20260928T0545Z-merge-request-flock-soundness-199-205.md`.

| PR | Head | What | Base | State |
|---|---|---|---|---|
| [#199](https://github.com/danielreuter/verity/pull/199) | `76d74fd8` | S1: `Flock.Derive.derive`, `flock-rows`, the logical order | #194 | In the train. No pins |
| [#205](https://github.com/danielreuter/verity/pull/205) | `b9dea1f7` | S2: `compose_sound`, `compose_complete` (pinned) | #199 | In the train. Granted |
| [#187](https://github.com/danielreuter/verity/pull/187) | `87a0e3b7` | L1 for RoPE on `main`'s pin `9cbdef19…` (the regression test) | `main` | In the train. Delta granted |
| [#207](https://github.com/danielreuter/verity/pull/207) | `55df8050` | the end-to-end skeleton, `flock_e2e_count` / `_drawn` (pinned), with `RowsL1` at the constant 1 and `hOne` | `main` | In the train. Granted at `89b15f38` |
| [#234](https://github.com/danielreuter/verity/pull/234) | `88735dd0` | S3a/S3b: `deriveAll`, every layout derived (calls, exports, reads) | #205 | In the train, with #247 |
| [#247](https://github.com/danielreuter/verity/pull/247) | `76ac1cfd` | S3c: `deriveChecked` and L1 over the type DAG, `Types.Dag.unit_sound` / `layout_sound` (pinned); the logical order; the Δ-copy lemma | #234 | In the train. Granted |
| [#263](https://github.com/danielreuter/verity/pull/263) | `6eb38c48` | S3c-2: reads in `deriveChecked`, inline and placed; the two S3c pins restated over the rows the verifier folds; `evalT_flat` | #247 | Granted. In the train, with #256 restated (granted) |
| [#271](https://github.com/danielreuter/verity/pull/271) | `c7b06dd1` | `Stmt.InRange` at `kLog ≤ 27`, for M0 | `main` | Granted. In the train |
| [#274](https://github.com/danielreuter/verity/pull/274) | `98494662` | S5: `flock-rows` holds every pinned template unit | the train | Ready; lands after the train (`coordinator/20260928T1510Z-merge-request-flock-soundness-274-rows-pins.md`). Peak 8.6 GiB |
| [#283](https://github.com/danielreuter/verity/pull/283) | `c92b376d` | S4a: `flatten`, `flatten_eval`, `flatCircuit` (an `Audit.Circuit`) | the train | Draft. Unpinned |
| [#285](https://github.com/danielreuter/verity/pull/285) | `67107ce2` | S4b: `RowsL1` from one pair per unit (`rowsL1_of_pairs`), each unit's rows on `C` and unit gates on `CB` | #283 | Draft. Unpinned |
| [#287](https://github.com/danielreuter/verity/pull/287) | `46ff28db` | S4c: `hL1` for every program of units (`UProg.rowsL1`): its rows circuit, its Boolean circuit, one pair per unit | #285 | Draft. `UProg.rowsL1` pinned and **granted** (15:51Z; the grant covers `46ff28db`) |
| [#293](https://github.com/danielreuter/verity/pull/293) | `fec2ffa5` | S4d, first part: #207's theorems on a program of units, `hL1` discharged, `hOne` the constant's gate | #287 | Draft. Unpinned |
| [#304](https://github.com/danielreuter/verity/pull/304) | `c066e4fe` | S4d-2: `UnitSpec.nodup` dropped (red team's lemma); `dp` from the tables' classes (`TableClass`, `derivedPlaces_of_classes`), #293's theorems without `dp` | #293 | Draft. Unpinned. Plan `flock-soundness/20260928T1625Z-plan-dp-for-a-program-of-units.md` |
| [#316](https://github.com/danielreuter/verity/pull/316) | `05ca65fd` (merges #319) | N1 (b): a unit may read one source on several inputs, and the statement's zero is a program input; `UnitPlace.aliased`; the six `Lowering` pins re-recorded (`373252e2`); `TableClass`'s copy positions and forced-zero rows derive `aliased` | #304 | Ready. **Granted** (red team 20:34Z, at `373252e2`, covering `ae9142fb`), with C1 on claims: bind the committed zero (checklist row at `05ca65fd`). Kernel replay PASS at `81c6bd25` and `ae9142fb`. In the merge request for the Lean train |
| [#318](https://github.com/danielreuter/verity/pull/318) | `8fe41c93` | R10: salted leaves beside the unsalted ones (`Merkle.Leaf`, `Leaf.hm96`, `hm96Leaf_bind`, `VerifiesL`, `OpensOKL`, `tableCL`); additions only | `main` | Ready. No record moves. Kernel replay PASS (`r20260928-190115-b3c6`). R7 and R8 can start. In the merge request for the Lean train |
| [#345](https://github.com/danielreuter/verity/pull/345) | `544bfc37` | The ExecSetup fix: `setupH_spec` steps over #267's `checkInRange` (`6ade34c6`), on `main` `5810574d` with #267, #260 and #319, then #316 and #318 merged on top | `main` | Merge request `coordinator/20260929T0024Z-merge-request-flock-soundness-execsetup-267-260-316-318.md`. Every pin as recorded |
| [#394](https://github.com/danielreuter/verity/pull/394) | `971e8a7e` | A template unit's parts as its statement reads them: `partsChecked` in `deriveChecked`, and `Types/Parts.lean`'s lemmas for audit-lean's T3 (regions, shifted rows, Δ exactly, own reads) | `main` | Ready. **Granted** (red team 09:41Z at `971e8a7e`; four pins' reads move, no statement does). Merge request `coordinator/20260929T0946Z-merge-request-flock-soundness-394-parts-checked.md`; merges clean on `main` `55ba1f32` |

**Next, in order (18:50Z):**
0. **T3's row facts (#394):** granted at `971e8a7e`, merge request sent 09:46Z; audit-lean has the lemma shapes (`audit-lean/20260929T0903Z-answer-from-flock-soundness-template-unit-rows.md`).
0. **The ExecSetup fix (#345, landed 05:25Z):** D3′ + W's Lean build broke at `ExecSetup` on #267's `checkInRange`. #345 carries the fix with #267, #260, #319, #316 and #318 as one head (`544bfc37`), every pin as recorded. audit-lean rebases #319 onto `6ade34c6`.
1. **N1 (#316): granted,** with C1 (bind the committed zero, a condition on claims). The merge request for #316 and #318
   is `coordinator/20260928T2037Z-merge-request-flock-soundness-316-318.md`, for the Lean train after the test-rework
   train and D3′. Whether R11d takes `hZero` is the refinement lane's call
   (`coordinator/20260928T2038Z-note-to-refinement-from-flock-soundness-207-reads-granted.md`).
   No `zeros` and no `hZero`: the zero is a program input, and `RowsL1` holds at any value of it. #207's text is
   unchanged, so the refinement lane's R11d targets it as it is.
2. **`dp` for a program:** `TableClass` now carries copy positions and forced-zero rows. audit-lean and flock-verifier
   supply them from an accepted typed statement. `TableClass.Copies` (the slot's inputs that read one source copy one
   position, or forced-zero rows) comes from the netlist's sources, which is S4's.
3. **R10 (#318):** the model draft builds, and R7 and R8 can start. `table_sound_compiled` for any leaf scheme is best
   done after both trains land, by generalizing the chain once
   (`coordinator/20260928T1844Z-note-to-refinement-from-flock-soundness-r10-draft-builds.md`).
4. **#274 (S5):** the train is on `main` (`ac412eb8`). Merge `main` in and record `check`: that needs about 10 GB, and
   this VM has about 6.
5. **Completeness over the DAG.**

**Other lanes' pieces in the skeleton:**
- `hExec` belongs to the refinement lane, bc-159ce83b. It stays a hypothesis until R11.
- `DerivedPlaces` is 1d (audit-lean) and 1e (flock-verifier). They should derive DAG classes with `deriveChecked` and
  read the unit's rows through `blockRow` (`coordinator/20260928T0645Z-note-to-flock-verifier-and-audit-lean-derive-checked.md`).
  After #263, `flock-rows --archive --part` prints `deriveChecked`'s rows.
