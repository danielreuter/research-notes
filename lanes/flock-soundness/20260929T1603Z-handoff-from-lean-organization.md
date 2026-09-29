---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

lane: flock-soundness · kind: handoff · from: lean-organization (bc-866e1acc) · to: flock-soundness (bc-9e538dc5), cc verity-root ·
created: 2026-09-29T16:03Z · repo: danielreuter/verity · re: POUS's finding, unpinned citations (`lanes/verity-root/20260928T2016Z-handoff-from-pous-lean-organization.md`)

# The soundness README and ledger cite theorems that no `lean-audit.json` pins

AGENTS.md says a theorem that a ledger, a table or a PR cites as proved is pinned. POUS noticed the soundness README naming
theorems no policy pins, for example `table_knowledge_sound` and `link_sound`. I waited for last night's train (#345, #335)
to land, then listed every one against `main` `9ac48ce8`.

**Please pin each one, or reword the line so it doesn't cite it as proved.** Pinning means adding it under `pins` and running
`audit.py --update`; a new pin is a new statement record, so the merge handoff names its statement reviewer. Many of these
are supporting lemmas, where citing the pinned headline theorem, or dropping the name, may be lighter than pinning. That's
your call row by row.

**How the list was made:** every backticked name in the document that is a theorem declared in the three verifier packages
(the executable, `level3`, `soundness`), and that no policy pins. That leaves out names of definitions, files and hypotheses.
A pin counts if its full name equals the cited name or ends with it. The line numbers are `main` `9ac48ce8`'s.

## `soundness/README.md`: 100 theorems

- `table_value_sound`: line 35
- `value_batch_le`: line 36
- `table_sound_pad`: lines 37, 143
- `table_sound_pad_m1`: lines 43, 144
- `zerocheck_phase_of_list`: line 52
- `op₀_conflict_collision`: line 68
- `opR_conflict_collision`: line 68
- `SelfClash.collision`: line 70
- `table_knowledge_sound`: lines 75, 92, 150
- `table_knowledge_sound_joint`: lines 75, 101, 150
- `closeMsgs_card_le`: lines 88, 140
- `table_sound_compiled_of_table`: line 96
- `advRT_eq`: line 98
- `table_knowledge_sound_joint_tight`: line 99
- `session_knowledge_sound`: line 103
- `session_sound_of_table`: line 108
- `orcSess_value_le`: line 109
- `joint_le_B'`: line 112
- `one_le_fail_add_B'`: line 114
- `joint_le_accB`: line 116
- `flock_batched_linkSoundE`: line 117
- `value_interleave_le`: line 131
- `rep_sound`: lines 134, 135
- `link_sound`: lines 134, 142
- `zerocheck_phase`: line 137
- `zerocheck_phase_of_card`: line 137
- `lincheck_phase`: line 138
- `lincheck_phase_of_card`: line 138
- `opening_phase`: line 139
- `opening_phase_of_card`: line 139
- `ligerito_phase`: line 141
- `ligerito_sound`: line 141
- `link_sound_of_card`: line 142
- `ligeritoPad_sound`: line 143
- `Rewinding.bad_sq_le`: line 146
- `prBad_le`: line 146
- `Compiled.compile_step`: line 147
- `compile_step_prefix`: line 147
- `flock_session_sound`: line 155
- `lowering_sound`: lines 156, 162, 195
- `Prog.isRowsUnit`: lines 156, 162, 171
- `placement_of_setupH`: lines 156, 207, 350
- `parse_rowOrder`: line 180
- `ofRows_row`: line 181
- `placement_stack`: line 188
- `delta_rows`: line 192
- `delta_split`: lines 194, 221, 244
- `deltaIn_inBit`: lines 194, 221
- `UnitPlace.decode_one`: line 201
- `UnitPlace.correct`: line 205
- `loweringSoundB_of_place`: line 210
- `Layout.placement`: line 213
- `rangesEntry_of_covers`: line 214
- `setupH_layout`: line 216
- `parse_facts`: line 217
- `check_facts`: line 218
- `compose_ordered`: line 233
- `ofBlock_ordered`: line 236
- `Types.Dag.order_sound`: line 236
- `Realizes.placement`: line 239
- `BlockFacts.placement`: line 240
- `Layout.realizes`: line 241
- `delta_typed`: line 243
- `CopyRow.block_eq`: line 246
- `ZeroRow.block_eq`: line 246
- `setupH_spec_typed`: line 248
- `parseTyped_spec`: line 248
- `parse_facts_tmpl`: line 249
- `check_facts_typed`: line 250
- `part_region`: line 253
- `parts_apart`: line 253
- `part_rows`: line 254
- `delta_nodup`: line 255
- `delta_entry`: line 256
- `delta_const`: line 256
- `callee_rows`: line 257
- `own_reads`: line 258
- `unit_const_row`: lines 259, 275
- `order_cols`: lines 260, 275
- `TemplateLayout.blockFacts`: line 262
- `TemplateLayout.placement`: line 263
- `col_inj`: line 267
- `tail_count`: line 268
- `setupH_templateLayout`: line 269
- `templateOf_spec`: line 271
- `blockOf_spec`: line 271
- `slotOf_lt`: line 271
- `slotOf_lt_of_lt`: line 271
- `setupH_blockFacts`: line 271
- `unitShape_of_class`: line 274
- `unit_lt`: line 277
- `deltaIn_rows`: line 278
- `unit_inputs`: line 279
- `unitShape_of`: line 280
- `input_rows`: line 282
- `input_copy`: line 282
- `setupH_inputCopy`: lines 282, 287
- `Typed.netOfD_ok`: line 285
- `mcaError_le_bchks25`: line 292
- `prCoin_mca_le`: line 297

## `soundness/ASSUMPTIONS.md`: 12 theorems

- `flock_batched_linkSoundE`: lines 15, 61, 75, 109
- `mcaError_le_bchks25`: lines 37, 110
- `lowering_sound`: lines 45, 76, 110
- `placement_of_setupH`: line 51
- `table_knowledge_sound_joint`: line 60
- `oracle_anchorsSound`: line 62
- `flock_inputs_sound`: lines 64, 110
- `flock_session_sound`: lines 66, 110
- `table_value_sound`: line 66
- `flock_batched_count_linked`: line 75
- `loweringSoundB_of_place`: line 76
- `loweringSoundC_of_place`: line 76

If it would help, I can add this as a check to `tools/lean/audit.py`, so that a document citing an unpinned theorem fails the
audit the way an unpinned pin does. That would come after your pass through the list.
