---
id: vllm-refactor/survey-check-commit
lane: vllm-refactor
kind: survey
status: draft
created: 2026-09-24
checkout: f0810a11 (lane/vllm-cleanup-2), read-only
slice: integrations/vllm/verity_vllm/check/ (37 files, 24,875 lines) + integrations/vllm/verity_vllm/commit/ (39 files incl. fa2_prototype + engine_rs, ~7,000 lines of code + 2 MB fixtures)
---
# Code-smell survey: `check/` and `commit/`

Paths below are relative to `integrations/vllm/verity_vllm/` unless they start with `packages/` (Verity core, `packages/verity/src/verity/`) or `tests/` (`integrations/vllm/tests/`). Line numbers are at `f0810a11`. Method: `rg`, `wc`, reading; no Python was run. "Importers" means absolute imports, relative imports, `importlib` strings, `python -m` in `ops/*.sh`, and tests; `tests/dead_code_keep.json` (the dead-module allowlist enforced by `tests/test_no_dead_modules.py`) was consulted before every DEAD claim.

Severity: **high** = affects what the verifier can soundly claim, or blocks the refactor; **medium** = real duplication or coupling that will cost a refactor; **low** = cosmetic or local.

---

## 1. `commit/`

**Job vs name.** The name suggests "the commitment scheme". What it actually holds: (a) the PoC capture-bundle Merkle scheme (`hashing`, `identity`, `merkle`: id-bound `verity-vllm/leaf/v1` leaves, a near copy of core `commitments/leaves.py`); (b) five alternative tree engines from perf/research rounds (`fasttree`, `stream_merkle`, `semantic_layout`, `hidden_engine`, `reference_engine/` "CMT-1", `engine_rs/`); (c) the FA2 hidden-stream chunk format (`hidden_stream`) whose chunk header production's native committer reuses as the leaf header for *every* tensor; (d) Commit-stage record logic that is really check/harness logic (`binding`: binding map, coverage, challenge draw; `padding_steps`: padded-record synthesis, population checks, a CLI); (e) a test-only FA2 prototype with 2 MB of fixtures. The production committer itself lives in `acquire/native_host.py`; `commit/` is primitives plus experiments.

| module | lines | job |
|---|---:|---|
| `__init__.py` | 6 | docstring is acquire's "R10 acq-native ... `native_collect.NativeCollectCommitter`" text; describes nothing in `commit/` |
| `hashing.py` | 161 | `H(tag, *parts)`, leaf/node/lift/ids/empty/challenge tags, canonical JSON digest, `profile_id` |
| `identity.py` | 406 | canonical value/weight/boundary id grammar (parse, format, `sort_key`, `tree_sorted`) |
| `merkle.py` | 735 | id-sorted Merkle trees, `Opening`/`RangeOpening`, `TreeCache`, `commitments.json` build/verify over capture_v1 bundles |
| `fasttree.py` | 134 | packed-identity leaf digest + `fold`/`fold_levels` with a pluggable hash (sha256/blake3/noop); the fold `native_host` uses |
| `stream_merkle.py` | 179 | O(log n) streaming frontier + replay-to-open |
| `semantic_layout.py` | 190 | "C0" position-identified layout, `pos_leaf`, `semantic_root` (only `pos_leaf` is used by library code) |
| `hidden_engine.py` | 107 | re-export shim + `bind_root` (the step-root binding production uses) + cost-model helpers |
| `hidden_stream.py` | 394 | FA2 hidden "M1" stream layout, `fa2h` chunk header, chunk/thread leaf digests, stream/thread root binding |
| `binding.py` | 739 | binding map (identity -> leaf range), member rules per vLLM module class, coverage vs required manifest, `challenge_identities` draw |
| `padding_steps.py` | 936 | synthesize padding steps (leaves, roots, openings, map entries), pod hook, offline record conversion CLI, padded-population and oracle checks |
| `reference_engine/__init__.py` | 80 | re-exports of the CMT-1 experimental engine |
| `reference_engine/engine.py` | 437 | CMT-1 position-leaf committer, openings, `Verifier` |
| `reference_engine/positions.py` | 147 | leaf index <-> (class, instance, element) layout for one engine step |
| `reference_engine/torch_sha256.py` | 241 | batched SHA-256 in torch ops; pos-leaf/node/lift digests |
| `reference_engine/triton_sha256.py` | 239 | generated Triton SHA-256 kernels, written to `~/.cache/verity_cmt` |
| `reference_engine_adapter.py` | 259 | `acquire` Committer subclass wrapping CMT-1 over `native_host` (class-id table) |
| `engine_rs/src/main.rs` (+Cargo) | 166 | Rust "C1 pilot" Merkle engine; no callers |
| `fa2_prototype/__init__.py` | 6 | package doc naming `costs.py` and `test_*.py`, which are not there |
| `fa2_prototype/encoding.py` | 246 | canonical encoding of FA2 in-kernel values (SmolLM2 geometry defaults) |
| `fa2_prototype/layouts.py` | 495 | two commitment layouts over the attention value stream |
| `fa2_prototype/fixture.py` | 173 | loads p0 `.npz` fixtures (with a `/private/tmp` fallback) + a 4,390-line geometry JSON |
| `fa2_prototype/derived.py` | 75 | derived-value openings (`F2fpBf16`, `Bf16ToF32`) |
| `fa2_prototype/oracle.py` | 163 | `AttentionHead_v3` via `evaluate_call` transcript; MUFU tables preloaded at import |
| `fa2_prototype/reference.py` | 126 | numpy FA2 approximation (not bit-exact) for mechanics tests |
| `fa2_prototype/kernel_dump.py` | 181 | reads instrumented-kernel P0 dumps |
| `fa2_prototype/fixtures/` | 2.0 MB | 7 `p0_*.npz` + `p0_summary.json` + `SHA256SUMS` + `b0_c256_attention_geometry.json` (4,390 lines), inside the library package |

### 1.1 Findings in `commit/`

**CORE-DUP**
- `commit/hashing.py:50-131` vs `packages/verity/src/verity/commitments/leaves.py:73-150`: same tags, same `H` framing, same `leaf_hash`/`node_hash`/`lift_hash`/`ids_digest`/`empty_root`. Core's module says it is "the generic core of veritor `vllm-poc/verity_vllm/commit/hashing.py`" (`leaves.py:27`). Only error types differ (`ValueError` vs `InvalidArtifact`). **high**
- `commit/hashing.py:133-138` `canonical_json_bytes` uses `ensure_ascii=True` and accepts floats; core `packages/verity/src/verity/commitments/identity.py:44-62` uses `ensure_ascii=False` and rejects floats. Same name, different bytes for any non-ASCII string or float, so `json_digest`/`profile_id`/`Challenge.digest` are not core-compatible. **medium**
- `commit/merkle.py:44-157,374-513` (`path_shape`, `tree_depth`, `Opening`, `fold_path`, `verify_opening`, `MerkleTree`) vs core `leaves.py:169,276,304` (`fold_path`, `verify_opening`, `LeafTree`). The additions (id-grammar validation, `RangeOpening`) are integration-layer concerns core explicitly leaves out; everything else is a copy. **high**
- `commit/fasttree.py:31-111`, `commit/stream_merkle.py:31-160`, `commit/reference_engine/torch_sha256.py:132-215`, `commit/engine_rs/src/main.rs:17-69`: the same node/lift fold re-implemented four more times (packed, streaming, torch, Rust) instead of calling one core fold. **medium**

**INTERNAL-DUP**
- Tag constants re-typed as literals instead of imported: `reference_engine/torch_sha256.py:132-136`, `engine_rs/src/main.rs:17-19`, `semantic_layout.py:44`, and (outside the slice) `acquire/native_tree.cu:72-73`, `acquire/native_leafhash.cu:73-75`. **medium**
- Run-root formula `sha256(ROOT_TAG_RUN || program || geo || u64 S || fold(step roots))` exists three times: `padding_steps.py:49,308-310` and `acquire/native_host.py:57,2063,2484`. `padding_steps.layout_digest`/`ctx_digest` (`:242-251`) restate native_host's. **medium**
- `reference_engine/engine.py:344` `verify_opening` and `:386-427` `Verifier.verify` implement the same check twice. **low**
- `hidden_engine.py:92` `path_in_levels` duplicates `merkle.MerkleTree.path`; `padding_steps.py:313-323` `opening` hand-rolls the same sibling walk. **low**
- `binding.py:676-716` `challenge_identities` is one of seven sample/challenge derivations in the slice (see Map 1 and §2.3). **medium**
- `padding_steps.py:54` `LIFTED_CONTAINER` dtype-alias table restates dtype names other modules already normalise (`program/dtypes.py`, `check/sampled_replay.py:66-69`). **low**

**VERSION-RESIDUE** (code names, not hashed data)
- `commit/reference_engine/` = "CMT-1", `reference_engine_adapter.py` bridges "CMT-1 to CMT-2/3", `semantic_layout.py:1` "C0", `engine_rs` "C1 pilot", `hidden_engine` "C0/C1": round codenames as module identities. **medium**
- `merkle.py:35` imports `observe.capture_v1` (versioned module name) and its private `_write_json`. **low**
- `hidden_stream.py:75,145` `legacy_tile` switches the chunk header layout; "duck-typed layouts (native_host._L) = legacy". **medium**
- `binding.py:39` `RULES_VERSION = "r14-v1"` (a round id) written into every binding map. Legit as data, but named after a round, not a rule. **low**
- `fa2_prototype/` name and its `encoding.py:5` docstring reference `b1.AttentionHeadV3` (the "b1" registry) and R8 lanes. **low**

**HARDCODING**
- `binding.py:47-53` `MEMBER_RULES` keyed by vLLM module class names, `FIRST_NORM_SUFFIX = ".layers.0.input_layernorm"`; `:245-251` OLMoE/Qwen3 `q_norm` rule; `:263-265` hidden source picked by sniffing `"FA3"`/`"HiddenM1"` in the class name. Model-family knowledge outside `program/registry/quarantine/`. **medium**
- `reference_engine_adapter.py:38-53` `CLASS_ID`/`FAMILY_OF_CLASS_ID` tables including a SmolLM2 vocab-specific id. **medium**
- `fa2_prototype/encoding.py:103-107` geometry defaults `D=64, NH=9, KVH=3` (SmolLM2-135M). **low**
- `hidden_stream.py:34-35` `TAG = 0x68326166 ('fa2h')`, `VERSION = 7`: an FA2-specific header constant that production uses for every tensor's leaves (see Map 2). **medium**

**SCRIPT/ENV/PATH**
- `hidden_engine.py:22-24` and `reference_engine/engine.py:27-29`: `Path(__file__).parents[2|3] / "vllm-poc"` + `sys.path.insert`; `integrations/vllm/vllm-poc` does not exist (dead code at import). **medium**
- `padding_steps.py:37` `sys.path.insert(0, parents[2])` at import; `:405` `VERITY_LEAF_LAYOUT` env var chooses the leaf rule of a commitment; `:413` `print` from library code; `:919-936` CLI with `SystemExit`. **high** (the env var changes committed bytes)
- `binding.py:526-528` `raise SystemExit(...)` inside a library function. **medium**
- `reference_engine/triton_sha256.py:70,188` `VERITY_CMT_CACHE` env var / `~/.cache/verity_cmt` for generated kernel source. **low**
- `fa2_prototype/fixture.py:42` `_BKERNEL_P0 = Path("/private/tmp/w-perf/out/gen/r8/fa2-kernel/results/p0")`; `fa2_prototype/kernel_dump.py:2` docstring points at `out/gen/r8/...`. **medium**

**LAYERING**
- `padding_steps.py:40` imports `check.executed_prefix`; `binding.py:384,561` import `check.executed_prefix`; `padding_steps.py:664` imports `check.oracle_compare` inside `padded_population`, which rewrites a `sampled_replay` result in place. The commit layer depends on, and edits the output of, the check layer. **high**
- `binding.py:34-36` re-exports `query.manifest.format` symbols ("re-exported (R19 int-20)"). **low**
- `reference_engine_adapter.py:26-27` imports `acquire.committer_api` and private `native_host._mro_names`, `_StepJob`; `acquire` imports `commit` back: an import cycle with private names. **medium**
- `fa2_prototype/fixtures/` (npz + JSON data) inside the library package; `fixture.py` reads it. **low**

**GOD-MODULE**
- `padding_steps.py` (936): (1) padding identity/tensor naming, (2) padding step layout + leaf digests under two leaf rules, (3) step/run root binding and refold, (4) openings + verify, (5) binding-map entries, (6) pod hook into `NativeHostCommitter.finalize`, (7) offline conversion of a pulled record dir (`padded_map_of_record`: reads `manifest.json.gz`, `commit/binding_map_p0.json.gz`, ...), (8) padded-population and padding-vs-oracle checks that mutate the sampled-replay result in place (`:656-663`), (9) coverage over manifest, (10) CLI. **high**

**DEAD** (confidence; what was searched: absolute/relative imports, importlib strings, `ops/*.sh`, tests, `dead_code_keep.json`)
- `engine_rs/` (whole crate): no Python/shell caller, not in a workspace; its input planner `cprof_c1_plan.py` does not exist. high confidence. **medium**
- `merkle.py:702` `verify_source_linkage`, `:732` `write_openings`; `fasttree.py:113` `chunk_layout`, `:126` `opening_bytes`; `hidden_engine.py:60` `CountingHash`, `:105` `fold_digests`; `semantic_layout.py:139` `rank_fast`, `:154` `semantic_root` (only its own `Layout.root`); `semantic_layout` `Template`/`StaticContext`/`verify_position_opening` are test-only. high confidence. **low**
- `reference_engine/engine.py:432` `leaf = hashing.leaf_hash if False else pos_leaf`: a dead conditional. **low**
- `fa2_prototype/*`: no library importer; kept for `tests/commit/test_{oracle,kernel_dump,negatives,roundtrip,encoding,derived_rule}.py` per `dead_code_keep.json`. Test support living in the library. high confidence. **medium**
- Not dead, but a parallel path: `reference_engine/` + `reference_engine_adapter.py` (CMT-1) are reachable only through `harness/commit_delta.py:456-457`, which offers `cmt_ref_torch | cmt_ref_host | cmt_ref_torch_compiled` as committer names beside the native committer. That is a second production-selectable leaf scheme (`pos_leaf`), not an experiment behind a test. **medium**

**NAMING**
- "hidden" names an FA2-specific stream (`hidden_stream`) *and* the generic step-root binder (`hidden_engine.bind_root`) that every native step uses; "engine" means a Merkle builder (`hidden_engine`, `reference_engine`, `engine_rs`) and elsewhere the vLLM engine. **medium**
- `commit/identity.py` vs core `commitments/identity.py`: same module name, different jobs (id grammar vs canonical JSON). **low**
- `reference_engine/__init__.py:75` `open = open_value` shadows the builtin. **low**
- `commit/__init__.py:1-6` docstring belongs to `acquire/`. **low**

**DOCS**
- Lab-notebook docstrings: `binding.py` (~36 round/lane/review tags: "R14 BIND-01", "TABLE-RULES r14-v1", "Draft 3 §12"), `padding_steps.py` (~33: "revb M-1419", "LIFTING-SPEC v0.7 A9.3", "moe F-moe-r17-06 (int-8)"), `hidden_stream.py` (R9/R13 lanes, tap layout v8). **medium**
- Stale references: `hidden_engine.py:5-7` names `commit_bench.fasttree`/`.semantic`/`.stream`; `fa2_prototype/encoding.py:44-46` names `hier.py`, `packed.py`; `fa2_prototype/__init__.py:5` names `costs.py`; `reference_engine_adapter.py:252` cites `out/gen/r8/fa2-commit/derived_value_rule.md`; `fa2_prototype/oracle.py:38-42` documents a laptop `~/.veritor/mem_guardian.py` limit as design rationale. **medium**

**FALLBACKS**
- `binding.py:309-310` manifest rows accepted from any of `entries`/`rows`/`identities`; same chain in `padding_steps.py:377`. **low**
- `padding_steps.py:405` leaf rule: `VERITY_LEAF_LAYOUT` if `com.gpu_tree` else `host-pos-leaf` (`getattr` default). **medium**
- `semantic_layout.py:179` broad `except Exception` returns False in an opening verifier. **low**

**OTHER-WEIRD**
- `fa2_prototype/oracle.py:79` import-time side effect: `preload_mufu_tables_low_peak()` writes into the private cache `fa2_relation._TABLES`. **medium**
- `padding_steps.py:271,331` and `hidden_stream.py:145`: local `class _L` duck-typed stand-ins for `StreamLayout` to reach a header branch. **low**
- `reference_engine/triton_sha256.py:21-199` generates Triton source at run time and imports it from a cache dir. **low**
- `binding.py:309` `json.loads(open(path).read())` leaves the file handle to GC. **low**

<!-- SECTION-CHECK -->
