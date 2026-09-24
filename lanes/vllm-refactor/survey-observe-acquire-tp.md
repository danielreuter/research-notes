---
id: vllm-refactor/survey-observe-acquire-tp
lane: vllm-refactor
kind: survey
status: in-progress
created: 2026-09-24
checkout: f0810a11 (lane/vllm-cleanup-2)
slice: integrations/vllm/verity_vllm/{observe,acquire,tp,input_provenance}
---
# Survey: observe/, acquire/, tp/, input_provenance/

Read-only survey against `/Users/danielreuter/projects/verity` at `f0810a11`. No Python was run. Evidence is `rg`, `git grep`, `wc` and reading.

Paths below are relative to `integrations/vllm/verity_vllm/` unless they start with `packages/` (verity core, `packages/verity/src/verity/`), `tests/`, `tools/` or another top-level directory. `ops/` means `verity_vllm/ops/`.

## Slice size

| Subpackage | .py files | .py lines | other files |
|---|---:|---:|---|
| `observe/` | 38 | 15,578 | `profiles/expected/*.json` (18 files, 18,669 lines), `profiles/quarantine/*.json` (2 files, 10,266 lines), `profiles/hf_configs/*.config.json` (16 files, 573 lines), `profiles/corpus_coverage.json` (291 lines, a Gutenberg prompt corpus) |
| `acquire/` | 20 | 8,269 | `native_collect.cpp` (1,612), 4 `.cu` kernels (635), FA2 tap sources (`verity_tap_v7.patch` 1,009, `verity_tap.h` 677, `.cpp`/`.cu` stubs), FA3 tap sources (219), `hidden_gpu_tree.cu` (199) |
| `tp/` | 16 | 6,459 | none |
| `input_provenance/` | 4 | 1,857 | none |
| total | 78 | 32,163 | about 30k lines of JSON data and about 4.4k lines of C++/CUDA/patch |

Global counts over the slice (before per-module detail):
- 16 modules end in `if __name__ == "__main__":` and 16 import `argparse` (`tp/worker.py` imports argparse without a main block).
- 14 modules read `os.environ`; the heaviest are `acquire/native_collect.py` (19 reads), `acquire/native_host.py` (14), `observe/vllm_adapter.py` (12) and `observe/engine_profile.py` (8, including writes with `setdefault`).
- `Path(__file__)` / `os.path.abspath(__file__)` arithmetic in 9 modules (`acquire/leafhash.py`, `acquire/native_collect.py`, `acquire/native_jit.py`, `acquire/native_host.py`, `acquire/hidden_gpu_src/hidden_gpu.py`, `input_provenance/weights_of_record.py`, `tp/worker.py`, `observe/profiles/dense_generic.py`, `observe/profiles/canonical.py`).
- verity core imports: only `verity.ir.{defs,refs,types,codec,program}` (`observe/fold.py`, `observe/memory.py`, `observe/patterns*.py`, the `profiles/gen_*` pattern modules, `tp/embedding_shard.py`, `tp/rank_match.py`, `input_provenance/analytic.py`). Nothing in the slice imports `verity.verification.*` or `verity.commitments.*`, although `acquire/` is mostly a commitment engine.
- Cross-subpackage back-edges (file:line in each section): `observe` imports `harness`, `check`, `acquire`, `tp`, `correspondence`, `commit`; `acquire` imports `harness`, `observe`, `correspondence`, `input_provenance`; `tp` imports `harness` (7), `check` (6), `acquire` (4), `query` (3); `input_provenance` imports `check` (3), `query` (3), `harness` (1), `observe` (3).

(Sections below are appended as each module group is finished.)

---

## 1. `observe/` (38 .py files, 15,578 lines, plus about 30k lines of JSON under `profiles/`)

**What it actually does vs its name.** The name promises "the observer". The runtime observer is about 1,100 lines (`observer.py`, `triton_adapter.py`, `storage.py`, `events.py`, `log.py`). The package actually holds five things:
1. The runtime observer itself (the five modules above): a `TorchDispatchMode`, a Triton `JITFunction.run` wrapper, storage ids and the `verity-capture/log/v1` event log.
2. The vLLM engine adapter and capture CLI (`vllm_adapter.py`, `engine_profile.py`, `engine_driver.py`, `arrivals.py`, `m1_capture.py`): engine construction with environment mutation, manifest and profile-id construction, cubin/Inductor code identity, the runner monkeypatch, workload loading and request driving.
3. A compiler front end that has nothing to do with observing (`tree.py`, `views.py`, `memory.py`, `resolver.py`, `patterns*.py`, `fold.py`, `resolve_log.py`): raw log plus profile to an unexpanded Verity `Program`.
4. Model dispatch (`profiles/`): kappa pins for one vLLM/GPU build, a per-`model_type` family-facts table, per-architecture pattern libraries, a `sys.meta_path` finder that fabricates `derived_<ROLE>[_tpW]` modules, HF config copies, 18 expected-profile fixtures and quarantine difftest records.
5. Leftovers that belong elsewhere: the v1 run-directory format that `commit/merkle.py` reads (`capture_v1.py`), a prefix-cache linkage tool (`prefix_cache.py`, `patterns_prefix.py`) and a record-reading adapter (`contract.py`).

### Modules

| module | lines | job |
|---|---:|---|
| `__init__.py` | 17 | docstring and `SCHEMA = "verity-capture/log/v1"`; module list is stale (see DOCS) |
| `observer.py` | 317 | `Observer(TorchDispatchMode)` records every dispatcher call; re-enters custom ops through their registered impls; `EmptyMode` (overhead control); `ModuleNamer` forward hooks; `encode_arg` |
| `triton_adapter.py` | 140 | replaces `triton.runtime.jit.JITFunction.run` process-wide to emit `TritonLaunch` events |
| `storage.py` | 210 | stable allocation ids and generations for tensor storages (weakref free tracking); `ViewDesc` of a tensor |
| `events.py` | 333 | event dataclasses of `verity-capture/log/v1` and their JSON codec |
| `log.py` | 100 | gzip JSONL `LogWriter`, `read_log`, `split_steps` |
| `tree.py` | 167 | rebuild the per-step dispatcher/Triton call forest (`TreeNode`, `StepEvents`) |
| `views.py` | 142 | pure view algebra on `ViewDesc` (row/rows/flat views, contiguity, element runs, byte extent) |
| `memory.py` | 583 | versioned memory model: (allocation, byte interval) to IR `Refs`; unresolved reads; row cache |
| `resolver.py` | 359 | resolution kinds (Compute/Transparent/Unsupported/Group), operand kinds (Shared, PerRow, Gather, Const, Param, Collective), `Profile`, `resolve_step` |
| `patterns.py` | 1,903 | the pattern library: op-name parsing, argument binding, view geometry, transparent-op classes, pin checks, GEMM target selection, and a recognizer for every kernel family (GEMM, bias, RMSNorm x2, RoPE, KV update, FA2/FA3 attention, SiLU, embedding, three sampler chains, logits gather) |
| `patterns_fp8.py` | 158 | FP8 per-token-group quant and sm90 blockwise CUTLASS scaled-mm recognizers |
| `patterns_prefix.py` | 170 | Program-level reading of a prefix-linkage record (state edges, alias obligations, closure) |
| `fold.py` | 1,318 | log + profile to `Captured_v1{PROFILE, WORKLOAD}`: parameter layout, token wiring, resolution execution through `memory`, TP collective parts and `peers` parameters, served/discarded sample rules, access journal, digests, reports |
| `resolve_log.py` | 427 | CLI: resolve a log against a profile, op histogram, JSON/markdown reports, tree dump |
| `contract.py` | 296 | `ValueObservation` / `RuntimeOccurrence` records adapted from record dirs (regex scan of `program.json`) |
| `arrivals.py` | 196 | step-indexed request arrivals; forward attribution from the V1 scheduler's `num_computed_tokens` |
| `engine_driver.py` | 69 | `external_id` (live) and `run_requests` (no callers) |
| `engine_profile.py` | 446 | env pins (`apply_env`), role-to-repo table `CASES`, checkpoint lookup and sha verification, `engine_kwargs`, GPU/software/backend probes (nvidia-smi), `build_manifest`, `profile_id_of` |
| `vllm_adapter.py` | 1,949 | workload loading, engine build, target checks, compile-cache prep, cubin ELF parsing, Triton/Inductor code inventory, profile manifest (+ fallback), request driving, `Capture` (runner monkeypatch, step buffering, pinned D2H copies, snapshots), header/versions/host docs |
| `m1_capture.py` | 320 | capture/control CLI: build engine, install observer (and optionally acquisition hooks), write `log.jsonl.gz`, `tokens.json`, `stats.json`, `versions.json`, analytic tables |
| `capture_v1.py` | 2,102 | v1 run-directory format: leaf/value records, replay-unit index and writer (duplicate detection, taint), slot families, boundary/step/output/cached-prefix records, weights index v1/v2, run writer, lazy readers |
| `prefix_cache.py` | 554 | three CLIs in one: prefix-caching workload generator, KV linkage extractor over a capture log, warm/cold evidence report |
| `profiles/__init__.py` | 62 | installs a `sys.meta_path` finder that fabricates `derived_<ROLE>[_tpW][_ovs]` / `dense_<ROLE>` modules; `profile_for_case` |
| `profiles/generic.py` | 523 | config-derived kappa profile per architecture class (dense, dense-ln, moe), TP rank sharding of the config, module synthesis |
| `profiles/vllm_d9105ea80_sm89_eager.py` | 291 | kappa pins (GEMM/RMS/attention/KV/sampler constexprs), Llama parameter-name map, header check, base pattern list; the B0 profile |
| `profiles/vllm_d9105ea80_sm89_eager_qwen15.py` | 30 | the B1 profile (golden corpus, protected file) |
| `profiles/family_facts.py` | 270 | per-`model_type` table of vLLM hard-codes with source citations (the declared by-name home) |
| `profiles/dense_generic.py` | 150 | HF config lookup over five sources; legacy `dense_<ROLE>` names; test-only shims |
| `profiles/canonical.py` | 232 | canonical JSON form of a profile; CLI that rewrites `profiles/expected/*.json` |
| `profiles/gen_llama_patterns.py` | 108 | `GemmLaunchTuned` (vLLM's tuned GEMM table rows) |
| `profiles/gen_dense2_patterns.py` | 112 | FA2 scope with an inert sliding window |
| `profiles/gen_dense_gemma2_patterns.py` | 403 | Gemma-2 unfused norm / GeGLU / embed-scale chains to quarantine Definitions |
| `profiles/gen_dense_softcap_patterns.py` | 104 | FA2 softcap scope to quarantine `AttentionSoftcap_v1` |
| `profiles/gen_ln_patterns.py` | 267 | GPT-NeoX LayerNorm, erf GELU, residual add, partial rotary |
| `profiles/gen_ov_moe_patterns.py` | 428 | fused-MoE block as pair-major Computes; MoE kernel pins |
| `profiles/gen_ov_sampling_patterns.py` | 249 | Gumbel sampler recognizer for the experimental `_ovs` profiles |
| `profiles/gen_ov_easy_family.py` | 73 | untied serving-family reference (diagnostic; test-only) |

### Findings

**CORE-DUP (3)**
- `observe/engine_profile.py:437-442` `canonical_json_bytes` + `profile_id_of` (sha256[:12] of sorted-key JSON). Core has `verity.commitments.identity.canonical_json_bytes` / `identity_digest` (`packages/.../commitments/identity.py:68,106`); the integration has two more copies (`commit/hashing.py:133`, `correspondence/runtime.py:319`). Core refuses floats and tags the hash, so switching changes every profile id: it needs a decision, not a mechanical swap. *medium*
- `observe/capture_v1.py:49, 200, 263` computes every leaf through `commit.hashing.leaf_hash`, the known copy of `verity.commitments.leaves` (brief). The v1 format bakes the duplicated framing into records. *medium*
- `observe/profiles/canonical.py:80-106` `_jsonable` is a generic object-to-JSON walker used to pin profiles; core `verity.ir.codec` (`canonical_json` at `packages/.../ir/codec.py:317`) owns canonical encoding of IR objects. Only partly overlapping (patterns are not IR). *low*

**INTERNAL-DUP (8)**
- Three request drivers: `observe/engine_driver.py:23-60 run_requests` (no callers), `observe/arrivals.py:98 run_requests_arrivals` (its docstring says it is the former plus one addition) and `observe/vllm_adapter.py:1016 run_requests`. *medium*
- `observe/fold.py:230-258` `_substitute` / `_replayer` are near copies of `program/frontend/derive.py:743-770`. *medium*
- `observe/patterns.py:234-290` `is_row_major`, `sub_rows`, `split_heads`, `as_weight_view`, `as_slot_rows` re-implement `observe/views.py:70-100` (`row_view`, `rows_view`, `is_contiguous`); `patterns.py:24` justifies it with "views.py is a skeleton at the time of writing", which is no longer true. *medium*
- Two ways to reach vLLM internals: `observe/engine_profile.py:192-211` `get_model_runner` / `get_scheduler` and `observe/arrivals.py:45 scheduler_of` walk the same `llm_engine.engine_core[.engine_core]` chain with different fallbacks. *low*
- `observe/profiles/dense_generic.py:127-136 derive_config` is an older subset of `observe/profiles/generic.py:174-200 derive_config`; only `build_dense_profile` (test-only) reaches it. *low*
- `observe/profiles/gen_dense_gemma2_patterns.py:58, 61, 82` and `observe/profiles/gen_ln_patterns.py:35, 70` both define `KERNELS_ELEMENTWISE` and a `_compute` helper; `_scalar` is defined in `gen_dense_gemma2_patterns.py:61` and `gen_ov_moe_patterns.py:61`. *low*
- `observe/profiles/gen_ov_moe_patterns.py:128 ROUTER_VPT_BY_E = {64: 8, 128: 8}` and the formula `observe/profiles/generic.py:161-172 router_vpt_bf16` state the same fact twice and assert they agree. *low*
- Two capture formats in one package: the event log (`events.py`, `log.py`) and the v1 run directory (`capture_v1.py`) are both called "capture format" in docstrings. *low*

**VERSION-RESIDUE (10)** (legit hashed/serialized identifiers listed separately below)
- `observe/m1_capture.py`: the capture entry point of record is named after milestone M1; `:51 ACCEPTED_TOKENS = va.ACCEPTED_TOKENS` is "kept for the older importers". *medium*
- `observe/capture_v1.py`: the module name is a format version; it is imported by `commit/merkle.py:35`, `check/relations.py:40`, `check/poc_required_interface.py:38`, `check/poc_description.py:49`, `harness/synthetic.py:32`. *medium*
- Module names that encode a vLLM commit and GPU: `observe/profiles/vllm_d9105ea80_sm89_eager.py`, `..._qwen15.py`; `observe/resolve_log.py:34 DEFAULT_PROFILE = "vllm_d9105ea80_sm89_eager"`. *medium*
- Lane names in module names: `observe/profiles/gen_ov_moe_patterns.py`, `gen_ov_sampling_patterns.py`, `gen_ov_easy_family.py` (lanes `ov-*`), `gen_dense2_patterns.py`, `gen_ln_patterns.py` (lane `cov-ln`), `gen_llama_patterns.py`; the `_ovs` profile suffix (`observe/profiles/generic.py:54-56, 77-81`). *medium*
- Checkpoint case names as defaults in code: `observe/vllm_adapter.py:68 CASE = "B0"`; `observe/m1_capture.py:140` help "B0 SmolLM2-135M, B1 Qwen2.5-1.5B"; `observe/prefix_cache.py:63-64 PROFILE_LABEL = "B2-prefix"`, `CTX_LABEL = "C256"`, `:86, 114, 520 case="B0"`. *medium*
- `tp2` in the log schema: `RunHeader.notes.tp2` is read at `observe/fold.py:443` and documented at `observe/resolver.py:96`, although the fold is world-parametric since lane `vllm-tp-n` (`fold.py:449-453`). The key is serialized; renaming needs a reader shim. *medium*
- The legacy module name `dense_<ROLE>` ("X-07, the pre-P6 name") is still accepted: `observe/profiles/generic.py:24, 67-74`, `observe/profiles/dense_generic.py:47, 61-68`; plus a glob for "earlier lanes' copies" `*_<ROLE>.config.json` at `dense_generic.py:103-104`. *low*
- `observe/engine_profile.py:255` builds the production manifest with `check.poc_verify_bindings.dist_identity` (a `poc_` module on the record path). *low*
- `observe/fold.py:154 REFERENCE_INTEGRITY_RULE = "R1/2026-09-18"`: a round and date as an emitted rule id. *low*
- Scratch keys named after decisions: `observe/patterns.py:597 X01_SCRATCH_KEY = "x01_num_sms"`, `:631 GEMM_TARGET_SCRATCH_KEY = "r13_gemm_target"`. *low*
- LEGIT (serialized or hashed; do not rename in code without a decision): `verity-capture/log/v1`, `verity-vllm/ru-index/v1|v2`, `verity-vllm/weights-index/v1|v2`, `verity-vllm/profile/v1`, `verity-capture/profile-fallback/v1`, `Captured_v1{PROFILE, WORKLOAD}`, Definition ids (`Gemm_v1`, `AllReduce2_v1`, `AllGather2_v1`, `Fp8GroupQuant_v1`, `ScaledMmFp8Block_v1`, `TokenSelect_v1`, `AttentionSoftcap_v1`), recorded profile ids `vllm-d9105ea80-sm89-eager-…`.

**HARDCODING (9)**
- `observe/engine_profile.py:39-60 CASES`: a role-to-HF-repo table (SmolLM2, Qwen2.5, …, case names B0/B1/B2/B5/B7/M0/M1/M2/SMOL360/QWEN05) outside `program/registry/quarantine/`; `observe/profiles/dense_generic.py:79-87` falls back to it. *medium*
- `observe/profiles/generic.py:333-335 profile_id` prefixes every derived profile with `vllm-d9105ea80-sm89-eager-`, including sm90-only FP8 roles: `observe/profiles/expected/derived_QWEN3_4B_FP8.json:151` is `vllm-d9105ea80-sm89-eager-fp8-block128-qwen3_4b_fp8` for a model that needs the sm90 blockwise CUTLASS kernel. The id misstates the target. *medium*
- `observe/patterns.py:802` (SmolLM2 vs Qwen2 bias), `:1140, :1195` (vllm-flash-attn `506341a1` source lines), `:1519-1520` (vLLM sampler constants `TOPP_STATS_BLOCK, TOPP_STEP_BLOCK, TOPP_FANOUT, TOPP_ROUNDS = 8192, 2048, 8, 5`, `TEMPERATURE_BLOCK = 8192`): the generic pattern library is pinned to one vLLM and FlashAttention build. *medium*
- `observe/vllm_adapter.py:71-76 ACCEPTED` (B0/B1 accepted profile ids and record paths under `out/scale/...`, `fixtures/results/...`) and `:154-156 ACCEPTED_TOKENS` (16 token ids of one B0 request) in the engine adapter. *medium*
- `observe/m1_capture.py:137-138` defaults `--wheel-sha256 7aa52ac7…` and `--vllm-commit d9105ea80`: a run on another build is labelled with the pinned build unless the caller overrides both. *medium*
- `observe/prefix_cache.py:114, 521` default model `HuggingFaceTB/SmolLM2-135M`; `:203 KV_PRODUCER_RE` assumes Llama module names (`k_proj|v_proj|qkv_proj|rope…`). *medium*
- `observe/profiles/vllm_d9105ea80_sm89_eager.py:100-119` the Llama/Qwen parameter-name map, `:273-276` kappa notes (RTX 4090 sm_89, torch 2.13.0, Triton 3.7.1), `:290-291` SmolLM2 model note. Expected inside a pinned profile, but it is also the base every other architecture inherits. *low*
- `observe/profiles/family_facts.py:41-194` per-family table (declared and allowlisted in `tests/by_name_allowlist.json`; this is the intended pattern). Every `provenance` cites `file:line @ d9105ea80`, so a vLLM bump invalidates the whole table. *low*
- `observe/fold.py:862` world-2-only field names (`s<step>_k<k>` at world 2, `…_r<peer>` otherwise) and world-2 Definition identities kept for recorded runs; `observe/vllm_adapter.py:988-995 model_config_subset` hand list of HF keys per family (Gemma softcaps, GPT-NeoX keys). *low*

**SCRIPT/ENV/PATH (8)**
- Import-time environment mutation: `observe/m1_capture.py:44-46` calls `prof.apply_env()` at import; `observe/engine_profile.py:81-86` sets `VLLM_BATCH_INVARIANT`, `VLLM_USE_V2_MODEL_RUNNER`, `VLLM_ENABLE_V1_MULTIPROCESSING`, `VLLM_USE_FLASHINFER_SAMPLER`, `HF_HOME=/workspace/hf` and `HF_HUB_OFFLINE=1`. *high*
- Runtime environment mutation in library functions: `observe/vllm_adapter.py:291-309 prepare_compiled_process_cache` (`TORCHINDUCTOR_CACHE_DIR`, a private marker var, `VLLM_DISABLE_COMPILE_CACHE=1`) and `:324 os.environ.update(target.env())`. *medium*
- CWD-relative defaults: `observe/vllm_adapter.py:313, 348` and `observe/m1_capture.py:122, 124` (`manifests/checkpoints.json`, `workloads/…`); `observe/vllm_adapter.py:1944` and `observe/m1_capture.py:155` read `EXPORT.json` from the CWD; `observe/resolve_log.py:416` writes to `out/capture/reports/`. *medium*
- `Path(__file__)` arithmetic and writes into the package: `observe/profiles/dense_generic.py:48-51` (`parents[3]` to reach `manifests/checkpoints.json` and `data/hf_configs`); `observe/prefix_cache.py:523` writes generated workloads into `observe/profiles/`; `observe/profiles/canonical.py:187, 209-222` rewrites `profiles/expected/`. *medium*
- `SystemExit` raised from library functions: `observe/engine_profile.py:102, 105, 107, 120`. *medium*
- `__main__` + argparse in library modules: `observe/m1_capture.py` (acceptable as a CLI module), `observe/resolve_log.py:360-427`, `observe/prefix_cache.py:514-554`, `observe/profiles/canonical.py:225-232`. *low*
- Env reads that change recorded facts: `observe/engine_profile.py:230` (`RUNPOD_POD_ID`), `:321` (`VLLM_BATCH_INVARIANT`), `:349-350` (NCCL vars); `observe/profiles/dense_generic.py:109` (`HF_HOME`); `observe/vllm_adapter.py:614, 857, 861` (`TRITON_CACHE_DIR`, `TORCHINDUCTOR_CACHE_DIR`). *low*
- Machine paths in usage docstrings: `observe/m1_capture.py:3-5` (`/workspace/venv-cu129/bin/python`, `/vol/cp/l1/m1`). *low*

**LAYERING (8)**
- Cycle observe <-> commit: `observe/capture_v1.py:49` imports `commit.hashing` and `commit.identity`; `commit/merkle.py:35` imports `observe.capture_v1`. The v1 run directory is a commit-layer artifact living in observe. *high*
- observe -> harness: `observe/prefix_cache.py:92, 117, 539` (`harness.coverage_workloads`), `observe/m1_capture.py:49` (`harness.timeline`). *medium*
- observe -> check: `observe/engine_profile.py:255` (`check.poc_verify_bindings`), `observe/vllm_adapter.py:855` (`check.kernel_identity`), `observe/profiles/vllm_d9105ea80_sm89_eager.py:255` (`check.kernel_allowlist`). *medium*
- Cycle observe <-> tp: `observe/profiles/generic.py:41-42` imports `tp.collective_pattern` and `tp.embedding_shard`; `tp/` imports `observe` 22 times. *medium*
- Cycle observe <-> input_provenance: `observe/fold.py:106`, `observe/profiles/generic.py:37`, `dense_generic.py:43`, `canonical.py:27`, `gen_ov_easy_family.py:35` import `input_provenance.analytic` (the weights Record type and config derivation), while `input_provenance/root_policy.py:42-43, 111` imports `observe.events`, `observe.log`, `observe.fold`. *medium*
- Library code reads top-level data dirs: `observe/profiles/dense_generic.py:48-51, 73-76, 115-117` (`manifests/checkpoints.json`, `data/hf_configs`); `observe/vllm_adapter.py:313, 348` default to `manifests/checkpoints.json`. *medium*
- Cycle observe <-> acquire: `observe/m1_capture.py:193-194, 234` imports `acquire.install` / `acquire.stage`; `acquire/compiled_source.py:69` imports `observe.engine_profile`. *low*
- Cycle observe <-> correspondence: `observe/vllm_adapter.py:66` (`correspondence.chunk_attribution`), `observe/contract.py:165` (`correspondence.batch_decomp`); 3 correspondence modules import observe. *low*

**GOD-MODULE (5)**
- `observe/vllm_adapter.py` (1,949): (1) workload loading and execution labels; (2) target parsing and mismatch checks; (3) engine build with env mutation and compile-cache prep; (4) engine introspection (FA version, FlashInfer, async scheduling, compilation facts); (5) cubin ELF parsing and code-identity digests; (6) Triton cache and Inductor loaded-code inventory; (7) profile manifest, profile id and fallback; (8) model-config subset and sampling params; (9) request driving and throwaway warm-up; (10) `Capture`: runner monkeypatch, step buffering, pinned D2H copies, snapshots; (11) header, versions and host docs. *high*
- `observe/patterns.py` (1,903): (1) op-name vocabulary; (2) schema/argument binding; (3) view geometry (duplicate of `views.py`); (4) transparent-op classification; (5) pin checking; (6) GEMM target selection; (7-16) one recognizer per kernel family (GEMM, bias, RMSNorm Triton, fused-add RMSNorm, RoPE, KV update, attention scope, SiLU, embedding, logits gather); (17) three sampler chains; (18) the `ctx.scratch` protocol. *high*
- `observe/capture_v1.py` (2,102): (1) leaf/value records; (2) replay-unit index and writer with duplicate detection and taint; (3) slot families; (4) boundary, step, output and cached-prefix records (`:703-1190`); (5) weights index v1/v2 with row-block leaves; (6) run writer; (7) lazy readers with validation. One format, but 2,100 lines. *medium*
- `observe/fold.py` (1,318): (1) header and parameter layout; (2) token wiring; (3) resolution execution through the memory model; (4) TP collectives and `peers` parameters; (5) served/discarded sample rules; (6) access journal; (7) Program construction and digest; (8) report generation. *medium*
- Under the threshold but multi-job: `observe/prefix_cache.py` (554: generator, extractor, evidence), `observe/engine_profile.py` (446: env, role table, checkpoint verify, engine kwargs, hardware/software probes, manifest). *medium*

**DEAD (7)**
- `observe/engine_driver.py:23-60 run_requests`: no callers. Only `external_id` (`:18`) is used (`harness/commit_delta.py:88`, `observe/vllm_adapter.py:1464`). Searched absolute and relative imports, `-m` in `ops/*.sh`, string references in tests and tools. *high confidence*
- `observe/engine_profile.py:123-126, 158, 171-181` the replay branch of `engine_kwargs`: every caller passes `replay=False` (`tp/match.py:51`, `tp/commit.py:432`, `tp/capture.py:108`, `engine_profile.py:394`, `vllm_adapter.py:332`); `TP_WORKER_EXTENSION` names `verity_vllm.tp.poc_tp_worker`, deleted per `tools/gen_move_map.py:484` ("DELETE-BY:ghost"); `enable_trace_replay` is not a stock vLLM kwarg. *high confidence*
- `observe/vllm_adapter.py:75-76 ACCEPTED_PROFILE_ID`, `ACCEPTED_RECORD`: no readers (the `ACCEPTED` dict only feeds a notes field at `:890-891`). *high confidence*
- `observe/profiles/gen_ov_easy_family.py`: its docstring says "nothing the gates consume"; the only consumer is `observe/profiles/generic.py:520-521` (`mod.SERVE_FAMILY`), read only by `tests/observe/test_gen_ov_easy.py`. Searched `serve_family` / `SERVE_FAMILY` in py and sh. *medium-high confidence*
- `observe/profiles/dense_generic.py:121-150` `supported_family`, `derive_config`, `build_dense_profile`, `make_module`: test-only (`tests/observe/test_dense_generic.py`, `tests/program/test_fp8_profile.py`). `find_hf_config`, `role_of_module`, `checkpoint_entry` are live. *medium confidence*
- `observe/prefix_cache.py` and `observe/patterns_prefix.py`: reachable only from `tests/observe/test_prefix_cache.py` and the module's own CLI; no ops script, harness or check module imports them. Searched `prefix_cache`, `patterns_prefix` over py/sh. *medium confidence (generated workloads may be consumed by file name)*
- `observe/m1_capture.py:51 ACCEPTED_TOKENS` alias: the only readers are two tests that AST-scan for the name (`tests/observe/test_gen_sampling.py:98`, `tests/observe/test_gen_ov_sampling.py:24`). *medium confidence*

**NAMING (6)**
- "profile" has at least five meanings here: the kappa capture `Profile` (`observe/resolver.py`, patterns + config + pins), the "execution profile" (`observe/engine_profile.py:1`, env + engine kwargs), the `verity-vllm/profile/v1` manifest whose hash is the profile id (`engine_profile.py:441`), `TargetProfile` (GPU target), and "serving profile" (`observe/vllm_adapter.py:108`, B8-mixed). There are also two unrelated "profile ids": `observe/profiles/generic.py:333` names a kappa profile, `engine_profile.profile_id_of` hashes a manifest. *high*
- case vs role are one concept with two names: `CASE`, `--case`, `case_of` vs `ROLE`; `observe/profiles/generic.py:504` sets `mod.CASE, mod.ROLE = role, role`. *medium*
- The package name `observe` covers the compiler front end (resolver/patterns/fold) and model dispatch; `m1_capture` names a milestone, `capture_v1` names a format version of a commit-side artifact. *medium*
- `contract.py` is a record-reading adapter; `engine_profile.py` is env + engine kwargs + manifest; `vllm_adapter.py` is everything. *low*
- "kappa" (κ) as a code-level term for the pinned stack (`observe/profiles/*`, `Profile.notes["kappa"]`). *low*
- "accepted" means accepted tokens (`vllm_adapter.py:154`), an accepted record (`:71`) and the `Profile.accepted` flag. *low*

**DOCS (5)**
- Lab-notebook tags throughout: `observe/vllm_adapter.py` (`[R13 hopper]`, `[R15 compiled]`, `[R16 sys int-3, coord M-0213 RULING 21]`, `rev-pm M-0266/M-0268 (b)`, `[r8 E-cleanup, fp16 M12]`, `[coverage D87]`, `[chunked 2026-09-17]`, `lane tp2`), `observe/m1_capture.py:72, 272` (`[R17-1 / DP-pad-02 (b)]`), `observe/fold.py:331, 436, 723, 757` (`[R17 D90, COORD R17-4]`, `[F-r19-tp2-5]`), `observe/arrivals.py:1` ("coverage campaign D87, serving profile B8-mixed"), `observe/profiles/dense_generic.py:1-10` ("[X-07, M-NOPROFILE]", "R12 finding M-NOPROFILE, lane dC", "Daniel's rule"), `observe/profiles/gen_dense_softcap_patterns.py:1-3` ("r8 lane E-cleanup, 2026-09-18 — closes the M10 ADAPTER item", "job 0917T223335-9ad747"), `observe/profiles/gen_ov_moe_patterns.py:1-3` ("Wave 1 … retired in P6"). *medium*
- References to files that do not exist: `observe/observer.py:10` (`observe/capture.py:493-511`), `observe/capture_v1.py:3, 329` (`docs/vllm-poc/capture-format.md`, `docs/vllm-poc/speculative.md`), `observe/engine_profile.py:1, 6` (`CONTRACT.md`), `observe/profiles/vllm_d9105ea80_sm89_eager.py:2, 8, 97, 221` and `observe/__init__.py:9` (`DESIGN.md`), `vllm_d9105ea80_sm89_eager.py:55` (`fixtures/results/B0-535f2cb2cd26-…`), `:79` (`out/curve/e10/KERNEL-GEOMETRY.md`), `observe/profiles/dense_generic.py:28` (`record_v5/ship.sh`). *medium*
- `observe/__init__.py:6-9` lists `census`, `noninterference`, `bench`, `compare` as observe modules (they moved to `check/`). *low*
- Stale statements: `observe/patterns.py:24` ("views.py is a skeleton"); `observe/profiles/gen_dense2_patterns.py:1-2` names retired profile modules (`gen_dense2_phi3_mini`, `gen_dense2_gemma2_2b`); `observe/profiles/generic.py:464` and `observe/fold.py:437` cite renamed modules (`tp2_rank_match`, `tp2_worker.tp2_install`); `observe/profiles/family_facts.py:7-8` points to a Notion findings index. *low*
- Design prose emitted into records: `observe/m1_capture.py:282-283` (the served/executed rule text), `observe/vllm_adapter.py:970-972` (profile-id method notes), `observe/profiles/generic.py:410-474` (profile notes). *low*

**FALLBACKS (7)**
- `observe/vllm_adapter.py:973-983 profile_manifest`: any exception inside `build_manifest` swaps in a different schema (`verity-capture/profile-fallback/v1`) and a profile id hashed from other fields; only `notes["profile_id_method"]` says so. The profile id prefixes every leaf id (`p=<profile_id>/…`). *high*
- `observe/vllm_adapter.py:125-126` merges the hardcoded B0 `ACCEPTED_TOKENS` into every workload's `accepted` map with `setdefault`. *medium*
- `observe/profiles/dense_generic.py:94-118 find_hf_config`: five-source first-hit chain (package copy, legacy `*_<ROLE>.config.json` glob, manifest `local_path`, `$HF_HOME` snapshot, `data/hf_configs`); `:79-82 except Exception: return None` around importing `engine_profile.CASES`. *medium*
- `observe/triton_adapter.py:100-105`: when the private binder call fails, it records positional args and a note instead of failing, so the launch loses named args; `:14` documents a second hook path. *medium*
- `observe/engine_profile.py:311-327 _backends_of_runner` reports the linear backend from the `VLLM_BATCH_INVARIANT` env var rather than from the engine: the manifest attests a fact it did not observe. *medium*
- `observe/m1_capture.py:155` and `observe/vllm_adapter.py:1944`: revision is `"unknown"` when `EXPORT.json` is missing from the CWD. *low*
- `observe/m1_capture.py:196`: `$ACQUIRE_MANIFEST` (`acquire.stage.MANIFEST_ENV`) silently switches on acquisition hooks during capture. *low*

**OTHER-WEIRD (10)**
- Monkeypatching: `observe/triton_adapter.py:30-50` replaces `triton.runtime.jit.JITFunction.run` process-wide and relies on Triton 3.7.1's private `device_caches[device][-1]` binder (`:100`); `observe/vllm_adapter.py:1391-1392, 1412` replace `runner.execute_model`, `runner.sample` and `model.compute_logits` on live objects; `observe/observer.py:62-82, 219-226` re-enters custom ops by calling their registered implementations directly. Inherent to capture, but spread over three modules with no single install/uninstall owner. *high*
- `observe/profiles/__init__.py:13-39` installs a `sys.meta_path` finder at import that fabricates modules (`observe/profiles/generic.py:487-523`, including `mod.__file__ = __file__`); consumers pick profiles by building module-name strings for `importlib`. *medium*
- The profile id depends on the host: `observe/engine_profile.py:230` records `RUNPOD_POD_ID` or the hostname as `gpu.pod` inside the hashed manifest (`observe/vllm_adapter.py:970-972` notes the id "differs … by construction: gpu.pod, gpu.driver, adapter.revision"). Leaf ids change per pod. *medium*
- Patch-after-build manifest: `observe/vllm_adapter.py:911-968` overwrites about 15 fields of `build_manifest`'s result (dtype that `build_manifest` "hard-codes" as bfloat16, generated-kernel placeholders, async scheduling, FA version, FP8 kernel, compile facts). *medium*
- Latent bug: `observe/engine_profile.py:105` formats an undefined `repo`, so the intended `SystemExit` becomes a `NameError`. *medium*
- Hidden ordered state between patterns: `ctx.scratch` keys (`observe/patterns.py:445 int_copies`, `:597`, `:631`, `:1360 token_select`, `:1565 topp_token_select`; `observe/profiles/gen_ov_sampling_patterns.py:38`). Correctness depends on first-match order in the profile's list. *medium*
- `observe/contract.py:127-160 _program_json_layout` regex-scans `program.json` text for `n_input_nodes`, `digest`, `params`, `tp` instead of parsing it. *medium*
- Private helpers imported across modules: `observe/profiles/gen_dense_gemma2_patterns.py:53`, `gen_ln_patterns.py:30`, `gen_ov_sampling_patterns.py:34` import `_check_pins`, `_fmt`, `_group_compute`, `_positions_ok` from `patterns.py`. *low*
- Subprocess and host probing in library code: `observe/engine_profile.py:213-224` (`nvidia-smi`), `observe/vllm_adapter.py:1882-1911` (`/proc/cpuinfo`, `/sys/fs/cgroup/cpu.max`). *low*
- Data in the package tree: `observe/profiles/quarantine/GEMMA2_2B.json` (9,143 lines), 18 expected fixtures (18,669 lines) and `profiles/corpus_coverage.json` (a Gutenberg prompt corpus used only by `harness/workload.py:41` and `harness/coverage_workloads.py:38`); `observe/profiles/family_facts.py:22, 270` exports an unused `math`; `observe/profiles/canonical.py:187` and `generic.py:508` use inline `__import__("pathlib")`. *low*

Counts for `observe/`: CORE-DUP 3, INTERNAL-DUP 8, VERSION-RESIDUE 10, HARDCODING 9, SCRIPT/ENV/PATH 8, LAYERING 8, GOD-MODULE 5, DEAD 7, NAMING 6, DOCS 5, FALLBACKS 7, OTHER-WEIRD 10.

---

## 2. `acquire/` (20 .py files, 8,269 lines, plus about 4.4k lines of C++/CUDA/patch)

**What it actually does vs its name.** The name promises value acquisition, and about 900 lines do that (`plan.py`, `install.py`, `stage.py`, `gate.py`): derive from the required-value manifest and the runtime correspondence where each required Value can be read, then install exactly those hooks. The other 7,300 lines are a GPU commitment engine and its kernel taps: two committer classes (pinned-memory and device-arena staging, SHA-256 chunk-leaf Merkle trees on host and GPU, padding, run roots, openings, verification, coverage declarations, capacity planning), four acquisition "sources" that each monkeypatch a different layer of vLLM or torch, and the build tooling for two patched FlashAttention forks. Only one committer configuration (`native_collect_v2b`) is used by any ops script.

### Modules

| module | lines | job |
|---|---:|---|
| `__init__.py` | 15 | package docstring; lists `correspondence` and `runtime_tree` (now in `correspondence/`) and omits the committer (see DOCS) |
| `plan.py` | 475 | `acquisition_plan(manifest, correspondence)`: Value classes, candidate sites per Value, policy choice, residual tables, `acquisition-plan/v1` body and digest |
| `install.py` | 237 | installs the plan's hooks (forward hooks plus a `runner.sample` wrapper) into an `OccurrenceSink`; `apply_plan_to_committer` rewrites a committer's module list |
| `stage.py` | 56 | the plan at a GPU stage's entry: live runtime tree, manifest from an argument or `$ACQUIRE_MANIFEST`, writes `runtime_tree.json` and `acquisition_plan.json` |
| `gate.py` | 129 | CPU gate CLI: the plan of one row from a meta-device runtime tree; plan-vs-plan comparison |
| `committer_api.py` | 113 | `Committer` protocol, `StepCommitment` / `RunCommitment` / `Opening`, Fiat-Shamir `challenge_positions`, coverage-declaration schema |
| `native_host.py` | 2,587 | base committer: module-class tables, pinned-host and device arenas, capacity bounds, hooks and runner patch, D2H staging, host and GPU chunk trees, padding steps, run root, manifest identity check, openings, verification, coverage declaration |
| `native_collect.py` | 1,940 | the production committer (`native_collect_v2b`): JIT-built C++ collector, `module.forward` wrappers, gather windows, windowed and bounded staging, FA2/FA3 native tap sources, top-p split-kernel proxies, fault injection |
| `hidden_source.py` | 411 | FA2/FA3 hidden-value tap source: swaps vLLM's attention op for a patched FlashAttention build; tap geometry and stream names |
| `fa2_plane_classes.py` | 363 | expected per-layer FA2/FA3 hidden-plane inventory of a step (attention statics x active sequences) and its check |
| `moe_source.py` | 184 | fused-MoE interior values: wraps three vLLM MoE launch sites and snapshots router, up, act, down and sum |
| `compiled_source.py` | 520 | acquisition under torch.compile + CUDA graphs: `verity::collect_c` custom op, Inductor lowering, class patches of `VllmBackend.__call__` and `GPUModelRunner.load_model` |
| `compiled_kernel_source.py` | 325 | acquisition at Inductor-kernel granularity through a patched Inductor debug printer |
| `leafhash.py` | 79 | device-side weight hashing (JIT CUDA) with host / device / device-checked modes |
| `native_jit.py` | 75 | source-digest-keyed build directory and pybind binding checks for the native collector |
| `hidden_gpu_src/hidden_gpu.py` | 226 | GPU chunk-tree driver (JIT) with a check/bench/commit CLI; imported by `sys.path` manipulation |
| `fa2_tap_src/apply_v8.py` | 69 | turns a pinned vllm-flash-attn tree into the "v8" tapped tree (`git apply` plus text edits) |
| `fa2_tap_src/build_ext.py` | 117 | builds one FA2 forward variant as a torch extension (sm_80) |
| `fa3_tap_src/apply_fa3_tap.py` | 235 | text-patches the FA3 (hopper) sources with the M1 tap |
| `fa3_tap_src/build_fa3_ext.py` | 113 | builds the tapped or untapped FA3 extension (sm_90a) |

### Findings

**CORE-DUP (3)**
- The production commitment stack does not use core. `acquire/` imports `verity.commitments` zero times and `verity_vllm.commit` 13 times (`acquire/native_host.py:52, 1428, 1504, 1601, 1983, 2460, 2467`, `acquire/native_collect.py:1368, 1771, 1857`, `acquire/leafhash.py:74`). Tree folding goes through `commit/fasttree.py:97 fold_levels` (same pairing/lift rule as `packages/.../commitments/leaves.py:184 levels`), opening verification through `commit/hidden_engine.py` `fold_path` (core has `leaves.py:151 path_shape`, `:169 fold_path`, `:276 verify_opening`, `:304 LeafTree`), and roots are bound with integration tags (`acquire/native_host.py:57 ROOT_TAG_RUN = b"verity/cmt-integ/run-root/v0"`, `commit/hidden_engine.py:34 ROOT_TAG`). The chunk-leaf framing (`verity/pos-leaf/v0`, `commit/semantic_layout.py:150`) has no core equivalent, so the fix is a core tree with a pluggable leaf hash, not a straight swap. *high*
- `acquire/native_host.py:407-418 _open_levels` computes the sibling path over device level tensors with the same rule as core `packages/.../commitments/leaves.py:198-209 open_path`; a third copy is `commit/hidden_engine.py:92-103 path_in_levels` and a fourth `hidden_gpu.gpu_open` (cited at `native_host.py:408`). *medium*
- `acquire/committer_api.py:26-62` defines `StepCommitment`, `RunCommitment` and `Opening` records; core has `packages/.../commitments/leaves.py:224 LeafOpening` and `commitments/merkle.py` `Opening` (same name, different shape). *low*

**INTERNAL-DUP (5)**
- FlashAttention geometry rules are written at least four times: `acquire/hidden_source.py:35 fa2_kblock_n`, `:48 fa2_swapped`, `:61 mat_total_words`, `:241 fa3_tile` (whose docstring at `:245` says it is "the same rule as `program.registry.targets.fa3_kblock_n`"), `program/registry/b1.py:379 fa2_kblock_n`, `program/registry/targets.py:100 fa3_kblock_n`, `check/fa2_attn_oracle.py:42 fa2_kblock_n`, `query/manifest/format.py:297 mat_total_words`; `acquire/native_host.py:507-510` and `:768-771` define the nested `hidden_words` / `launch_words` twice in one module; `KBLOCK_N` is 128 in `commit/hidden_stream.py:38` and `program/numerics/fa3_model.py:52` but 64 in `program/numerics/fa2_model.py:39`. *high*
- Two live module-selection mechanisms: the plan (`acquire/plan.py`) and the hand-written tables it is meant to replace (`acquire/native_host.py:64-76 ACQUIRE_CLASSES` / `ACQUIRE_INPUT_CLASSES` / `SKIP_CLASSES`, `:1617 HAZARD_LEAVES`, `:2491 FAMILY_OF_MODULE`, `acquire/native_collect.py:199-203` flush tables). TP rank committers and compiled rows still select by the tables (`acquire/__init__.py:4-5`, `native_host.py:60-62`), and the plan reads its residuals back from the committer classes (`plan.py:371-377`). *medium*
- Four Fiat-Shamir challenge derivations: `acquire/committer_api.py:76-103 challenge_positions`, `commit/binding.py:676 challenge_identities`, `check/relations.py:547 make_challenge`, `check/sampled_replay.py:2522 challenge_seed`; core has none. *medium*
- Five native build paths with different staleness rules: `acquire/native_collect.py:143 ext` (keyed by source digest through `native_jit.py:34`), `acquire/leafhash.py:32 ext` (`$VERITY_LEAFHASH_BUILD`), `acquire/hidden_gpu_src/hidden_gpu.py:73` (`$HIDDEN_GPU_BUILD`), `acquire/fa2_tap_src/build_ext.py` and `acquire/fa3_tap_src/build_fa3_ext.py` (argparse `--build-dir`). `native_jit.py:1-14` documents why mtime-keyed builds are unsafe (a stale `.so` killed every Commit on one pod), but only one of the five uses the fix. *medium*
- Program-directory discovery: `acquire/gate.py:38-41` globs `build_request*` with a `result.json`, while `input_provenance/weights_of_record.py:820-823`, `tp/commit.py:484` and `harness/commit_delta.py:1848` glob `build_request_LP*_T*`; `build_paths.py` exists to own this layout. *low*

**VERSION-RESIDUE (6)** (legit hashed/serialized identifiers listed separately below)
- Nine committer arms stay reachable from `harness/commit_delta.py:410-442` (`native_host`, `native_host_direct`, `native_collect`, `native_collect_hook`, `native_collect_gather`, `native_collect_v2`, `native_collect_v2_memcpy`, `native_collect_v2_auto`, `hooks_only`), with their code paths inside `acquire/native_collect.py` (non-wrap hook path, per-hook profiling, Python worker) and `acquire/native_host.py`; the variant name is assembled from flags at `native_collect.py:757-763`. Every ops script uses `native_collect_v2b` (`ops/canary.sh`, `compiled_commit.sh`, `fa3_row_negatives.sh`, `row_pod.sh`, `tp_stage.sh`). *medium*
- `acquire/native_collect.py:721-723` `VERITY_LAYOUT=chunk-leaf-v1|chunk-leaf-v2` switches the committed leaf layout by environment variable, and v2 exists only on the windowed path. *medium*
- `acquire/hidden_source.py:29-32` `KBLOCK_N = 128  # legacy constant` and `LEGACY_TILE` ("same stream layout, names and roots as before R13"), the `self.v8` switch (`:137`), and tap versions in file names (`fa2_tap_src/apply_v8.py`, `verity_tap_v7.patch`, "layout v9" in `fa3_tap_src/apply_fa3_tap.py:2`). *low*
- `acquire/native_host.py:168 EXACT_MODES` keeps `"exact-registered"`, "retired by F-fp8-FORKPIN". *low*
- `acquire/plan.py:37 AnnotationCorrespondence = AcquireCorrespondence` re-exports a former name (already aliased at `correspondence/reader_for_acquire.py:215`); five test files use it. *low*
- `acquire/install.py:229` stamps `"engine": "v2"` into its record; `acquire/__init__.py:1` "(v2, Phase 4a)". *low*
- LEGIT (hashed or serialized): `acquisition-plan/v1`, `verity-vllm/acquisition-plan-compare/v1`, `verity/commit-integ/coverage-declaration/v1`, the hash tags `verity/cmt-integ/run-root/v0`, `verity/cmt-integ/challenge/v0`, `verity/pos-leaf/v0`, `verity/fa2c/root/v0`, and the Definition ids in `COVERS_FAMILIES` (`MoeRouterTopK_v1`, `MoeExpertGemm_v1`, `SiluMul_v1`, `MoeExpertGemmW_v1`, `MoeSum_v1`).

**HARDCODING (5)**
- By-name lifetime and selection facts outside `program/registry/quarantine/`: `acquire/native_host.py:64-76` (vLLM class names), `:1617 HAZARD_LEAVES = ("qkv_proj", "o_proj", "down_proj", "embed_tokens", "sampler")` (comment at `:1610`: "vLLM (d9105ea80, Llama architecture)"), `:393-400 FAMILY_RULES` (substring of tensor name to value family), `acquire/native_collect.py:199-203` (`GATHER_FLUSH_LEAVES = {"qkv_proj", "o_proj", "down_proj", "q_norm", "k_norm"}`, `PRE_FLUSH_LEAVES = {"input_layernorm", "norm"}`, `MOE_FLUSH_PLANES`). The docstring (`native_host.py:3-4`) says they are pinned by `tests/test_no_by_name_rules.py`. *medium*
- Magic constants measured on one model: `acquire/native_host.py:462-466` (`_ARENA_SAFETY = 1.25  # decode steps: measured 2.50 MB vs bound 2.72 MB (Llama-3.2-1B, 48/16)`, `_ARENA_SAFETY_PREFILL = 1.5`, `_ARENA_MIN = 512 MiB`). *medium*
- Monkeypatch targets spelled as vLLM/torch internals: `acquire/native_collect.py:612-614` (`vllm.v1.sample.ops.topk_topp_triton` and three private kernel names), `acquire/moe_source.py:36` (MoE class names), `acquire/compiled_source.py:245` (two runner module paths for two vLLM layouts), `acquire/compiled_kernel_source.py:48` ("DebugPrinterManager (torch 2.13)"). *medium*
- FlashAttention pins and build defaults: `acquire/hidden_source.py:1-4` (vllm-flash-attn `506341a1`, `VERITY_TAP=3`, `VERITY_MAT_SRC=63`), op namespaces `verity_fa2_matAll` / `verity_fa3_matReq` (`native_collect.py:213, 419`), `fa2_tap_src/build_ext.py:35, 40` (`--arch 8.0`, `CUDA_HOME=/usr/local/cuda-12.9`), `fa3_tap_src/build_fa3_ext.py:37, 42` (`9.0a`, `/usr/local/cuda`). *low*
- `acquire/native_collect.py:769-770` default of 32 gather blocks per descriptor ("R10's labelled-extra Llama geometry"). *low*

**SCRIPT/ENV/PATH (6)**
- Environment variables change committed behaviour: `acquire/native_collect.py:714-787` reads `VERITY_WINDOW_MB`, `VERITY_WINDOW_SLOTS`, `VERITY_LAYOUT` (changes the leaf layout, so the root), `VERITY_STAGING_BOUNDED`, `VERITY_LEARN_HOST_BUDGET_MB`, `VERITY_RETAIN_EXCLUDE`, `VERITY_HI_PRIO`, `NATIVE_GATHER_BLOCKS`, `NATIVE_GATHER_AUTO_BYTES`, `VERITY_CONSUMER_DELAY_MS`, `VERITY_FAULT`; `:217-223, 423` (`VERITY_FA2_COMPACT`, `VERITY_FA2_ZERO`, `VERITY_FA2_TAP_CAP_MB`, `VERITY_FA3_ZERO`); `:1339-1350` (watchdog vars); `acquire/native_host.py:87-89` (`VERITY_SKIP`), `:133` (`VERITY_PINNED_EXACT`, read at import), `:816` (`VERITY_MEMTRACE`, at import), `:915` (`VERITY_FOOTPRINT`); `acquire/leafhash.py:25-26` (`VERITY_WEIGHTS_HASH`). *high*
- `acquire/native_host.py:1376-1424 _gpu_ext_load` finds the repo root from `__file__`, prepends `<tree>/out/gen/r9/cmt-hidden/src` (or `acquire/hidden_gpu_src`) to `sys.path`, imports `hidden_gpu` as a top-level module, reads `HIDDEN_GPU_BUILD` and `VERITY_SOURCE_IDENTITY_DIR`, writes a JSON file and calls torch's private `_get_build_directory`; `acquire/hidden_gpu_src/hidden_gpu.py:18-42` also reads `VERITOR_REPO` (the old repo name) and edits `sys.path`. *high*
- `acquire/stage.py:22 MANIFEST_ENV = "ACQUIRE_MANIFEST"` passes the manifest path by environment "when the stage's CLI has no flag for it"; `observe/m1_capture.py:196` switches acquisition on when it is set. *medium*
- `acquire/compiled_source.py:225` sets `os.environ["VLLM_DISABLE_COMPILE_CACHE"] = "1"` process-wide. *medium*
- Build tools inside the package: `fa2_tap_src/apply_v8.py` (`subprocess` `git apply`), `fa2_tap_src/build_ext.py`, `fa3_tap_src/apply_fa3_tap.py`, `fa3_tap_src/build_fa3_ext.py`, `hidden_gpu_src/hidden_gpu.py`: five `__main__` scripts that set `CUDA_HOME`, `TORCH_CUDA_ARCH_LIST` and `MAX_JOBS` (`build_ext.py:40-42`, `build_fa3_ext.py:42-44`), driven by `ops/pod_fa2_tap.sh`, `ops/pod_fa3_tap.sh`, `ops/pod_hidden_gpu.sh`. *medium*
- Machine paths in docstrings: `acquire/native_jit.py:5` (`/workspace/cp/nc_build`), `acquire/hidden_gpu_src/hidden_gpu.py:18` (`/workspace/cp/veritor`). *low*

**LAYERING (3)**
- Cycle acquire <-> commit: the committer imports `commit.hidden_engine`, `hidden_stream` and `padding_steps` (13 imports, listed under CORE-DUP), while `commit/__init__.py` and `commit/reference_engine_adapter.py` import `acquire.native_host` / `acquire.committer_api`. The commitment engine is split across two packages. *high*
- Cycle acquire <-> harness: `acquire/native_host.py:54` imports `harness.spans` at module level and `:1392` imports `harness.source_identity`; four harness modules import acquire. *medium*
- Cycles inside acquire: `acquire/native_host.py:1409` (base class) imports `native_collect._clear_stale_jit_lock` (subclass module); `acquire/plan.py:371-377` imports `native_collect` and `native_host` for its residual tables; `native_host` imports `plan` / `install` back. *medium*

**GOD-MODULE (3)**
- `acquire/native_host.py` (2,587): (1) module-class tables and the `VERITY_SKIP` ablation; (2) pinned host allocator (mmap + `cudaHostRegister`, pools); (3) device arena allocator; (4) capacity math (`schedule_stream_bound`, `bounded_host_bound`, `step_bound_bytes`, `size_arena`); (5) memory footprint tracing; (6) hook install and runner monkeypatch; (7) per-step acquisition and D2H staging; (8) GPU extension loading with a source-identity precheck; (9) host hashing worker and CPU pinning; (10) GPU tree commit; (11) padding steps; (12) finalize and run root; (13) expected manifest and a 134-line `identity_check`; (14) openings and verification; (15) coverage declaration. *high*
- `acquire/native_collect.py` (1,940): (1) JIT build and stale-lock clearing; (2) native FA2/FA3 tap sources; (3) retained host windows and ranges; (4) retain-exclude families; (5) top-p split-kernel proxies; (6) the committer subclass with Python and C++ wrappers, gather flush points, windowed staging (`_commit_step_windowed`, `:1362-1767`, about 405 lines in one method), native worker, bounded learning steps and fault injection. *high*
- Under the threshold but multi-job: `acquire/compiled_source.py` (520): op registration, Inductor lowering, two class patches, graph renumbering, slot staging, eager fallback. *low*

**DEAD (4)**
- `acquire/native_host.py:2319-2331`: the first `layouts_dump` is shadowed by a second definition in the same class at `:2333-2340`; Python keeps the last. The two return different keys (`ordinal` vs `first_leaf`, `n_leaves`, `stream_off`); the only caller is `harness/commit_delta.py:2097`. *high confidence (language semantics)*
- `acquire/hidden_source.py:29 KBLOCK_N`: no reader (searched `\bKBLOCK_N\b` over the integration; other modules define their own). *high confidence*
- References to missing files, including the only named evidence that the patched FlashAttention kernels are bit-identical to vLLM's: `fa2_tap_xcheck.py` and `fa3_tap_xcheck.py` (`acquire/hidden_source.py:234, 387`, `acquire/fa3_tap_src/build_fa3_ext.py:11`, `ops/pod_fa2_tap.sh:18`, `ops/pod_fa3_tap.sh:12`), `hidden_tap.kernel_geometry` (`hidden_source.py:5`), `check_base.json` / `xcheck_m1.json` (`:8`), `out/gen/r9/cmt-hidden/API.md` (`:2`), `out/gen/r10/acq-live/lifetimes.md` (`native_collect.py:178`), `out/gen/r8/fa2-commit/derived_value_rule.md` (`native_host.py:2559`), `required_manifest.coverage_check` (`native_host.py:2320, 2334`; now `query/manifest/format.py:514`). Searched `rg --files` over the whole repo. *high confidence*
- The eight non-`native_collect_v2b` committer arms: no ops script names them, and tests name only `native_collect_v2b` and `native_collect_v2_auto` (searched all nine names over `ops/*.sh` and `tests/`). Reachable through `commit_delta --committer` and direct construction. *medium confidence*

**NAMING (5)**
- `acquire` names the 11% of the package that plans acquisition; the rest is the commitment engine (committers, trees, openings, verification, coverage declarations, capacity planning). *medium*
- "native" means C++ hook bodies (`native_hooks`), the GPU-resident tree, the "naturally materialised" interface class (`native_host.py:1`) and host-side hashing (`native_host`). *medium*
- Committer variant names are composed from flags (`native_collect_v2_nw_hp`, `…-STRESS[skip_copy:3+delay5ms]`, `native_collect.py:757-763, 786-787`) and docstrings call them "arm 2", "arm 3", "candidate B" (`native_collect.py:1, 690, 752`). *medium*
- `FAMILY_RULES` means tensor-name-to-value-family here (`native_host.py:393`) and per-model-family config rules in `input_provenance/analytic.py:39`; `committer_api.Opening` collides with core's `merkle.Opening`. *low*
- `gate.py` is a CPU plan builder and comparer ("the CPU gate"); "gate" means many things across the integration. *low*

**DOCS (4)**
- Lab-notebook docstrings: `acquire/native_host.py:1-26` ("EXPERIMENTAL (R9 CMT-3)", "DANIEL-BRIEF A2", "Draft 3 §12"), `:140-153` (`[R17 fp8, F-fp8-POW2]`, `F-fp8-FORKPIN (B8 attempt 2, 03:0xZ)` incident narrative), `:1383-1415` (`[R18 infra, F-r17-tp-06]`, "R13 07:24Z: 3 runs 'hung' here", "[R17 fp8, 04:37Z cp-h100]"), `acquire/native_collect.py:1-49` ("Candidate arm 3 (R10 acq-native)"), `:724-736` (`[R17 fp8, F-fp8-B8MEM]`, "two OOM-kills, R16"), `acquire/native_jit.py:1-14` ("COORD R17-41 (1), stoch M-0756 / rel M-0803", pod names and timestamps), `acquire/fa2_plane_classes.py:1` ("X-03 … (F-r19-int-22)"), `acquire/moe_source.py:1` ("[R13 moe / MOE-03]"), `acquire/compiled_source.py:1-3` ("R15 lane compiled", "M-0055, F-dse-12 at rc3"), `acquire/compiled_kernel_source.py:1` ("DECISIONS-2 §7; M-0389 tier (b)"), `acquire/leafhash.py:1` ("[R16 sys SYS-05]"). *medium*
- Stale status: `acquire/native_host.py:6` calls the base class of the only production committer "EXPERIMENTAL", and `native_collect.py:1` calls the production committer "Candidate arm 3". *medium*
- `acquire/__init__.py:6-11` lists `correspondence` and `runtime_tree` as acquire modules (they are `correspondence/reader_for_acquire.py` and `correspondence/runtime_tree.py`) and does not mention the committer, which is 7,300 of the 8,269 lines. *medium*
- `acquire/native_host.py:22` points to `verity_vllm.commit.merkle.path_shape` / `fold_path` for verification while the code verifies through `commit.hidden_stream` / `commit.hidden_engine` (`:2460-2467`). *low*

**FALLBACKS (5)**
- `acquire/plan.py:371-377 _lifetime_tables`: if importing `native_collect` fails (it imports torch at module level), the flush tables silently become empty. `residuals_of` then emits no flush residuals (`:397-401`), and residuals are part of the digested plan body (`:161-172`, `:194-201`). The same Program, manifest and tree therefore get a different `plan_digest` on a torch-less CPU gate than on the GPU stage. The tests pass `tables=` explicitly (`tests/acquire/test_install.py:75`), which hides it. *high*
- `acquire/compiled_source.py:234-239` swallows graph-renumbering errors into `self.errors`, and `:245-249` silently skips runner modules that fail to import (two vLLM layouts). *medium*
- `acquire/native_host.py:1380-1385` imports `hidden_gpu` from the generated `out/gen/r9/…` copy when present, else the shipped copy: two sources for one module, disambiguated only by the source-identity precheck that follows. *medium*
- `acquire/native_collect.py:644-651 install_split_kernel_proxies` returns `{}` on any import error (documented: the split rows then fail coverage later); `acquire/native_host.py:1276` appends sampler acquisition errors to `self.errors` and continues. *low*
- `acquire/native_host.py:1416-1421` `except Exception: pass` around torch's private `_get_build_directory`. *low*

**OTHER-WEIRD (6)**
- Seven independent monkeypatch sites, each with its own install/uninstall: `acquire/hidden_source.py:149-153, 306-310` (replaces `torch.ops._vllm_fa2_C.varlen_fwd` / the FA3 `fwd` with a patched FlashAttention build), `acquire/moe_source.py:101-109` (three MoE launch sites), `acquire/native_collect.py:644-667` (three top-p Triton kernels in vLLM's module namespace), `:818-823` (`module.forward` on instances), `acquire/native_host.py:1244-1276` (`runner.execute_model`, `runner.sample`), `acquire/install.py:159-173` (`runner.sample` again; `observe/vllm_adapter.py:1391-1392` wraps it a third time), `acquire/compiled_kernel_source.py:41-48` (torch Inductor `DebugPrinterManager.codegen_intermediate_tensor_value_save`). *high*
- `acquire/compiled_source.py:231-265` patches `vllm.compilation.backends.VllmBackend.__call__` and `GPUModelRunner.load_model` at class level, registers a torch custom op (`:102`) and an Inductor lowering (`:140`), and routes the op to a module-global `_SRC` (`:50, 221-224`); `uninstall()` is `pass` (`:389-390`), so none of it is undone in the process. *high*
- Fault injection in the production class: `acquire/native_collect.py:28-49, 782-787` (`VERITY_FAULT=release_before_keep|drop1_dup0|skip_copy:<k>|hang_after_dead`, `VERITY_CONSUMER_DELAY_MS`), `_commit_step_gpu_faulty` (`:1825`), and `acquire/compiled_source.py:187`. Labelled in the committer name, but it lives in the hot path. *medium*
- A custom pinned-memory allocator inside the committer: `acquire/native_host.py:137-165` (anonymous shared `mmap` + `cudaHostRegister` through `torch.cuda.cudart()`), `:1718 _load_cudart` (ctypes). Justified by documented incidents, but surprising here. *low*
- `acquire/install.py:226, 234` writes the committer's private `_modules`; `:42` uses `assert` for a plan-consistency check (dropped under `python -O`). *low*
- `acquire/committer_api.py:94-103` draws challenge positions with replacement, so a k-position challenge can repeat positions. *low*

Counts for `acquire/`: CORE-DUP 3, INTERNAL-DUP 5, VERSION-RESIDUE 6, HARDCODING 5, SCRIPT/ENV/PATH 6, LAYERING 3, GOD-MODULE 3, DEAD 4, NAMING 5, DOCS 4, FALLBACKS 5, OTHER-WEIRD 6.

---

## 3. `tp/` (16 .py files, 6,459 lines)

**What it actually does vs its name.** The name suggests general tensor-parallel support, and the package docstring says it is a torch-free linkage tool. In fact it holds four things: (1) the rank-process seam, a class mixed into every rank's vLLM Worker through `worker_extension_cls` that installs the observer, a collective recorder and the committer in each rank; (2) TP twins of the single-rank drivers (`capture.py` of `observe/m1_capture.py`, `commit.py` of `harness/commit_delta.py`, `match.py`, `fold_match.py`); (3) fold-side patterns and export ops that belong with `observe/patterns` and `program/frontend` (`collective_pattern.py`, `embedding_shard.py`, `export_ops.py`); (4) research tools kept alive for tests (`analyze.py`, `collective_link.py`, `collective_record.py`). The code is mostly world-parametric (world = number of rank builds); "tp2" in names is the lane name, not the degree.

### Modules

| module | lines | job |
|---|---:|---|
| `__init__.py` | 12 | package docstring; stale (see DOCS) |
| `worker.py` | 1,579 | `TP2CaptureWorkerExtension`: 21 `tp2_*` RPC methods run in every rank (probe, observer install/close, parameter hashes, semantic probes, collective recorder, committer make/install/finalize, binding map, sampled replay, cross-rank dumps, openings, value check, profiler census) |
| `commit.py` | 1,177 | TP Commit driver CLI: the pairs protocol over ranks, `tp_run_root`, negatives, per-rank verdicts; one 854-line `main` |
| `partial_source.py` | 575 | `TPPartialSource`: wraps vLLM's module-level collective names to commit each rank's collective inputs (and received outputs); hook-time clone comparisons |
| `rank_match.py` | 499 | structural cross-rank checks over per-rank folds, recorder rows and `tp_links.json` (count, kind, N, site, order, producer, link binding) |
| `analyze.py` | 478 | research CLI over per-rank raw logs: collective inventory, root sharding vs TP1, numerical body of snapshotted collectives (numpy) |
| `collective_link.py` | 421 | research CLI: per-rank collective shards from raw logs, joined across ranks by `(communicator, step, k)` |
| `match.py` | 346 | TP Match driver: capture / control / check arms through the worker extension; received == Definition(partials), token parity |
| `fold_match.py` | 325 | per-rank fold match: fold, compare and GM-01 as subprocess chains per rank, then `rank_match` |
| `export_ops.py` | 258 | TP-aware export for `derive_step`: `verity_tp::*` custom ops, `CollectiveBus` (probe/trace), `TPStub` (stands in for vLLM's `GroupCoordinator`) |
| `xrank_collectives.py` | 255 | cross-rank replay of collective outputs from the ranks' committed partials |
| `capture.py` | 214 | TP capture driver CLI (the TP twin of `observe/m1_capture.py`) |
| `collective_record.py` | 98 | schema of the per-rank collective record and the cross-rank link record |
| `collective_sites.py` | 90 | finds mid-module collective call sites by scanning vLLM model-class source |
| `collective_pattern.py` | 80 | fold pattern: `vllm.all_reduce` / `vllm.all_gather` to one `AllReduce*` / `AllGather*` instance with a `resolver.Collective` operand |
| `embedding_shard.py` | 52 | fold pattern: `_C.vocab_parallel_embedding` to `EmbeddingShard_v1` |

### Findings

**CORE-DUP (0).** Nothing here copies core. The rank-combining root (`tp/commit.py:32-44 tp_run_root`, `SHA-256("verity/tp-run-root/v1" || u32 world || (u32 r || root_r)…)`) has no core counterpart: `packages/.../verification/statement.py:131-144 CommitmentRef.owner` admits only -2, -1 or a replay-unit index, and `verity.ir.layout` is gate layout, not device sharding (see the collectives map).

**INTERNAL-DUP (6)**
- Collective semantics are implemented four times: the registered Definitions (`program/registry/b1_tp2.py:98-177`), torch custom ops (`tp/export_ops.py:42-80`), inline reference evaluation in `tp/match.py:240-256` and again in `tp/xrank_collectives.py:166-172`; the world-2 vs world-N family choice is branched separately at `tp/export_ops.py:141, 154` and `program/registry/b1_tp2.py:169, 177`. *high*
- TP drivers copy the single-rank drivers: `tp/capture.py` vs `observe/m1_capture.py` (same pinned defaults `tp/capture.py:87-88` = `m1_capture.py:137-138`, same `EXPORT.json` read `tp/capture.py:101` = `m1_capture.py:155`, and `tp/capture.py:42-52 parse_engine_args` re-implements `observe/vllm_adapter.py:272-285`; `check/noninterference.py:724 _engine_args` is a third copy); `tp/commit.py` is "commit_delta's pairs protocol" (`:1-2`); `tp/worker.py:1019-1114 _tp2_binding` and `:1115-1242 _tp2_sampled_replay` redo the orchestration of `harness/commit_delta.py:549 binding_record` and `:2375-2470` (the docstring at `tp/worker.py:1116` says the sampled-replay binding was "taken verbatim"). *high*
- The collective-site list and its monkeypatch are written twice: `tp/partial_source.py:23-31 SITES` (installed at `:242-257`) and `tp/worker.py:546-560`. Their MoE coverage differs: `partial_source` patches `fused_moe.runner.moe_runner` and `fused_moe.layer`, while `worker.py:81-82` also patches `fused_moe.shared_fused_moe`, so the recorder can see an all-reduce whose input the committer does not bind. The three MoE class lists also disagree (`tp/partial_source.py:35`, `tp/worker.py:78`, `acquire/moe_source.py:36`). `tp/collective_sites.py:1-2` calls itself "the ONE finder the GPU-side observers share", but covers only mid-module sites. *medium*
- Source-tree identity is computed in several places: `tp/commit.py:75-99 tree_of_record` (`EXPORT.json` or `git diff`), `tp/worker.py:42-72 repo_modules_loaded` (re-lists the three JIT sources that `acquire/native_jit.py:22 SOURCES` holds), `harness/source_identity.py`, `harness/experiment.py:83-88`, `harness/commit_delta.py:97 git_head`. `EXPORT.json` is read ad hoc in ten places (`tp/capture.py:101`, `tp/commit.py:82`, `observe/m1_capture.py:155`, `observe/vllm_adapter.py:1944`, `check/noninterference.py:133`, `harness/derive_step.py:309`, `harness/experiment.py:84`, `harness/hot_commit.py:114`, `harness/commit_delta.py:98`, `harness/release_json.py:147`). *medium*
- Program-directory discovery for rank builds: `tp/worker.py:176-193 _tp2_request_program_dirs` delegates to `query/manifest/format.program_dirs_for` (with its own single-request special case), while `tp/commit.py:470-490 _pd` re-globs `build_request_LP*_T*/result.json` and `build_workload/workload_program.json` itself, restating "required_manifest's rule". *low*
- Small helpers: `tp/worker.py:99 _jsonable` is one of seven (`observe/resolve_log.py:296`, `observe/profiles/canonical.py:80`, `program/frontend/triton_capture.py:39`, `program/frontend/derive.py:116`, `harness/run_config.py:1181`, `check/fold_compare.py:855`); `tp/analyze.py:265 f32_to_bf16_rne` duplicates `program/dtypes.py:119 f32_to_bf16_bits`. *low*

**VERSION-RESIDUE (4)** (legit hashed/serialized identifiers listed separately below)
- The lane name `tp2` on world-parametric code: `tp/worker.py:74 EXTENSION = "verity_vllm.tp.worker.TP2CaptureWorkerExtension"`, 21 RPC methods named `tp2_*` (`tp2_probe` … `tp2_profiler_stop`) that the drivers call by string through `collective_rpc`, log prefixes `[tp2]` (`tp/capture.py:117`) and `[tp2commit]` (`tp/commit.py:941`). Renaming touches driver and rank side together. *medium*
- World-2 and world-N collective families live side by side: `AllReduce2_v1{N}` / `AllGather2_v1{N}` stay the world-2 identities so recorded Program digests do not change, `AllReduce_v2{WORLD,N}` / `AllGather_v1{WORLD,N}` serve world > 2 (`program/registry/b1_tp2.py:120-177`), with matching binary and list custom ops (`tp/export_ops.py:42-80`); `tp/partial_source.py:32 COVERS_FAMILIES` names only the world-2 families. The ids are legit; the `world == 2` branching in code is the residue. *medium*
- Two-rank CLI spellings kept beside the general one: `tp/match.py:298-307, 335-336` and `tp/fold_match.py:151-156, 176-193` accept `--build-rank0/--build-rank1`, `--derived-rank0/1`, `--gprog-rank0/1` next to repeated `--build-rank`. *low*
- `tp/match.py:96` records `"campaign": os.environ.get("VERITY_CAMPAIGN", "r15")` ("was the hard-coded 'r13' label"). *low*
- LEGIT: `verity/tp-run-root/v1` (hash tag), `verity/commit-integ/delta-tp/v1` (`tp/commit.py:33`), `verity/commit-integ/value-check-tp/v1` (`:953`), the collective record schemas in `tp/collective_record.py`, Definition ids `AllReduce2_v1`, `AllGather2_v1`, `AllReduce_v2`, `AllGather_v1`, `EmbeddingShard_v1`.

**HARDCODING (4)**
- vLLM internals as patch targets: `tp/partial_source.py:23-31` (six module/name pairs in `vllm.model_executor.layers.*`), `tp/worker.py:81-82 MOE_COLLECTIVE_MODULES` (module paths from two vLLM layouts, "moved … in 0.28"), `tp/collective_sites.py:30 MODEL_MODULE_PREFIX`. *medium*
- Pinned build and workload defaults in the TP capture: `tp/capture.py:65, 67, 87-88` (`workloads/workload_qwen15_32x16_1req.json`, `manifests/checkpoints.json`, wheel sha `7aa52ac7…`, vLLM `d9105ea80`). *medium*
- Rank 0 as the binding default: `commit/binding.py:74, 94` default `rank=0` in the leaf identity, and the sampled-replay stratum key takes "manbind's population(rank=0) at v1 (M-0523 (1) pending)" with the true rank carried beside it (`tp/worker.py:1124-1125`). *medium*
- TP degree 2 as a default: `tp/capture.py:69 --tp default=2`. World > 2 is otherwise real: `AllReduce_v2` is exact-model-tested at WORLD=4 (`program/registry/b1_tp2.py:137`). *low*

**SCRIPT/ENV/PATH (5)**
- Import-time environment mutation: `tp/capture.py:34-36` calls `prof.apply_env()` at import (and again at `:104`). *high*
- CWD-dependent behaviour: `tp/capture.py:65, 67, 101` (workload, checkpoints manifest and `EXPORT.json` relative to the CWD); `tp/commit.py:82` (`Path.cwd() / "EXPORT.json"`) and `:92-95` (runs `git` in the CWD). *medium*
- Subprocess orchestration in library code: `tp/fold_match.py:36-45, 74, 90, 104, 119` runs `harness.run_config --worker fold`, `correspondence.batch_decomp`, `check.program_compare` and `check.global_match` as `python -m` subprocesses per rank (`--python` defaults to `sys.executable`, `:165`) instead of calling functions. *medium*
- `__main__` + argparse in six modules (`capture.py`, `commit.py`, `match.py`, `fold_match.py`, `analyze.py`, `collective_link.py`); the committer reads env side channels shared with `acquire/` (`tp/commit.py:567` `VERITY_WINDOW_SLOTS`, `:921` `VERITY_RETAIN`). *low*
- Machine paths in docstrings: `tp/capture.py:3-4` (`HF_HOME=/workspace/hf`, `/workspace/venv-cu129/bin/python`, `/vol/cp/tp2/runs/<name>/capture`); `tp/worker.py:47` `Path(__file__).resolve().parents[2]`. *low*

**LAYERING (4)** (the observe <-> tp cycle is counted under `observe/`)
- tp -> harness: the rank worker builds its committer through the single-rank driver module (`tp/worker.py:639` `harness.commit_delta.baseline_state`, `make_committer`; `:887, 1435` `assert_pristine`, `class_coverage`), and `tp/commit.py:330` imports `harness.commit_delta.git_head`, `run_workload`. One-directional (harness names `tp.commit` / `tp.match` only in comments, `harness/research_outputs.py:26-27, 205-206`), but the rank worker depends on a driver module. *high*
- tp -> check, including private names: `tp/commit.py:216` imports `check.commit_verdict._query_population_scope`; `tp/commit.py:331` `check.commit_verdict`; `tp/worker.py:1416` `check.value_check.ValueChecker`; `:1550` `check.census`. *medium*
- Program construction lives in tp: `harness/derive_step.py` and `program/frontend/rules/vllm_bindings.py` import `tp.export_ops`, and `observe/profiles/generic.py:41-42` imports the fold patterns `tp.collective_pattern` / `tp.embedding_shard`; `tp/worker.py:184` imports `query.manifest.format`. *medium*
- Private helpers across tp modules: `tp/worker.py:953, 1258, 1492` import `partial_source._committed`. *low*

**GOD-MODULE (2)**
- `tp/worker.py` (1,579): one class mixed into vLLM's Worker with 21 RPC entry points and 6 private methods, plus 8 module-level helpers: (1) process and communicator probe; (2) observer install/close in the rank with a per-rank header; (3) parameter-shard hashes; (4) semantic probes; (5) collective recorder with module-name patching; (6) committer construction plus the TP partial source; (7) request attribution; (8) binding map; (9) sampled replay; (10) cross-rank dumps; (11) openings and population openings; (12) value check; (13) profiler census; (14) repo module listing. *high*
- `tp/commit.py` (1,177): `main()` spans `:322-1173` (852 lines): arguments, engine build with the worker extension, the pairs loop, per-pair commit/finalize/openings, value check, cross-rank replay, rank match, negatives, verdict assembly and record writing. *high*

**DEAD (3)**
- `tp/analyze.py`, `tp/collective_link.py`, `tp/collective_record.py`: reachable only from `tests/tp/test_tp2_analyze.py`, `tests/tp/test_tp_collective.py` and `tests/tp/test_tp_world_n.py` (`program/registry/quarantine/collective/__init__.py:14` names `collective_link.py` in a docstring only); kept on purpose by `tests/dead_code_keep.json` ("TP path (lane/vllm-tp-n)"). Searched absolute and relative imports (`collective_link.py:31` is the one relative import), `-m` in `ops/*.sh`, string references. *medium confidence (deliberately kept)*
- `tp/worker.py:48, 63` scans a `vllm-poc` root that no longer exists (also `acquire/hidden_gpu_src/hidden_gpu.py:40`), and `:68` falls back to `verity_vllm/commit` for the collector sources, which moved to `acquire/`. *high confidence (`ls`)*
- `tp/commit.py:92` `roots = ["verity_vllm", "record_v5", "e2e", "verity_vllm", "verity_vllm"]`: `verity_vllm` three times and two directories that do not exist, the trace of a mechanical rename; the dirty-tree digest covers less than intended. *high confidence (`ls`)*

**NAMING (4)**
- `tp` means tensor parallel, but `tp2` in class, method, CLI and log names means the lane, and `TP2CaptureWorkerExtension` runs at any world; `tp/worker.py:1482 _t6_4_check` is named after a task id. *medium*
- "match" means four different checks: `tp/match.py` (collective values + tokens), `tp/fold_match.py` (per-rank fold vs Program, then cross-rank), `tp/rank_match.py` (structural cross-rank), `check/global_match.py` (GM-01). *medium*
- `tp/commit.py` is a driver CLI while `verity_vllm/commit/` is the commitment engine. *low*
- Four words for a collective's rank-local inputs: "partial" (`partial_source.py`), `part_rank<r>` / `shard_rank<r>` (`acquire/native_host.py:372 TP_PARTIAL_RE`), "peers" (`peers_<request>` fold parameters), "parts" (the Definition operand). *low*

**DOCS (3)**
- `tp/__init__.py:1-12` is stale: it says "Torch-free", lists 2 of 15 modules and says "Nothing here changes observer / fold / patterns … the record is the input a future `Collective` pattern needs", while `tp/collective_pattern.py` and `observe/resolver.py`'s `Collective` exist and `worker.py`, `export_ops.py`, `partial_source.py`, `capture.py` import torch or vLLM. *high*
- Lab-notebook docstrings in almost every module: `tp/__init__.py:1` ("lane tp2 (window 2026-09-17)"), `tp/worker.py:1` and `tp/capture.py:1` ("Lane tp2 (mechanism prototype)"), `tp/export_ops.py:1` ("[R13 lane tp, P4 step 2] … Bet A"), `tp/match.py:1` ("P4 step 3"), `tp/commit.py:1` ("P4 step 4"), `tp/partial_source.py:1` ("R14 lane tp, TP-03"), `tp/xrank_collectives.py:1` ("[R16 tp TP-12, rev F-r16-18]"), `tp/collective_pattern.py:1`, `tp/rank_match.py:1`, `tp/fold_match.py:1` ("[R17 D90, COORD R17-4]"), `tp/collective_sites.py:1` ("[R19 moe F-r19-moe-1, row #70]"), `tp/embedding_shard.py:1`, `tp/worker.py:1116-1125` ("[TP-08; manbind MAN-06 …, coord M-0451 form (A), interface note M-0523]"). *medium*
- Stale references: `tp/capture.py:7` (`bench/m1_capture.py`), `:12` ("PROPOSED: build_engine(engine_args=...)", which exists at `observe/vllm_adapter.py:349`), `tp/capture.py:13` and `tp/collective_sites.py:2` (`tp2_worker.*`), `tp/embedding_shard.py:1` (`profiles/gen_llama_llama32_1b_tp2rank.py`), `tp/commit.py:2` (`tp2_worker.*`), `tp/match.py:3-5` and `tp/commit.py:4` (`tp2_match` / `tp2_commit` program names), `tp/worker.py:20` (`MECHANISM_TP2.md`), `tp/collective_record.py:2-3` (`out/gen/lanes/ov-tp2/…`), `tp/export_ops.py:4` (`out/gen/sweep/evidence/tp/tp2_semantics/RESULT.md`); none of these files exist (`rg --files`). *medium*

**FALLBACKS (3)**
- `tp/collective_sites.py:42-45` returns `{}` when a model class's source cannot be read, so its collectives silently stop being sites; `:81-84` skips modules that fail to import. *medium*
- `tp/worker.py:85-96 _moe_collective_modules` skips vLLM modules that fail to import ("older/newer vLLM"), so which MoE all-reduce is patched depends on the installed vLLM. *low*
- `tp/commit.py:83-99 tree_of_record` returns an error record instead of failing when `EXPORT.json` is malformed or `git` fails. *low*

**OTHER-WEIRD (4)**
- Monkeypatching vLLM's module-level collective functions twice in one rank process: `tp/partial_source.py:242-257` (committer side) and `tp/worker.py:546-560` (recorder side), each with its own restore. *medium*
- `tp/collective_sites.py:34-49` finds collective sites by running a regex over `inspect.getsource(cls)` of vLLM model classes. *medium*
- `tp/export_ops.py:36-93` registers `verity_tp::*` torch custom ops into the global registry behind a module flag, and `:170 TPStub` impersonates vLLM's `GroupCoordinator` during export. *low*
- Negative tests (fault injection) are CLI flags of the production driver: `tp/commit.py:55-72 negatives_applied`, `:102 parse_serve_shard_from`, `tp/partial_source.py:102` (`relabel_rank`, `omit_site`), `:355 parse_flip`. *low*

Counts for `tp/`: CORE-DUP 0, INTERNAL-DUP 6, VERSION-RESIDUE 4, HARDCODING 4, SCRIPT/ENV/PATH 5, LAYERING 4, GOD-MODULE 2, DEAD 3, NAMING 4, DOCS 3, FALLBACKS 3, OTHER-WEIRD 4.

---

## 4. `input_provenance/` (4 .py files, 1,857 lines)

**What it actually does vs its name.** The one-line package docstring ("weights of record, prescribed constants and their basis") fits `weights_of_record.py` and `root_policy.py`. `analytic.py` is broader than its name: besides the two analytic tables it holds the model-configuration layer (HF `config.json` to `C` with per-key provenance and family rules), the FP8 quantization policy, and the Program's weights Record type for every family. `observe/`, `check/` and `harness/` build on those two functions, so part of this package is a foundation that sits in the wrong place.

### Modules

| module | lines | job |
|---|---:|---|
| `__init__.py` | 1 | one-line docstring |
| `weights_of_record.py` | 1,001 | checkpoint index (safetensors headers, shard sha256 vs `manifests/checkpoints.json`); composition of each served tensor from checkpoint tensors (fused q/k/v and gate/up, MoE experts, tied `lm_head`, Gemma-2 normalizer, TP rank shards); engine constants (kv scales, FP8 loader placeholders, rotary table); the record, its root, re-root and diff; live-side digests and `check`; of-record set stamping; CLI |
| `analytic.py` | 477 | `config_of` (HF config to `C`, provenance per key, `FAMILY_RULES`); `quant_refusal` (block-FP8 only); `weights_type` and the per-family layer Records; Gemma-2 `normalizer_word`; rotary `cos_sin_table` and the bounded `check_cos_sin` (gate I9) |
| `root_policy.py` | 378 | gate G3 (root closure): classifies every `Root` of a raw log (weight, analytic-table, alias, request-input, config, ignored) and validates each against an independent source; CLI |

### Findings

**CORE-DUP (2)**
- Ad hoc canonical-JSON digests: `weights_of_record.py:474-479 analytic_key` (`json.dumps(sort_keys=True, separators=(",", ":"))`) and `:482-491 root_of_fields` (sha256 of `SCHEMA + "\n" + json.dumps(ordered)`). Core's `packages/.../commitments/identity.py canonical_json_bytes` / `identity_digest` refuse floats, and `analytic_key`'s inputs carry floats (`ROPE_THETA`, `rope_scaling` factors), so reuse needs a float policy in core first. *low*
- `weights_of_record.py:111 sha256_file` is one of nine file-hash helpers in the integration (`harness/run_config.py:367`, `check/verdict.py:263`, `program/instances_form.py:36`, `harness/hot_commit.py:86`, `harness/experiment.py:40`, `observe/profiles/dense_generic.py:91`, `check/global_match.py:106`, `check/kernel_identity.py:48`); core has a private one (`packages/.../verification/trust.py:325 _sha256_file`). *low*

**INTERNAL-DUP (5)**
- Two per-family fact tables: `analytic.py:39-50 FAMILY_RULES` (7 model types; keys `qkv_bias` / `qkv_bias_key`, `default_theta`, `default_eps`, `qk_norm`) and `observe/profiles/family_facts.py` (same keys and values, e.g. Qwen2 `{"qkv_bias": True, "default_theta": 1_000_000.0}` at `:58`, plus citations and more families such as GPT-NeoX at `:122`), which `observe/profiles/generic.py:183-185` feeds back into `config_of(family_rules=...)`. *medium*
- The rotary buffer and attention-scale names are recognised by ten patterns: `root_policy.py:62` (`analytic_table_of_buffer`, whose docstring says it is "the one place the two derived tables are recognised by name", repeated at `observe/m1_capture.py:61`), `:74 ALIAS_OF_COS_SIN`, `:75 IGNORED_ROOT_NAMES`, `:76 _LAYER0_COS_SIN`; `weights_of_record.py:98 ENGINE_CONSTANT_RE` (the union of the next three), `:99 PLACEHOLDER_RE` (same names as `:365`), `:364-366 ENGINE_KV_SCALE_RE`, `ENGINE_KV_PLACEHOLDER_RE`, `ENGINE_ROTARY_RE`; and a Llama-only `ALIAS_OF_COS_SIN` again at `observe/profiles/vllm_d9105ea80_sm89_eager.py:114`. *medium*
- Safetensors headers are parsed in four places: `weights_of_record.py:104-108, 145` (`CheckpointIndex`), `program/frontend/vllm_meta.py:169`, `check/fold_compare.py:306` (`WeightSource`), `correspondence/capture_identities.py:282`. *medium*
- Two bf16 roundings inside this package with different NaN handling: `analytic.py:371 f32_to_bf16_words` (no NaN quieting; also used by `check/fold_compare.py:315`) and `weights_of_record.py:192 _f32_to_bf16_bits` (quiets NaN), beside the shared `program/dtypes.py:119 f32_to_bf16_bits`. *low*
- Build layout, source identity and parameter hashing restated: `weights_of_record.py:820-826 component_program_dirs` globs `build_request_LP*_T*` (as do `tp/commit.py:470-490` and `query/manifest/format`), `:829-895 stamp_of_record_set` reads `manifest.json` and `build_workload/workload_program.json` by path, `:898-930 derivation_provenance` computes code identity (see the source-identity item under `tp/`); live parameters are hashed by both `weights_of_record.py:600-628 live_param_digests` and `tp/worker.py:308-349 tp2_param_hashes`. *low*

**VERSION-RESIDUE (2)**
- Frozen-file layering: `analytic.py:252-291 weights_type` is `b1.weights_type(C)` followed by up to seven successive rewrites (dense per-head norm / FP8, LayerNorm, partial rotary, MoE, extra norms, untied `lm_head`, normalizer) because "`b1.py` is frozen (D57)". The `layers` rewrites overwrite each other in a fixed order: `moe_layer_weights_type` (`:162-185`) has no FP8 branch, so a block-FP8 MoE configuration would silently get bf16 expert fields. No refusal of that combination was found in `analytic.py` or `observe/profiles/generic.py`; end-to-end behaviour not checked. *medium*
- Two vLLM layouts at once: `weights_of_record.py:73-77 EXPERTS_RE` accepts `<container>.experts.w13_weight` (vLLM <= 0.11) and `.experts.routed_experts.w13_weight` (vLLM 0.28), and `:90-97` cites vLLM line numbers (`kv_cache.py:106-109, 209-212`). *low*
- LEGIT: `verity/commit/weights-of-record/v2` and `SCHEMA_V1` (v1 records exist and are re-rooted by `reroot` / `diff_records`; tests at `tests/input_provenance/test_weights_of_record_root_host_independent.py:90-119`), `verity-gen/root-policy/v1`.

**HARDCODING (3)**
- HF/vLLM parameter names and stacking rules restated: `weights_of_record.py:62-72 FUSED`, `EXPERTS`, `EXPERTS_MIXTRAL` (vLLM model classes carry these as `packed_modules_mapping` / `stacked_params_mapping`); tied `lm_head.weight` <- `model.embed_tokens.weight` only (`:278-280`, `:717-718`). *medium*
- The "frozen" root policy is a per-family naming table: `root_policy.py:72-73` (`_MODULE_PREFIX = (?:model|gpt_neox)`, `_ATTN_MODULE = (?:self_attn|attention)`), `:151, 278` (embed / `lm_head` names for two families), `:283, 290` (records `alias_of: "model.embed_tokens.weight"` even for GPT-NeoX), `:49-50 IGNORED_ROOT_CONSUMERS` (vLLM op names). Every new family naming edits the protected module. *medium*
- The config-root check compares a fixed list of 11 keys (`root_policy.py:302`); facts that change the Program (`BIAS`, `QK_NORM`, `FP8_BLOCK`, `NUM_EXPERTS`, `TOPK`, `rope_scaling`, `ROT`) are not compared against `config.json` there. *low*

**SCRIPT/ENV/PATH (2)**
- `weights_of_record.py:796-802 _default_manifest` looks for `manifests/checkpoints.json` two directories above the file, then in the CWD; the comment names the old layout ("veritor: vllm-poc/"). *medium*
- CLIs in library modules (`weights_of_record.py:933-1001`, `root_policy.py:352-378`), driven by `ops/row_pod.sh:1026-1067` (which also runs `python -c "…import SCHEMA; print(SCHEMA)"` to read a constant) and as a subprocess by `harness/run_config.py:230`; `derivation_provenance` shells out to `git -C <file dir> rev-parse HEAD` (`weights_of_record.py:923`). *low*

**LAYERING (3)**
- Cycle observe <-> input_provenance: `root_policy.py:42-43` imports `observe.events` and `observe.log`, `:111` `observe.fold.config_for_weights`; `observe/fold.py:106`, `observe/m1_capture.py:61, 101` and four `observe/profiles/*` modules import `input_provenance`. `config_of` and `weights_type` are model description that `observe`, `check` (`check/fold_compare.py:315, 408`) and `harness` (`harness/run_config.py:377`) build on. *medium*
- input_provenance -> check / query / harness / program, partly through private names: `root_policy.py:110` (`check.fold_compare.SnapshotStore`, `WeightSource`, `_extent`), `:353` (`check.fold_compare.load_profile`), `:39` (`program.frontend.rules.family._field_intervals`); `weights_of_record.py:357` parses the Program's struct type through `check.sampled_replay.parse_struct`; `:540, 807, 836` `query.manifest.format`; `:912` `harness.experiment.code_version`. *medium*
- `weights_of_record.py:451` calls the private `analytic._inv_freq`. *low*

**GOD-MODULE (1)**
- `weights_of_record.py` (1,001): (1) safetensors checkpoint index and shard pinning; (2) served-width casting; (3) composition rules including TP shards; (4) engine constants with the kv-scale remap; (5) record, root, re-root, diff; (6) torch live-side digests; (7) `check` with seven refusal reasons (`:651-791`); (8) of-record set stamping over build directories; (9) derivation provenance; (10) CLI. The torch-free derivation and the torch live side share one file. *medium*

**DEAD (1)**
- `root_policy.py:110` imports `_extent` from `check.fold_compare` and never uses it. *high confidence (`rg`)*

**NAMING (3)**
- `analytic.py` holds five jobs; only the normalizer and rotary table are "analytic". `config_of` and `weights_type` would be looked for in a model-config or registry module. *medium*
- "of record" has at least five meanings in the slice: weights of record, Program / digests of record, checkpoint of record, the stamped of-record set, and "tree of record" (`tp/commit.py:75`). *low*
- `root_policy.py` calls its tables "Frozen" and itself "PROTECTED (gate G3)" but has been generalized in place (`:51` "[ADAPTER lane cov-dense 2026-09-17]", `:68` "[SHARED-CODE lane cov-ln]"); nothing enforces the freeze. *low*

**DOCS (3)**
- Governance references to files that do not exist: `root_policy.py:22-23` (`out/capture/decisions.md`, `out/gen/RULES.md`), `weights_of_record.py:5` ("DECISIONS-2 §4"), `analytic.py:9` ("plan §2 I9, §3", "the M6 comparison"). *medium*
- Lab-notebook docstrings: `weights_of_record.py:1` ("(R15 manbind MAN-09; rev-cb M-0610, coord M-0614 (1))"), `:73, 81, 90` ("[R19, F-r19-int-11] … #74 (Qwen3-4B-FP8 B8, H100): 579/579 compared equal …"), `:370, 385, 407, 830, 900`; `analytic.py:1` ("Phase 0 of the generalization sweep"), `:46, 52, 146, 213, 221, 286`; `root_policy.py:51, 68`. *medium*
- Docstrings that contradict the code: `analytic.py:6` says `check_cos_sin` passes "within COS_SIN_MAX_ULP of analytic", but `:412-418, 476` decide by the error bound and report `max_ulp` as informational; `:36-37` says an unlisted family is "hand" for BIAS, but `:138-139` sets `BIAS=False` as "derived"; `:163, 255` still call `moe_layer_weights_type` "PROPOSED" though every MoE configuration uses it. *medium*

**FALLBACKS (4)**
- Silent defaults in `config_of`: an unlisted family gets `BIAS=False` (`analytic.py:132-139`) and `ROPE_THETA=10000` (`:128`), both labelled "derived". The cos/sin bound catches a wrong θ; nothing here checks BIAS. *medium*
- `tie_word_embeddings` defaults disagree: False at `analytic.py:140` and `weights_of_record.py:250, 587`, True at `analytic.py:283` and `root_policy.py:279` (transformers' default depends on the model class). The runtime tie check (`root_policy.py:277-293`) catches a mismatch on runs that go through G3. *low*
- `weights_of_record.py:540-548`: with no attention row to read the wrapper prefix from, the prefix becomes the one under which most fields match checkpoint names. *low*
- `root_policy.py:226-230`: a weight root without a snapshot passes as `checkpoint-identity` when the header says the checkpoint sha was verified at build (documented at `:11`, recorded as the validator). *low*

**OTHER-WEIRD (2)**
- Truncated identities in an authentication check: `weights_of_record.py:676-677 _eq` treats two Program digests as equal when one is a >= 16-hex-character prefix of the other (also `:863, 885`), and checkpoint revisions match on 10 characters (`:160, 705`). *medium*
- `root_policy.py:335-337` parses the request id and position back out of the prompt root's string name `prompt[<request>][<pos>]`. *low*

Counts for `input_provenance/`: CORE-DUP 2, INTERNAL-DUP 5, VERSION-RESIDUE 2, HARDCODING 3, SCRIPT/ENV/PATH 2, LAYERING 3, GOD-MODULE 1, DEAD 1, NAMING 3, DOCS 3, FALLBACKS 4, OTHER-WEIRD 2.
