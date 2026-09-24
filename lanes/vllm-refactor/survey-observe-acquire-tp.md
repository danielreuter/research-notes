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
