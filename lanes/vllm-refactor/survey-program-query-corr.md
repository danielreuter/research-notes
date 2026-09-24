---
id: vllm-refactor/survey-program-query-corr
lane: vllm-refactor
kind: survey
status: in-progress
created: 2026-09-24
checkout: f0810a11 (lane/vllm-cleanup-2)
slice: integrations/vllm/verity_vllm/{program,query,correspondence}
---
# Survey: program/, query/, correspondence/

Read-only survey against `/Users/danielreuter/projects/verity` at `f0810a11`. No Python was run. Evidence is `rg`, `git grep`, `git log`, `wc` and reading.

Paths below are relative to `integrations/vllm/verity_vllm/` unless they start with `packages/` (verity core, `packages/verity/src/verity/`) or another top-level directory.

## Slice size

| Subpackage | .py files | .py lines | other files |
|---|---:|---:|---|
| `program/` | 119 | 36,252 | 4 `.cu` probes, 3 `.cpp` models, 2 table files (`mufu_tanh_sm89.json`, 450 KB `.xzblocks`) |
| `query/` | 14 | 6,613 | none |
| `correspondence/` | 13 | 5,602 | none |
| total | 146 | 48,467 | |

Global counts over the slice (before per-module detail):
- 18 modules end in `if __name__ == "__main__":` and 17 import `argparse`.
- 11 modules read `os.environ` (plus `vllm_meta.py`, which *writes* 5 env vars with `setdefault` at import).
- verity core imports: mostly `verity.ir.{defs,refs,types,codec}`. Only `query/module_body.py`, `query/program_view.py`, `query/v1_bridge.py` import `verity.verification.query`; `correspondence/capture_identities_program.py` imports `verity.verification.{programs,typed_obligation}`. Nothing imports `verity.commitments` or `verity.verification.plan`.

(Sections below are appended as each module group is finished.)

---

## 1. `query/` (14 files, 6,613 lines)

**What it actually does vs its name.** The name promises "the verification query" (Q over a Program). The package actually holds three unrelated things:
1. Generic `verity.ir` analyses with no vLLM content: `boundary.py`, `partition.py`, `query_artifact.py`. Core's own docstrings say these are parked here "until promoted" (`packages/.../ir/parts.py:15-18`, `packages/.../ir/layout.py:19`).
2. The vLLM required-value manifest builder: `module_body.py`, `program_view.py`, `v1_bridge.py`, `manifest/format.py`, `cli.py`, `manifest/verify.py`, `compare.py`. This encodes v1 identity spellings, FA2/FA3 kernel geometry, MoE planes and TP policy.
3. Two things that are not query code at all: an Inductor-source parser for compiled rows (`manifest/compiled.py`) and a replay-population enumerator that depends on `check/` and `observe/` (`vu_query.py`).

Only `module_body.py` is the thing the name describes, and it is 65 lines that correctly delegate to core `verity.verification.query.partition_by` / `boundary`.

### Modules

| module | lines | job |
|---|---:|---|
| `__init__.py` | 21 | docstring only (module list is stale, see DOCS) |
| `boundary.py` | 1,182 | exact / bounded in(S), out(S), w_out(S) over `verity.ir.parts.Part` via a per-specialization consumer index |
| `partition.py` | 964 | checks a `query_ast` Family is a partition (tiling induction or interval sweep), checks width `w_out <= w_max`, 32-bit gate readiness |
| `module_body.py` | 65 | `Q_module_body_v1`: `partition_by(owning module)` plus dropping literal Calls from the boundary |
| `program_view.py` | 751 | columnar `verity.verification.query.Program` view from `descriptor.json.gz` or streamed `instances.json.gz`; `repr(Type)` parser; imports registry modules for port signatures |
| `v1_bridge.py` | 802 | required values under Q_module_body_v1 plus policy, spelt as v1 manifest rows; TP rank partials; B>=2 composition; TP rank merge |
| `vu_query.py` | 813 | deterministic enumeration, indexing and uniform sampling of "tier-A" local VUs of a `FoldResult`; evaluates one VU via `check.replay.Replayer` |
| `query_artifact.py` | 185 | `verity-ir/query/v1` and `query-use/v1` JSON documents, `binding_id` |
| `compare.py` | 145 | classify identity differences between two manifests (v1 vs v2) |
| `cli.py` | 241 | argparse: `build`, `build-global`, `compare`, `check-correspondence` |
| `manifest/__init__.py` | 1 | empty |
| `manifest/format.py` | 671 | manifest schema/digest constants, instance-name parsing, FA2/FA3/MoE geometry, "promoted" v1 rows, `coverage_check`, Build-dir discovery |
| `manifest/compiled.py` | 670 | regex-parses Inductor wrapper `.py` files and vLLM's split graph into a compiled-row manifest; own `verify` subcommand |
| `manifest/verify.py` | 102 | rebuild the manifest through `cli.build` and compare digests |

### Findings

**CORE-DUP (5)**
- `query/boundary.py:227-286` `_resolve_prim` re-walks `verity.ir.layout.resolve` / `param_leaf` (its docstring says so) only to also return the producing primitive. Extend core `resolve` instead. *medium*
- `query/v1_bridge.py:340-346` re-implements half of core `required_values()` validation (`packages/.../verification/query.py:256-268`) inline because the core function recomputes the boundary; protocol-required Values are not validated at all. Core should accept a precomputed `Boundary`. *medium*
- `query/program_view.py:477-545` `parse_type_repr` parses `repr(Type)` strings because `harness/derive_step.py:39-47` writes param types as reprs; core already has `verity.ir.types.type_from_json` (`packages/.../ir/types.py:166`). *low*
- `query/query_artifact.py:73-81` falls back to its own sha256-of-canonical-JSON `query_id` when the query is not a core `query_ast.Query`; core `verity.ir.query_codec.query_id` is the one owner. *low*
- Interval helpers: `query/boundary.py:86-110` (`_full/_total/_contains/_isect`), `query/vu_query.py:115-155` (`_merge/_covers/_disjoint/_count/_intersect`), `program/frontend/liveness._norm` and core `packages/.../ir/query_ast.py:65 _merge_intervals` are four copies of one interval algebra. *low*

**INTERNAL-DUP (6)**
- `IDENTITY_KEY` is defined three times: `query/manifest/format.py:30`, `query/compare.py:24`, `query/manifest/compiled.py:29` (plus `tests/regression/checks/manifest_digest.py:52 _identity_key`). *medium*
- Build-dir lookup (`*LP<lp>_T<t>` then `build_request*/result.json`) is copy-pasted: `query/cli.py:54-75` and `query/manifest/format.py:646-671`. *medium*
- Two functions named `spec_statics` with different semantics: `query/program_view.py:438` (JSON values via core `_split_record`, floats, tuples) and `query/manifest/format.py:53` (hand parser, ints else strings). Also `spec_base` / `spec_family` / `sampling_event.family_of` are three spec-id splitters. *medium*
- Sampling-event vocabulary exists in four places: `program/sampling_event.py:13` (3 families; the allowlist calls it "the ONE vocabulary site"), `query/v1_bridge.py:66-69` (adds `ArgmaxTokenSelect_v1`, plus its own `STOCHASTIC_SAMPLING_EVENTS`), `query/manifest/format.py:315-344` (prefix matching `TOKEN_SELECT_FAMILIES`, `STOCHASTIC_SELECT_PREFIXES`). *medium*
- Manifest verification logic is duplicated: `query/manifest/compiled.py:619-648` re-implements `query/manifest/verify.py:48-71` (same ok formula and same "why" strings). *medium*
- `query/vu_query.py` (VU population over a FoldResult) and `query/partition.py` (VU partition over a Family) are two unrelated "VU" machineries in one package with no shared type. *low*

**VERSION-RESIDUE (7)** (legit hashed/serialized identifiers noted separately below)
- Module name `query/v1_bridge.py`: names the job by a retired engine version. *medium*
- `query/program_view.py:550` `REGISTRY_MODULES = ("b1", "dense", "fp8", "moe", "sampling", "b1_tp2", "moe_pad")`: case names in a module list. *medium*
- `query/manifest/compiled.py:476-478, 611` `weights_in_dataflow` / `--digest-v1`: a flag that reproduces an old digest for "records built on <= 2b6573893". *medium*
- `query/manifest/format.py:127-227, 530-537` "promoted" rows exist to read "a pre-flip v1 manifest's `promoted: true` rows". *medium*
- `query/cli.py:111-157, 191` `check-correspondence` compares the record against the `v1_annotations` fallback. *low*
- `query/compare.py` whole module compares a manifest against "v1" (the v1 engine is deleted per README). *low*
- `query/partition.py:637-644` `_BOUNDARY` injection and "absent until lane/q-boundary is merged". *low*
- LEGIT (serialized, do not rename in code without a decision): `Q_module_body_v1` / `Q_MODULE_BODY_ID`, `verity-sweep/required-manifest/v1`, `verity-ir/query/v1`, `fa2.m1` / `fa3.m1` tap names, `"engine": "v2-query"`, Definition ids in `FLASH_ATTENTION_LAUNCHES`.

**HARDCODING (7)**
- `query/manifest/compiled.py:264-267` `_weight_name` hardcodes Llama-style module names (`self_attn_`, `mlp_`, `_proj`, `emb_cos`, `tokens_weight`); `:305` the Inductor symbol `s72`; `:284` `unified_attention_with_output`; `:355-356` wrappers classified by `"embedding" in kernel` and `kernel.endswith("rms_norm_2")`. Inductor/vLLM-version and model specific, inside the query layer. *high*
- `query/manifest/format.py:270-299` FA2/FA3 launch tiling (`BN = 128 if D <= 64 else 64`, FA3 `192/128`, the decode "swapped" rule citing `flash_api.cpp:646`, Gemma-2 even layers) and `mat_total_words`. Kernel-version knowledge in the query layer. *medium*
- `query/v1_bridge.py:455-462` `_profile`: defaults compute capability to `[8, 9]` and picks "hopper" vs "ampere" from it. *medium*
- `query/v1_bridge.py:103-130` `NAMED_RESIDUALS`: a by-Definition-family table encoding vLLM's `LinearBase.forward` and `RotaryEmbedding.forward` return conventions. Not in `tests/by_name_allowlist.json`. *medium*
- `query/manifest/format.py:100-111` `wrapper_prefix_of` (`"model."`, `model.model.`), `:229` `MOE_LEAF = "experts"`, `:359-360` `layer_of` on `".layers."` (all allowlisted, retire P2/P3). *low*
- `query/cli.py:60-62`, `query/manifest/format.py:655-658` Build-dir naming conventions baked into library lookup. *low*
- `query/v1_bridge.py:234-243` `DTYPE_OF_WIDTH` guesses dtype from width (32 bits is both f32 and i32). *low*

**SCRIPT/ENV/PATH (5)**
- `__main__` + argparse in library modules: `query/manifest/compiled.py:595-670` (library and CLI in one file), `query/manifest/verify.py:74-102`, `query/cli.py:165-241` (a dedicated CLI module; acceptable). *low*
- `SystemExit` raised from library functions: `query/manifest/compiled.py:359, 362, 397, 489, 491, 495, 501, 522`; `query/cli.py:73`; `query/manifest/format.py:669`; `query/manifest/verify.py:45`. A caller cannot catch these as ordinary errors. *medium*
- `query/manifest/format.py:143-146` library constants encode `row_pod.sh`'s exit status and fail class. *low*
- Unclosed `open()`: `query/manifest/compiled.py:109, 276, 620, 652`; `query/manifest/format.py:305, 309, 662`. *low*
- No `os.environ` reads in `query/`.

**LAYERING (7)**
- `query/boundary.py` and `query/partition.py` are core-level analyses parked in the integration; core documents them as pending promotion (`packages/.../ir/parts.py:15-18`, `packages/.../ir/layout.py:19`). *high*
- `query/vu_query.py:58-60` imports `check.fold_compare`, `check.replay` (including private `_diff`) and `observe.fold`: query depends on check and observe. README: query "Never: execution data ... anything read from a run". *high*
- Cycle query <-> correspondence: `query/module_body.py:25`, `query/v1_bridge.py:54`, `query/cli.py:25` import `correspondence.reader_for_query`, which imports `query.program_view` (`correspondence/reader_for_query.py:38`); `correspondence/resolve.py:110,133` and `correspondence/reader_for_acquire.py:32` import `query.manifest.format`. *medium*
- Cycle query <-> program: `query/boundary.py:54` imports private `program.frontend.liveness._norm/_strided_targets`; `query/v1_bridge.py:79` imports `program.registry.b1_tp2`; `query/manifest/compiled.py:23` imports `program.numerics.compiled_relations`; `program/registry/lifted.py:1717-1826` imports `query.boundary/partition/query_artifact`. *medium*
- Private core API: `query/program_view.py:440` `verity.ir.codec._split_record`, `:750` `verity.ir.codec._spec_id`. *low*
- `query/v1_bridge.py:452-462, 483-487, 613-615` reads run facts from `result.json` (`attention_impls_observed`, `vllm_flash_attn_version`, `sliding_window`). *low*
- Core points back at the integration: `packages/.../ir/query_ast.py:8` cites `verity_vllm.query.vu_query._Planner`. *low*

**GOD-MODULE (5)**
- `query/v1_bridge.py` (802): protocol family tables; named residuals; member naming; shared-module-instance aliasing; collective-site numbering; the `Population` (policy + TP rank partials); manifest row emission for five families (weights, instance outputs, token ids, FA hidden stream, MoE planes); B>=2 composition; TP rank merge. *high*
- `query/boundary.py` (1,182): interval algebra, node geometry, gate resolution, canonical return form, consumer index, used-parameter leaves, exact in/out/w_out, bound, explain. Large but one analysis. *low*
- `query/partition.py` (964): verdict types, duck-typed tiling reader, tiling induction, interval sweep, three-tier width validation, 32-bit readiness, composition. *medium*
- `query/vu_query.py` (813): VU type, interval helpers, hull classification, planner, index, module cache API, replay-based evaluation. *medium*
- `query/manifest/format.py` (671, under the threshold but its own docstring lists 5 jobs), `query/manifest/compiled.py` (670: wrapper parser, kernel-signature parser, split-graph parser, dataflow resolver, manifest builder, verify CLI). *medium*

**DEAD (3)**
- `query/manifest/format.py:332 has_splits_param` and `:343 is_stochastic_select`: no callers anywhere (searched absolute/relative imports, `rg -w` over the repo including `.sh`/`.json`/tests). The allowlist still pins a by-name rule inside `is_stochastic_select`. *high confidence*
- `query/manifest/format.py:275` `from_words = None  # noqa: F841 (documentation...)`. *high confidence*
- `query/cli.py:111 check_correspondence` and `:97 build_global_ranks` are only reachable through the CLI (live via `row_pod.sh` for `build-global`; `check-correspondence` has no caller in `ops/` or tests). *medium confidence for `check-correspondence` (searched `ops/*.sh`, tests, tools)*

**NAMING (5)**
- "VU" has three meanings: `vu_query.VU` is a descent path in a folded Program; `partition.py` "VU partition" is a GateSet family; core `VerificationUnit` and the README define a VU as a set of Calls. *medium*
- `_profile` in `query/v1_bridge.py:453` means GPU architecture (hopper/ampere); elsewhere "profile" means target profile, capture profile, kappa. *medium*
- `query/manifest/format.py` holds much more than a format (coverage check, geometry, discovery). *low*
- `compose_global(fixture, ...)` (`query/v1_bridge.py:673`) calls the workload declaration a "fixture". *low*
- `v1_bridge` names a past engine rather than the job (Program Values to manifest identity rows). *low*

**DOCS (8)**
- `query/__init__.py:6-11` lists a `correspondence` module inside `query/` (moved to `correspondence/reader_for_query.py`); `:18-20` points the narrative to a Notion page. *low*
- `query/partition.py:33-36, 148` cite "gateset.py, INTERFACE NOTE of 21:20Z" and `out/gen/window/qpart.md` (does not exist); `:643` "absent until lane/q-boundary is merged". *medium*
- Stale references to the deleted `required_manifest.py`: `query/cli.py:1, 55`; `query/manifest/compiled.py:4, 24-25`; `query/manifest/verify.py:14`. *medium*
- `query/manifest/format.py` carries about 20 notebook tags: `[R15 tp TP-04]`, `M-0247`, `M-0254`, `F-r17b-52`, `F-r19-int-20`, `[R14 moe]`, `COORD R15 ruling 2`, `MAN-01 c41cae46a`, `F-rel-01`, `rev-cb M-0108`, `[R17 reqval finding 7]`, `revb M-0143`, `[MAN-02]`, `[R15 B8]`, "the wire lane saw exactly that on #57". *medium*
- `query/manifest/compiled.py:1, 176, 183, 559, 568` "R15 compiled", "DECISIONS-2 §3", "[R16 compiled, Qwen row]", "[rev-pm F-pm-29 / M-0687]", "MAN-09", "rev-cb M-0655 W2". *low*
- `query/vu_query.py:3` "Gate G5 (D82)"; `query/program_view.py:21-22` "F-r19-int-25", "#11"; `query/v1_bridge.py:6` "F-r19-int-20"; `query/boundary.py:12` "design report v2 §5"; `query/manifest/verify.py:11-13` "rev-cb F-cb-11", "EXEC-05". *low*
- README layer table rows for query/correspondence cite files that moved or never existed here (`check/poc_required_interface.py`, `observe/vu_canonical.py`, `experimental/cb_a/batch_decomp.py`). *low*
- Long prose constants emitted into records (`TP_PEER_BINDING_RULE`, `PROMOTED_OBSERVATION_RULE`, `NAMED_RESIDUALS[*].why`) double as design notes. *low*

**FALLBACKS (6)**
- `query/partition.py:500-504, 511-514, 649-653` `except Exception: return None`: a Family whose `tiling()` or `count()` raises is silently swept; `index_of` failures silently become `None`. *medium*
- `query/program_view.py:709-714` on an out-of-order stream silently re-reads the whole file with `json.load`, the tens-of-GB path its own docstring warns about. *medium*
- `query/v1_bridge.py:460` silent default compute capability `[8, 9]` when `result.json` has no target. *medium*
- `query/manifest/format.py:110-111` `wrapper_prefix_of` silently returns `"model."` when nothing matches. *medium*
- `query/query_artifact.py:47-50` `except ImportError: return None` around core `verity.ir.query_ast`, which is a hard dependency. *low*
- `query/cli.py:63-67`, `query/manifest/format.py:659-664` `except Exception: continue` on unreadable `result.json`; `query/cli.py:149` broad except around the manifest build. *low*

**OTHER-WEIRD (5)**
- `query/manifest/compiled.py:103-209, 271-333` regex-parses generated Python (Inductor `call()` bodies, `async_compile.triton` blocks, `print_readable()` split graphs). Fragile and version-coupled. *high*
- `query/program_view.py:550-569` populates the global Definition registry by importing a hardcoded module list via `importlib` (registration side effects), with module-level `_REGISTRY` / `_PORTS_CACHE` dicts. *medium*
- `query/program_view.py:622-687` hand-rolled streaming JSON parser that scans raw text for `"rows"` and relies on the writer's key order. *medium*
- Module-level mutable caches: `query/boundary.py:363, 818-820` (WeakKeyDictionaries), `query/vu_query.py:705` (`_CACHE` keyed by `id(result)`), `query/partition.py:637` (`_BOUNDARY` test hook). *low*
- `query/v1_bridge.py:103-130` data table rows carry multi-sentence prose that is emitted into every manifest header. *low*

Counts for `query/`: CORE-DUP 5, INTERNAL-DUP 6, VERSION-RESIDUE 7, HARDCODING 7, SCRIPT/ENV/PATH 5, LAYERING 7, GOD-MODULE 5, DEAD 3, NAMING 5, DOCS 8, FALLBACKS 6, OTHER-WEIRD 5.

---

## 2. `correspondence/` (13 files, 5,602 lines)

**What it actually does vs its name.** The name promises the Program-to-runtime correspondence: for each Call, which runtime occurrence (module, fx node, tensor slot) holds its Value. Only 4 modules (about 1,370 lines) do that: `runtime.py` (the `runtime-correspondence/v1` record), `emit.py` (writes it during lowering) and the two readers. The other 9 modules (about 4,230 lines) were parked here by the package move (`tools/move_map.txt`) from `verity_capture/`, `experimental/cb_a/`, `acquire/` and `frontend/`:
- Match-stage checking at batch > 1: `batch_decomp.py`, `resolve_decomp.py`, most of `resolve.py`.
- Runtime observation: `chunk_attribution.py` (reads vLLM's scheduler), `runtime_tree.py`.
- Replay verification of committed capture leaves against the hand-built B1 registry Program: `capture_identities.py`, `capture_identities_program.py`.
- A lane diagnostic that renders markdown: `batch_candidate.py`.

### Modules

| module | lines | job |
|---|---:|---|
| `__init__.py` | 1 | empty |
| `runtime.py` | 554 | `runtime-correspondence/v1` JSON schema, per-Call records (`CallCorrespondence`, `ReturnSlot`, `ArgSlot`, `CollectiveOccurrence`), digest, the one loader `read_program_dir`, a streaming reader for the descriptor's `annotations`, a stdlib validator |
| `emit.py` | 415 | frontend-side emitter run by `program/frontend/derive.py:552`: maps each Call to its fx node, locates return and argument Values as leaf ranges, records lifetime facts and collectives |
| `reader_for_query.py` | 187 | query's reader: the record, else the `v1_annotations` naming-hint fallback; `parse_call_name`; wrapper prefix by suffix match against `attention_impls_observed` |
| `reader_for_acquire.py` | 218 | acquire's reader: the record, else the `v1_annotations` fallback; wrapper prefix by vote against the runtime tree; hook `ReturnSlot`/`ArgSlot`; in-place lifetime facts |
| `runtime_tree.py` | 131 | the runtime's module tree (MRO names, buffers, runner facts) from a live engine or a meta-instantiated model; CLI run by `ops/pod_gate.sh:59` |
| `resolve.py` | 661 | occurrence resolution: runtime observation to (request, step, site, slot, ordinal, Call); a third reader `DescriptorCorrespondence`; `LiveState`; `validate`; whole-record `attribute_record` |
| `resolve_decomp.py` | 270 | re-runs the batch decomposition through `resolve` and compares it field by field with `batch_decomp`'s `match_decomp.json` (old path vs new path) |
| `batch_decomp.py` | 916 | Match at batch > 1: capture-log reader, request attribution, per-request `Projection` of the eager fold, comparison with the derived request Program, DAG criterion, profiling, CLI run by `ops/row_pod.sh:610` |
| `batch_candidate.py` | 457 | diagnostic markdown report on a frozen fold (KV sources, prompt consumption, returned tokens) |
| `chunk_attribution.py` | 356 | reads vLLM's in-process V1 scheduler after each `step()` to attribute prefill chunks and token-producing forwards; repairs the run's `timing` record in place |
| `capture_identities.py` | 882 | replay check of capture-format-v2 leaves against the hand-built B1 circuit: safetensors weights binding, commit-store reader, region recomputation, port loader, CLI |
| `capture_identities_program.py` | 554 | Program-source loader (`registry:`/`python:`/`descriptor:`), vocabulary pin, record pins and binding check, structural B1 circuit map, GemmCoordinate to `tc-ampere-bf16` subcircuit lowering |

### Findings

**CORE-DUP (5)**
- `correspondence/emit.py:35-77` `_runs` re-implements `verity.ir.refs.runs` (`packages/.../ir/refs.py:234`) with a run budget (its docstring says so). Add `max_runs` to core `runs`. *medium*
- `correspondence/capture_identities_program.py:480-538` `TC_LOWERING_RULES` and `lower_call_to_subcircuit` hand-lower a GemmCoordinate call to a typed-obligation subcircuit over `tc-ampere-bf16@2`. Core owns gate-set lowering (`packages/.../verification/lowering.py`, `gateset.py`); only `make_subcircuit` is reused. *medium*
- `correspondence/capture_identities_program.py:302-333` `binding_check` is a second binding check (program digest, LP/STEPS, vocabulary, profile) beside core `verification/binding.check_binding` (`packages/.../verification/binding.py:168`). The scopes overlap only partly. *low*
- `correspondence/runtime.py:319-320` `canonical_json` is byte-identical to core `packages/.../ir/codec.py:317-318`. *low*
- `correspondence/batch_candidate.py:353-363` `_ret_runs` re-implements the private core `codec._decode_refs` alias/concat resolution (`packages/.../ir/codec.py:452-469`). *low*

**INTERNAL-DUP (10)**
- Three readers carry the same two-source adapter (the record, else `v1_annotations`): `correspondence/reader_for_query.py:113 Correspondence`, `correspondence/reader_for_acquire.py:86 AcquireCorrespondence`, `correspondence/resolve.py:114 DescriptorCorrespondence`, all over `runtime.RuntimeCorrespondence`. `resolve.py:117` says so: "the same shim shape as". *high*
- Three rules infer the export wrapper prefix: `correspondence/reader_for_query.py:90 implementation_prefix` (suffix match against observed attention paths), `correspondence/reader_for_acquire.py:67 infer_wrapper_prefix` (vote against the runtime tree), `query/manifest/format.py:100-111 wrapper_prefix_of` (falls back to `"model."`). `resolve.py:152,156` uses one or the other depending on the source. *high*
- Request attribution is implemented twice: `correspondence/batch_decomp.py:589-674` (inline loop) and `correspondence/resolve.py:391-437 attribute_request`, which says it "wraps rather than restates" but re-codes the channel order meta, dataflow, weight-only, rows. *high*
- The per-request leg (Projection, shape, `compare_steps`, divergence report) is copied: `correspondence/batch_decomp.py:716-818` and `correspondence/resolve_decomp.py:125-181`; `resolve_decomp.py:31-44 _owned_layout` repeats `batch_decomp.py:570-585`. *high*
- Three parsers of the naming hint `<module>/<fx>[/<member>][<row>]`: `correspondence/emit.py:164 _member_row`, `correspondence/reader_for_query.py:55 parse_call_name`, `query/manifest/format.split_name`. *medium*
- Two hand-written streaming JSON readers: `correspondence/runtime.py:359-453` (`_Stream`, `_walk`) and `query/program_view.py:622-687`. *medium*
- Three safetensors readers: `correspondence/capture_identities.py:269`, `check/fold_compare.py:285`, `input_provenance/weights_of_record.py:104`. Two cos/sin table builders: `correspondence/capture_identities.py:287` and `input_provenance/analytic.py:378`. *medium*
- `correspondence/capture_identities_program.py:182-213 vocabulary_version` re-implements `program/frontend/provenance.registry_version` over a fixed subset (`registry.prims` + `registry.b1`); `provenance.py:45` notes they share a schema. *medium*
- Build-dir globs `build_request*` and `build/rank*/build_request*` appear again at `correspondence/resolve_decomp.py:248-251` (third copy, after `query/cli.py:54-75` and `query/manifest/format.py:646-671`). *low*
- `correspondence/chunk_attribution.py:61-71 scheduler_of` duplicates `observe/engine_profile.py:207 get_scheduler` (its docstring says "as"). *low*

**VERSION-RESIDUE (6)**
- The `v1_annotations` source and fallback in every reader: `correspondence/reader_for_query.py:42,131-134`, `correspondence/reader_for_acquire.py:36-37,105`, `correspondence/resolve.py:154-156`; `runtime.py:487-489` calls a Build without the record "a v1-frontend Build". *medium*
- `correspondence/reader_for_acquire.py:215` `AnnotationCorrespondence = AcquireCorrespondence  # the adapter's former name`, used only by 4 test files. *medium*
- The old-vs-new migration harness: `resolve.py` / `resolve_decomp.py` "v2 Phase 4b", `resolve.py:647 compare_attributions(v1, v2)`, `resolve_decomp.py:193 compare_with_record(v2, record)`, result keys `only_v1` / `only_v2`. *medium*
- Experiment ids in hook and env-var names: `correspondence/batch_decomp.py:451 X09_LEGS`, `:460 X09_PROFILE_OUT`, `X09_FORCE_DAG`; `:445` "`sequence` is the r14-v1 criterion". *medium*
- B0/B1 case names as API: `correspondence/capture_identities.py:680, 687, 858` (`config="B1"`, `{"B1": b1.B1_CONFIG, "B0": b1.B0_CONFIG}`, `--config B1|B0`, `Port.id="b1"`), `correspondence/capture_identities_program.py:116-121` (`registry:B0|B1`), `:353 requalify` (migrates `verity-ir/correspondence/v0` records). *medium*
- `correspondence/runtime_tree.py:24` `RUNNER_PATH = "runner.sampler"  # v1's path`; `correspondence/reader_for_query.py:150-155 site_path` "the v1 frontend's spelling". *low*
- LEGIT (serialized): `runtime-correspondence/v1`, `verity-vllm/runtime-tree/v1`, `verity-vllm/resolve-decomp/v1`, `cb-a/batch-decomp/v1` (written into `match_decomp.json`; the `cb-a` prefix names a dissolved experiment directory), `cb-a/x09-profile/v1`, `verity-ir/correspondence/v0`, `verity-ir/registry-version/v0`, `capcorr.tc-lowering` v1, gate set `veritor.tc-ampere-bf16@2`.

**HARDCODING (7)**
- `correspondence/emit.py:30, 318-325` recognises only the binary collectives `verity_tp::all_reduce2` / `all_gather2`, takes `operands[:2]` and sets the peer as `1 - own_i`. The world-size-2 assumption is baked into the correspondence emitter, and the n-ary `verity_tp::all_reduce` / `all_gather` used for world > 2 (`tp/export_ops.py:60-80`) silently get `collective: null`. *high*
- `correspondence/capture_identities.py:67-82 _LAYER_OPS` (Llama-family op suffixes), `:746-752` (`qkv_proj.add` / `qkv_proj.gemm`, `down_proj.gemm`, `post_attention_layernorm.rmsnorm`), `:851` `--layers` default `[0, 1, 13, 27]` (layer indices of one 28-layer model), `:856` `[MAX_POS,128]`. Not in the by-name allowlist; `_LAYER_FIELDS` / `_WEIGHT_FIELDS` (`:243-255`, HF checkpoint names such as `model.layers.{L}.self_attn.q_proj.weight`) are allowlisted with `retires: P4W`. *high*
- `correspondence/capture_identities_program.py:341-400 StructuralCircuitMap` assumes the `Serve_v1` root-call shape (`Embedding`, `LayerPre`, `Attention`, `LayerPost`, `Final`). *medium*
- `correspondence/capture_identities_program.py:480-527` Ampere tensor-core lowering (`AmpereBF16TcDot16`, `tc-ampere-bf16`) inside correspondence. *medium*
- `correspondence/chunk_attribution.py:61-71, 146-158` reaches `llm.llm_engine.engine_core[.engine_core].scheduler` and strips vLLM's internal `-{8 hex}` request-id suffix ("pinned wheel 0.28.1rc1"): vLLM-version internals. *medium*
- `correspondence/resolve.py:183` magic slot names `("0", "1", "in", "sampled_token_ids")`; `:47 _LAYERS_RE` reads `layers.<k>` out of names; `correspondence/reader_for_acquire.py:173` special-cases `RUNNER_PATH`. *medium*
- `correspondence/batch_candidate.py:136, 168-169, 195, 233` spec-prefix predicates (`Embedding_v`, `Attention_v`, `TokenSelect_v`, allowlisted P3), operand names `["q", "kc", "vc"]`, `[None] * 999`; `correspondence/batch_decomp.py:158-163` the MoE pair-row rule, justified by one OLMoE count. *low*

**SCRIPT/ENV/PATH (6)**
- `__main__` + argparse in 5 of 13 library modules: `runtime_tree.py:110-131`, `resolve_decomp.py:238-270`, `batch_decomp.py:893-916`, `batch_candidate.py:440-457`, `capture_identities.py:841-882`. *medium*
- `os.environ` in library code: `correspondence/batch_decomp.py:460-466, 547, 886` (`X09_PROFILE_OUT` changes output side files; `X09_FORCE_DAG` changes which fields are emitted). *medium*
- `correspondence/batch_decomp.py:912` exit codes 0 / 3 / 4 exist so `row_pod.sh` can derive missing shapes and rerun. *low*
- Paths in docstrings and help text: `batch_candidate.py:17-18` (`out/gen/lanes/ov-batch/runs/...`, `workloads/workload_b0_prefix64_2req.json`), `capture_identities.py:636, 860` (`vllm-poc/profiles/<port>/static_config.py`, which does not exist). *low*
- Library code executes external `static_config.py` files: `capture_identities.py:656-674 Port.load`, `capture_identities_program.py:123-135`. It also prints progress: `capture_identities.py:716, 726, 783, 829`. *low*
- Unclosed `open()`: `batch_decomp.py:426, 431, 889, 905`; `resolve_decomp.py:255`; `capture_identities_program.py:168`. *low*

**LAYERING (8)**
- correspondence imports check, and check imports it back: `correspondence/batch_decomp.py:59` (`Projection` subclasses `check.program_compare.Prog`), `correspondence/resolve_decomp.py:23`; `check/global_match.py:85`, `check/global_match_fast.py:32`, `check/oracle_compare.py:569`, `check/sampled_replay.py:313` import correspondence. *high*
- correspondence imports observe, and observe imports it back: `correspondence/resolve.py:44`, `correspondence/resolve_decomp.py:25` (`observe.contract`); `observe/contract.py:165` (`batch_decomp`), `observe/vllm_adapter.py:66` (`chunk_attribution`). *high*
- correspondence <-> query cycle: `correspondence/reader_for_query.py:38` imports `query.program_view`; `reader_for_acquire.py:32` and `resolve.py:110, 133` import `query.manifest.format`; query imports `correspondence.reader_for_query` (`module_body.py:25`, `v1_bridge.py:54`, `cli.py:25`). *medium*
- correspondence <-> program cycle: `correspondence/emit.py:24, 205` imports `program.frontend.torch_frontend` and, lazily because "derive imports this module", `derive._mutates` / `fx_arg_nodes`; `program/frontend/derive.py:552` imports `emit`. `emit.py` reads a dozen private fields of derive's `Ctx`: it is lowering code. *medium*
- `program/global_program.py:52` imports `correspondence.batch_decomp.derived_shape`, so program depends on the Match module to read a Build dir. *medium*
- `correspondence/capture_identities.py:40`, `capture_identities_program.py:116, 192` import the hand-built `program.registry.b1` / `prims`. *medium*
- Private names across modules: `capture_identities_program.py:49, 553` imports and re-exports `_returns_component`, `_select_child`; `check/fold_compare.py:367` imports `capture_identities._LAYER_FIELDS/_WEIGHT_FIELDS`; `resolve.py:140` calls `RC._document_of`. *low*
- Run artifacts read by correspondence: `reader_for_query.py:181-187` (`result.json` `attention_impls_observed`); `capture_identities_program.py:248-299 record_pins` reads a certified record (`program/program.json`, `certificate.json`, `manifest.json`, `summary.json`, `bundle/bundle.json`), which is verifier binding work. *medium*

**GOD-MODULE (4)**
- `correspondence/batch_decomp.py` (916) does 11 jobs: capture-log reader with a regex fast path; request/parameter layout; row-count attribution (including MoE pair rows); weight-only sharing; weights Input-node layout validation; `Projection` (canonicalisation with cross-request detection, run and progression forms); live cone and DAG hashing; Build-dir shape discovery over three file formats; a profiling harness (env vars, monkeypatched counters, RSS); the decompose driver with a fork hook; CLI with shell exit codes. *high*
- `correspondence/capture_identities.py` (882) does 13 jobs: capture-id grammar; B1 layer-op table and locator; value segments and lazy transcript; safetensors reader; vLLM cos/sin re-implementation; weights binding with sha256 checks; v0 record requalification; commit-store reader; shape check; region recomputation; call check with coordinate sampling; port loader; driver and CLI. *high*
- `correspondence/resolve.py` (661, under the threshold) does 7 jobs: contract types, a correspondence reader, a component-Program index, live state, request attribution, validation, whole-record attribution and comparison. *medium*
- `correspondence/capture_identities_program.py` (554) does 7 jobs: Program loader, vocabulary pin, record pins, binding check, structural map, value address, tensor-core lowering. *medium*

**DEAD (6)**
- `correspondence/batch_candidate.py` (457): imported only by `tests/observe/test_gen_ovbatch.py` and `tests/program/test_compact.py:453`; `tests/dead_code_keep.json:6` keeps it as a "fixture generator"; `tools/move_map.txt:348` marks it `DELETE-BY:vllm-dead-code`. *high confidence* (searched absolute and relative imports, `-m` in `.sh`, string references, keep-list)
- `correspondence/capture_identities_program.py` (554): only `tests/program/test_derive_negative.py:1050` (`importorskip`, reason "not merged yet") and a comment in `program/frontend/provenance.py:45`; `move_map.txt:796` `DELETE-BY:vllm-dead-code`; keep-list `:28`. *high confidence*
- `correspondence/capture_identities.py` driver (`run`, `main`, `Port`, `CommitStore`, `Recomputer`, `bind_weights`, `requalify`): no shell or production caller. The only production importer is `check/fold_compare.py:367` (two tables), and `fold_compare` is a stage `row_pod.sh` skips (`tests/dead_code_census.py:69 RUN_CONFIG_SKIPPED_STAGE_MODULES`). Tests use `LazyTranscript`, `Segments`, `check_call`, `_shape_ok`, `_coll_range`, `requalify`. *medium confidence* (imports, `-m`, strings, census skip list)
- `correspondence/resolve_decomp.py` (270): run only by `tests/regression/checks/decomp_hashes.py:99`; no shell entry. A migration check. *medium confidence*
- Test-only helpers: `resolve.py:647 compare_attributions`, `reader_for_acquire.py:215 AnnotationCorrespondence`, `:61 read_program_correspondence` (a pure alias of `read_program_dir`), `runtime.py:294 calls_under`, `:516 validate_document`. *medium confidence*
- References to paths that no longer exist: `capture_identities.py:636, 860` (`vllm-poc/profiles`), `:684` (`verity_vllm.check.poc_conformance`), `capture_identities_program.py:33, 492` (`veritor.interface...`), `resolve.py:122` (`query.correspondence.implementation_prefix`, moved), `resolve_decomp.py:2` (`cb_a.batch_decomp`), `reader_for_acquire.py:15, 38` (`required_manifest.split_name`, deleted). *high confidence*

**NAMING (6)**
- Two `ReturnSlot` and two `ArgSlot` classes with different fields: `correspondence/runtime.py:129, 150` (leaf-range location) vs `correspondence/reader_for_acquire.py:41, 54` (hook slot index / attribute). `acquire/plan.py:35` imports the second; tests import both. *medium*
- Six `*Correspondence` types: `reader_for_query.Correspondence` (class), `resolve.Correspondence` (Protocol), `AcquireCorrespondence`, `DescriptorCorrespondence`, `RuntimeCorrespondence`, `CallCorrespondence`. *medium*
- "attribution" has three meanings: request ownership of fold instances (`batch_decomp.attribute`; `batch_decomp.py:7` admits the glossary calls it occurrence resolution), prefill-chunk accounting (`chunk_attribution`), and a lane file `attribution.json` (`batch_candidate`). *medium*
- "oracle" means the eager fold (`batch_decomp --oracle`, `load_oracle`, `oracle_rows`). "profile" means capture profile (`CaptureIdentity.profile`), "profile port", semantic profile and timing profile (`X09_PROFILE_OUT`). *low*
- `resolve.py:94 Program` (a Protocol) shadows core `verity.ir.program.Program`. *low*
- `capture_identities` / `capture_identities_program` name the input format, not the job (replay check of capture leaves against a registry Program). *low*

**DOCS (6)**
- `correspondence/batch_decomp.py` is the densest lab-notebook file in the slice: `M-BATCH-DECOMP, R13 X-09`, `[R14 moe]`, `[R15 stoch]`, `[R16 global, F-fp8-GM1 / M-0823]`, `[R17 D90]`, `[R17 mfast]`, `[R18 x09, F-r18-x09-1]`, `[R19, F-r19-int-15]`, `COORD M-0169 (4)`, `COORD ruling M-0177 on DECISION M-0021`, `r15-int-2`, `BRIEF §5 step 3`, `GM-01`, "#57 B8 1024/128", "87 GB on cp-dev1", a Notion pointer. *medium*
- `correspondence/chunk_attribution.py:1-53, 165-174`: "window 2026-09-17", `D87`, "lane/coverage (integ, 22:12Z)", "run 0917T213719-880581", `rev F-r17-16 / R17-1`, "exec r17_2216", `GM-01 G6`, `G1/G2`. *medium*
- `correspondence/capture_identities*.py`: "IR §C.5", "TA1", "QZ", "CF2", "CH", "W1cF", "typed-b1.md §5.2", "GUIDANCE §18.7 / §43.1 / §43.5 S4-S5 / §44.1", "lane CAPCORR", "lane DERIVE", "mandate boundary 6", "merge 2026-09-08". *medium*
- `correspondence/resolve.py`, `resolve_decomp.py`: "v2 Phase 4b", `X-09`, `G2`, `F-r19-int-14/15/20`, "Draft 3.1 §12.4", "R19 record". *low*
- `correspondence/runtime_tree.py:10-11` "m1_capture's runtime_tree.json on the l40s b64 reference row, 2026-09-23"; `batch_candidate.py:1-20` "GEN ov-batch lane", `D85`, "RULES §1"; `emit.py:11` "stated in the lane report". *low*
- Stale references (listed under DEAD). *medium*

**FALLBACKS (6)**
- Every reader falls back from the record to naming-hint parsing. `reader_for_acquire.py:143-145` drops all tables when one component Program lacks the record; `resolve.py:142-145` drops a record whose Call count mismatches. The choice is recorded in provenance, so it is not silent, but four readers carry it. *medium*
- `correspondence/batch_decomp.py:421-436 derived_shape` tries `construction_manifest.json`, then `artifact.json`, then `derive-report.json`, reading `structural_inputs`, `shape` or `provenance.*`. *medium*
- `correspondence/chunk_attribution.py:70, 92, 107` `except Exception` around scheduler reads; two sources (scheduler state vs outputs); a correction that is applied and then possibly reverted (`:231-345`). *medium*
- `correspondence/runtime.py:501-502 read_program_dir` treats a Build without `correspondence_digest` as having no record, and reports no problem. *low*
- `correspondence/resolve_decomp.py:54-69` runs without the archived capture log; the rows channel and the meta-vs-rows cross-check are then off (recorded in `log_state`). *low*
- Broad or silent excepts: `emit.py:93`, `batch_decomp.py:885`, `runtime_tree.py:79-80`, `capture_identities_program.py:450-451` (silently skips the prompt dataflow check for decoded Programs). *low*

**OTHER-WEIRD (8)**
- `correspondence/batch_decomp.py:500-520` monkeypatches `check.program_compare.Prog._per_run/_srcP/_src` with counting wrappers. The patch is process-global and never removed. *high*
- `correspondence/batch_decomp.py:451` `X09_LEGS = None` is a module-level hook that `check.global_match_fast` overwrites to fork the per-request legs; `:469` reads `sys.modules` for `global_match_fast.stats`. *medium*
- `correspondence/capture_identities.py:510, 550, 576` finds the missing gate by regex over core `MissingValue`'s message text (`packages/.../ir/evaluate.py:38, 44`). Core should carry the gate as an attribute. *medium*
- `correspondence/chunk_attribution.py:165-356 attribute` mutates the caller's `timing` dict in place and may revert its own edits. *medium*
- `correspondence/reader_for_query.py:181-187` takes the collector's module vocabulary from `attention_impls_observed` keys, so only attention modules are seen. *medium*
- `correspondence/capture_identities.py:830-837` rewrites the output file inside the per-record loop (quadratic I/O), and with no located records `out` is unbound at `return out` (`:838`). *low*
- `correspondence/capture_identities.py:876-881` the `__main__` block re-imports its own module so exception classes are single objects; `emit.py:229` detects constants by `type(v).__name__` strings. *low*
- `correspondence/batch_decomp.py:733`, `resolve_decomp.py:136` set `_all_seed_nodes` on a `Projection` after construction; `reader_for_acquire.py:177-178 arg_slot` ignores the Call and never consults the record. *low*

Counts for `correspondence/`: CORE-DUP 5, INTERNAL-DUP 10, VERSION-RESIDUE 6, HARDCODING 7, SCRIPT/ENV/PATH 6, LAYERING 8, GOD-MODULE 4, DEAD 6, NAMING 6, DOCS 6, FALLBACKS 6, OTHER-WEIRD 8.
