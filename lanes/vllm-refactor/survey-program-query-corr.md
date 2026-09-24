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
