---
id: 20261004T2241Z-draft-move-map-answers
campaign: circuits
lane: circuits
kind: draft
status: open
repo: verity
origin: bc-4632b079-2045-51d2-8ef9-01640bee6e61
---

# circuits: answers to the move maps

These are circuits' answers to the core map's questions 3, 5 and 8, and to the backends-integrations-tools map's circuits
questions 2–7. Question 1 is settled by top's default 3. Every claim was checked read-only against origin/main
`9400e83d5`. Paths are relative to the repository root. "Core map" is `20261004T2125Z-draft-move-map-core`, and
"backends map" is `20261004T2125Z-draft-move-map-backends-integrations-tools`.

Two facts underlie several of the answers:

- A primitive is keyed in a descriptor by its id and signature only. So a test-local
  `PrimitiveDefinition(..., register=False)` with the same name, version and signature encodes to byte-identical
  descriptors. `tests/ir/format_vectors.json` already uses only toy ids (`TAdd32_v1`, …).
- `register_kernel` already takes a Definition id string (`verity/evaluation`), so default 3 needs no new API.

## Core map, question 3: is `ml.library` part of the verifier or a public parameter?

**Answer:** It is part of the verifier. Keep `ml/library.py` whole in `verity/`, and do not split the mechanism from the
list. C-Flock's verifier of record compiles in the same list (`LIBRARY_TABLES`), and `Typed.lean`, `CircuitType.lean`
and `Layout.lean` refuse any other table, so changing the list changes the verifier. Only the table bytes
(`ml/tables/`, sm_89 measurements named by SHA-512) are catalog device data. proofs should confirm this.

**Evidence:**
- `packages/verity/src/verity/ml/library.py` imports only `verity.ir.codec`, and its `DEFINITIONS` are id strings. Its
  docstring says these are "the only objects the verifier holds".
- `backends/flock/verifier/lean/Flock/Library.lean` defines `LIBRARY_TABLES`.
- `backends/flock/tests/test_table_library.py` checks that the Python and Lean lists agree.
- The table bytes are read in `ml/mufu.py:48` and `ml/boolean/mufu.py:116,463`.

## Core map, question 5: the ten tests (eleven test-only edges)

**Answer:** Machinery tests that use a catalog Definition only as a convenient leaf switch to toy registrations. This
needs `const` in `verity.ir` (question 8). Toys of FP operations call `verity/primitives/fp/`.

The three pinned-vector tests also switch to toys, but keep the same ids and signatures. That way
`partition_vectors.json`, `qword_vectors.json` and `qcall_vectors.json` stay byte-identical: check with `--write` and
an empty diff. They are worth keeping identical because C-Flock's Lean verifier and the agreement scripts read them.
`qword_program_agree.py` even imports `test_qword_vectors` by path. The alternative, renaming them to `T*` ids and
re-pinning, costs a `lean-agreement` rerun.

Everything that tests a particular Definition's kernel, or replays a capture, moves to the catalog's suite.

| Test (file::name) | Call | Reason |
|---|---|---|
| `tests/ir/test_annotations.py` (all) | toy | `F32Fabs`, `F32Fmaxf` and `I32Add` are only leaves of local composites, and no JSON is pinned. |
| `tests/ir/test_codec.py::test_a_self_compare_round_trips` | toy | Its lazy `BIT`/`F32`/`F32Eq` import is a codec round trip. Any 1-bit comparison primitive works. |
| `tests/ir/test_constants.py` (all) | toy | It needs `const` and `I32Add`. `const` moves to `verity.ir`, and `I32Add` becomes a toy adder. |
| `tests/ir/test_units.py` (all) | toy | Unit cutting is generic. The four primitives are leaves. |
| `tests/ir/test_partition_object.py` (all) | toy, same ids | It pins `partition_vectors.json` (`I32Add_v1`, `F32Fmaxf_v1`, `F32Fabs_v1`), which the Lean verifier and `qword_agree.py --vectors` read. |
| `tests/ir/test_qword_vectors.py` (all) | toy, same ids | It pins `qword_vectors.json` and already has toys (`TWide`, `TNarrow`, `TAdd64`). Six more primitives become same-id toys. `qword_program_agree.py` imports this module by path. |
| `tests/ir/test_qcall_vectors.py` (all) | toy, same ids | It pins `qcall_vectors.json`. Note that `qcall_agree.py:120` imports `verity.ml.scalar.I32Add` itself and needs the same toy. |
| `tests/evaluation/test_bits.py` (all but one) | toy | Bit-sliced evaluation of generic composites. |
| `tests/evaluation/test_bits.py::test_peak_bytes_bounds_what_evaluate_bits_holds` | toy | It uses `ml.boolean.gemm` only as a large circuit. A generated gate chain of the same size tests the same memory bound. |
| `tests/evaluation/test_registered_tables.py` (all) | toy | `S.I32Add` (line 64) is a batch adder. The property is registered-table evaluation. |
| `tests/evaluation/test_evaluation.py`: `test_oracle_is_the_ir_evaluator`, `test_inputs_are_validated`, `test_a_broadcast_operand_is_read_in_place`, `test_batch_equals_reference_and_kernel_choice`, `test_register_kernel_is_one_function_per_name`, `test_partial_decline_goes_to_the_reference`, `test_self_check_catches_a_wrong_adder` | toy | These test the evaluator's machinery. `test_partial_decline_goes_to_the_reference` is already a toy. |
| `tests/evaluation/test_evaluation.py`: `SELF_CHECKED`, `test_every_registered_kernel_is_self_checked_here`, `test_kernel_matches_the_reference`, `test_evaluate_is_the_primitive_and_the_direct_chain`, `test_scalar_reference_statics`, `test_gemm_batch_shapes`, `test_unknown_step_falls_back_to_the_reference`, `test_declined_instances…` (NVFP4), and the capture replays (ampere, hopper, nvfp4, gemm_coordinate, group_sum) | catalog suite | These are about particular Definitions' kernels, and the replays read `tests/ml/fixtures`. AGENTS.md's "every registered kernel is listed" rule moves with them. |
| `tests/proofs/test_profile.py` (the eleventh edge) | toy | It binds `gemm.Gemm` with `GEMM_AMPERE` only to get a Program with partition levels. |

When the self-check list moves, fix its completeness filter. `test_evaluation.py:81` keeps only kernels whose
`fn.__module__` starts with `verity`, so kernels registered under any other import name drop out of the check silently.
That fails open. Key the filter on `_KERNELS` minus an explicit allow-list instead.

**Evidence:**
- `packages/verity/tests/ir/*.py` and `packages/verity/tests/evaluation/*.py`.
- `packages/verity/tests/ir/format_vectors.json` (the toy precedent).
- `backends/flock/verifier/qword_program_agree.py`, `qcall_agree.py` and `qword_agree.py`.
- `backends/flock/tests/test_lean_verifier.py`.

## Core map, question 8: seven smaller calls

1. **`ir.liveness`** stays in `verity/primitives/circuits/`. It is a generic query over circuits (P4): stdlib, imports
   only `ir`. The frontend (`frontend/derive.py`, `torch_frontend.py`), `program/boolean.py:352` and
   `circuit_check/checks.py:505` all use it.
2. **`ir.annotations`** (`verity/annotations/v0`): the validator goes to `tools/circuit_check/`. The annotation JSON
   files (`ml/annotations.json`, the registry's `annotations.json`) go to the catalog beside their Definitions. An
   annotation is never in a digest, so it is not TCB. Evidence: `tools/circuit_check/tests/test_annotation_files.py`.
3. **`proofs.query`** (draft 3.1 Call-level units) moves to `integrations/vllm/verity_vllm/query/` under a vLLM name
   (P7). Its only users are 4 vLLM modules and 11 vLLM tests (`query/required.py`'s `Q_module_body_v1`,
   `module_body.py`, `program_view.py`, `norm_scales.py`). It is not the same thing as `ir.query` (the path language) or
   `partition_object`. Superseding it with `partition_object` later is a `circuits/<slug>` approach entry, not part of
   this move.
4. **`boolean.universal`** (protocol 2's `UniversalUnit_v1`) goes to `experimental/private_circuits/`, since it has no
   guarantee yet (P9). Its users must follow: `circuit_check/targets.py:53,350` takes its binding from
   `experimental/`, and `backends/flock/tests/test_wired_links.py` (§16.13 linking) moves with it or switches to a toy
   unit.
5. **`boolean.gather`** goes to `verity/primitives/circuits/boolean/` with `forms`. It is a 30-line gadget that imports
   only `forms`, and it has no Definitions.
6. **The `ml.operations` guard and its list** stay together in `verity/`, beside `ir.constants`. `OPERATIONS` and
   `DERIVATIONS` are id strings resolved through `REGISTRY` at run time, so the module imports no catalog module. The
   list is zero-knowledge policy ("no data"), not a parameter. Its callers are tests only.
7. **`ml.prims.const`** (the `Const<w>[0x..]_v1` family and its lazy family) moves to `verity.ir`, beside
   `ir.boolean.constant`, to which w=1 already delegates. `prims` re-exports it, so the ids are unchanged. PoUW's
   `circuit/hashes.py`, five `ir` tests and at least seven registry modules need it (`b1`, `boolean_norms`, `fa2_check_inf`,
   `fa3_check_inf`, `fa2_softcap`, `pouw_rows`, `tables`).

## Backends map, question 2: the registry classes

**Answer:** Agree, with three corrections.
- The kernels need twin helpers and constants moved, not only ids. Row kernels import `fp8.np_f32_to_e4m3_sat`,
  `MIN_SCALE_BITS`, `dense.softcap_mul_bits` and `fp8_moe.check_act_st…`, and they call `bind` on Definitions.
- The quarantine goes to `experimental/`, not deletion (see question 7).
- No registry module calls `register_kernel`, so moving the registry moves no kernel registration.

`lifted`'s split is the right order for freeing `moe_pad`: `moe_pad` imports `lifted` at module level, and nothing else
holds it. The counts at the next tip (59 modules, with `mla`, `mla_check`, `mla_capture` and `rope_gptj_difftest`)
match an AST scan of origin/main, and the six module-level external importers match too.

**Evidence:** `integrations/vllm/verity_vllm/program/registry/*.py` and `program/kernels/{rows,dense_rows,fp8_moe_rows}.py`.

## Backends map, question 3: is the Commit VERDICT a verifier role?

**Answer:** No. The VERDICT (`vllm-verdict/v1`) is the integration's row evidence, evaluated from v1's `commit_rules`,
and it stays in `integrations/vllm/`. The verifier's draws already live inward: `commit/challenge.py` draws through
`verity.randomness.derive` and `verity_sampled_proofs.law`, so `challenge.py` is an adapter. Its legacy Fiat–Shamir
forms stay for replay until decision 42 retires them. The row kernels therefore need no `verity/` home on the
VERDICT's account; they go to `verity/kernels/` only because default 3 puts every kernel there.

**Evidence:** `integrations/vllm/verity_vllm/check/verdict.py`, `check/commit_rules.py` and `commit/challenge.py`.

## Backends map, question 4: conformance and targets

**Answer:** Each Definition's conformance status already lives on the Definition itself (`conformance=`,
`ir/defs.py:78`), and `registry/conformance.py`'s `record()` only reads it from `REGISTRY`. So the catalog index
derives both `status` (`current`/`superseded`) and the conformance kind from the Definition, and nothing moves from
`conformance.py`. Its B1/B0-specific data (`DIVERGENCES`, `INPUT_QUALIFICATIONS`, `NAN_CANONICALISATION`) and its CLI
stay in vLLM. `targets` and `gemm_targets` are integration vocabulary. The representative statics come from
circuit-check's bindings, which are being split per Definition module.

**Evidence:**
- `packages/verity/src/verity/ir/defs.py:78`.
- `integrations/vllm/verity_vllm/program/registry/conformance.py`.
- `tests/program/test_conformance_record.py`.

## Backends map, question 5: `commit/merkle.py` and the committer kernels

**Answer:** `merkle.py` duplicates `verity.commitments.leaves` (the `verity-vllm/leaf/v1` contract), not `vllm_v1`'s
chunked framing.
- The duplicated pieces (`path_shape`, `tree_depth`, `verify_opening`, `MerkleTree`) consolidate onto `leaves`
  (`LeafTree`, `levels`, `open_path`), bridged by vectors.
- `RangeOpening`, `fold_range` and `verify_range_opening` stay in vLLM until a verifier reads them. Then they go to
  core.
- `hashing.py` already imports H and the tags from `leaves`.

The committer's `.cu` leaf-hash and tree kernels (references `vllm_v1.pos_leaf`/`fold`) become a `verity/kernels/`
entry later. No soundness result rests on them, because the verifier recomputes leaves from the opened bytes; only
completeness does. They stay put for now.

**Evidence:**
- `integrations/vllm/verity_vllm/commit/merkle.py` and `hashing.py`.
- `packages/verity/src/verity/commitments/leaves.py`.
- `commit/committer/leafhash.py` and `tests/commit/test_leafhash_device.py`.

## Backends map, question 6: `bench/templates.py`, `program/boolean.py`, `boolean_export.py`

**Answer:**
- `bench/templates.py` goes to `benchmarks/`, not the catalog. It binds templates to input-set ports and VU-export
  relation names, which are benchmark vocabulary, and it lazily imports `kernels.rows`.
- `program/boolean.py` has no link table to move. The Definition→Boolean link is each Boolean Definition's own `word`
  (`verity.ml.boolean.trace.word_of`), and `boolean_version()` just scans modules. So the lookup goes to the catalog's
  loader, and `lift`, `purity`, `dry_run` and `derived` stay in vLLM.
- `boolean_export.py` goes to `tools/`. Its docstring calls it "the website visualizer's dataset; a derived format, not
  a statement". It is an exporter, not an integration adapter.

**Evidence:**
- `backends/numerical/src/verity_numerical/bench/templates.py`.
- `integrations/vllm/verity_vllm/program/boolean.py`.
- `backends/flock/python/verity_flock/boolean_export.py`.

## Backends map, question 7: counts

**Answer:** At origin/main the registry holds 59 modules counting `__init__` (`annotations.json` is not counted), and the
quarantine holds 39 `.py` files in 6 subpackages. I can't say which method gave the plan its 43; the plan predates the
current tree. Don't reconcile the counts. Use the AST scan as the record.

**Evidence:** `ls integrations/vllm/verity_vllm/program/registry/*.py` and `find …/registry/quarantine -name '*.py'`.

## Row corrections

| Map | Row / path | Map says | Should be | Why |
|---|---|---|---|---|
| core | `verity/ml/boolean/fp.py` | `catalog/definitions/boolean/fp` | `verity/primitives/circuits/boolean/fp` | It has zero Definitions. It holds the lowering's per-op gadgets (its docstring: "formerly C-Flock's `fp`"), and C-Flock's lowering imports it. |
| core | `verity/ml/boolean/softmax.py`, `tc_step.py` | `catalog/definitions/boolean/` | `verity/primitives/circuits/boolean/` | They are gadgets with zero Definitions, imported by C-Flock's `tail_pieces` and the lowering. |
| core | `verity/ml/boolean/fp4.py` | catalog (or experimental) | `verity/primitives/circuits/boolean/`, unless NVFP4 is ruled experimental | It is a gadget with zero Definitions. compute-accounting's NVFP4 call still decides it. |
| core | `verity/ml/boolean/scalar.py`, `mufu.py` | catalog, whole | split: the gadget functions to `verity/`, the Definitions to the catalog | `tail_pieces` imports `e4m3_to_f32`, `f32_to_e2m1_sat`, `f32_to_e4m3_sat` and `fmaxmin` from `boolean.scalar`. |
| core | `verity/ml/boolean/forms.py` | owner question | yes, it is part of the lowering | `trace` and every gadget build on it, and it has no imports. |
| core | `verity/ml/boolean/gather.py` | owner question | `verity/primitives/circuits/boolean/` | It is a gadget and imports only `forms`. |
| core | `verity/ml/boolean/universal.py` | owner question | `experimental/private_circuits/` | It has no guarantee yet. `test_wired_links` follows it. |
| core | Forbidden-import split 6: `ml.operations` and `ml.library` | split the mechanism into `verity/` and the list into the catalog | keep both whole in `verity/`; only `ml/tables/` bytes go to the catalog | The Lean verifier hard-codes the list. Both lists are id strings, so there is no catalog import to break. |
| core | Forbidden-import split 7: `ml.prims.const` | "to `verity/`" | to `verity.ir`, beside `ir.boolean.constant` | `verity.ir` is stdlib-only and imports no other core module, so `const` can live there and the `ir` tests can use it. |
| core | `ir.annotations` | catalog or tools | the validator to `tools/circuit_check/`, the JSON to the catalog | It is never in a digest. circuit_check is its main user. |
| core | Test-only edges | "seven `ir`, three `evaluation`, `test_profile`" | 11 edges; split as in question 5 | Also add `qcall_agree.py:120`'s `ml.scalar` import (agreement script, not a test). |
| core | `test_evaluation.py` self-check list | moves to the catalog | moves, with a filter keyed on `_KERNELS` | Its `__module__ == "verity"` filter fails open for kernels under any other import name. |
| backends | `program/registry/quarantine/` | deleted | `experimental/` (consolidate, don't delete) | It is live. `gen_ov_sampling_patterns.py`, `gen_dense_softcap_patterns.py`, `gen_ln_patterns.py`, `gen_ov_moe_patterns.py`, `gen_dense_gemma2_patterns.py` and `generic.py:354/356` import it at module level. Gate G4 (`check/gates.py:716`, `observe/fold/resolver.py`, `resolve_log.py`) finds it by the `.quarantine.` path. A deletion is first a `circuits/<slug>` superseded entry. |
| backends | `class_statement.py` (and `partition_units.py`) | blocked only by `program_graph` | also blocked by `circuit_check.targets` | Both lazily import `circuit_check.targets` (`class_statement.py:421`, `partition_units.py:233`). `load_registries()` and `definition(spec)` must become the catalog loader before C-Flock's prover enters `verity/`. |
| backends | `class_statement.py`: lift `definition_digest` into `verity.ir` | lift it | lift `_encoded`; for the digest, choose one existing core digest rather than adding another | Three different `definition_digest` functions exist (`ir/annotations.py:60`, `query/word.py:221`, `pipeline/program_graph.py:650`, plus `torch_frontend.py:1332`). The catalog entry pins one canonical descriptor digest. |
| backends | `commit/merkle.py`, `hashing.py` | onto `verity.commitments` (`vllm_v1`) | onto `verity.commitments.leaves` | Those are the functions it duplicates. Range openings stay. |
| backends | `program/boolean.py` | the link table goes to the catalog | no table: the link is `word_of`; only the `boolean_version` lookup goes to the catalog loader | See question 6. |
| backends | `registry/conformance.py` | to the catalog as status | stays in vLLM; the index derives status from each Definition's `conformance` | The field is already on the Definition. |
| backends | C-Flock shims `fp.py`, `gf2.py`, `unit.py`, `unit_fp4.py` | deleted | kept, or replaced together with `boolean_export`'s patching | `BX._patch()` (used by `type_trace.trace_types`) patches through them. `ir_lower`, `tail`, `tail_pieces`, `lowering`, `class_statement`, `partition_units`, `sha512_circuit`, `ir_sampling` and `circuit_types` import via the shims. |
| backends | `boolean_export.py` | integration or tools | `tools/` | It is a visualizer dataset and not a statement. |
| backends | `program/kernels/` `_jit.py`, `kernel_registry.py` | "mostly a rename" | a rename plus an import-name change | `verity_vllm` is not a namespace package, so `verity/kernels/` needs a new import name. About 94 importer files change (86 in vLLM). |
| backends | Row kernels (`rows.py`, `dense_rows.py`, …) | register against Definition ids | ids plus the twin helpers and constants they import | They import helper functions and constants from registry modules and `bind` Definitions, so those helpers must move to `verity/kernels/` with them. |
| backends | `bench/templates.py` | `catalog/definitions/templates.py` | `benchmarks/` | It is input-set and VU-export vocabulary. |
| protocols | `verity_pouw/circuit/hashes.py` → `verity/primitives/circuits/hashes.py` | SHA-512, SHAKE256 and TurboSHAKE128 in gates | goes wherever `words.py` goes (catalog per the entry format) | It is a word-level composite (`Emit` builds `CompositeDefinition`s) over PoUW's own word primitives (`W.PouwCh32`, `PouwMaj32`, `PouwXor32`, `PouwAdd64*`, `PouwRotl64*`), not a gate circuit. In `verity/` it would import catalog-bound `words.py` (P6). "One SHA-512" is a vectors bridge to `ml/boolean/sha512`. |
| protocols | `verity_pouw/circuit/words.py`, `boolean.py` | `catalog/definitions/pouw/` | agree | `boolean.py` imports `ml.boolean.fp`, `forms` and `trace`, which are all `verity/` after the corrections, so P6 holds. |
| catalog entry | `status` and conformance as two fields | stored | derived from the Definition's `conformance` attribute at index time | `superseded` sits today inside the same `STATUSES` set as the conformance kinds. One source, no drift. |

## Rulings (22:46–22:50Z, thread 1791150333.889129)

Top ruled on the open points, and circuits settled the two left to it. These replace the answers above where they differ.

- **Gadget placement (core 8.5 and the row corrections).** Daniel renamed `verity/primitives/fp/` to
  `verity/primitives/silicon/`, the bit-exact models of the hardware's low-level ops.
  - To `verity/primitives/silicon/`: `ml/boolean/fp`, `tc_step` and `fp4`, beside the models they implement, and the
    gadget halves of `boolean/scalar` and `mufu` (conversions and MUFU ops) when those modules split.
  - To `verity/primitives/circuits/boolean/`: the generic pieces `forms`, `gather`, `trace` and `softmax`. `softmax`
    composes the `fp` gadgets and models no single hardware op.
- **The catalog digest (backends `class_statement` row, open point 5a).** It is none of the four `definition_digest`
  functions. The catalog entry pins `verity.ir.codec.program_digest` of the one-call Program at given statics, the
  wrapper `_encoded` builds, lifted into `verity.ir`. It covers everything the call reaches and is the same in any
  program. The switch is cheap: `class_statement` checks a capture graph's `definitions_index` against
  `program_graph`'s v0 digest, which is recorded in the graphs and pinned nowhere. That check moves with `program_graph`
  and keeps the v0 digest until graphs are re-recorded, and the catalog's digest is a new field.
- **`ml.library` (core 3).** proofs' answer (`note:proofs/20261004T2240Z-handoff-move-map-answers`) is that
  `Flock/Library.lean`'s `LIBRARY_TABLES` becomes a file generated from the catalog entry, with a no-diff test (the
  `Vectors.lean` pattern). This answer's Lean objection therefore no longer holds. The captain decides the
  mechanism/list split after the moves; no move PR waits on it. `ml.operations` stays whole in `verity/`.
- **The 43 (backends 7).** It was the plan's first draft, now superseded. The plan cites the scan at main: 59 modules,
  53 of which import nothing outside the registry, `verity` and numpy.
- **Import names (4c), settled by Daniel at 22:50Z.** Import names follow the new directories (`verity/primitives/silicon/` is
  `verity.primitives.silicon`), and `program/kernels` takes its new import name when it moves. The move script carries a
  module map beside its path map. It rewrites imports, `import_module` strings, `module:attr` specs and module-keyed test
  data, and each move PR runs it on its own branch after a restack. Lean comments that name Python modules are left to a
  later Lean PR. See `note:20261004T2058Z-draft-repo-organization-principles`, packaging section.

## Rulings after 23:00Z (Daniel 4:19 PM and 4:25 PM PDT, plan commits 27ac6fbc and 10cf6e8d): the rows as they now stand

These replace the gadget-placement and kernel rows above.

- **Silicon to `catalog/silicon/`, not `verity/`.** The models, their Lean, the FP formats, the device instances and the
  gadgets that implement them go to `catalog/silicon/`: `ml/boolean/fp`, `tc_step`, `fp4`, the gadget halves of
  `boolean/scalar` and `mufu`, and the `ml/tables/` bytes. A circuit is claim content pinned by digest, so no guarantee reads
  a model.
- **What stays in `verity/`.** Only the circuit machinery stays. That means the generic Boolean pieces `forms`, `gather` and
  `trace` in `verity/primitives/circuits/boolean/`, plus any builder the verifier runs at verification time (PoUW's
  `ncp2`). `softmax` composes the `fp` gadgets, so it follows them to `catalog/silicon/`.
- **Kernels to a top-level `kernels/`, untrusted.** That covers vLLM's `program/kernels/` (`_jit.py`, `kernel_registry.py`,
  `rows.py`, `dense_rows.py`, `fp8_moe_rows.py`, …) and the registry helpers and constants the row kernels import. They
  stay bit-exact with their reference. `gpu_proofs_match_cpu` becomes a completeness test. Backends question 3 stands:
  the row kernels never needed a `verity/` home.
- **Nothing moves to `experimental/`.** That replaces this note's `boolean.universal` → `experimental/private_circuits/`
  row and its quarantine row: the non-recursive proof system stays in `verity/`. Where the quarantine goes now is the
  layout-move worker's call. Consolidate, don't delete, still holds.
- **The move is one generated commit** on `cursor/layout-move-c3b2` (Daniel, 4:30 PM PDT). Circuits' per-family split
  scripts and the per-Definition bindings split (`cursor/circuit-check-bindings-per-module-8c79`) are inputs to it.
