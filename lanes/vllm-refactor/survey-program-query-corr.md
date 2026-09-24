---
id: vllm-refactor/survey-program-query-corr
lane: vllm-refactor
kind: survey
status: complete
created: 2026-09-24
checkout: f0810a11 (lane/vllm-cleanup-2)
slice: integrations/vllm/verity_vllm/{program,query,correspondence}
---
# Survey: program/, query/, correspondence/

Read-only survey against `/Users/danielreuter/projects/verity` at `f0810a11`. Evidence is `rg`, `git grep`, `git log`, `wc` and reading.

**Deviation from the brief.** Python was run, read-only, against the checkout: `tests/dead_code_census.py` (module liveness, several times) and two short import probes (to confirm the core/integration Definition-id collision and the `_LAZY_PRIMITIVE_FAMILIES` rebinding, both under program/ CORE-DUP and OTHER-WEIRD). No tracked file changed and `git status` is clean at `f0810a11`. The runs probably wrote gitignored bytecode caches: 32 `.pyc` files under `__pycache__/` in `integrations/vllm` and `packages/verity/src` are newer than 10 hours. They were left in place. Liveness claims below were re-derived with `rg` and do not depend on the census output.

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
- 11 modules read `os.environ` (10 in `program/`, 1 in `correspondence/`). `program/frontend/vllm_meta.py` also *writes* 5 env vars with `setdefault` at import.
- verity core imports: mostly `verity.ir.{defs,refs,types,codec}`. Only `query/module_body.py`, `query/program_view.py`, `query/v1_bridge.py` import `verity.verification.query`; `correspondence/capture_identities_program.py` imports `verity.verification.{programs,typed_obligation}`. Nothing imports `verity.commitments` or `verity.verification.plan`.

Sections: 1 `query/`, 2 `correspondence/`, 3 `program/`, 4 slice-specific maps (core usage, registry, lowering, collectives), 5 disposition table.

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

---

## 3. `program/` (119 files, 36,252 lines)

**What it actually does vs its name.** The name suggests "build the Program". The package holds five different things:
1. **The Definition library** (`registry/`, 59 files, 14,467 lines). This includes:
   - composites hand-authored for four named models on two GPU families (`b1.py`, `b1_tp2.py`, `hopper.py`, `fp8.py`, `moe.py`, `spec.py`, `dense.py`);
   - the primitive set (`prims.py`, `ref_prims.py`, `pad_prims.py`);
   - the lifted padded programs (`lifted.py`, `serve3.py`, `moe_pad.py`);
   - target tables (`targets.py`, `gemm_targets.py`);
   - numpy twins of Definitions (`derived_rows.py`, `sampling_rows.py`, `serve3_reference.py`);
   - an exact model of vLLM's top-p pipeline (`topp_split.py`, `sampling.py`);
   - conformance data, two difftest adapters, a sweep script, and `quarantine/`.
2. **Lowering** (`frontend/`, 31 files, 14,001 lines). Two paths produce Programs:
   - an authoring API (`torch_frontend.py`), used by tests and `b1_authored.py`;
   - derivation from `torch.export` of the real vLLM model classes (`derive.py` plus 7,339 lines of `rules/`).

   Around them sit vLLM instantiation and monkeypatch shims (`vllm_meta.py`, `export_compat.py`, `triton_capture.py`), the applicability contract (`target_profile.py`) and three generic IR analyses (`liveness.py`, `correspond.py`, `provenance.py`).
3. **Independent numerics** (`numerics/`, 17 files, 4,176 lines, plus 3 C++ models JIT-compiled with `g++` and 4 CUDA probe sources). These are CPU bit-models of vLLM kernels (FA2, FA3, RMSNorm, GEMM, Inductor kernels, the Gumbel sampler). They register into `check.relations` at import. Two GPU probe scripts live here too.
4. **Workload construction** (`global_program.py`, `workload.py`, `lifting/`; 2,023 lines). A CLI driver assembles the multi-request workload Program from Build directories. This group also holds the continuation logic of the padded Program.
5. **Storage and tooling** (`compact.py`, `instances_form.py`, `descriptor_equivalence.py`, `profile_descriptor.py`, `dtypes.py`, `sampling_event.py`). These cover instance-file encodings, two descriptor CLIs, and a dtype helper that only `commit/` uses.

### Modules

Top level and `lifting/`:

| module | lines | job |
|---|---:|---|
| `__init__.py` | 1 | empty |
| `global_program.py` | 844 | GP-01 CLI: the workload Program of a declared manifest from derived request-wrapper Programs; compilation facts, EOS lag, MoE construction, sampler geometry, stop rule, weights binding |
| `workload.py` | 610 | the workload Program: one rooted Program over the declared requests |
| `compact.py` | 556 | operand references as run progressions (instances v2 form); used by `check/`, `correspondence/`, `tp/` |
| `descriptor_equivalence.py` | 442 | CLI: denotational comparison of two encodings of one program (definitions, gates, calls, boundaries, sampled evaluation) |
| `profile_descriptor.py` | 291 | CLI: byte profile of a serialized descriptor by field |
| `dtypes.py` | 150 | torch dtype strings, item sizes, exact BF16<->f32 in numpy (used only by `commit/hashing.py`) |
| `instances_form.py` | 119 | `instances.jsonl` stored forms (runs vs progressions) and a converter CLI |
| `sampling_event.py` | 26 | the three sampling-event Definition families and `family_of` |
| `lifting/__init__.py` | 1 | empty |
| `lifting/continuation.py` | 481 | `Continuation_v1`: the emit/run Boolean chain of the padded Program and its host-side evaluation |
| `lifting/dump.py` | 87 | per-gate dump of the reference evaluator's assignment of a lifted Program |

`frontend/`:

| module | lines | job |
|---|---:|---|
| `__init__.py` | 24 | conditional re-export of `torch_frontend` (pure-IR use without torch) |
| `torch_frontend.py` | 1,340 | authoring API (`function`, `bind`, `batch`, `scan`, `Ops`, custom-op minting) plus the Coll/Type/view helpers that derive and the rules import |
| `derive.py` | 1,012 | derivation engine: `torch.export` a module, translate fx nodes through rules into a Program, report and provenance, emit correspondence |
| `vllm_meta.py` | 559 | instantiate the pinned vLLM model class on `meta` through vLLM's config and registry; fake forward context; TP rank wrapper with peer inputs; sets env vars at import |
| `export_compat.py` | 298 | shims that let `torch.export` trace pinned vLLM: patches `Tensor.data`, platform capability, `num_compute_units`, tuned-GEMM caches, MoE dispatcher ops |
| `target_profile.py` | 626 | `TargetProfile` / `ArtifactIdentity`: the applicability contract and artifact digest; defaults to sm_89 with 128 SMs |
| `triton_capture.py` | 118 | patch `triton.runtime.jit.JITFunction.run` during export so direct Triton launches become opaque graph nodes |
| `inputs_trace.py` | 67 | `sys.addaudithook` that logs every file opened during construction (record-freeness evidence) |
| `liveness.py` | 444 | dead gates of a Program: hierarchical liveness with interval sets (generic IR analysis) |
| `correspond.py` | 331 | Program correspondence across reference encodings (generic IR analysis) |
| `provenance.py` | 120 | `registry_version()` and derivation-rule provenance records |
| `b1_authored.py` | 668 | the B1 serving program authored through `torch_frontend` (its only importer is the test-only `serve3_authored.py`) |
| `serve3_authored.py` | 107 | `Serve@3` authored through the frontend (test-only) |
| `examples.py` | 218 | authored frontend examples (test-only, via `derive_examples.py`) |
| `derive_examples.py` | 730 | plain torch modules shaped like vLLM's, for derivation tests (test-only) |

`frontend/rules/`:

| module | lines | job |
|---|---:|---|
| `__init__.py` | 56 | `DEFAULT_RULES`; lazy loading of the concrete rule sets |
| `base.py` | 156 | rule base classes (`ViewRule`, `OpRule`, `InPlaceRule`, `StateRule`), `RuleInfo`, `RuleSet` |
| `common.py` | 51 | shared rule helpers |
| `vocab.py` | 343 | four kind vocabularies (`b1-eager`, `b1-eager-v2`, `b1-eager-v3`, `dense2-eager-v1`) binding semantic roles to registered Definitions |
| `vllm_bindings.py` | 1,905 | about 30 per-op rules for `torch.export` graphs of real vLLM classes (Triton GEMM/RMSNorm, KV cache, attention, dense elementwise, unfused norm chain, FP8, TP collectives), plus kernel source pins and process-global observations |
| `vllm_moe.py` | 865 | rules for the leaf kernels of vLLM's fused-MoE block |
| `vllm_sampling.py` | 135 | rule for the stochastic token select |
| `vllm_iface.py` | 96 | vLLM's `torch.ops._C.*`, or a stand-in library with the same schemas when vLLM is absent |
| `triton_iface.py` | 42 | defines the `verity_cba::triton_launch` op |
| `profile.py` | 505 | profile-mode rules binding vLLM-shaped modules to the B0/B1 kinds |
| `reference.py` | 879 | reference-mode op rules (f32/bf16 torch ops to `ref_prims` kinds) |
| `patterns.py` | 764 | multi-node pattern rules (a decomposed computation bound to one Definition), used by `reference.py` |
| `views.py` | 519 | view rules: reference rearrangements, static index tensors, allocations |
| `padding.py` | 394 | padded-serving rules (`Serve@3`) |
| `family.py` | 591 | claims a registered program identity for a derived flat Program by isomorphism |
| `ref_kinds.py` | 38 | width-conversion composites for reference mode |

`numerics/`:

| module | lines | job |
|---|---:|---|
| `__init__.py` | 14 | docstring |
| `_jit.py` | 99 | atomic, lock-serialized `g++` builds of the C++ twin libraries at first use |
| `mma.py` | 143 | per-instruction Ampere `mma.sync.m16n8k16` models (BF16 through core `silicon`; FP16 local) |
| `cpu_model.py` | 214 | ctypes wrapper of `cpp/tc_model.cpp` |
| `relations.py` | 528 | `independent` GEMM relations; registers into `check.relations` at import |
| `kernel_zoo.py` | 146 | A100 cuBLAS launch signatures for Qwen2.5-1.5B shapes and the model that reproduces each |
| `fa2_model.py` | 310 | CPU model of vLLM's FA2 forward (JIT C++) |
| `fa2_relation.py` | 267 | `attention.bf16.v1` relation; registers at import |
| `fa3_model.py` | 234 | CPU model of the FA3 forward on Hopper |
| `rms_triton_model.py` | 279 | CPU models of the two RMSNorm kernels (JIT C++) |
| `rms_relation.py` | 186 | `rmsnorm.*.bf16.v1` relations; registers at import |
| `compiled_norm_literal.py` | 348 | literal Triton transcriptions of Inductor's generated RMSNorm kernels |
| `compiled_relations.py` | 332 | relations for every Inductor-generated kernel of the Llama compiled execution |
| `inductor_models.py` | 139 | CPU bit-models from the compiled/eager divergence study (test-only) |
| `libdevice_sampling.py` | 207 | libdevice transcription for the Gumbel-max noise; CLI (test-only) |
| `sampling_rng.py` | 308 | torch-free recomputation of vLLM's Gumbel-max noise from a capture log; CLI |
| `beyond_gemm.py` | 422 | GPU probe script (SiLU, RMSNorm, RoPE vs IEEE models); `registry/crosscheck.py` imports its `rope_model` |
| `cpp/*.cpp` (3), `cuda/*.cu` (4) | n/a | C++ models built by `_jit.py`; CUDA measurement probes (two are referenced only by `tools/move_map.txt`) |

`registry/` (without `quarantine/`):

| module | lines | job |
|---|---:|---|
| `__init__.py` | 88 | imports the library and registers 18 lazy families (`Const`, `GatherBf16xN`, `L*`, `SplitsForSMS`, `{ORD=}`, `Lifted[..]_v1` and `_v2`) |
| `b1.py` | 1,285 | four model configs (B1 Qwen2.5-1.5B, B0 SmolLM2-135M, SMOL360, QWEN05) and 35 composites in three generations (Gemm, norms, RoPE, Attention v1/v2/v3, Layer*, Serve v1/v2/v4) |
| `b1_tp2.py` | 411 | TP composites: `AllReduce2`, `AllGather2`, world-ary `AllReduce_v2` / `AllGather_v1`, `EmbeddingShard`, `*TP2`, `ServeTP2`; `allreduce_order`, `cross_rank_families` |
| `hopper.py` | 265 | Hopper bindings: `HopperBF16WgmmaDot16_v1` and the B1 composites re-instantiated over a copied globals dict |
| `fp8.py` | 619 | block-scaled FP8 linear on Hopper (5 primitives, 13 composites) |
| `moe.py` | 375 | vLLM fused-MoE block Definitions (promoted from `quarantine/ov_moe`) |
| `moe_pad.py` | 305 | the padded fixed-slot MoE construction |
| `dense.py` | 627 | generic elementwise / reduction / softcap Definitions, promoted from `quarantine/dense` (Gemma-2) |
| `spec.py` | 380 | speculative-decoding composites and `DRAFT_CONFIG` (test-only) |
| `prims.py` | 783 | 37 one-output primitives of the B1 profile (conversions, FMA/MUFU, tensor-core dot, tanh table) |
| `ref_prims.py` | 994 | reference-mode primitives and composites; rebinds core codec's lazy-family table |
| `pad_prims.py` | 65 | primitives of `Serve@3` |
| `lifted.py` | 2,368 | lifting: encodings, strict/specified/ordinary classes, lifted-composite replay, Continuation members, SplitsFor, `LServe_v2`, lag rule, served-prefix checks, width summary |
| `serve3.py` | 166 | `Serve@3`, the padded serving circuit |
| `serve3_reference.py` | 88 | vectorized reference evaluator of `Serve@3`'s padding layer (test-only) |
| `targets.py` | 245 | target-keyed bindings (DOT, FA version, BN) and launch-context parsing |
| `gemm_targets.py` | 221 | GEMM target specializations of vLLM's batch-invariant persistent matmul; Ada and Hopper tuned tables |
| `derived_rows.py` | 944 | vectorized numpy evaluators of interior values of B0/B1 Definitions |
| `sampling.py` | 505 | stochastic token-select Definitions (Gumbel with top-p) |
| `sampling_rows.py` | 256 | numpy twins of the sampler Definition |
| `topp_split.py` | 601 | exact-fp32 model of vLLM's `_apply_topp_split`; `SplitsFor_v1` |
| `sampling_topp_difftest.py` | 125 | difftest adapter for the sampler; production code also imports it (`check/stoch_recompute.py`, `check/sampled_replay.py`) |
| `conformance.py` | 128 | conformance record of the library as data; CLI (test-only) |
| `crosscheck.py` | 148 | CLI: registered composites against validated CPU models and captures |
| `rmsnorm_fused_sweep.py` | 263 | sweep script over a B0 commit store; `derived_rows.py` imports its numpy twin `fused_rows` |

`registry/quarantine/` (34 files, 2,212 lines):

| module | lines | job |
|---|---:|---|
| `__init__.py` | 19 | the quarantine rules (import only `verity.ir.*` and a few stdlib modules) |
| `collective/__init__.py`, `allreduce.py`, `allreduce_difftest.py` | 23, 106, 80 | `AllReduceSumBf16{N,R}` and its 2-GPU difftest adapter (imports `torch.distributed`) |
| `dense/__init__.py` | 40 | re-exports |
| `dense/` 19 op modules (`add_scalar_bf16` 14, `add_scalar_f32` 15, `add_widened_bf16` 15, `bf16_div_scalar` 18, `bf16_mul_scalar` 15, `bf16_mul_scalar_tensor` 20, `bf16_tanh` 15, `gelu_tanh_mul` 14, `gelu_tanh_mul_bf16` 40, `mean_triton` 37, `mul_vec_f32` 13, `narrow_f32_bf16` 15, `rsqrt_f32` 16, `scale_row_bf16` 15, `scale_row_f32` 14, `softcap` 32, `square_bf16` 15, `square_f32` 13, `tanh_f32` 21) | 357 | one ATen/vLLM op each; 18 are one-line re-exports of `registry/dense.py`, `bf16_mul_scalar_tensor` re-exports `registry/b1.py` |
| `dense/tables/mufu_tanh_sm89.{json,xzblocks}` | 37 KB, 450 KB | the default `MufuTanh_v1` table, read by live `registry/prims.py:507` |
| `ln/__init__.py`, `ln/_common.py` | 19, 10 | pythia-160m lane; `_common` imports `registry.prims` and `registry.b1` |
| `ln/gelu_erf.py`, `gelu_erf_bf16.py`, `gelu_erf_table.py` | 17, 37, 1,203 | exact GELU(erf) through an embedded base64+zlib table |
| `ln/layer_norm_aten.py` | 153 | `aten.layer_norm` composite (imports numpy) |
| `ov_moe/__init__.py`, `ov_moe/moe.py` | 5, 11 | re-export of `registry/moe.py` |
| `ov_sampling/__init__.py`, `ov_sampling/gumbel.py` | 3, 129 | `GumbelArgmaxBf16@v1` |

### Findings

**CORE-DUP (6)**
- The integration re-registers core's promoted ML Definitions under the same ids:
  - `registry/prims.py:183, 189, 199` (`Bf16ToF32_v1`, `F32ToBf16Rn_v1`, `F2fpBf16_v1`) duplicate `packages/.../ml/prims.py:30, 36, 44`;
  - `registry/b1.py:1010, 1021, 1028` (`DotBf16_v2`, `GemmCoordinate_v2`, `Gemm_v2{K,N,DOT}`) duplicate `packages/.../ml/gemm.py:27, 38, 45`;
  - `registry/hopper.py:71` (`HopperBF16WgmmaDot16_v1`) duplicates `ml/prims.py:62`;
  - the `Const<w>[0x..]_v1` lazy family in `registry/__init__.py` duplicates `ml/prims.py:94`.

  Importing `verity.ml.prims` alongside `verity_vllm.program.registry` raises `ValueError` (duplicate id; confirmed with an import probe). So no integration code can use core's library, and nothing in the integration imports `verity.ml.prims` or `verity.ml.gemm`. Delete the copies and import core. *high*
- `registry/prims.py:381` registers `AmpereBF16TcDot16_v1`, but its body (`:375`) is core's `tc_dot_total` on `AMPERE_BF16_M16N8K16`. Core ships those semantics as `AmpereBF16TcDot16_v2` (`ml/prims.py:52`). The integration's `_v1` changed meaning in place. *high*
- `registry/prims.py:51-70` float-word helpers (`f32_of`, `bits_of`, `bf16_to_f32_bits`, `f32_to_bf16_rn_bits(u, nan)`) re-implement core `verity.ml.tc.cast` (`packages/.../ml/tc/cast.py:24 bf16_to_f32_word`, `:29 f32_to_bf16_rn_word(u, nan)`). *medium*
- `numerics/mma.py:31-143` defines `TCModel`, `tc_dot`, `tc_dot_chain`, `MODELS` and `model_for`, mirroring core `verity.ml.tc.models` under the same names (`GroupSum`, `tc_dot` :217, `tc_dot_chain` :227, `PIPELINES` :349, `pipeline_for` :362, `MODELS` :786). The BF16 path already delegates to core `silicon`. Only the FP16 product (`mma.py:31 f16_product`) is new; core's product table (`ml/tc/term.py:252`) lacks it. Upstream FP16 and delete `mma.py`. *medium*
- `frontend/target_profile.py:29-38` `canonical_bytes` is core `verity.ir.codec.canonical_json` (`packages/.../ir/codec.py:317`) plus a `default` hook. It is the third copy, after `correspondence/runtime.py:319`. *low*
- Reference-run decompositions: `descriptor_equivalence.py` `canonical_runs` and the progressions in `compact.py` sit beside core `verity.ir.refs.runs` and `correspondence/emit._runs`. `frontend/liveness._norm` is one of the four interval algebras listed under query/. *low*

**INTERNAL-DUP (8)**
- Two modules test "same circuit, different encoding", both citing frontend rulings §8.5: `frontend/correspond.py` (331; used by `torch_frontend.export_report`) and `descriptor_equivalence.py` (442; test-only CLI). *high*
- Two TP all-reduce Definitions disagree on reduction order for more than two ranks:
  - `registry/quarantine/collective/allreduce.py:66-70` (`AllReduceSumBf16{N,R}`) folds ranks 0..R-1 ascending;
  - `registry/b1_tp2.py:128-134` (`allreduce_order`, used by `AllReduce_v2{WORLD,N}`) folds R-1..0 and calls itself "the ONE statement of the order".

  `tp/collective_record.py` still imports the quarantine one. *high*
- Numpy twins of registered Definitions live in four places besides `check/twins.py`: `registry/derived_rows.py` (944), `registry/sampling_rows.py` (256), `registry/serve3_reference.py` (88), and the twin inside the sweep script (`registry/rmsnorm_fused_sweep.py:121 fused_rows`, imported by `derived_rows.py:753`). Each restates a Definition body in numpy and relies on tests to stay equal. *medium*
- Five BF16<->f32 word converters: `dtypes.py`, `registry/prims.py:59-70`, `registry/rmsnorm_fused_sweep.py:56-66`, `numerics/beyond_gemm.py:53-70`, `registry/derived_rows.py`, plus core `ml/tc/cast.py`. *medium*
- Two configs of Qwen2.5-0.5B disagree. `registry/b1.py:80` `QWEN05_CONFIG` pins the revision and says the FA2 block trait is "not established". `registry/spec.py:37` `DRAFT_CONFIG` has revision `None` and `FA2_BN: 128`. *medium*
- Two mechanisms vary a composite by target. `registry/targets.py` binds statics (`Gemm_v2{DOT}`, `Attention_v2{BN,DOT,INV}`). `registry/hopper.py:112-122` re-evaluates the B1 functions' code objects over a copied globals dict with `P` and `BN` swapped. *medium*
- FA tile rules are restated:
  - FA2 `BN`: `registry/b1.fa2_kblock_n` and `query/manifest/format.py:276`;
  - FA3 `kBlockN`: `registry/targets.py:100` and `numerics/fa3_model.py:60` (a deliberate independent twin, cross-checked), plus the FA3 geometry in `query/manifest/format.py:270-299`. *low*
- Two authored B1 serving programs: `registry/b1.py` (Serve v1/v2/v4) and `frontend/b1_authored.py` (668; the same program through the torch frontend, test-only). *low*

**VERSION-RESIDUE (6)** (LEGIT hashed identifiers listed separately)
- Case names used as module, package and API names:
  - modules `registry/b1.py`, `registry/b1_tp2.py`, `frontend/b1_authored.py`;
  - the package docstring `registry/__init__.py:1` ("library for the B1 (Qwen2.5-1.5B) ... serving program");
  - `B0_CONFIG` / `B1_CONFIG` (`b1.py:31, 47`), the `b1-eager*` vocabularies, `frontend/rules/profile.py` "(B0/B1)", ports `b1-hopper` / `b1-fp8`.

  The module holding the generic Gemm, RMSNorm, RoPE and Attention composites is named after one model case. *high*
- `registry/prims.py:381` `AmpereBF16TcDot16_v1` now carries core's `_v2` semantics under an unchanged id (see CORE-DUP). *high*
- Three generations of the same composites live side by side in `registry/b1.py`:
  - `Attention_v1/_v2/_v3` (`:524, :1127, :840`), `Serve_v1/_v2/_v4` (`:701, :1237, :885`);
  - `Gemm_v1/_v2` (`:149, :1028`), `RMSNormFusedCuda_v1/_v2` (`:271, :305`), `LayerPre/LayerPost/Final _v1/_v2`.

  The Python names do not follow id order (`AttentionV3` at `:846` comes before `AttentionV2` at `:1133`), and no record says which generations are retired. *medium*
- Four vocabularies in `frontend/rules/vocab.py` (`b1-eager`, `b1-eager-v2`, `b1-eager-v3`, `dense2-eager-v1`). vLLM exports bind `b1-eager-v3`. *medium*
- Re-export shims left after promotion: the 19 `registry/quarantine/dense/*` op modules and `quarantine/ov_moe/moe.py` hold no Definitions. They exist "so the difftest adapters and the eager profile keep working" (`ov_moe/moe.py:1-2`). *medium*
- Lane and experiment ids in code names:
  - `frontend/rules/triton_iface.py:18` `_LIB_NAME = "verity_cba"` (op `verity_cba::triton_launch`, named after the dissolved `cb_a` experiment);
  - `REGISTERED_WITH_W2` / `register_with_w2` / `owner="W11"` in `numerics/relations.py`, `fa2_relation.py`, `rms_relation.py`;
  - "GP-01" (`global_program.py:1`), `DP_PAD_02` (`registry/lifted.py:2173`);
  - `lifted_prim_v1` beside `lifted_prim`, and both `Lifted[..]_v1` and `_v2` lazy families registered (`registry/__init__.py`). *medium*
- LEGIT (hashed or serialized; do not rename without a decision): Definition ids (`Gemm_v2`, `Attention_v3`, `Serve_v4`, `AllReduce2_v1`, `AllReduce_v2`, `Continuation_v1`, `LServe_v2`, `Lifted[..]_v2`, `TokenSelect_v1`); vocabulary names (hashed into provenance); relation ids (`gemm.bf16.v1`, `attention.bf16.v1`, `rmsnorm.bf16.v1`); schema ids (`verity-gen/instances/v1|v2`, `verity-ir/registry-version/v0`); quarantine `SEMANTIC_ID`s (`dense/Bf16MulScalarTensor@v1`, `ov-moe/MoeExpertGemm@v1`). The op name `verity_cba::triton_launch` appears in derive reports; check before renaming.

**HARDCODING (9)**
- Model configs outside quarantine: `registry/b1.py:31-95` (Qwen2.5-1.5B, SmolLM2-135M, SmolLM2-360M, Qwen2.5-0.5B, with HF revisions and kernel-profile prose) and `registry/spec.py:37`. `frontend/vllm_meta.py:30` makes `SmolLM2-135M@93efa2f` the default model. *high*
- Target defaults. `frontend/target_profile.py:114-115` defaults the dataclass to `compute_capability=(8, 9)`, `num_sms=128` (RTX 4090). `numerics/fa2_model.py:256-258` infers `sm_89` from marketing names ("4090", "L40", "6000 Ada"). `numerics/rms_relation.py:122` writes "sm_89" into the coverage reason. *medium*
- vLLM source pins in library rules and tables:
  - `frontend/rules/vllm_bindings.py:45-67, 143` (`GEMM_PINS`, `RMS_PINS`, `MEAN_PINS`, `ATTN_PINS`: kernel qualnames and source sha256 at vLLM d9105ea80);
  - `registry/gemm_targets.py:62-100` (`ADA_TUNED_GEMM` / `HOPPER_TUNED_GEMM`, copied from vLLM's tuned table);
  - `global_program.py:139` `_MODE_NAMES` (vLLM's `CompilationMode` numbering).

  This is deliberate: derivation refuses on mismatch. But the vLLM commit string appears in 12 files (`target_profile.py` 7, `dense.py` 5, `topp_split.py` 4, `gemm_targets.py` 4, ...). *medium*
- `numerics/kernel_zoo.py:1-146` hardcodes A100 cuBLAS launch signatures for Qwen2.5-1.5B shapes. It is live through `numerics/relations.py`, outside quarantine. *medium*
- `numerics/compiled_relations.py:2, 205-206, 285` covers "every Inductor-generated kernel of the production Llama execution", with per-model epsilon discussion (Llama-3.2 vs Qwen2.5) and a Qwen qkv-bias special case. `numerics/compiled_norm_literal.py` carries model constants. *medium*
- `numerics/beyond_gemm.py:77` defaults `HF_HOME` to `/workspace/hf` and hardcodes the snapshot path `models--Qwen--Qwen2.5-1.5B`; the usage line at `:26` gives `/workspace/results/numerics/qwen_acts`. *medium*
- TP world size 2 in names and rules: `AllReduce2`, `AllGather2` and `*TP2` / `ServeTP2` (`registry/b1_tp2.py:98-365`); `frontend/rules/vllm_bindings.py:1678` `AllReduce2Rule` (world 2, "recorded identity") beside `:1751` `AllReduceRule` (world > 2). World-ary support exists. *low*
- Model specifics in generic modules. `registry/dense.py:8, 505-605` carries Gemma-2 prose and conformance strings. Gemma-2's `Bf16MulScalarTensor` lives in `registry/b1.py` (re-exported by `quarantine/dense/bf16_mul_scalar_tensor.py:16`). *low*
- `frontend/inputs_trace.py:11` `_FORBIDDEN_MARKERS` lists `/vol/corpus`, `census/B0-` and `experimental/aot/` (machine and retired paths). *low*

**SCRIPT/ENV/PATH (7)**
- `__main__` plus argparse in 10 library modules: `global_program.py` (run by `ops/row_pod.sh`, `ops/canary.sh`, `ops/tp_stage.sh`), `descriptor_equivalence.py`, `profile_descriptor.py`, `instances_form.py:95-118`, `numerics/beyond_gemm.py:388`, `numerics/libdevice_sampling.py`, `numerics/sampling_rng.py`, `registry/conformance.py`, `registry/crosscheck.py`, `registry/rmsnorm_fused_sweep.py:241-262`. *medium*
- `frontend/vllm_meta.py:21-25` writes environment variables at import: `setdefault` of `VLLM_BATCH_INVARIANT=1`, `VLLM_USE_LAYERNAME=0`, `HF_HUB_OFFLINE=1`, `VLLM_LOGGING_LEVEL`, `TOKENIZERS_PARALLELISM`. Importing the module changes vLLM's behavior for the whole process. *high*
- Environment reads that change results:
  - `VERITY_ARCH` (`numerics/fa2_model.py:253`, `numerics/rms_relation.py:117`) picks the arch when the node declares none;
  - `VERITY_MUFU_TANH_TABLES` (`registry/prims.py:638`) replaces `MufuTanh_v1`'s table;
  - `VERITY_RMS_TABLES` and `VERITY_MUFU_TABLES` (`numerics/rms_relation.py:55`, `numerics/fa2_relation.py:113`);
  - `STOCH_DECLARED_CHRONOLOGY_S` (`global_program.py:696`), `VERITY_REAL_LOGITS` (`registry/sampling_topp_difftest.py:48, 64`), `VERITY_NUMERICS_BUILD_DIR` and `CXX` (`numerics/_jit.py:29, 94`). *medium*
- Path arithmetic into top-level data:
  - `numerics/rms_relation.py:58-60` and `numerics/fa2_relation.py:116-117` compute `dirname` x3 + `fixtures/W11*-…`, so library code reads `integrations/vllm/fixtures/`;
  - `registry/rmsnorm_fused_sweep.py:45-48` resolves `Path(__file__).resolve().parents[3]` to `vllm-poc/bundles/…` and `fixtures/verity-ir/…`, both missing;
  - `registry/prims.py:34-38` inserts `integrations/vllm/vllm-poc` and `integrations/vllm/src` (both missing) into `sys.path` at import. *medium*
- Subprocess in library code: `numerics/_jit.py:94-99` runs `g++ -fopenmp` (retrying without `-fopenmp`) at the first use of a relation, in whatever process that is. *medium*
- `frontend/vllm_meta.py:93-110` `ensure_distributed` starts a real gloo process group on a free TCP port and retries when an exception's text contains "EADDRINUSE". It sets the process-global `_DIST_READY`. *low*
- Machine and lane paths in strings: `numerics/beyond_gemm.py:26, 77` (`/workspace/...`), `registry/gemm_targets.py:174` (`out/gen/sweep/evidence/...`). *low*

**LAYERING (9)**
- The registry depends on a driver and on query:
  - `registry/lifted.py:1438` imports the CLI driver `program.global_program` (`eos_lag_rows_declared`);
  - `:1717-1826` imports `query.boundary`, `query.partition`, `query.query_artifact`;
  - `:2239-2280` imports `program.workload`. *high*
- Core-level IR analyses are parked in the frontend: `frontend/liveness.py`, `frontend/correspond.py`, `frontend/provenance.registry_version` and `descriptor_equivalence.py` contain no vLLM content. `query/boundary.py` imports the private `liveness._norm` / `_strided_targets`. Promote them with `query/boundary.py`. *medium*
- numerics registers upward into check at import. In `numerics/relations.py:524`, `fa2_relation.py:267` and `rms_relation.py:186`, `REGISTERED_WITH_W2 = register_with_w2()` imports `verity_vllm.check.relations` and registers. `relations.py:528` then imports `fa2_relation` at the bottom of the file, while `fa2_relation` imports `relations` (a cycle). *medium*
- `numerics/sampling_rng.py:166-168, 260, 274` reads the capture log through `check.fold_compare.SnapshotStore`, `observe.events` and `observe.log`. *medium*
- Live code imports scripts and adapters:
  - `registry/derived_rows.py:753` imports its twin from the sweep script `registry/rmsnorm_fused_sweep.py`;
  - `registry/crosscheck.py:101` imports the GPU probe `numerics/beyond_gemm.py`;
  - `check/stoch_recompute.py:91, 408` and `check/sampled_replay.py:726` import the difftest adapter `registry/sampling_topp_difftest.py`. *medium*
- Quarantine breaks its own rule. `registry/quarantine/__init__.py:18` says lane packages import only `verity.ir.*` and a few stdlib modules; 30 of 34 files import other things:
  - re-exports from the promoted `registry/dense.py`, `registry/b1.py`, `registry/moe.py`;
  - `ln/_common.py:4-5` (`registry.prims`, `registry.b1`), `ln/layer_norm_aten.py:39` (numpy), `ln/gelu_erf_table.py` (base64, zlib), `collective/allreduce_difftest.py` (`torch.distributed`).

  In the other direction, live `registry/prims.py:507` reads its default table from `quarantine/dense/tables/`. *medium*
- `global_program.py:52` imports `correspondence.batch_decomp.derived_shape` (cross-listed under correspondence/). *medium*
- Private names cross module boundaries:
  - `torch_frontend` privates are imported elsewhere (`_tensor_type` by 9 modules, `_permute` by 4; also `_stack`, `_slice`, `_select`, `_norm_dim`, `_expand`, `_dim_len`), as is derive's `_LiftedConstant`;
  - `numerics/rms_relation.py:32` imports five `fa2_relation` privates;
  - `frontend/rules/family.py` imports core's private `codec._spec_id`. *low*
- Misplaced helpers. `dtypes.py` is used only by `commit/hashing.py` and `verity_vllm/__init__.py`. `compact.py` is a storage format used by `check/`, `correspondence/` and `tp/`, not Program construction. *low*

**GOD-MODULE (7)**
- `registry/lifted.py` (2,368) does 12 jobs:
  1. lifted encodings and boundary checks (`:66-138`);
  2. type lifting (`:140-183`);
  3. the strict class and its enable wrappers (`:185-376`);
  4. the specified-class primitives `LSelect`, `LIsActive`, `LEnable`, `LBot`, `LGatherRow`, `LFixedSelect`, `LStepLive` (`:378-630`);
  5. Continuation_v1 members and gate counts (`:631-754`);
  6. `SplitsFor` (`:755-833`);
  7. the ordinary class and class inference (`:840-1082`);
  8. hand lifts and composite lifting by replay (`:1083-1365`);
  9. `Prefill`, `StepBody`, `LServe_v2`, with the lag rule reading `global_program` (`:1366-1600`);
  10. served-prefix and activity checks (`:1601-1716`);
  11. width summary and query-artifact emission through `query.*` (`:1717-1830`);
  12. workload-level request lifting (`:2239-2368`). *high*
- `frontend/rules/vllm_bindings.py` (1,905) does 12 jobs:
  1. vLLM kernel source pins and GEMM target selection (`:45-128`);
  2. process-global observation state (`:129-254`);
  3. declared/derived accounting (`:255-300`);
  4. Triton RMSNorm and GEMM launch rules (`:356-508`);
  5. KV cache write and unified attention (`:509-730`);
  6. dense elementwise rules (`:731-872`);
  7. the unfused norm chain, 9 rules (`:873-1276`);
  8. FP8 rules (`:1277-1456`);
  9. fused-add RMSNorm dispatch (`:1457-1486`);
  10. alloc views, id widening, padded cache clear (`:1487-1627`);
  11. TP collectives (`:1628-1873`);
  12. rule-set assembly (`:1876-1895`). *high*
- `global_program.py` (844) does 11 jobs: descriptor loading; manifest request parsing; compilation-fact normalization; EOS-lag declaration and check; MoE-construction check; modelled engine; applicability aggregation; sampler geometry and schedule binding; stop rule; weights-of-record binding; the build driver writing four artifacts, plus the CLI. *high*
- `frontend/torch_frontend.py` (1,340) does 9 jobs: errors; dtype/Type mapping; Coll split/join; a schema DSL and unification; custom-op minting; callables (`Prim`, `Registered`, `Bound`, `Function`); the authoring API (`function`, `bind`, `batch`, `scan`, `Ops`); the export guard; the view/reference algebra that derive and the rules use, plus export and report. About half is authoring API used by tests; the rest is derive's shared library. *medium*
- `registry/b1.py` (1,285) does 6 jobs: four model configs; constants; three generations of composites; Gemma-2's `Bf16MulScalarTensor`; profile binding records (`GEMM_AMPERE`, `ATTENTION_FA2`); serve-program helpers. *medium*
- `frontend/derive.py` (1,012): reasons and refusals, static structure values, `Ctx` (260 lines of lowering state), report, export, weights, fx translation. It is one cohesive engine. *low*
- `registry/ref_prims.py` (994) and `registry/derived_rows.py` (944) are large but each holds one theme (reference kinds; numpy twins). *low*

**DEAD (7)**
- Test-only modules, with no production importer. Searches: absolute imports including multi-line parenthesized ones, relative imports, `python -m` in `ops/*.sh` and `tools/`, and string references.
  - `registry/spec.py` (1 test);
  - `registry/serve3_reference.py` (22 tests; only docstring mentions in `serve3.py:32` and `lifting/dump.py:5`);
  - `registry/conformance.py` (3 tests; no script runs its CLI);
  - `frontend/derive_examples.py` (10 tests) and `frontend/examples.py` (reached through `derive_examples.py`);
  - `frontend/b1_authored.py` and `frontend/serve3_authored.py` (`b1_authored`'s only importer is `serve3_authored`);
  - `descriptor_equivalence.py` (4), `profile_descriptor.py` (3);
  - `instances_form.py` (2; `harness/run_config.py:1028` defines its own `instances_form()` rather than importing this module);
  - `lifting/dump.py` (2), `numerics/inductor_models.py` (2);
  - `numerics/libdevice_sampling.py` (2; `registry/sampling.py:163` mentions it in a docstring).

  *high confidence for "no production importer"*
- `registry/quarantine/collective/allreduce_difftest.py` is reachable only as `python -m verity_vllm.check.difftest --adapter <dotted name>`. No script passes that name; 2 tests. *medium confidence* (searched `ops/`, `tools/`, tests, strings)
- `numerics/cuda/fa2_softmax_probe.cu` and `numerics/cuda/mma_tiles_sm80.cu` are referenced only by `tools/move_map.txt`. *high confidence*
- The `registry/rmsnorm_fused_sweep.py` driver (`sweep`, `main`, `load_store_leaves`, `extract_bundle`) defaults to `vllm-poc/bundles/B0-…tar.xz` and `fixtures/verity-ir/rmsnorm-fused-b0/…npz`, which exist neither under `integrations/vllm/` nor at the repo root. Only its numpy twin is used. *high confidence*
- `registry/prims.py:34-38` adds `sys.path` entries for directories that do not exist. *high confidence*
- Stale references in `program/`:
  - 26 `veritor.core.silicon*`, 17 `vllm-poc/…`, and about 10 `cb_a.*` module paths (e.g. `sampling_event.py:2`, `instances_form.py:7`, `cb_a/tp_ops.py` at `rules/vllm_bindings.py:1628`);
  - `experimental/aot` (`frontend/inputs_trace.py:11`);
  - `rules_vllm.py::TritonRmsNormRule` (`frontend/triton_capture.py:12`; now in `rules/vllm_bindings.py`) and `tp_ops.CollectiveBus` (`frontend/vllm_meta.py:61`; now `tp/export_ops.py:97`);
  - 40 of the 44 distinct `docs/…`, `out/gen/…` and `fixtures/…` paths cited in `program/` do not resolve (e.g. `docs/frontend-pytorch-2026-09-07.md`, `docs/vllm-poc/serve3-spec.md`, `out/gen/r17/LIFTING-SPEC-v0.5.md`, `docs/data/tc-total-2026-09-07`, `fixtures/verity-ir/rmsnorm-fused-b0/…`). *high confidence*
- The quarantine re-export shims (19 `dense/*` op modules, `ov_moe/moe.py`) are imported by difftest adapters and `observe/profiles/gen_*_patterns.py` but define nothing. *medium confidence that they can go once those importers point at `registry/dense.py` / `registry/moe.py`*

**NAMING (6)**
- "B"-numbers are overloaded:
  - B0 and B1 are model cases (`B0_CONFIG`, `B1_CONFIG`, `b1.py`, `b1-eager-*`, `b1-hopper`, `b1-fp8`);
  - B1 through B5 are also FA2 algorithm steps (`b1.py:450-470`, `dense.py:477-527`: "row max (B1), rescale factor (B2), exp2 stage (B3)");
  - B6 and B7 are LIFTING-SPEC sections (`lifted.py:25, 302`; `registry/__init__.py:76, 84`);
  - B8 is batch size 8 (`instances_form.py:5`). *medium*
- "profile" in `program/` means six things: `TargetProfile`, a vocabulary mode (`rules/profile.py`, "profile mode"), a byte profile (`profile_descriptor.py`), binding records (`GEMM_AMPERE`, `ATTENTION_FA2`), the prose `profile` dict inside model configs, and the capture/target profile passed to `vllm_meta`. *medium*
- "twin" means numpy re-statements (`derived_rows.py`), C++ libraries (`_jit.py`, "the C++ twin libraries") and difftest counterparts. "relation" means a `check.relations` checker (`numerics/*_relation.py`) and core `verity.ml.tc.relation`. *low*
- `numerics/` holds independent reference models for checking. The numerics of the Definitions themselves live in `registry/prims.py`. *low*
- `registry/` holds much that is not registry: a sweep script, difftest adapters, numpy twins, target tables, conformance data. *low*
- Six sampler modules across three packages: `sampling_event.py`, `registry/sampling.py`, `registry/sampling_rows.py`, `registry/sampling_topp_difftest.py`, `numerics/sampling_rng.py`, `numerics/libdevice_sampling.py`. *low*

**DOCS (6)**
- 826 lab-notebook tags across `program/` (R1x, M-0nnn, F-r.., COORD, lane names, dates, HH:MMZ, rev-, D-numbers, GUIDANCE §, BRIEF §). The densest files: `registry/lifted.py` 75, `global_program.py` 61, `frontend/target_profile.py` 46, `lifting/continuation.py` 36, `rules/vllm_bindings.py` 30, `registry/dense.py` 29, `registry/b1.py` 29. *medium*
- Dangling design references: about 40 cited `docs/`, `out/gen/` and `fixtures/` paths do not exist (see DEAD). Conformance strings in `registry/conformance.py:45, 50`, `prims.py:203`, `fp8.py:125, 184` and `hopper.py:77` cite evidence directories that are not in the repo. *medium*
- Personal names and pending decisions in docstrings: `lifting/continuation.py:1` ("Daniel 20:17Z"), `registry/moe_pad.py:2` ("Daniel's decision"), `registry/lifted.py:2173` ("RULING 21 ... pending Da…"), `frontend/target_profile.py:270`. *low*
- Notion pointers as the narrative: `registry/__init__.py:30`, `frontend/rules/__init__.py:22`. *low*
- `instances_form.py:9-11` says the writer `run_config.persist_program` goes through this module; `run_config` has its own `instances_form()` and does not import it. *low*
- `registry/__init__.py:1` describes the package as the B1 library, but it registers FP8, MoE, dense, lifting and sampling families too. *low*

**FALLBACKS (6)**
- `global_program.py:38-50` wraps `import registry.hopper / fp8 / moe_pad` in `except Exception: print(...)`. A broken registry module becomes a "will not decode" line on stderr and the driver continues. *high*
- `frontend/rules/vocab.py:36-43` `Vocabulary.kind` turns any `TypeError` inside a binder into `None`, which derive reports as `Unsupported(numerics_unregistered)`. A bug in a binder looks like a missing Definition. *medium*
- Semantics chosen by override chains:
  - `registry/prims.py:630-653`: `MufuTanh_v1`'s table resolves as `mufu_tanh_use_tables()` > `$VERITY_MUFU_TANH_TABLES` > the in-tree default;
  - `numerics/fa2_model.py:253-258`: the arch resolves as argument > `consts` > `VERITY_ARCH` > GPU-name sniffing. *medium*
- `numerics/relations.py:491-496`, `fa2_relation.py:247-248`, `rms_relation.py:166-167` `except ImportError: return []`: if `check.relations` is missing, the relations silently do not register. *low*
- `frontend/export_compat.py:59-62, 93-96` `except Exception: continue` when importing the vLLM modules to patch; the file has 11 broad excepts. `read_back_applied()` re-reads what vLLM sees afterwards, which mitigates this. *low*
- `frontend/rules/vllm_iface.py:1-10, 24-32, 78`: when vLLM is absent, a stand-in op library with the same schemas replaces vLLM's `_C` ops (deliberate), with `except RuntimeError` for "already defined" and a broad except at `:78`. Across `program/` the 14 heaviest files hold 58 broad `except Exception` sites (`export_compat.py` 11, `vllm_meta.py` 9, `global_program.py` 8). *low*

**OTHER-WEIRD (10)**
- `registry/ref_prims.py:274-276` rebinds core's private `verity.ir.codec._LAZY_PRIMITIVE_FAMILIES`, a list, to a tuple at import. After that, core's `register_lazy_family` (which appends) raises `AttributeError` (confirmed with an import probe). Any lazy family registered after `ref_prims` is imported fails. *high*
- `registry/prims.py:630-653`: the evaluator of a registered primitive (`MufuTanh_v1`) depends on a process environment variable or a module-global override, and a table supplied through the environment is not hash-checked. One id can compute different functions in different processes. *high*
- Monkeypatching vLLM, torch and Triton during export:
  - `frontend/export_compat.py:17-50` (the `torch._C.TensorBase.data` descriptor);
  - `:72-115` (`current_platform.get_device_capability` at class level, `num_compute_units` in several modules, vLLM's private `_TUNED_MATMUL_CONFIGS_RESOLVED` / `_FOR_DEVICE`);
  - `:207-286` (MoE dispatcher custom ops, workspace manager);
  - `frontend/triton_capture.py:103-115` (`JITFunction.run`).

  The patches are scoped and restored, but they depend on private vLLM names. *medium*
- Process-global mutable state changes lowering. In `frontend/rules/vllm_bindings.py:171`, `_OBSERVED` (attention impls, export facts, target profile, launch context) is set by `observe_*` calls from `harness/derive_step.py` and read inside rules. Derivation is not re-entrant, and state leaks between derivations in one process unless `clear_observations()` is called. *medium*
- Import-time side effects: `registry/__init__.py` registers 18 lazy families and imports the whole library; `registry/prims.py:40` calls `np.seterr(all="ignore")` for the process; `frontend/vllm_meta.py:21-25` writes env vars; numerics registers into check (see LAYERING). *medium*
- `registry/hopper.py:112-122` builds the Hopper composites by re-evaluating B1 functions' code objects over a copied globals dict (`types.FunctionType(fn.__code__, env, ...)`). *medium*
- `frontend/inputs_trace.py:40` installs `sys.addaudithook`, which cannot be removed for the life of the process. *low*
- Large literal tables in source: `registry/quarantine/ln/gelu_erf_table.py` (1,203 lines of base64+zlib), `registry/quarantine/dense/tables/mufu_tanh_sm89.xzblocks` (450 KB), `registry/gemm_targets.py:62-100`, `numerics/kernel_zoo.py:88-146`. *low*
- `numerics/_jit.py` compiles C++ at first use inside whichever process calls a relation, Commit workers included, serialized with fcntl locks. *low*
- `registry/lifted.py:2173` sets an ad hoc attribute `sp.candidate` on a `SpecializedDefinition` (`# type: ignore[attr-defined]`). `frontend/rules/vocab.py:288, 292` sets `"attention"` twice in one dict literal. *low*

Counts for `program/`: CORE-DUP 6, INTERNAL-DUP 8, VERSION-RESIDUE 6, HARDCODING 9, SCRIPT/ENV/PATH 7, LAYERING 9, GOD-MODULE 7, DEAD 7, NAMING 6, DOCS 6, FALLBACKS 6, OTHER-WEIRD 10.

Counts for the slice (query + correspondence + program): CORE-DUP 16, INTERNAL-DUP 24, VERSION-RESIDUE 19, HARDCODING 23, SCRIPT/ENV/PATH 18, LAYERING 24, GOD-MODULE 16, DEAD 16, NAMING 17, DOCS 20, FALLBACKS 18, OTHER-WEIRD 23 (234 findings).

---

## 4. Slice-specific maps

### Map 1: Core usage

**What the slice imports from core.**
- `program/`:
  - `verity.ir.defs` (about 48 import sites), `refs` (about 45), `types` (about 38), `codec` (about 19), `program` (8), `layout` (4), `evaluate` (3), `query_ast` (1);
  - `verity.ml.tc.{total, silicon, total_fp8}` (in `registry/prims.py`, `hopper.py`, `fp8.py`, `numerics/mma.py`), and `verity.errors`.

  It imports nothing from `verity.verification`, `verity.commitments`, `verity.ml.prims` or `verity.ml.gemm`.
- `query/`:
  - `verity.ir.{codec, layout, defs, refs, parts, types, query_codec, query_ast, program, evaluate}`;
  - `verity.verification.query`, in three files. `module_body.py` imports `Boundary`, `Partition`, `boundary`, `partition_by`. `program_view.py` imports `ValueRef` and implements core's `Program` protocol as a columnar view. `v1_bridge.py` imports `Policy`, `RequiredValues`, `ValueRef`, `required_values`.
- `correspondence/`: `verity.ir.*`, plus `verity.verification.{programs, typed_obligation}` in the dead `capture_identities_program.py`.

**Concept by concept.**

| core concept | core location | slice | verdict |
|---|---|---|---|
| `Program` protocol, `ValueRef` | `verification/query.py:69` | `query/program_view.py` implements it columnar | uses core |
| `partition_by`, `boundary`, `Boundary` | `verification/query.py:107, 174, 185` | `query/module_body.py` | uses core (65 lines) |
| `Policy`, `RequiredValues`, `required_values` | `verification/query.py:220, 236, 256` | `query/v1_bridge.py:50` imports them, then re-does half the validation inline (`:340-346`) because `required_values` recomputes the boundary | partial shadow |
| `VerificationUnit` (a set of Calls) | `verification/query.py:84` | unused; `query/vu_query.py` has its own `VU` (a descent path in a folded Program); `query/partition.py` calls a GateSet family a "VU partition" | shadowed; three meanings of VU |
| `VerificationPlan` (per-gate-class sampling rates) | `verification/plan.py:68` | unused; `query/vu_query.py` does its own deterministic uniform sampling over "tier-A" VUs; the required-value manifest (`verity-sweep/required-manifest/v1`) plays the plan's role for replay | shadowed |
| subcircuit boundary over `Part` (in, out, w_out); partition validation | core points at the integration (`ir/parts.py:15-18`, `ir/layout.py:19`) | `query/boundary.py`, `query/partition.py`; also `frontend/liveness.py`, `frontend/correspond.py` | core-level code in the integration |
| `query_ast.Query`, `query_id` | `ir/query_ast.py:528`, `ir/query_codec` | `query/query_artifact.py` (own fallback id) | mostly core |
| `check_binding` | `verification/binding.py:168` | `correspondence/capture_identities_program.py:302 binding_check` | second binding check (dead module) |
| gate-set lowering, `make_subcircuit` | `verification/lowering.py`, `gateset.py`, `programs.py:44` | `correspondence/capture_identities_program.py:480-538` hand-lowers `GemmCoordinate` | reimplemented (dead module) |
| `refs.runs` | `ir/refs.py:234` | `correspondence/emit._runs` (with a run budget), `descriptor_equivalence.canonical_runs`, `compact.py` progressions | reimplemented |
| `codec.canonical_json` | `ir/codec.py:317` | `correspondence/runtime.py:319`, `frontend/target_profile.py:29` | copied twice |
| `ml.prims`, `ml.gemm` Definitions | `ml/prims.py:30-94`, `ml/gemm.py:27-45` | `registry/prims.py`, `b1.py`, `hopper.py`, `registry/__init__.py` register the same ids | duplicate; the two cannot be imported together |
| `ml.tc.cast` word conversions | `ml/tc/cast.py:24-44` | `registry/prims.py:51-70`, `dtypes.py`, `derived_rows.py`, `rmsnorm_fused_sweep.py`, `beyond_gemm.py` | reimplemented five times |
| `ml.tc.models` (`GroupSum`, `tc_dot`, `tc_dot_chain`, `MODELS`) | `ml/tc/models.py:161-786` | `numerics/mma.py` (same names; BF16 delegates to `silicon`, FP16 local) | shadow |
| `ml.tc.total.tc_dot_total` | `ml/tc/total.py:202` | `registry/prims.py:375`, `hopper.py:40`, `fp8.py:177` | uses core |
| `ml.tc.relation` | `ml/tc/relation.py` | `numerics/*_relation.py` register checkers into `check.relations` instead | parallel concept (check's slice) |
| `commitments.*` | `commitments/` | nothing in the slice | n/a |
| `ir.evaluate.MissingValue` | `ir/evaluate.py:38, 44` | `correspondence/capture_identities.py:510-576` regex-parses its message | core lacks an attribute |

**Does `program/numerics` duplicate `verity.ml.tc`?** Only partly. `numerics/mma.py` shadows `verity.ml.tc.models` in names and shape, but its BF16 path delegates to core `silicon`, and its FP16 path does not exist in core. The rest of `numerics/` has no core counterpart: independent models of vLLM's FA2, FA3, RMSNorm, Inductor and sampler kernels (numpy and JIT C++) are integration content. The larger duplication is in `registry/`, which re-registers core's tensor-core and conversion Definitions under core's own ids.

**What using core directly would look like.**
1. **Registry.** Import `Bf16ToF32`, `F32ToBf16Rn`, `F2fpBf16`, `AmpereBF16TcDot16`, `HopperBF16WgmmaDot16` from `verity.ml.prims`, and `DotBf16`, `GemmCoordinate`, `Gemm` (`_v2`) from `verity.ml.gemm`. Delete those Definitions and the `Const` lazy family from `registry/`. Decide what `AmpereBF16TcDot16_v1` means: restore its old body, or retire it in favour of core's `_v2`. Replace the word helpers in `registry/prims.py` with `verity.ml.tc.cast`.
2. **Lazy families.** `registry/ref_prims.py` should call `verity.ir.codec.register_lazy_family` rather than rebinding the private list.
3. **Numerics.** Add an FP16 product and pipeline to `verity.ml.tc.term` / `models.PIPELINES`, then delete `numerics/mma.py`. `cpu_model.py` and `kernel_zoo.py` call `verity.ml.tc.models.tc_dot_chain`.
4. **Query.**
   - Promote `query/boundary.py`, `query/partition.py`, `frontend/liveness.py` and `frontend/correspond.py` into `verity.ir`, as core's docstrings already plan.
   - Give `required_values` an entry point that takes a precomputed `Boundary`, so `v1_bridge` stops re-validating.
   - Express `vu_query`'s replay sampling as a `VerificationPlan` over core `VerificationUnit`s instead of a private `VU`.
5. **Small items.** Use core `canonical_json`, `refs.runs` with a `max_runs` option, `types.type_from_json` for parameter types, and `query_codec.query_id`.

### Map 2: The registry

**How Definitions are organized.**
- **Registration is an import side effect.** `registry/__init__.py` imports the library and registers 18 lazy families (id regex to factory): `Const<w>[0x..]_v1`, `GatherBf16x<N>_v1`, `TopPMaskWordx<N>_v1`, `BitAtx<N>_v1`, `LSelect`, `LIsActive`, `LBot`, `LGatherRow`, `LStepLive`, `LIsEOS`, `LEmitNext[H]`, `LFixedSelect`, `LEnable_v1`, `SplitsForSMS<n>_v1`, `LSplitsForSMS<n>_v1`, `<id>{ORD=<mask>}`, `Lifted[<id>]_v1` and `Lifted[<id>]_v2`. Decoders must also import more modules by name: `query/program_view.py:550` and `global_program.py:36-50`.
- **Primitives** (counts of `@primitive` decorators; factories add more):
  - `prims.py` 37: conversions, f32 FMA and MUFU ops, `AmpereBF16TcDot16_v1`, and `MufuTanh_v1` with an external table;
  - `ref_prims.py` 8 (plus 22 composites): torch-CPU reference semantics, no proof support;
  - `fp8.py` 5, `moe.py` 5, `pad_prims.py` 2, `hopper.py` 2, `dense.py` 2, `sampling.py` 2.
- **Model composites:**
  - `b1.py` 35, the dense decoder: Gemm, RMSNorm (Triton and fused CUDA), RoPE, SiluMul, Attention v1/v2/v3, Embedding, LayerPre/LayerPost/Final, TokenSelect, Serve v1/v2/v4;
  - `b1_tp2.py` 11 (TP), `fp8.py` 13, `moe.py` 11;
  - `dense.py` 18: unfused norm chain, GeGLU, softcap attention;
  - `spec.py` 8 (speculative decoding), `sampling.py` 8 (Gumbel with top-p).
- **Target variation:** `targets.py` binds `DOT` / `BN` / `INV` statics per target family; `gemm_targets.py` holds the Ada and Hopper tuned tables; `hopper.py` re-instantiates code objects.
- **Padded and lifted:**
  - `serve3.py` (`Serve@3`);
  - `lifted.py`, which lifts any registered Definition (`Lifted[..]_v1/_v2`) and defines `LServe_v2` and the Continuation members;
  - `moe_pad.py` 9, `topp_split.py` (`SplitsFor_v1`).
- **Twins and evidence:**
  - numpy evaluators in `derived_rows.py`, `sampling_rows.py`, `serve3_reference.py`;
  - `conformance.py`, the library's conformance record as data (every Definition also carries a `conformance=` string);
  - `crosscheck.py`, `rmsnorm_fused_sweep.py`, `sampling_topp_difftest.py`.
- **`quarantine/`** is meant for provisional by-name Definitions (import rule at `__init__.py:18`). In practice:
  - `dense/` and `ov_moe/` are re-export shims of promoted Definitions;
  - `ln/` (pythia-160m GELU and LayerNorm) and `ov_sampling/` are the only quarantined Definitions;
  - `collective/` holds an all-reduce that contradicts `b1_tp2`.
- **`lifted.py`, `derived_rows.py`, `ref_prims.py` and `conformance.py`** (named in the prompt) are respectively:
  - generic lifting over the registry;
  - numpy twins of B0/B1 interior values;
  - the torch-CPU reference vocabulary;
  - evidence data.

  None of them is a case.

**Case names.**

| name | meaning | where |
|---|---|---|
| B0 | SmolLM2-135M eager batch-invariant case (the first capture store) | `b1.B0_CONFIG` (`b1.py:47`), `correspondence/capture_identities*`, `rmsnorm_fused_sweep.py` (the "B0 commit store"), `derived_rows.py` |
| B1 | Qwen2.5-1.5B eager batch-invariant case; its program is the lane-TA1 "typed serving program" | `b1.B1_CONFIG` (`b1.py:31`); modules `b1.py`, `b1_tp2.py`, `b1_authored.py`; vocabularies `b1-eager*`; ports `b1-hopper`, `b1-fp8` |
| B1..B5 (+C) | steps of the FA2 inner loop: row max, rescale factor, exp2, per-lane sums, P to bf16 and PV | comments at `b1.py:450-470, 770-784, 1056-1070`, `dense.py:477-527` |
| B6, B7 | LIFTING-SPEC v0.6 sections (B7 = explicit enablement) | `lifted.py:25, 302`, `registry/__init__.py:76, 84` |
| B8 | batch size 8 (the "B8 1024/128" row) | `instances_form.py:5`, `query/manifest/format.py:580`, `correspondence/batch_decomp.py:595` |
| SMOL360, QWEN05 | SmolLM2-360M and Qwen2.5-0.5B configs | `b1.py:64, 80`; `spec.DRAFT_CONFIG` repeats QWEN05 with differences |
| TA1, `Serve@3`, `LServe` | the hand-typed B1 program; the padded serving circuit; the lifted serving circuit | `b1.py`, `serve3.py`, `lifted.py` |

**How much is model-specific.**
- **By-name model data outside quarantine is small:** four HF configs (`b1.py:31-95`) plus `spec.py:37`, the default model (`frontend/vllm_meta.py:30`), A100/Qwen launch signatures (`numerics/kernel_zoo.py`) and Llama/Qwen Inductor constants (`numerics/compiled_*`).
- **The Definitions are mostly parametric.** Statics `K, N, T, NH, KVH, D, BN` let one Definition cover every Llama/Qwen-style dense decoder. Model identity enters through the config dict `C`, bound as a static of `LayerPre`, `LayerPost`, `Final` and `Serve` ("`C` is the whole model config", `profile_descriptor.py:9`), and through which kernels vLLM runs (the vocabulary).
- **Kernel and target specificity is much larger than model specificity.** Every numerical Definition states one kernel's arithmetic on one architecture: Ampere/Ada `mma.sync`, Hopper `wgmma`, FA2 vs FA3 tiles, vLLM d9105ea80's batch-invariant Triton kernels. About half of `registry/` is per-target or per-kernel: `hopper`, `fp8`, `gemm_targets`, `targets`, `topp_split`, `sampling`, `moe`, `dense`. The generic IR machinery is `lifted.py`, `serve3.py`, `pad_prims.py` and the lazy families.

### Map 3: Lowering

Two paths lead from torch to a Program. Both build bodies with `verity.ir.defs.Builder` and serialize with `verity.ir.codec`.

1. **Authoring (`frontend/torch_frontend.py`).**
   - The author writes torch code that calls registered Definitions through minted custom ops (`function`, `bind`, `batch`, `scan`, `Ops`).
   - `torch.export` records the graph. `export` / `export_report` translate it, check identity against the registered bodies, and run liveness (`liveness.py`) and cross-encoding correspondence (`correspond.py`).
   - Only tests, `b1_authored.py`, `serve3_authored.py` and `examples.py` use it. No production path does. Its private helpers (`_tensor_type`, `_permute`, the view algebra) are the shared library of path 2.
2. **Derivation (`frontend/derive.py` + `rules/`).** This is the production path, run by `harness/derive_step.py`.
   1. `vllm_meta.instantiate_meta` builds the pinned vLLM model class on `meta` through vLLM's own config and model registry.
      - Environment variables are set at import. `ensure_distributed` starts a world-1 gloo group. `fake_forward_context` supplies attention metadata.
      - For TP, `WithPeers` wraps the rank with peer inputs, and `probe_collectives` records the collective signature.
   2. `export_compat.export_compat(profile, model)` patches what `torch.export(strict=False)` cannot trace in the pinned vLLM: `Tensor.data`, the device capability and SM count of the declared target, tuned-GEMM caches, MoE dispatcher ops, the workspace manager. `triton_capture.intercept_triton_launches` turns direct Triton launches into `verity_cba::triton_launch` nodes.
   3. `derive._derive_flat` walks the fx nodes.
      - Exactly one rule (`ViewRule`, `OpRule`, `InPlaceRule`, `StateRule` in `rules/base.py`) must claim each node; otherwise the derivation refuses or reports `Unsupported`.
      - Rules bind nodes to Definitions through a vocabulary (`rules/vocab.py`: role to registered Definition, e.g. `attention` to `Attention_v3{T,NH,KVH,D,BN}`).
   4. `vllm_ruleset()` (`vllm_bindings.py:1886`) combines the default rules with the vLLM bindings and the MoE and sampling rules. The vLLM rules check kernel-source pins and the observed target (`_OBSERVED`) before binding.
   5. `derive_report` adds provenance (`provenance.registry_version`, rule applications), liveness and `rules/family.py` identity claims. `correspondence/emit.py` writes the runtime-correspondence record.

   Modes: `profile` (vLLM kernels to the B1 kinds), `reference` (torch-CPU semantics to `ref_prims`), padded (`rules/padding.py` to `Serve@3`).

**vLLM-version specific parts.**
- `rules/vllm_bindings.py:45-67, 143`: source sha256 pins of `matmul_kernel_persistent`, `_rms_norm_kernel`, `mean_kernel`, and the FA implementation and version. The commit `d9105ea80` is named in 12 files.
- `export_compat.py`: patches private vLLM names (`_TUNED_MATMUL_CONFIGS_RESOLVED`, `current_platform`, `num_compute_units`, the `_MOE_DISPATCH_OPS` list).
- `vllm_meta.py`: vLLM's config and model registry, forward context, `init_distributed_environment`. `vllm_iface.py` binds `torch.ops._C.*` names.
- `registry/gemm_targets.py` tuned tables; `global_program.py:139` `CompilationMode` numbering.
- `rules/vllm_moe.py`: the fused-MoE kernel structure.
- vLLM d9105ea80's sampler: `rules/vllm_sampling.py`, `registry/topp_split.py`, `numerics/sampling_rng.py`.
- Inductor-generated kernels (compiled mode): `numerics/compiled_*`, `query/manifest/compiled.py`.

**Model specific parts.** The default model (`vllm_meta.py:30`), the default target (`target_profile.py:114-115`), the `b1.py` configs, Gemma-2 specifics in `dense.py`, and `rules/profile.py` (B0/B1 profile mode). The derivation engine itself is model-agnostic: it derives any model vLLM's registry can instantiate, as long as a rule claims every node.

### Map 4: Collectives

**There is no collective concept in the IR.** Collectives are ordinary registered composites, and core has none:
- `AllReduce2_v1{N}` (`b1_tp2.py:98`): `batch(Bf16Add, parts[0], parts[1])` (`:106`);
- `AllGather2_v1{N}` (`:109`): a copy;
- `AllReduce_v2{WORLD,N}` (`:136`): one-rounding bf16 adds in `allreduce_order`, i.e. ranks WORLD-1..0, NCCL's intra-node tree chain (`:128-134`);
- `AllGather_v1{WORLD,N}` (`:155`) and `EmbeddingShard_v1{VS,H,START}` (`:180`);
- `quarantine/collective/allreduce.py` `AllReduceSumBf16{N,R}`, which folds in ascending order and contradicts `AllReduce_v2` for R > 2. `tp/collective_record.py` still uses it.

**TP has two representations.**
1. **Hand-authored: one Program for all ranks.** `ServeTP2_v1` (`b1_tp2.py:365`) treats the rank as an ordinary `batch` axis (`:7-20`):
   - column-parallel GEMM is `batch(Gemm{K,N/2}, axes=(None,0))`;
   - row-parallel GEMM is `batch(Gemm{K/2,N})` followed by `AllReduce2`.

   The collective is an internal Call, and cross-rank consistency lives inside the Program.
2. **Derived from vLLM: one Program per rank.** This is the production path.
   - At export, `tp/export_ops.py:97` `CollectiveBus` emits `verity_tp::all_reduce2` / `all_gather2` (world 2) and `verity_tp::all_reduce` / `all_gather` / `embedding_shard` (any world size).
   - `vllm_meta.WithPeers` turns the other ranks' partials into extra inputs of the rank's forward (`vllm_meta.py:58-72`). The rules at `vllm_bindings.py:1628-1873` bind these ops to the Definitions above, with W-1 peer partials as prescribed Inputs.
   - The identity "peer input k of rank r equals the committed partial of rank s" is not in any Program. It lives in `tp_links.json`, which `harness/derive_step.py` writes and `tp/match.py`, `tp/rank_match.py`, `tp/fold_match.py`, `observe/resolver.py` and `check/program_compare.py` read. The Commit's cross-rank pass checks it over `b1_tp2.cross_rank_families(world)` (`b1_tp2.py:407`).

**Correspondence.** `correspondence/runtime.py` has a per-Call `CollectiveOccurrence` record. `correspondence/emit.py:30, 318-325` fills it only for `all_reduce2` / `all_gather2` and computes the peer as `1 - own_i`, so collectives over more than two ranks get `collective: null`.

**Query and manifest.** `query/v1_bridge.py` also handles TP outside the Program: rank partials, collective-site numbering (`TP_PEER_BINDING_RULE`) and the TP rank merge. It imports `program.registry.b1_tp2` (`v1_bridge.py:79`).

**Net.** Only the hand-authored `ServeTP2` expresses TP inside a Program. On the production path each rank is its own Program, and a collective's cross-rank meaning is split in two:
- inside the Program: a Call with peer Inputs;
- outside it: a link table plus a Commit pass.

Core `verity.verification` has no notion of a binding across Programs, so this contract lives entirely in `tp/`, `harness/` and `query/`.

---

## 5. Disposition table

`query/`:

| module | disposition | reason |
|---|---|---|
| `query/__init__.py` | keep | fix the stale module list |
| `query/boundary.py` | move to core `verity.ir` | generic `Part` boundary analysis; core already documents the promotion |
| `query/partition.py` | move to core `verity.ir` (with `boundary.py`) | generic partition and width validation over `query_ast.Family` |
| `query/module_body.py` | keep | the vLLM Q; 65 lines over core |
| `query/program_view.py` | keep | drop the `REGISTRY_MODULES` list, `parse_type_repr` (use `type_from_json`) and private-core imports; share one streaming reader with `correspondence/runtime.py` |
| `query/v1_bridge.py` | split and rename | population/policy into a `query/required.py`; row emission into `manifest/format.py`; validation through core `required_values` with a precomputed `Boundary` |
| `query/vu_query.py` | move to `check/` | replay population over a `FoldResult`; depends on check and observe; its sampling should become a `VerificationPlan` |
| `query/query_artifact.py` | keep | drop the `ImportError` fallback and the private `query_id` |
| `query/compare.py` | delete | compares against the deleted v1 engine |
| `query/cli.py` | keep | the one CLI; take Build-dir discovery from one helper |
| `query/manifest/__init__.py` | keep | package marker |
| `query/manifest/format.py` | split | keep schema, digest and identity; move FA/MoE geometry to `program/registry/targets.py`; merge Build-dir lookup with `cli.py`; delete dead helpers |
| `query/manifest/compiled.py` | move to `acquire/` | Inductor-source parsing is capture-side; delete its `verify` copy |
| `query/manifest/verify.py` | keep | the one manifest verify |

`correspondence/`:

| module | disposition | reason |
|---|---|---|
| `correspondence/__init__.py` | keep | package marker |
| `correspondence/runtime.py` | keep | the record; use core `canonical_json` |
| `correspondence/emit.py` | move to `program/frontend/` | lowering code that reads derive's `Ctx`; make collectives work for any world size |
| `correspondence/reader_for_query.py` | merge into one reader over `runtime.py` | same two-source adapter as the other readers |
| `correspondence/reader_for_acquire.py` | merge into the same reader | idem; one `ReturnSlot` / `ArgSlot` |
| `correspondence/runtime_tree.py` | move to `observe/` | runtime observation |
| `correspondence/resolve.py` | keep | occurrence resolution; drop `DescriptorCorrespondence` (use the reader) and migration helpers |
| `correspondence/resolve_decomp.py` | delete | old-vs-new migration check |
| `correspondence/batch_decomp.py` | move to `check/` and split | Match at batch > 1; move the profiling harness out; remove the monkeypatch and X09 hooks |
| `correspondence/batch_candidate.py` | delete | diagnostic; `move_map` marks it DELETE-BY |
| `correspondence/chunk_attribution.py` | move to `observe/` | reads vLLM's scheduler |
| `correspondence/capture_identities.py` | delete | the driver is unused; move its two tables into `check/fold_compare.py` if that stage stays |
| `correspondence/capture_identities_program.py` | delete | no production importer; `move_map` marks it DELETE-BY |

`program/` top level and `lifting/`:

| module | disposition | reason |
|---|---|---|
| `program/__init__.py` | keep | package marker |
| `program/global_program.py` | move to `harness/` and split | CLI driver; separate compilation facts, EOS lag, MoE check, sampler geometry and stop rule; make registry imports hard failures |
| `program/workload.py` | keep | the workload Program |
| `program/compact.py` | move to `commit/` (or a shared storage module) | instance storage form used by check, correspondence and tp |
| `program/descriptor_equivalence.py` | merge into `frontend/correspond.py` | the same §8.5 check; then move to core with it |
| `program/profile_descriptor.py` | move to `tools/` | developer CLI |
| `program/dtypes.py` | move to `commit/` | only `commit/hashing.py` uses it; use `verity.ml.tc.cast` for scalar conversions |
| `program/instances_form.py` | merge into `compact.py` | converter for the same form; `run_config` has its own selector |
| `program/sampling_event.py` | keep | make `query/` use it as the one vocabulary site |
| `program/lifting/__init__.py` | keep | package marker |
| `program/lifting/continuation.py` | keep | host-side Continuation logic |
| `program/lifting/dump.py` | move to tests | test helper |

`program/frontend/`:

| module | disposition | reason |
|---|---|---|
| `frontend/__init__.py` | keep | package marker |
| `frontend/torch_frontend.py` | split | shared Coll/view helpers into a public module for derive and rules; the authoring API stays only if it is wanted, otherwise to tests |
| `frontend/derive.py` | keep | the derivation engine |
| `frontend/vllm_meta.py` | keep | env writes into an explicit call; the default model becomes an argument |
| `frontend/export_compat.py` | keep; isolate per vLLM pin | shims tied to private vLLM names |
| `frontend/target_profile.py` | keep | require an explicit target; use core canonical JSON |
| `frontend/triton_capture.py` | keep | needed for direct Triton launches |
| `frontend/inputs_trace.py` | move to `harness/` | construction-time audit tool |
| `frontend/liveness.py` | move to core `verity.ir` | generic IR analysis |
| `frontend/correspond.py` | move to core `verity.ir` | generic; absorb `descriptor_equivalence.py` |
| `frontend/provenance.py` | keep | `registry_version` could later move to `verity.ir.defs` |
| `frontend/b1_authored.py` | move to tests | fixture |
| `frontend/serve3_authored.py` | move to tests | fixture |
| `frontend/examples.py` | move to tests | fixture |
| `frontend/derive_examples.py` | move to tests | fixture |

`program/frontend/rules/`:

| module | disposition | reason |
|---|---|---|
| `rules/__init__.py`, `rules/base.py`, `rules/common.py` | keep | rule framework |
| `rules/vocab.py` | keep | hash bound Definition ids into `version`; stop swallowing `TypeError`; retire v1/v2 vocabularies once no record needs them |
| `rules/vllm_bindings.py` | split | one module per kernel family (GEMM/norm, KV/attention, dense and unfused norm, FP8, TP); pins into per-vLLM-pin data; pass observations explicitly instead of `_OBSERVED` |
| `rules/vllm_moe.py` | keep | MoE rules |
| `rules/vllm_sampling.py` | keep | sampler rule |
| `rules/vllm_iface.py` | keep | vLLM op interface |
| `rules/triton_iface.py` | keep | rename the `verity_cba` namespace when derived artifacts allow |
| `rules/profile.py` | keep (review) | B0/B1 profile mode; delete with the v1/v2 vocabularies if unused |
| `rules/reference.py`, `rules/patterns.py`, `rules/views.py`, `rules/padding.py`, `rules/family.py`, `rules/ref_kinds.py` | keep | live rule sets |

`program/numerics/`:

| module | disposition | reason |
|---|---|---|
| `numerics/__init__.py` | keep | package marker |
| `numerics/_jit.py` | keep | build at install or CI time instead of first use |
| `numerics/mma.py` | replace with core `verity.ml.tc.models` | after upstreaming the FP16 product |
| `numerics/cpu_model.py` | keep | ctypes wrapper |
| `numerics/relations.py`, `fa2_relation.py`, `rms_relation.py` | keep; move registration into `check/` | no import-time registration into check |
| `numerics/kernel_zoo.py` | move to `registry/quarantine/` (or tests) | A100/Qwen by-name data |
| `numerics/fa2_model.py`, `fa3_model.py`, `rms_triton_model.py` | keep | drop GPU-name sniffing and the `VERITY_ARCH` fallback |
| `numerics/compiled_norm_literal.py`, `compiled_relations.py` | keep | label the Llama/Qwen constants as such |
| `numerics/inductor_models.py` | move to tests | test-only |
| `numerics/libdevice_sampling.py` | merge into `sampling_rng.py` | same noise path; test-only |
| `numerics/sampling_rng.py` | keep | move capture-log reading to `observe/` |
| `numerics/beyond_gemm.py` | split | models used by `crosscheck` into a model module; the probe script to `tools/` |
| `numerics/cpp/*.cpp` | keep | built by `_jit.py` |
| `numerics/cuda/*.cu` | move to `tools/probes/` | measurement sources; two are unreferenced |

`program/registry/`:

| module | disposition | reason |
|---|---|---|
| `registry/__init__.py` | keep | make registration an explicit function |
| `registry/b1.py` | split and rename | generic decoder composites named by job; configs into data; replace `DotBf16_v2` / `GemmCoordinate_v2` / `Gemm_v2` with core `verity.ml.gemm` |
| `registry/b1_tp2.py` | keep, rename (e.g. `tp.py`) | the TP Definitions |
| `registry/hopper.py` | replace with `targets.py` static binding | and core `HopperBF16WgmmaDot16_v1` |
| `registry/fp8.py`, `moe.py`, `moe_pad.py`, `dense.py`, `pad_prims.py`, `serve3.py`, `sampling.py`, `topp_split.py`, `targets.py`, `gemm_targets.py` | keep | live Definitions and target data |
| `registry/spec.py` | move to `quarantine/` | test-only; merge its config with `QWEN05_CONFIG` |
| `registry/prims.py` | keep; replace shared primitives with core `verity.ml.prims` | remove the `sys.path` hack and `np.seterr`; resolve `AmpereBF16TcDot16_v1` |
| `registry/ref_prims.py` | keep | use `register_lazy_family` |
| `registry/lifted.py` | split | lifting core / specified primitives / continuation / `LServe` / checks; drop the imports of `global_program` and `query` |
| `registry/serve3_reference.py` | merge into one twin library | test-only twin |
| `registry/derived_rows.py`, `sampling_rows.py` | merge with `check/twins.py` into one twin library | four twin sites today |
| `registry/sampling_topp_difftest.py` | split | the registry evaluation that `check/` imports goes into `registry/sampling.py`; the cases stay a difftest adapter |
| `registry/conformance.py` | keep | evidence data |
| `registry/crosscheck.py` | move to `tools/` | evidence CLI |
| `registry/rmsnorm_fused_sweep.py` | split | twin into the twin library; delete the sweep driver (its inputs are gone) |

`program/registry/quarantine/`:

| module | disposition | reason |
|---|---|---|
| `quarantine/__init__.py` | keep | enforce the import rule with a lint |
| `quarantine/collective/__init__.py`, `allreduce.py` | delete | contradicts `AllReduce_v2`; point `tp/collective_record.py` at `b1_tp2` |
| `quarantine/collective/allreduce_difftest.py` | move to the difftest adapters (or delete with `allreduce.py`) | operator tool |
| `quarantine/dense/__init__.py` and the 19 op modules | delete | re-export shims; point difftest adapters and profile generators at `registry/dense.py` |
| `quarantine/dense/tables/*` | move to `registry/tables/` | data of the live `MufuTanh_v1` |
| `quarantine/ln/*` (6 files) | keep | true quarantine; fix `_common.py` imports |
| `quarantine/ov_moe/*` (2 files) | delete | re-export shim |
| `quarantine/ov_sampling/*` (2 files) | keep | quarantined Definition |
