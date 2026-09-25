---
id: vllm-refactor/synthesis
lane: vllm-refactor
kind: synthesis
status: draft for owner approval
created: 2026-09-24
inputs: SURVEY_BRIEF.md, the four survey-*.md reports, the four 20260924T16*-coordinator-checks-*.md notes
---
# Verity x vLLM integration: refactor synthesis (at f0810a11)

**Conventions.** Paths are relative to `integrations/vllm/verity_vllm/`. `tests/`, `workloads/`, `manifests/` and `data/` are relative to `integrations/vllm/`, and `core/` means `packages/verity/src/verity/`.
- **Surveys:** [S1] survey-check-commit, [S2] survey-program-query-corr, [S3] survey-observe-acquire-tp, [S4] survey-harness-ops-tests-data. A section number or `#n` refers to the survey's top-findings list.
- **Coordinator notes:** [C1] to [C4], from 16:25Z (check/commit), 16:30Z (program/query), 16:40Z (harness) and 16:45Z (observe). Where a note corrects a survey, the note is used.
- **[syn]:** checked by this synthesis with `rg`, `wc` or `sed` at f0810a11. No Python was run and the checkout was not changed.

## 0. Summary

The integration works, but it does not yet read as "vLLM wrapped by Verity core", and some of its evidence means less than its verdicts say.

- **Evidence gaps (§2: 17 defects, 11 coordinator-verified).** Replay reads the committer's memory, not opened values (D1). Production roots use rules no core verifier knows (D2). Environment variables, torch importability and pod names change roots, plans and leaf ids (D3, D4, D12, D15). Code-identity stamps ignore core or never change (D5, D6). One Definition id names two functions, and core ids are re-registered (D8, D9).
- **Core copied, not used (T1).** 34 CORE-DUP findings, eight copies of core's Merkle node framing, a runtime monkeypatch of core, and no import of `verity.commitments`.
- **Jobs hidden (T2 to T6).** A 1,147-line bash script with 45 environment knobs drives 73 `__main__` modules. Acceptance is five verdict systems. Properties such as non-interference sit among the per-run checks, and `tp/` copies the single-rank pipeline for world 2.

**Plan (§6).**
1. Fix the defects as small independent PRs.
2. Make behavior-preserving moves gated by the regression harness: lint ratchets, import contracts, dead code out, a 12-module tree, and one CLI over a typed `RowSpec`.
3. Consolidate: one evaluator interface with numpy/torch backends replacing sampled_replay's special cases, one verdict over core codes, `properties/`, and `collectives/` replacing `tp/`.
4. Last, make the digest-changing alignment with core in one re-baseline epoch, behind the 8 decisions in §7.

## 1. Scale

At f0810a11, `verity_vllm/` holds 314 `.py` files with 125,500 lines in all: 286 modules in ten subpackages, `build_paths.py`, and 27 `__init__.py`. 41 modules exceed 800 lines, and together they hold 56,436 lines (45%) [syn].

| subpackage | modules | lines | `__main__` | files touching `os.environ` | findings | high |
|---|---:|---:|---:|---:|---:|---:|
| `program/` | 107 | 36,252 | 10 | 10 | 87 | 15 |
| `check/` | 35 | 24,875 | 19 | 9 | 77 | 17 |
| `observe/` | 36 | 15,578 | 4 | 4 | 86 | 7 |
| `harness/` | 25 | 12,986 | 19 | 12 | (S4 row) | (S4 row) |
| `acquire/` | 19 | 8,269 | 4 | 7 | 55 | 10 |
| `commit/` | 22 | 6,855 | 1 | 2 | 49 | 5 |
| `query/` | 12 | 6,613 | 3 | 0 | 69 | 5 |
| `tp/` | 15 | 6,459 | 6 | 3 | 43 | 8 |
| `correspondence/` | 12 | 5,602 | 5 | 1 | 78 | 11 |
| `input_provenance/` | 3 | 1,857 | 2 | 0 | 31 | 0 |
| top level (`__init__`, `build_paths`) | 1 | 154 | 0 | 0 | – | – |
| S4 slice: `harness/` above, plus `ops/` (16 bash scripts, 3,338 lines), `tests/` (319 files, 74,187 lines), data directories and packaging | | | | | 98 | 18 |
| **total** | **287** | **125,500** | **73** | **48** | **673** | **96** |

Where the numbers come from:
- Modules, lines, `__main__` and `os.environ` (208 sites in 48 files) are [syn].
- Findings are the surveys' category sums: [S1 §7], [S2 per-section counts], [S3 §7], [S4 "Findings by category"].
- High counts use each survey's severity tags. S3's 15 DEAD items carry confidence labels instead [S3 §7].

Findings by category (the totals that §3 uses):

| category | S1 | S2 | S3 | S4 | total |
|---|---:|---:|---:|---:|---:|
| CORE-DUP | 8 | 16 | 8 | 2 | 34 |
| INTERNAL-DUP | 15 | 24 | 24 | 11 | 74 |
| VERSION-RESIDUE | 11 | 19 | 22 | 8 | 60 |
| HARDCODING | 12 | 23 | 21 | 7 | 63 |
| SCRIPT/ENV/PATH | 14 | 18 | 21 | 11 | 64 |
| LAYERING | 10 | 24 | 18 | 6 | 58 |
| GOD-MODULE | 12 | 16 | 11 | 4 | 43 |
| DEAD | 11 | 16 | 15 | 18 | 60 |
| NAMING | 9 | 17 | 18 | 7 | 51 |
| DOCS | 5 | 20 | 15 | 8 | 48 |
| FALLBACKS | 9 | 18 | 19 | 7 | 53 |
| OTHER-WEIRD | 10 | 23 | 23 | 9 | 65 |
| **total** | **126** | **234** | **215** | **98** | **673** |

## 2. Correctness defects

Each of these changes what a result means, or can let a wrong result pass. Every fix is local, so none waits for the refactor.
- **verified:** a coordinator note confirmed it.
- **reported:** a survey claim whose lines this synthesis re-read at f0810a11.
- **Digest-changing fixes** (D2, D8, D9, D12) land together in the re-baseline epoch (Decision 4).

**D1. Value checks compare the committer's memory, not opened values.** verified [C1, C4]
- Where:
  - `harness/commit_delta.py:2339` and `tp/worker.py:1192` call `OC.oracle_compare(..., OC.committed_reader(com), ...)`.
  - The reader returns `com._layouts`, `com._gpu_blocks` and `meta.host` (`check/oracle_compare.py:914-953`).
  - Openings are a separate sample, verified at `commit_delta.py:734-742` and `:2022-2033`.
- Breaks: a C2 PASS does not show that the committed bytes satisfy the Definitions. A committer that commits A and hands B to replay passes. The PoC path did authenticate the values (`check/relations.py:735`, [S1 §3.5]).
- Fix: open every leaf that replay reads, verify it against the run root (or the rank root), and decode the evaluator's inputs from the opened bytes. Delete `committed_reader`. Add a negative test that mutates the retained buffer after commit and expects C2 to fail.

**D2. Production roots cannot be verified by core.** verified [C1]
- Where:
  - `pos_leaf` = `SHA-256("verity/pos-leaf/v0" ‖ u64 nbytes ‖ value)` and the semantic root (`commit/semantic_layout.py:1-45`).
  - The `fa2h` chunk leaf, used for every GPU tensor (`commit/hidden_stream.py:34-35, 144-151`; CUDA `acquire/native_tree.cu:163-165`).
  - Raw-SHA root bindings: `commit/hidden_engine.py:49`, and the run root in three copies (`acquire/native_host.py:57, 2063, 2484`, `commit/padding_steps.py:308-310`).
  - Only the PoC leaf matches `core/commitments/leaves.py`, and no integration root verifies under `core/commitments/merkle.py:26-149` [S1 §4].
- Breaks: "verified" means verified by the integration's own code. No core verifier, statement or multiproof can check a production root.
- Fix now: write the scheme once. One module holds the `pos_leaf` rule, the chunk leaf and the root bindings, with test vectors that Python and the four CUDA SHA-256 copies [S1 §4.4] are tested against. Add a standalone `verify_opening(root, opening)` that imports no committer code. Aligning with core is Decision 1 (digest-changing).

**D3. Environment variables change committed leaves.** verified [C4]
- Where: `acquire/native_collect.py:721` reads `VERITY_LAYOUT` to pick chunk-leaf v1 or v2. Padding leaves read a different variable, `VERITY_LEAF_LAYOUT` (`commit/padding_steps.py:405`). `harness/commit_delta.py:1197-1267` copies 12 CLI flags, `--layout` among them, into `os.environ` for `acquire/` and `commit/` to read back [S4 SCRIPT/ENV/PATH].
- Breaks: the root depends on undeclared process state, and padding and executed leaves can carry different headers in one run.
- Fix: pass one `layout` argument from the Commit config to both sites. The chunk header already records the version [S1 §4.1], so roots don't change when the two variables agreed.

**D4. The acquisition plan depends on whether torch imports.** verified [C4]
- Where: `acquire/plan.py:371-377`. `_lifetime_tables()` swallows the ImportError from `native_collect` and falls back to empty `GATHER_FLUSH_LEAVES` and `PRE_FLUSH_LEAVES`.
- Breaks: a CPU gate without torch and the GPU stage evaluate different plans (different digests) for the same inputs.
- Fix: move the two tables into a torch-free module that is imported unconditionally.

**D5. The hot worker's code key ignores core.** verified [C3]
- Where:
  - `harness/hot_commit.py:51-52` sets `CODE_ROOTS = ("verity_vllm", "verity_vllm_sampler", "e2e", "record_v5", "scripts", "manifests")`. Four of the six don't exist, and there is no core root.
  - The TP commit repeats the pattern: `roots = ["verity_vllm", "record_v5", "e2e", "verity_vllm", "verity_vllm"]` (`tp/commit.py:90-93`) [syn].
- Breaks: after an edit to `packages/verity/src`, a live hot worker keeps its key and serves Commits with stale core code.
- Fix: key on the closure that the `research` store hashes (`harness/research_tools.py:44-49`), and add `core/commitments/**` to that closure, which lacks it today [syn].

**D6. The Build's `construction_version` is constant.** verified [C3]
- Where: `harness/derive_step.py:66-80` joins the 13 `verity_vllm/...` sources to `packages/verity/src`, so every file hashes as "missing".
- Breaks: the stamp in each Build artifact cannot tell code versions apart. The research cache key is not affected.
- Fix: resolve the sources from `verity_vllm.__file__` and raise on a missing file, or replace the stamp with the closure digest (P12).

**D7. The Build records bf16 for FP8 rows.** verified [C3]
- Where: `harness/derive_step.py:371` always writes `model_pin.dtype = vm.PIN["dtype"]`. Model and revision also fall back to `vm.PIN` (`:366-372`) [syn].
- Breaks: FP8 Build artifacts misstate their dtype, and a silent fallback can pin the wrong model or revision.
- Fix: take model, revision and dtype from the row spec, and raise if any is missing.

**D8. One Definition id computes two functions.** verified [C2]
- Where: `program/registry/prims.py:381`. `AmpereBF16TcDot16` v1 was switched to total semantics in R17 without a version bump (docstring `:371-374`). Core registers those semantics as `AmpereBF16TcDot16` v2 (`core/ml/prims.py:52`).
- Breaks: evidence from before and after R17 cites one id for two functions, which differ on non-finite outcomes.
- Fix: move Programs to core's v2 id and retire the integration's v1 (digest-changing, Decision 3).

**D9. The integration re-registers core Definition ids.** verified [C2]
- Where: `program/registry/prims.py:183` (`Bf16ToF32` v1) and `:199` (`F2fpBf16` v1), against `core/ml/prims.py:30, 44`. `core/ir/defs.py:35-38` raises "registry already has a different definition" when both are loaded.
- Breaks: no process can load core `verity.ml` together with the integration, so integration evidence can't be checked with core's library. One id names two objects.
- Fix: import core's Definitions for the shared ids and delete the copies. Add a test that loads both registries in one process (digest-changing, Decision 3).

**D10. Core is monkeypatched at runtime.** verified [C1]
- Where: `check/global_match_fast.py:482-520` rebinds `verity.ir.codec._spec_id`, `verity.ir.refs.runs` and several Prog, compare and dag functions. It does this whenever `MATCH_IMPL=fast`, which is the default (`check/global_match.py:2063-2065`) [S1 #4].
- Breaks: anything core computes in that process (spec ids, runs, digests) is computed by integration replacements, so "core says equal" is not core's judgment.
- Fix: have `global_match` call the fast helpers directly and never assign to `verity.*` attributes. Upstream the speed-ups.

**D11. Truncated digests are accepted.** verified, corrected to medium [C4]
- Where: `input_provenance/weights_of_record.py:676-677`. `_eq` treats two Program digests as equal when one is a prefix of at least 16 characters of the other. Revisions match on 10 characters (`:160, 705`) [S3 #12].
- Breaks: a truncated digest passes Program-digest matching against the of-record set. Per [C4], this is not a checkpoint-shard hole.
- Fix: store and compare full digests and revisions.

**D12. The profile id, which prefixes every leaf id, is unstable.** reported [S3 #5]
- Where: any exception swaps in a fallback profile schema (`observe/vllm_adapter.py:973-983`). `RUNPOD_POD_ID` is hashed into the profile (`observe/engine_profile.py:228-232`). sm_90 FP8 roles are labelled `sm89-eager` (`observe/profiles/generic.py:333-335`).
- Breaks: the same code and inputs on two pods give different leaf ids and roots, an exception silently changes identity, and the target label is wrong.
- Fix: raise instead of falling back, keep the pod id in telemetry only, and derive the label from the probed capability (digest-changing).

**D13. Verdict rules match message text.** reported [S1 #6]
- Where: `check/commit_verdict.py:107` (`_WHY_BY_NAME`), `:152` (`_NO_EVALUATOR_PREFIX = "no registered evaluator for "`) and `:353-354` (`_REPLAY_SEED_ROOT_FORM = "run root (first 8 bytes, after commitment)"`) mirror message text written by `sampled_replay` and `commit_delta`.
- Breaks: rewording a message silently reclassifies an outcome. That includes the check that the replay seed is bound to the root.
- Fix: checks emit structured fields and codes, and the verdict reads those.

**D14. Challenges are predictable.** reported [S1 #7, §4.4]
- Where: `check/compiled_kernel_check.py:204-207` (`random.Random(self.seed if self.seed is not None else 0)`) and `check/relations.py:1158, 1292` (`default_rng(seed)`, where seed defaults to 0). Of the six derivations, only `commit/binding.py:676-716` and `check/sampled_replay.py:2522-2528` derive from the run root.
- Breaks: with a known seed, a prover can make exactly the sampled positions correct.
- Fix: make the seed a required argument, derived from the run root by one function. Core has no such function yet (C4).

**D15. Environment variables change Definition semantics.** reported [S2]
- Where: `MufuTanh_v1` reads `VERITY_MUFU_TANH_TABLES` (`program/registry/prims.py:494, 504, 632`). `VERITY_ARCH` is used as a fallback in `program/numerics/rms_relation.py:117` and `fa2_model.py:252-253`.
- Breaks: the function a Definition id denotes depends on the environment of the process that evaluates it.
- Fix: ship the tables as package data, selected by a Definition static or the declared target.

**D16. The collective hooks and semantics disagree.** reported [S3 #8, S2 Map 4]
- Where:
  - The committer hooks MoE collectives for `("MoERunner", "FusedMoE")` (`tp/partial_source.py:36`; its patch list at `:26-31` omits `shared_fused_moe`). The recorder hooks them for `("MoERunner", "FusedMoE", "SharedFusedMoE")` (`tp/worker.py:78-82`).
  - The quarantine `AllReduceSumBf16{N,R}` sums in ascending order (`program/registry/quarantine/collective/allreduce.py:64-71`). The measured order is descending (`program/registry/b1_tp2.py:128-134`), and at WORLD=4, 32 of 1,056 all-reduces differ from the ascending chain.
  - Correspondence records collectives only for the world-2 ops (`correspondence/emit.py:30, 319-322`).
- Breaks: on shared-expert MoE models, collectives are recorded but their partials are not committed. At world 3 or more, the quarantine Definition is the wrong function and correspondence has no collective records.
- Fix: share one class list between the two hooks. Delete the quarantine family or route it through `allreduce_order`. Refuse world > 2 in `emit` until B3 lands.

**D17. There is no in-repo evidence that the patched FlashAttention matches vLLM's.** reported [S3 #6]
- Where: `acquire/hidden_source.py:234, 239, 386-387` cite `fa2_tap_xcheck.py` and `fa3_tap_xcheck.py`, and neither file is in the repo.
- Breaks: hidden-state leaves come from a patched kernel whose bit-identity with the served kernel is asserted, not checked.
- Fix: restore the cross-check as a property (GPU pod) and require its record for FA-tap rows.

**Also fix now.** These are crashes and dead references, not wrong results.
- `program/registry/ref_prims.py:276` rebinds core's list `_LAZY_PRIMITIVE_FAMILIES` to a tuple, so the next `register_lazy_family` call raises `AttributeError` (`core/ir/codec.py:345-350` calls `.append`). Call `register_lazy_family` instead [syn].
- `acquire/native_host.py:2319-2340` defines `layouts_dump` twice, and the second definition shadows the first [syn].
- `observe/engine_profile.py:100-106`: the error path references an undefined `repo` [syn].
- `tests/acquire/schemes.py:13, 78-98` imports the non-existent `veritor.*` packages and prints "scheme skipped" [S4 CORE-DUP].
- `__init__.py:1-22`, the package's front door, calls it a "replay proof-of-concept harness (worker W2)" and maps four modules that don't exist (`relations_torch`, `negatives`, `render`, `verify`) [syn].

## 3. Cross-cutting themes

Where each owner smell is handled:

| owner smell | themes | practices | lanes |
|---|---|---|---|
| 1 sampled_replay as a general replay backend | T2 | P2, P3 | F1, B1 |
| 2 gates.py means acceptance, not circuits | T3, T10 | P4, P11 | B2, C3 |
| 3 non-interference and all property logic in one place | T4 | P5 | F6, B2 |
| 4 unclear what job is done where | T6, T8, T9 | P9, P10, P12 | A4, A5, B5 |
| 5 scripts behind a clear API, not `__main__` | T6, T7 | P6, P7 | A5 |
| 6 tp/ as part of a general collectives mechanism | T5 | P8, P9 | F5, B3, C4 |
| 7 v1/v2 names everywhere | T10 | P11 | A4, C3 |

**T1. Core is copied, forked or patched instead of used.** Covers the owner's goal of clearly using core, and smell 6.
- Counts:
  - CORE-DUP 34 (S1 8, S2 16, S3 8, S4 2).
  - Core's node, lift and empty framing is re-implemented in 8 places across Python, torch, CUDA and Rust [S1 §4.2].
  - Six JSON canonicalizations feed digests [S1 §4.4].
  - Integration files importing each part of core: `verity.ir` 85, `verity.ml` 4, `verity.verification` 4 (one of them dead), `verity.commitments` 0 [syn].
- Examples:
  1. The forked Definition library (D8, D9). In addition, `DotBf16_v2`, `GemmCoordinate_v2` and `Gemm_v2` duplicate `core/ml/gemm` [S2 §5 `registry/b1.py`].
  2. Patching core at runtime: D10, and `ref_prims.py:276`.
  3. Generic IR analyses parked in the integration: `query/boundary.py`, `query/partition.py` and `program/frontend/liveness.py`. Core's own docstrings already plan their promotion (`core/ir/parts.py:15-18`, `core/ir/layout.py:19`). There are also four copies of one interval algebra (`query/boundary.py:86-110`, `query/vu_query.py:115-155`, `frontend/liveness._norm`, `core/ir/query_ast.py:65`) [S2 §1].

**T2. Evaluation and replay have no backend interface.** Covers smell 1.
- Counts:
  - Nine evaluators (E1 to E9) compute what a Call should produce. Only `twins` (E2), and the sampler rows on a subset (E8), are compared with core's `evaluate_call` while a check runs [S1 §3.1].
  - Eight replay drivers each have their own sampler, input resolver, decoding and result dict [S1 §3.2].
  - There are six challenge derivations [S1 §4.4].
  - `check/sampled_replay.py` is 3,149 lines with 11 jobs [S1 #10].
- Examples:
  1. `sampled_replay.py:743-920` is a hand-written ladder over 20 families. It sits on `program/registry/derived_rows.py`, a second numpy twin library next to `check/twins.py`, and neither imports the other [S1 §3.3].
  2. Its value source is the committer's memory (D1).
  3. `replay.py`, `stoch_recompute.py`, `compiled_kernel_check.py` and `relations.check` share no code with it [S1 §3.3].

**T3. Acceptance is five verdict systems, named like circuits and keyed on prose.** Covers smells 2 and 4.
- Counts:
  - Five integration verdict systems: V1 `check/gates.py:1189-1203`, V2 `commit_verdict.py:480-704`, V3 `verdict.py:170, 200`, V4 `poc_rows.py:294-421` and V5 `relations.py:650-918`. None uses `core/verification/codes.py:16-50` [S1 §5].
  - Success is spelled four ways, and the Commit decision is written to four files [S1 §5].
  - `G1` to `G8` appear 420 times in 58 files, while core uses "gate" for circuits (`core/verification/gateset.py`, 28 core files) [syn].
- Examples:
  1. `verdict.py` re-implements `commit_verdict` through seven of its private helpers [S1 #5].
  2. Verdicts keyed on prose (D13).
  3. The Match verdict is a 113-line Python heredoc in `ops/row_pod.sh:686-800` [C3, reported].

**T4. Integration properties are mixed into per-run checks, and one is missing.** Covers smell 3.
- Counts:
  - Eleven property harnesses (non-interference, census plus allowlist, golden, holdout, difftest, quarantine lint, protected, adversarial, twins self-check, FA2 oracle, kernel identity) are consumed as per-run gates G1, G4, G6 and G7 [S1 §6].
  - Negative tests are spread over three shell scripts and fault-injection flags in five production modules [S1 §6].
- Examples:
  1. `check/noninterference.py:729-752` spawns three engine processes to re-establish a property of the build on every run. `tp/` re-implements token parity instead of reusing it [S3 #9].
  2. FA-tap exactness has no in-repo evidence (D17).
  3. `check/protected.py` enforces frozen paths against `out/capture/decisions.md`, which is not in the repo [S1 §6].

**T5. `tp/` is a copy of the single-rank pipeline, hardwired to world 2.** Covers smell 6.
- Counts:
  - `tp/` has 43 findings (8 high) [S3 §7].
  - Collective semantics are written four times: `program/registry/b1_tp2.py:98-177`, `tp/export_ops.py:42-80`, `tp/match.py:240-256` and `tp/xrank_collectives.py:166-172` [S3 #8].
  - The collective patch is written twice with different coverage (D16).
  - `tp/{capture,commit,match,fold_match}.py` total 2,062 lines that twin the single-rank drivers [syn]. `tp/worker.py:1116` says "taken verbatim" [S3 #9].
- Examples:
  1. World-2 op names in `correspondence/emit.py:30`.
  2. `tp/commit.py:322-1173` is one 852-line `main` [S3 #10].
  3. `TP2CaptureWorkerExtension` has 21 `tp2_*` RPC methods [S3 `tp/` modules].

**T6. The real interface is bash plus 73 `__main__` blocks, and nothing owns the shared keys.** Covers smells 4 and 5.
- Counts:
  - 73 of the 314 files end in `__main__`, and 71 import argparse [syn].
  - `ops/row_pod.sh` is 1,147 lines with 45 caller-settable environment knobs, 12 heredocs and 24 `python -c` lines [C3, S4 Map 1].
  - 12 test files regex-extract code from shell scripts, and 4 tests exec `commit_delta` source [C3, S4 Map 4].
  - The row id is parsed in 10 places and dtype is defined in 6. "The code this run depends on" is defined four ways, and they disagree [S4 INTERNAL-DUP; C3].
- Examples:
  1. `harness/run_config.py` runs 19 stages by spawning 9 check/observe CLIs [S4 §1].
  2. The `research` Tool command is `bash ops/run_row_v2.sh stage …` (`harness/research_tools.py:41, 254`), and `:71-80` mirrors `row_pod.sh` knobs.
  3. `harness/` holds the production pipeline, although `README.md:86-90` says "a check that lives here is misfiled" [S4 §1].

**T7. Hidden inputs change results: environment, import success, cwd, swallowed exceptions.** Covers smell 5.
- Counts:
  - SCRIPT/ENV/PATH 64 (S1 14, S2 18, S3 21, S4 11) and FALLBACKS 53 (S1 9, S2 18, S3 19, S4 7).
  - 48 library files touch `os.environ` (208 sites).
  - There are 350 `except Exception` sites, 8 `sys.path.insert` calls and 16 uses of `Path(__file__).parents[N]` [syn].
- Examples:
  1. D3, D4, D12 and D15.
  2. The environment is written at import: `program/frontend/vllm_meta.py` (5 `setdefault`s) [S2 slice size], and `observe/engine_profile.py:81-86` reached through `m1_capture.py:44-46` and `tp/capture.py:34-36` [S3 #4].
  3. Machine paths serve as defaults: `check/fold_compare.py:58` (`/Users/danielreuter/...`) [S1 #11] and `harness/research_tools.py:39` (`/workspace/venv312/bin/python`) [syn]. In addition, `program/numerics/fa2_relation.py:34-38` falls back to "verbatim" copies on any import error [syn].

**T8. Model and target facts are hardcoded outside quarantine.** Covers smell 4.
- Counts: HARDCODING 63 (S1 12, S2 23, S3 21, S4 7).
- Examples:
  1. vLLM class-name tables in `check/value_check.py:24`, `commit/binding.py:47-53` and `commit/reference_engine_adapter.py:38-53` [S1 #11].
  2. Two MoE class lists that disagree (D16), and the `sm89-eager` label on sm_90 (D12).
  3. Family facts in two tables with 9 and 7 model types (`observe/profiles/family_facts.py:43-176` vs `input_provenance/analytic.py:39-50`) [S3 profiles map].

**T9. No dependency direction, god modules, unowned patches.** Covers smell 4.
- Counts:
  - LAYERING 58 (S1 10, S2 24, S3 18, S4 6) and GOD-MODULE 43 (S1 12, S2 16, S3 11, S4 4).
  - 41 modules over 800 lines hold 56,436 lines, and 11 of them exceed 1,500 lines [syn].
  - About 15 monkeypatch points have no owner [S3 #7]. OTHER-WEIRD totals 65.
- Examples:
  1. Import cycles and wrong-direction imports:
     - observe ↔ commit (`observe/capture_v1.py:49`, `commit/merkle.py:35`), observe ↔ input_provenance, and acquire ↔ commit [S3 #11].
     - commit → check (`commit/padding_steps.py:40, 664`) and program → check (`program/numerics/relations.py:494-509`) [S1 #9].
     - Library → tests (`check/adversarial.py:448-462`, `harness/commit_delta.py:1793`) [S1 #9, S4 LAYERING].
  2. `check/global_match.py:828` `_check` is a single 1,234-line function [S1 #10].
  3. `acquire/native_host.py` is 2,587 lines with 15 jobs, and `observe/vllm_adapter.py` is 1,949 lines with 11 [S3 #10].

**T10. Names, docs and dead code record history instead of meaning.** Covers smells 7 and 2.
- Counts:
  - VERSION-RESIDUE 60, NAMING 51, DOCS 48 and DEAD 60 (per-slice counts are in §1).
  - 16 library files and 31 test files carry residue in the file name [syn].
- Examples:
  1. Residue in file names: `query/v1_bridge.py`, `observe/capture_v1.py`, `observe/m1_capture.py`, `check/global_match_fast.py`, `check/poc_*.py` (4), `program/registry/b1_tp2.py`, `ops/run_row_v2.sh` and `observe/profiles/vllm_d9105ea80_sm89_eager.py` [syn].
  2. Lab-notebook docstrings, such as `input_provenance/weights_of_record.py:1` "(R15 manbind MAN-09; rev-cb M-0610 …)" [S3 DOCS]. Words with several meanings: "attribution" (3), "twin" (3), "relation" (2) [S2 NAMING].
  3. Dead code:
     - `commit/engine_rs/`, whose empty root `[0u8; 32]` differs from Python's (`main.rs:69`).
     - The `poc_verify_bindings` → `poc_rows` chain: 1,459 lines behind one used function [S1 #12].
     - The stale package docstring (§2, "Also fix now").

## 4. Practices

There are twelve rules. Each one is enforced by one of three things:
- a CPU lint test in a new `tests/lint/`, in the style of the existing `tests/check/test_quarantine_lint.py`;
- an import-linter contract in `pyproject.toml`, run by one pytest test;
- a pod test.

The repo has no CI configuration today, so these run with the normal pytest invocation on a CPU pod before merge. Lints start as ratchets: today's violations are allowlisted, and the allowlist may only shrink.

**P1. Use core's abstractions; never copy or patch them.**
- Why: T1 (CORE-DUP 34) and D2, D8, D9, D10.
- Enforced by:
  - A test that imports `verity.ml` and every integration registry in one process. It fails today at `core/ir/defs.py:35-38`.
  - An AST lint that forbids assignment or `setattr` on `verity.*` module attributes and imports of `_private` core names.
  - After Decision 1, a test that verifies a production opening with core alone.
- Example: `codec._LAZY_PRIMITIVE_FAMILIES = tuple(...) + (...)` (`program/registry/ref_prims.py:276`) → `codec.register_lazy_family(pat, make)`.

**P2. Value checks read opened values only.**
- Why: T2 and D1.
- Enforced by: an import contract under which `check.replay` may not import `acquire` or `commit.committer`, plus a pod negative test (mutate the retained buffer after commit, and C2 must FAIL).
- Example: `OC.oracle_compare(..., OC.committed_reader(com), ...)` (`harness/commit_delta.py:2339`) → `compare(..., opened_values(commit_dir, sample))`.

**P3. One evaluator interface.** Replay, recompute, difftest and kernel checks become drivers over it, and there is one challenge derivation.
- Why: T2 (9 evaluators, 8 drivers, 6 challenge derivations).
- Enforced by:
  - A parametrized self-check that compares every registered (backend, Definition) pair with the core reference on seeded random inputs.
  - A lint: no per-family `if`-ladders outside `program/backends/`, and `random.Random` or `default_rng` only in the challenge module.
- Example: the family ladder at `check/sampled_replay.py:743-920` → `backend.evaluate(call.spec_id, call.statics, inputs)`.

**P4. Every check returns one result type, and one verdict reads it.** The result is `CheckResult(name, code, evidence)`, with `code` taken from `core/verification/codes.py`. "Gate" is reserved for circuits.
- Why: T3 (5 verdict systems, 420 `G1` to `G8` tokens) and D13.
- Enforced by: an import contract under which `check.verdict` imports only `check.result` and `properties.record`, plus a lint that forbids `G[1-8]` identifiers in code and string-prefix tests on reason fields.
- Example: `_REPLAY_SEED_ROOT_FORM = "run root (first 8 bytes, after commitment)"` (`check/commit_verdict.py:353`) → `result.code is VerificationCode.CHALLENGE_MISMATCH`.

**P5. Property logic lives in `properties/`, and runs cite property records by digest.**
- Why: T4 (11 property harnesses consumed as per-run gates, token parity duplicated in `tp/`).
- Enforced by: an import contract under which `check` and `pipeline` import only `properties.record` and `properties.check_properties`, plus a registry test that every property the verdict names exists in `properties.REGISTRY`.
- Example: `tp/`'s own token parity [S3 #9] → `properties.noninterference.check(spec)` with `spec.world == 2`.

**P6. One CLI over the public API. No `__main__`, heredocs or `python -c` in library code or `ops/`.**
- Why: T6 (73 `__main__`, 71 argparse modules, 12 heredocs, 12 shell-regex tests).
- Enforced by:
  - A lint under which `__name__ == "__main__"` and `import argparse` appear only in `pipeline/cli.py`.
  - A lint under which `ops/*.sh` may call only `verity-vllm` (no `python -m verity_vllm`, `<<` or `python -c`).
  - A `[project.scripts]` entry in `pyproject.toml`.
- Example: `python -m verity_vllm.harness.commit_delta …` inside `ops/row_pod.sh` → `verity-vllm commit ROW --config row.toml`.

**P7. Results depend only on declared inputs.** Library code doesn't read `os.environ`, cwd or machine paths. Optional imports fail loudly. No broad `except` changes output. Seeds are required arguments.
- Why: T7 (SCRIPT/ENV/PATH 64, FALLBACKS 53, 48 environment-touching files) and D3, D4, D12, D14, D15.
- Enforced by:
  - A lint: `os.environ` and `os.getenv` appear only in `pipeline/cli.py` and in `engine/env.py`, which writes vLLM's pins from config.
  - An AST lint for `except Exception` handlers that neither re-raise nor record, and for `seed` parameters with defaults.
  - A test that the plan digest is the same with torch present and with torch stubbed out.
- Example: `os.environ.get("VERITY_LAYOUT")` (`acquire/native_collect.py:721`) → a `layout` argument from `CommitConfig.layout`.

**P8. Model and target facts live only in `program/registry/quarantine/` and `engine/profiles/`.**
- Why: T8 (HARDCODING 63) and D16.
- Enforced by: extending `tests/check/test_quarantine_lint.py` with a literal scan for model names, vLLM layer class names, GPU names and `sm_8x`/`sm_9x` outside those two homes.
- Example: `MOE_SITE_CLASSES = ("MoERunner", "FusedMoE")` (`tp/partial_source.py:36`) → `profile.moe_collective_classes`.

**P9. Dependencies have a declared direction, and runtime patches have one owner.** The layers, from top to bottom:
  - `pipeline`
  - `check` | `properties`
  - `acquire`
  - `observe` | `commit`
  - `engine`
  - `query` | `correspondence`
  - `program`
  - `collectives`
  - `config`
  - core

No library code imports `tests/`, `tools/` or repo-level data. Package data is loaded with `importlib.resources`. Every vLLM or torch patch goes through `engine/hooks.py`.
- Why: T9 (LAYERING 58, four import cycles, about 15 unowned patches).
- Enforced by: import-linter layers and forbidden contracts. A1 records today's violations as explicit ignores. A lint limits attribute assignment on `vllm.*` and `torch.*` objects to `engine/hooks.py`.
- Example: `commit/padding_steps.py:40` imports `verity_vllm.check` → the population checks move to `check/`, and `commit` imports only `commit.scheme`.

**P10. Size ratchet.** Modules stay at or under 800 lines and functions at or under 150 lines. Today's offenders are allowlisted at their current size, which may only decrease.
- Why: T9 (GOD-MODULE 43; 41 modules over 800 lines hold 45% of the code).
- Enforced by: an AST line-span lint with an allowlist file.
- Example: `check/global_match.py:828` `_check` (1,234 lines) → one function per phase (structure, rows, batches, report).

**P11. Names say the job, and versions appear only in hashed data.** No module, function, class, flag or environment-variable name contains `v1`, `_v2`, `_fast`, `poc_`, `m1_`, `b1`, `tp2` or `G1`. Versioned strings stay only where they are hashed (Definition ids such as `Gemm_v1`, schema ids such as `runtime-correspondence/v1`). Docstrings say what and why. Board ids, lanes and dates go to the `research` store.
- Why: T10 (VERSION-RESIDUE 60, NAMING 51, DOCS 48).
- Enforced by: a regex lint over file, `def` and `class` names (Definition decorators exempt), and a docstring regex for `M-\d{4}`, `F-r\d+`, `[lane ` and `\bR1\d\b`.
- Example: `query/v1_bridge.py` → `query/required.py`, and `TP2CaptureWorkerExtension` → `engine.RankWorker`.

**P12. Each shared key has one owner.** `config.py` owns the row-id grammar, `RowSpec` and the dtype vocabulary. One `code_identity()` over the import closure (integration plus core) serves the research Tools, the hot worker, Build stamps and TP commits.
- Why: T6 (row id parsed 10 times, dtype defined 6 times, code identity defined 4 ways) and D5, D6.
- Enforced by: a lint that forbids row-id regexes (`__tp(\d+)__`, `__b(\d+)__`) and hand-written root lists outside `config.py` and `pipeline/identity.py`, plus a test that editing a core file in a temp tree changes the identity.
- Example: `CODE_ROOTS = ("verity_vllm", "verity_vllm_sampler", "e2e", …)` (`harness/hot_commit.py:51-52`) → `code_identity("verity_vllm.pipeline.commit")`.

## 5. Target shape

### 5.1 Package tree (12 modules or subpackages, plus `__init__.py`)

~~~text
verity_vllm/
  __init__.py      the public API (5.5), re-exports only
  config.py        RowSpec + row-id grammar, BuildConfig / MatchConfig / CommitConfig, RunEnv, dtype vocabulary, target table
  pipeline/        build.py, match.py, commit.py, report.py (stage drivers); cli.py (the one CLI); research.py (Tool adapter);
                   identity.py (code closure, provenance); admission.py; workloads.py; layout.py (Build/run directory layout); hot.py
  engine/          build.py (vLLM from a RowSpec), env.py (vLLM env pins, written at construction), driver.py (requests, arrivals),
                   hooks.py (sole owner of vLLM/torch patches), rank_worker.py, profiles/ (engine profiles, family facts, hf_configs data)
  program/         frontend/ (torch.export of vLLM classes, rules, lowering incl. correspondence emit, collective export ops);
                   registry/ (vLLM Definitions, quarantine/); model.py (config_of, weights_type); backends/ (numpy / torch / native
                   implementations: twins, derived rows, numerics models + tables); workload.py
  query/           module_body.py (Q_module_body -> BoundaryValues), required.py, manifest.py (schema, digest, verify)
  correspondence/  runtime.py (the record), reader.py (one reader), resolve.py
  observe/         observer.py (dispatch mode, Triton hook via engine.hooks), log.py, runtime_tree.py, chunks.py;
                   fold/ (log -> record Program; patterns/ one module per kernel family)
  acquire/         plan.py, install.py, sources/ (hidden FA tap, MoE, compiled, rank partials)
  commit/          scheme.py (every leaf and root rule, over verity.commitments), committer/ (host, collect, CUDA/C++), openings.py, binding.py
  check/           result.py; match/ (global match, program compare, batch decomposition, rank match); replay/ (sample, open, evaluate,
                   compare); determinism.py (value checks, oracle compare); provenance.py (weights of record, root policy);
                   executed_prefix.py; verdict.py
  properties/      record.py, noninterference.py, census.py (+ kernel allowlist), golden.py, holdout.py, admission.py (difftest),
                   quarantine_lint.py, protected.py, evaluator_selfcheck.py, fa_tap_exactness.py
  collectives/     record.py (one collective record), hook.py (one communicator hook for recorder and committer),
                   shards.py (one shard-layout description), semantics.py (kinds, world-parametric reduction order)
~~~

Each directory is one job. The mapping below is based on the survey disposition tables ([S1 §9], [S2 §5], [S3 dispositions], [S4 disposition]).

### 5.2 Where every current subpackage goes

| today | destination |
|---|---|
| `check/` (35) | Per-run checks stay in `check/`:<br>• match: `global_match` (with `global_match_fast` merged in), `program_compare`<br>• replay drivers<br>• `determinism`: `value_check` + `compiled_value_check` + `oracle_compare`<br>• `executed_prefix`, `kernel_identity`, `operand_provenance`<br>• `verdict`, which absorbs `commit_verdict` and `gates`<br>`noninterference`, `census`, `kernel_allowlist`, `golden`, `holdout`, `difftest`, `quarantine_lint` and `protected` go to `properties/`. The `twins` and `relations` checkers go to `program/backends/`. `adversarial`, `fa2_attn_oracle` and `mock_global_program` go to tests. `poc_rows`, `poc_verify_bindings` and most of `compiled_fx_kernels` are deleted. `poc_description` and `poc_required_interface` follow the bundle format (Decision 6). |
| `commit/` (22) | Leaf and root rules from `semantic_layout`, `hidden_stream`, `hidden_engine`, `padding_steps` and `fasttree` go to `commit/scheme.py`. Openings and the binding map stay; `binding`'s class sniffing goes to quarantine and its challenge to core. `hashing` and most of `merkle` are replaced by `verity.commitments`. `stream_merkle` and `fa2_prototype/` go to tests. `reference_engine*` and `engine_rs/` are deleted (Decision 6). |
| `program/` (107) | Stays: `frontend/`, `registry/`, `workload.py`. `numerics/` goes to `backends/`. `global_program.py` goes to `pipeline/build.py`. `frontend/liveness.py` goes to core. `frontend/b1_authored.py` and `numerics/inductor_models.py` go to tests. `numerics/cuda/*.cu` goes to pod probes outside the package. |
| `query/` (12) | Stays: `module_body`, `required` (from `v1_bridge`), `manifest`. `boundary` and `partition` go to core `verity.ir`. `vu_query` goes to `check/replay/`. `manifest/compiled.py` goes to `acquire/`. |
| `correspondence/` (12) | Stays: `runtime`, one reader (from `reader_for_query` + `reader_for_acquire`), `resolve`. `emit` goes to `program/frontend/`. `batch_decomp` goes to `check/match/`. `runtime_tree` and `chunk_attribution` go to `observe/`. `resolve_decomp`, `batch_candidate` and `capture_identities_program` are deleted. |
| `observe/` (36) | The observer, Triton adapter, storage, events and log stay in `observe/`. `fold`, `tree`, `views`, `memory`, `resolver` and `patterns` go to `observe/fold/`. `vllm_adapter`, `engine_profile`, `arrivals`, `engine_driver` and `profiles/` go to `engine/`. `m1_capture` and `tp/capture` become the capture stage of `pipeline/match.py`. `capture_v1` follows Decision 6. |
| `acquire/` (19) | `plan`, `install`, `stage` and the sources stay in `acquire/`. `native_host`, `native_collect`, `leafhash`, `hidden_gpu` and the CUDA/C++ sources go to `commit/committer/`. |
| `tp/` (15) | `collective_record`, `collective_sites`, `embedding_shard` and one hook go to `collectives/`. `worker` goes to `engine/rank_worker.py`. `partial_source` goes to `acquire/sources/`. `export_ops` goes to `program/frontend/`. `collective_pattern` goes to `observe/fold/patterns/`. `rank_match` and `xrank_collectives` go to `check/match/`. `capture`, `commit`, `match` and `fold_match` merge into world-parametric `pipeline/` drivers. `analyze` and `collective_link` go to tests or are deleted. |
| `input_provenance/` (3) | `analytic` goes to `program/model.py`. `weights_of_record` and `root_policy` go to `check/provenance.py`. |
| `harness/` (25) | Into `pipeline/`:<br>• `derive_step` becomes `build`, `run_config` becomes `match`, and `hot_commit` becomes `hot`<br>• `commit_delta` becomes `commit`, split three ways: verdict, C2 and prefix go to `check/`; `binding_record` and openings go to `commit/`; the driver stays in `pipeline/`<br>• the three `research_*` modules become `research`; the three admission modules become `admission`<br>• `source_identity`, `release_json` and `experiment.code_version` become `identity`<br>• `workload` and `coverage_workloads` become `workloads`; `card` becomes `report`; spans and timeline become one telemetry module<br>Elsewhere: `target_family` goes to `config.py`; `gc_tuning` is called once by the CLI; `synthetic` goes to tests; `rebuild_digest_gate` and `topp_split_probe` are deleted. |
| `ops/` (16) | `row_pod.sh`, `tp_stage.sh`, `run_row_v2.sh`, `canary.sh`, `compiled_commit.sh`, `cov_pod.sh`, `verify_lane.sh` and `pod_gate.sh` become CLI subcommands. The pod provisioning scripts stay (`pod_bootstrap.sh`, `pod_fa2_tap.sh`, `pod_fa3_tap.sh`, `pod_hidden_gpu.sh`). `row_pod_tp2.sh` and the three negative-campaign scripts are deleted or moved to tests. |
| `build_paths.py` | `pipeline/layout.py`. |
| data directories | Library-read data becomes subpackage data: `data/hf_configs` goes to `engine/profiles/`, `docs/data/ref-prims` to `program/registry/`, and `fixtures/W11*` to `program/backends/`. `manifests/` and `workloads/` stay as run definitions loaded by `config.py`. Unread data goes to an archive outside the package. `tools/` (relayout) is deleted [S4 disposition]. |

### 5.3 Verity core vs. the integration

| moves to core | today | core destination |
|---|---|---|
| Commitment scheme alignment (Decision 1) | D2. Eight framing copies; six JSON canonicalizations [S1 §4] | `verity.commitments`: the scheme that production uses, and `identity` canonical JSON |
| Challenge derivation | Six derivations, and core has none [S1 §4.4] | `verity.verification`: `derive_challenge(root, domain, n)`; sampling rates stay in `verification/plan.py` |
| Evaluator interface | E1 is `core/ir/evaluate.py:22, 50`; E2 to E9 are integration code [S1 §3.1] | `verity.ir.evaluate`: an `Evaluator` protocol, `CoreEvaluator` and `self_check(fast, reference, spec_id, rng)`. The backends stay here. |
| Generic IR analyses | `query/boundary.py`, `query/partition.py`, `program/frontend/liveness.py`, and four interval algebras | `verity.ir`. Core already plans this (`core/ir/parts.py:15-18`, `core/ir/layout.py:19`). |
| Collectives | Four semantics, world-2 records (T5) | `verity.commitments`: a group root over rank roots. `verity.verification`: a `CommitmentRef` that names a rank, plus a cross-Program link (peer input = committed partial). `verity.ml`: `AllReduce{WORLD,N}` with the reduction order as a static, and `AllGather{WORLD,N}`. |
| Shared Definitions | D8, D9; `*_v2` gemm; `numerics/mma.py` | These already exist in `core/ml/prims`, `ml/gemm` and `ml/tc/models`. Upstream the FP16 product [S2 §5]. |
| Outcome codes | Five verdict systems | `core/verification/codes.py`. Add codes only where a verifier would reject. |

**Stays in the integration:**
- the vLLM frontend and rules, the vLLM Definitions (FA2/FA3 attention, fused RMSNorm, sampler, MoE) and their numpy/torch/native backends;
- the engine, hooks, observer and fold patterns, acquisition, and correspondence to vLLM module paths;
- the GPU committer (CUDA/C++, implementing core's scheme);
- the pipeline, CLI and research adapter;
- the vLLM-specific properties (non-interference of hooks, kernel census, FA-tap exactness);
- quarantine tables and profiles;
- the NCCL reduction-order fact, as profile data.

### 5.4 What gets deleted

All sizes are [syn] `wc -l`.
- **Dead now** (about 5.2k lines):
  - `check/poc_rows.py` (681), `check/poc_verify_bindings.py` (573), and `check/compiled_fx_kernels.py` (205) except `normalise_kernel` [S1 §9].
  - `correspondence/resolve_decomp.py` (270), `batch_candidate.py` (457) and `capture_identities_program.py` (554) [S2 §5].
  - `commit/hidden_engine.py` (107, a shim), `commit/engine_rs/` (348 lines of Rust) and `harness/rebuild_digest_gate.py` (130).
  - `ops/row_pod_tp2.sh`, `tools/` (1,839 lines of Python plus a 1,229-line map), 3 superseded `manifests/semantic-profiles/` and 6 unread legacy workloads [S4 disposition].
- **Replaced by core:** `commit/hashing.py` (161), most of `commit/merkle.py`, and the fold copies in `fasttree.py` and `native_host.py`.
- **Replaced by merges:**
  - `check/global_match_fast.py` (729) and `tp/{capture,commit,match,fold_match}.py` (2,062).
  - `commit_verdict.py` (into `verdict.py`), `twins.py` + `derived_rows.py` (into backends), and the `sampled_replay` ladder.
  - `ops/row_pod.sh` + `tp_stage.sh` + `run_row_v2.sh` (1,654 lines of bash).
- **Moved to tests** (about 3.8k lines):
  - `commit/fa2_prototype/` (1,465 lines plus 2 MB of fixtures), `commit/stream_merkle.py` (179) and `harness/synthetic.py` (457).
  - `check/adversarial.py` (699), `check/fa2_attn_oracle.py` (229), `program/frontend/b1_authored.py` (668) and `program/numerics/inductor_models.py` (139).
- **If Decision 6 says so:** `commit/reference_engine/` (1,144) and `reference_engine_adapter.py` (259), which make up the CMT-1 committer, plus the PoC bundle chain once `merkle` comes from core.

### 5.5 Public API and the one CLI

~~~python
# verity_vllm/__init__.py re-exports exactly these names.
@dataclass(frozen=True)
class RowSpec:                       # verity_vllm.config
    model: str                       # HF repo id
    revision: str                    # full commit sha, checked against manifests/checkpoints.json
    dtype: Dtype                     # "bf16" | "fp8"
    target: str                      # "l40s", "h100", ... -> one compute-capability table
    world: int = 1                   # tensor-parallel degree
    batch: int = 1
    workload: Workload = ...         # prompts, lengths, sampling, arrivals
    query: str = "Q_module_body_v1"  # hashed id, not a code name
    @classmethod
    def load(cls, ref: str | Path) -> "RowSpec": ...   # a row id, or a workloads/<row>.json file
    @property
    def row_id(self) -> str: ...
    def digest(self) -> str: ...

def build(spec: RowSpec, out: Path, config: BuildConfig = BuildConfig()) -> Build: ...
    # torch.export of the vLLM model class on meta -> Program, BoundaryValues manifest, correspondence record
def match(spec: RowSpec, build: Build, out: Path, config: MatchConfig = MatchConfig()) -> MatchReport: ...
    # run vLLM with the observer, fold the log, compare with the Build's Program
def commit(spec: RowSpec, build: Build, out: Path, config: CommitConfig = CommitConfig()) -> Commitment: ...
    # run vLLM with acquisition hooks, commit the required values, write roots and openings
def replay(commitment: Commitment, build: Build, challenge: Challenge, backend: str = "numpy") -> list[CheckResult]: ...
    # reads opened values only (P2); backends: "reference" (core), "numpy", "torch", later "jax"
def check_properties(spec: RowSpec, names: Sequence[str] | None = None, out: Path | None = None) -> list[PropertyRecord]: ...
def verdict(results: Sequence[CheckResult], properties: Sequence[PropertyRecord]) -> Verdict: ...

@contextmanager                      # vLLM wrapped directly; match() and commit() use the same object
def open_engine(spec: RowSpec, *, observe: bool = False, acquire: AcquisitionPlan | None = None) -> Iterator[Engine]: ...
class Engine:
    llm: "vllm.LLM"
    def generate(self, workload: Workload) -> Tokens: ...
~~~

~~~text
verity-vllm row        ROW [--config FILE] [--out DIR]     build, match, commit, replay, verdict (replaces ops/row_pod.sh, tp_stage.sh)
verity-vllm build      ROW [--config FILE] [--out DIR]
verity-vllm match      ROW --build DIR [--out DIR]
verity-vllm commit     ROW --build DIR [--out DIR] [--hot]
verity-vllm replay     COMMIT_DIR [--backend numpy|torch]
verity-vllm properties ROW [--only NAME ...]
verity-vllm verdict    RUN_DIR
~~~

The `research` Tools `vllm.build`, `vllm.match` and `vllm.commit` run `verity-vllm <stage> ROW --config …` instead of `bash ops/run_row_v2.sh stage` (`harness/research_tools.py:41, 254`). `research` becomes an optional dependency, imported only by `pipeline/research.py`; today `research_tools.py:36` and `source_identity.py:36` import it at load [S4 LAYERING].

### 5.6 Where configuration lives

Configuration moves out of environment variables into five places:
- **What runs:** `RowSpec`, from a row id or a `workloads/` file. Checkpoint pins come from `manifests/checkpoints.json`, loaded once by `config.py`; today they come from 16 argparse defaults [S4 disposition].
- **How a stage runs:** the `BuildConfig`, `MatchConfig` and `CommitConfig` dataclasses. Defaults are in code, overrides come from `--config` or flags, and each config is serialized into its artifact and digest. For example:
  - `CommitConfig.layout`, `retain`, `window_mb`, `window_slots` and `hot` replace the environment copies at `harness/commit_delta.py:1197-1267`.
  - `MatchConfig.impl` replaces `MATCH_IMPL`.
- **Where it runs:** `RunEnv`, which holds the python, cache, scratch and output roots. It is read from the environment or flags in `pipeline/cli.py` only, recorded as telemetry, and never hashed into results.
- **vLLM's own switches:** one table in `engine/env.py`, written into the engine process at construction. Today they are written at import (`observe/engine_profile.py:81-86`, `program/frontend/vllm_meta.py`).
- **Model and target facts:** package data in `program/registry/quarantine/` and `engine/profiles/`.

Tests keep their own switches (`VERITY_REGRESSION*`). Documentation lives in docstrings and a rewritten existing `README.md`; no new Markdown goes into the repo.

## 6. Phased plan

**The gate for every lane:**
1. The regression harness is green: `VERITY_REGRESSION=1 pytest tests/regression -m regression` (the 12 frozen rows, tiers T0 and T1). The integration's full CPU test suite shows 0 failures and no new skips, measured against the lane's base commit. Both run on a CPU pod. (There are no fixture sets named "fA" and "fB". The integrator used those labels for two harness invocations, `20260924T1352Z-final.md:17`.) Lanes that touch GPU stages also produce candidate row dirs on a GPU pod through the `research` Tools and point `VERITY_REGRESSION_CANDIDATE` at them (`tests/regression/test_regression.py:77-88`).
2. From A1 on, `tests/lint/` and the import contracts are green, and no allowlist grows.
3. From A5 on, there is no `__main__` or `argparse` outside `pipeline/cli.py`.
4. Heavy runs happen only on pods.
5. Phase 1 and Phase 2 lanes leave Program digests, manifest digests, roots and verdicts unchanged. Code-identity digests and research cache keys may change.

Sizes: S is under 500 changed lines, M is 500 to 3,000, and L is over 3,000 lines or over 50 files.

**Phase 0: correctness fixes on today's layout.** These are independent PRs and can all run in parallel.

| lane | scope | size | validated on |
|---|---|---|---|
| F1 | D1: opened-value replay, single rank and per rank, plus the mutate-after-commit negative test | M | GPU pod: dense, MoE and TP2 Commit rows |
| F2 | D5, D6, D7: identity stamps and row-spec pins | S | CPU pod: Build T0, plus a test that a core edit changes the key |
| F3 | D3, D4, D14, D15: undeclared inputs | M | CPU pod; GPU pod for D3 (roots unchanged where the two variables agreed) |
| F4 | D10, D11, D13: Match and verdict integrity | M | CPU pod: Match and verdict rows unchanged |
| F5 | D16: one MoE class list, the quarantine AllReduce order, refuse world > 2 in `emit` | M | GPU pod with 2 GPUs (shared-expert MoE, TP2) |
| F6 | D17: FA-tap exactness as a property with a record | M | GPU pod (FA2 on L40S, FA3 on H100) |

The digest-changing defects (D2, D8, D9, D12) wait for Phase 3.

**Phase 1: mechanical, behavior-preserving moves.**
- **A1. Guardrails** (S; no dependencies; CPU). Add the `tests/lint/` ratchets for P1, P3, P4 and P6 to P12, with today's violations allowlisted. Add the import-linter contracts for P2, P5 and P9, with today's violations as ignores, and the `[project.scripts]` entry. Accept: lints green, allowlists committed.
- **A2. Dead code out** (M; parallel with A1; CPU). The §5.4 "dead now" and "moved to tests" lists, plus the §2 "Also fix now" items. Accept: about 5k library lines deleted and about 3.8k moved to tests.
- **A3. Data and paths** (S to M; parallel with A1 and A2; CPU plus one GPU smoke row). Load library-read data with `importlib.resources`. Remove the 8 `sys.path.insert` calls, the 16 uses of `Path(__file__).parents[N]`, the machine paths, and the library read of `tests/` (`harness/commit_delta.py:1793`).
- **A4. Re-home** (L; after A1 and A2 and after the Phase 0 lanes have merged, because a tree-wide `git mv` under open fix branches produces conflicts in every one of them; CPU plus one GPU smoke row per stage). `git mv` into §5.1 and rename code names, but not hashed ids. Update every importer in the same change, with no compatibility shims, including string module paths such as `EXTENSION` at `tp/worker.py:74`. Accept: the target layering contract passes.
- **A5. One CLI and typed config** (L; after A4; GPU pod). Add `config.py` and `pipeline/cli.py` and remove library `__main__` and argparse. `row_pod.sh`, `tp_stage.sh` and `run_row_v2.sh` become `verity-vllm row`, and the research Tools call the CLI. Environment reads move into the CLI, keeping today's defaults. The shell-regex and source-exec tests become unit tests. Accept: every regression row family re-runs through `verity-vllm row` with identical artifacts.

**Phase 2: consolidation, with the same digests and verdicts.**
- **B1. Evaluator backends and replay** (smell 1; L; after F1 and A4). `program/backends/` merges `twins`, `derived_rows`, the `sampled_replay` ladder, the `relations` checkers and `numerics`. `check/replay/` becomes sample, open, evaluate, compare. `replay`, `stoch_recompute`, `compiled_kernel_check` and `difftest` become drivers sharing one challenge function. Accept: the self-check covers every (backend, Definition) pair and `sampled_replay.py` is gone, validated on a CPU pod plus one GPU Commit row per model family.
- **B2. One verdict and `properties/`** (smells 2 and 3; M to L; after F4 and A4, with the heredoc after A5). Add `check/result.py`, and a `check/verdict.py` that absorbs V1 to V5 and the heredoc at `ops/row_pod.sh:686-800`. Runs cite `properties/` records by digest, and a world-parametric non-interference check replaces `tp/`'s token parity. Accept: the verdict JSON of regression rows is unchanged. Non-interference and census need a GPU pod.
- **B3. Collectives** (smell 6; L; after F5 and A5). Add `collectives/`. World-parametric drivers replace the `tp/` drivers, and the rank worker moves to `engine/rank_worker.py`. Accept: TP rows #70 and #75 are unchanged and a TP4 row passes, on GPU pods with 2 and 4 GPUs.
- **B4. Engine and hooks** (M; after A4; GPU pod). Add `engine/`, which writes environment pins at construction, and `hooks.py`, which owns every patch and can uninstall it. This is the behavior-preserving part of D12; C3 changes the identities.
- **B5. God-module splits** (L; after A4; one PR per module, all in parallel). `harness/commit_delta.py`, `acquire/native_host.py`, `check/global_match.py` (`_check`), `program/registry/lifted.py`, `frontend/rules/vllm_bindings.py`, `observe/patterns.py`, `observe/vllm_adapter.py` and `correspondence/batch_decomp.py`. Accept: their entries leave the size ratchet. The committer modules need a GPU pod.

**Phase 3: semantic changes, behind decisions, in one re-baseline epoch.**
- **C1. Commitment scheme** (D2, Decision 1). M to L; after B1. Validated on a GPU pod: the CUDA kernels, plus commit throughput measured before and after.
- **C2. Definition library** (D8, D9, Decision 3). M; after A4. Core ids replace the shared Definitions, and `core/ml/gemm` replaces the `*_v2` gemm Definitions. Program digests on a CPU pod, spot rows on a GPU pod.
- **C3. Identities and artifact keys** (D12, Decision 4). S; after B4; GPU pod. The profile id loses the pod id and the fallback, and the G1 to G8 artifact keys get names.
- **C4. Upstream to core** (Decision 5). M to L; CPU. The IR analyses can go at any time after A4. The challenge derivation, evaluator protocol, rank-indexed commitments and collective families follow B1 and B3.
- **Epoch.** One reviewed `tests/regression/rebaseline.py write` after C1 to C3 land (Decision 4).

**Parallelism.**
- F1 to F6 run in parallel. A1, A2 and A3 run in parallel, then A4, then A5.
- After A4, B1, B4, B5, C2 and the IR-analysis part of C4 run in parallel. After A5, B3 and B2's heredoc part follow.
- C1 follows B1, and C3 follows B4.

**GPU pods are needed for** F1, F3 (the D3 part), F5, F6, A5, B1 (spot rows), B2, B3, B4, B5 (the committer modules), C1, C2 (spot rows) and C3. F2, F4, A1 to A4 (apart from smoke rows) and C4 need only a CPU pod.

## 7. Owner decisions

1. **Commitment scheme (D2).**
   - (a) Production adopts core's `commitments.merkle` framing: domain-bound leaves, nodes bound to (level, index), and padding. Core statements and multiproofs can then reference production positions [S1 §3.5]. The CUDA constants change, and every row is re-baselined.
   - (b) Core adopts the production rules (`pos_leaf`, the chunk leaf, the root bindings) as named schemes with a core verifier. Roots don't change, but core statements still can't address production positions.
   - (c) Keep the status quo, behind one `commit/scheme.py`.
   - **Recommendation: (a).** Gate it on a pod measurement of commit throughput under core framing, and fall back to (b) if the cost is unacceptable. Build the single scheme module in Phase 1 either way.
2. **Where value checks run (D1).**
   - (a) In the Commit process, over openings.
   - (b) Only in a separate verifier process over the committed directory (Build plus openings).
   - (c) Both, with (b) as the result of record.
   - **Recommendation: (a) now (F1), and (c) once B1 lands,** so the prover's process never grades itself.
3. **Definition ids that collide or changed meaning (D8, D9).**
   - (a) Retire the integration copies, have Programs cite core's ids (including `AmpereBF16TcDot16` v2), and mark pre-R17 evidence that cites v1 as superseded.
   - (b) Restore v1's pre-R17 body and add a new id for the current semantics.
   - (c) Keep both as they are.
   - **Recommendation: (a).** It leaves one Definition library, and only one epoch of old evidence needs a note.
4. **Re-baseline policy.**
   - (a) One epoch bump that batches every change to digests, roots or artifact keys (D2, D8, D9, D12, and the G1 to G8 key renames), reviewed as one `rebaseline.py` diff.
   - (b) Re-baseline after each fix.
   - **Recommendation: (a).** Fixes that don't change digests (D1, D3 to D7, D10, D11, D13 to D17) land immediately.
5. **Order of upstreaming to core.**
   - (a) Upstream first, then consolidate.
   - (b) Consolidate first, behind core-shaped interfaces in the integration, then upstream.
   - (c) Keep everything in the integration.
   - **Recommendation: (b) for the evaluator protocol, challenge derivation and collectives,** so one real user shapes the API. Use (a) for boundary, partition and liveness, whose promotion core already plans.
6. **Experimental and PoC paths.**
   - (a) Delete CMT-1 (`commit/reference_engine/`, its adapter and `cmt_ref_*` in `commit_delta`: 1,403 lines), `engine_rs`, and the PoC bundle chain once `merkle` comes from core.
   - (b) Move them to a bench directory.
   - (c) Keep them.
   - **Recommendation: (a).** None has a production caller [S1 §9], and git history keeps them.
7. **Tensor-parallel scope (D16).**
   - (a) Refuse world > 2 now (F5), and generalize in B3 with a 4-GPU validation.
   - (b) Support world N immediately by patching `emit` and the quarantine family in place.
   - (c) Support world 2 only, permanently.
   - **Recommendation: (a).** A silent world-2 assumption is worse than a refusal.
8. **Public API scope.**
   - (a) Build engines only from a `RowSpec` (pinned model, revision and environment), through `open_engine(spec)`.
   - (b) Also wrap a user-built `vllm.LLM`.
   - **Recommendation: (a) first.** Pinning is what makes non-interference and identity meaningful. Revisit (b) once `engine/hooks.py` owns every patch (B4).

**Decision log (owner, after the survey):**
- 2026-09-25 (owner, relayed 06:32Z): evaluator implementations are "kernels". The directory §5.1 and §5.2 call `program/backends/` is named **`program/kernels/`** (`numerics/` with its tables and C++ sources, twins, derived rows). B1's "`program/backends/`" means `program/kernels/` too.
- 2026-09-25, decision 1: vLLM keeps its existing framing as the named core scheme `vllm-v1`, and proof backends implement `vllm-v1` as well. frame-v3 stays as a second scheme, and both are benchmarked at serving and proving time. There is no planned migration of production to frame-v3. C1 = the named-scheme form (vLLM commit path over `verity.commitments.vllm_v1`, byte-exact against its conformance vectors) plus per-scheme commit-throughput instrumentation. Assessment: Project store `internal/commitment-format-assessment.md`.
- 2026-09-25, decisions 3, 4 and 5: approved as recommended (3a, 4a, 5b with (a) for boundary, partition and liveness). The principle for 3: core owns the basic Definitions and all silicon semantics, and the integration cites core for those and defines only its own application-specific Definitions; C2 flags anything on the line between the two.
- 2026-09-25, decision 8: ship our own wrapped vLLM that behaves like `vllm.LLM`. The user constructs `verity_vllm.LLM(model, revision=..., {supported options})` the way they would construct `vllm.LLM`; we build and pin the engine internally, and it returns what vLLM returns plus our records. The API starts limited, every supported option is documented, and unsupported options fail loudly. Wrapping a user-built engine is out of scope for now. The name "RowSpec" leaves the public API and the docs; the pinned internal record keeps a descriptive internal name. Applied in A5.
- 2026-09-25, budget: vLLM gets $300 of new spend tonight (of $600 overnight across both campaigns); the vyv- cap was raised from $600 to $623 at 06:47Z.
