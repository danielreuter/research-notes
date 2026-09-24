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
- `padding_steps.py:37` `sys.path.insert(0, parents[2])` at import; `:413` `print` from library code; `:919-936` CLI with `SystemExit`. **medium**
- `padding_steps.py:405` picks the padding leaf rule from `VERITY_LEAF_LAYOUT`, but `harness/commit_delta.py:1087,1258` `--layout` sets `VERITY_LAYOUT`, which is what `acquire/native_collect.py:721` reads for executed leaves (`commit_delta.py:583` records `VERITY_LEAF_LAYOUT` in the config). Two names for one switch that changes committed bytes: under `--layout chunk-leaf-v2` the padding leaves default to the v1 header. **high**
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
- `stream_merkle.py` (179): re-exported by `hidden_engine.py:30,32` but no library code uses `StreamingMerkle`/`stream_root`/`replay_to_open`; only `tests/commit/test_stream_merkle.py`. high confidence. **low**
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

---

## 2. `check/`

**Job vs name.** The name suggests "the verifier's checks over a run". What it holds: (a) three separate verdict pipelines, one per era of the integration: `gates` (observe/fold run directory), `commit_verdict` + `verdict` (native Commit), and `relations` + `poc_*` (the PoC capture-bundle contract); (b) six different value-correspondence ("C2") mechanisms; (c) harnesses that establish properties of the integration rather than checking a run (`noninterference`, `census`, `golden`, `holdout`, `difftest`, `quarantine_lint`, `protected`, `adversarial`); (d) a structural Match (`global_match` + `program_compare` + a monkeypatch speed layer); (e) evaluator libraries and oracles (`twins`, `fa2_attn_oracle`). The Commit-path checks (`sampled_replay`, `oracle_compare`, `value_check`, `compiled_*`) run inside the committing process against the live committer object (`harness/commit_delta.py`, `tp/worker.py`); `gates` and `verdict` run afterwards over JSON. No module consumes only published artifacts plus core's verifier.

| module | lines | job |
|---|---:|---|
| `__init__.py` | 1 | docstring only |
| `adversarial.py` | 699 | mutation harness: named mutations of a toy record must be rejected by the detectors; imports `tests.*` |
| `census.py` | 586 | kernel census: GPU half profiles a vLLM run, laptop half reconciles every kernel against `kernel_allowlist` (G1) |
| `commit_verdict.py` | 704 | first-failure Commit verdict `(ok, reason)` for the sweep harness; helpers reused privately by `verdict.py` |
| `compiled_autotune.py` | 237 | autotune equivalence of an Inductor kernel's candidate launch configs, on committed data |
| `compiled_fx_kernels.py` | 205 | normalise and compare Triton sources Inductor generated for production vs replay compiles |
| `compiled_kernel_check.py` | 574 | C2 for compiled rows: sampled exact replay of Inductor launches (`numerics.compiled_relations`) + id/argmax linkage |
| `compiled_value_check.py` | 186 | C2 for compiled rows: eager Linear re-exec, lm_head vs logits, greedy chain |
| `difftest.py` | 240 | randomized differential test of a registered body vs the production kernel via a one-call `evaluate_call` (G4) |
| `executed_prefix.py` | 613 | executed prefix of record per request (served vs executed length, LAG rule) linked to the Match account |
| `fa2_attn_oracle.py` | 229 | standalone numpy FA2 attention reference for the P0 tap; loaded by file path from one acquire test |
| `fold_compare.py` | 923 | four comparisons of a folded observation log (tokens, boundary hashes, subcircuits via `evaluate_call`, structure) + `SnapshotStore`/`WeightSource` |
| `gates.py` | 1397 | frozen G1..G7 (+G8, R1) over a run directory -> ACCEPTED / REJECTED / INCOMPLETE |
| `global_match.py` | 2206 | global Match of a batched execution vs the rooted workload Program |
| `global_match_fast.py` | 729 | `MATCH_IMPL=fast`: memoised/forked replacements monkeypatched over `program_compare`, `batch_decomp` and core `ir.codec`/`ir.refs` |
| `golden.py` | 129 | golden corpus: previously accepted logs must still resolve identically (G6) |
| `holdout.py` | 128 | holdout workload generator and assembler (G7) |
| `kernel_allowlist.py` | 28 | the census allowlist tuple |
| `kernel_identity.py` | 384 | generated-kernel identity: kernel-set digests over Inductor/Triton caches, PTX identity |
| `noninterference.py` | 803 | non-interference: three fresh engine processes (observer off/on/hooks) compare tokens and boundary hashes |
| `operand_provenance.py` | 444 | exhaustive operand provenance (G5): every operand read matched by an independent last-writer map |
| `oracle_compare.py` | 953 | live C2: committed bytes vs the Match capture's snapshot bytes; also `committed_reader`, which other checks use |
| `poc_description.py` | 643 | `description.json` schema: the node list the PoC checker runs from |
| `poc_required_interface.py` | 254 | `required.json` schema: the frozen required-interface set |
| `poc_rows.py` | 681 | PoC Table 1-4 rows and the PASS derivation rule |
| `poc_verify_bindings.py` | 573 | helpers for a `check/poc_verify` / `verify.py` that does not exist; one function has a caller |
| `program_compare.py` | 906 | structural comparator of a derived Program vs the record's, over its own `Prog` representation; CLI |
| `protected.py` | 214 | frozen protected-path list + diff check of a lane candidate (git and python subprocesses) |
| `quarantine_lint.py` | 128 | AST purity + identity lint of `program/registry/quarantine/` |
| `relations.py` | 1344 | PoC relation registry (`REGISTRY`), op-type checkers, challenge record, sample draw, `check` runner, `CheckReport` |
| `replay.py` | 1178 | the derived Program as its own oracle: tiers a/b/c/chain via `evaluate_call` or twins |
| `sampled_replay.py` | 3149 | C2 of record: stratified sampled exact VU replay from committed bytes (numpy), population accounting, linkage, fork pool |
| `stoch_recompute.py` | 748 | recompute `GumbelTopPTokenSelect_v1` on captured logits vs the served token |
| `twins.py` | 1054 | vectorized twins (numpy + C++ via ctypes, built with g++ at run time), bit-exact vs `evaluate_call`; self-check CLI |
| `value_check.py` | 196 | eager C2: hook-time tap clones + re-execution of the same torch kernel vs committed bytes |
| `verdict.py` | 1409 | typed verdict records (`vllm-verdict/v1`) re-deriving each `commit_verdict` rule; CLI |
| `golden/corpus.json` | data | golden corpus manifest inside the package |

### 2.1 Findings in `check/`

**CORE-DUP**
- No module in `check/` (or `commit/`) imports `verity.verification` or `verity.commitments`. The verdict, obligation, sampling-policy and opening machinery below is all local. Core offers `verification/codes.py:16,44` (`VerificationCode`, `Reject`), `verification/plan.py:68` (`VerificationPlan`), `verification/statement.py:76,249` (`KindProgram`, `Obligation`), `commitments/multiproof.py`. **high**
- `sampled_replay.py:294-690` (`ProgramIndex`, `CommittedStore`, resolver) + `:743-920` (`evaluate`) is a local obligation model: VU identity, input resolution, relation dispatch, compare. Core's `Obligation`/`KindProgram` is the same concept as data (Map 1). **high**
- `program_compare.py:84-440` `Prog`: a second in-memory Program representation (instance list with run or progression operands) built from `verity.ir.codec.decode_program`, including private `verity.ir.codec._spec_id` (`:112`). **medium**
- `relations.py:508-560` `Challenge`/`make_challenge` and `:735` `_open_verified`: local challenge and opening verification over `commit.merkle`, beside core's `commitments` openings/multiproofs. **medium**

**INTERNAL-DUP**
- Six value-correspondence mechanisms: `sampled_replay`, `oracle_compare`, `value_check`, `compiled_value_check`, `compiled_kernel_check`, `stoch_recompute` (plus `replay` and `fold_compare.compare_subcircuits` on the observe path). Each has its own reader, sampler and result dict. **high**
- Two vectorized twin libraries for the same nine families: `twins.py` (GemmTwin ... AttentionTwin, numpy + C++) and `program/registry/derived_rows.py` (944 lines, numpy), used by `replay` and `sampled_replay` respectively; `twins.py` never imports `derived_rows`. `sampled_replay.evaluate` then composes Embedding/BiasAdd/MoeExpertGemm/MoeSum inline (`:835-919`), a third copy of those. **high**
- `verdict.py` re-implements `commit_verdict.commit_verdict` rule by rule (`verdict.py:346-1050`, ~20 `rule_*` functions) and reaches into seven private helpers of it (`CV._partial_replay_named_gap`, `CV._complete_replay_population_gap`, `CV._replay_seed_of_record`, ...). Its docstring (`:1-30`) says the Commit decision is now recorded four times. **high**
- Greedy linkage (argmax of logits == sampled id; embed ids of step s+1 == sampled ids of step s) in `compiled_value_check.py:158`, `compiled_kernel_check.py:98,461`, `sampled_replay.py:2846-3100`. **medium**
- Sample/seed derivations: `sampled_replay.py:2522` (sha256(challenge|root)[:8] -> `random.Random` at `:2051`), `compiled_kernel_check.py:206` (`random.Random(seed or 0)`), `relations.py:1143-1158` (`np.random.default_rng(seed=0)`), `replay.py:533,948` (`random.Random(seed)`), `stoch_recompute.py:610` (`random.Random(rows*7919 + len(pending))`), plus `commit/binding.py:676`. Core has none (see §4.4). **high**
- "Wrap one spec in a program and evaluate it": `difftest.py:140-170` `evaluate_spec`, `program/registry/crosscheck.py:33` `_standalone` (used by `twins.py:769`), `commit/fa2_prototype/oracle.py:90-104`, and three test copies. **medium**
- Dtype-name tables: `sampled_replay.py:66-70`, `fold_compare.py:72`, `compiled_value_check.py:20`. **low**
- Committed-bytes readers: `oracle_compare.committed_reader` (`:914`) vs `sampled_replay.CommittedStore` (`:606`) vs `relations._open_verified` (`:735`). **medium**

**VERSION-RESIDUE**
- `poc_description`, `poc_required_interface`, `poc_rows`, `poc_verify_bindings`: `poc_` module prefix on a live contract (the schemas are imported by `observe/capture_v1.py` and `harness/synthetic.py`). **medium**
- `replay.py:527,845,940,1003` `tier_a`/`tier_b`/`tier_chain`/`tier_c`, `--tier a|b|c|chain` (`:1101`). **medium**
- `gates.py:108-120` G1..G8/R1 and the constants block `:94-114` are the public API of the module (`__all__` at `:1390`). Gate ids are residue in code names; `gates.GATE_NAMES` already gives real names. **medium**
- `global_match_fast.py` (`_fast`) exists as a module-wide override of `global_match` + `program_compare`, selected by `MATCH_IMPL` with default `"fast"` (`global_match.py:2063-2065`), so the "slow" path is the reference kept for audit. **medium**
- `commit_verdict.py:1` "X-03 (R12)", `compiled_*` "R15", `executed_prefix.py:1` "R17-1 / F-moe-r17-03": round ids as the first line of the module doc. **low**
- `fold_compare.py:891` `case == "B0"` default-record branch; `holdout.py:3` `--case B0`. **low**
- Legit (hashed data, not residue): `Gemm_v1`, `Attention_v3`, `verity-sweep/sampled-replay/v1`, `vllm-verdict/v1`, `verity-gen/gates/v1`.

**HARDCODING**
- `value_check.py:24,29` `REEXEC_CLASSES` and member tables keyed by vLLM module class names (`GemmaRMSNorm`, `SiluAndMul`, ...). **medium**
- `compiled_kernel_check.py:107,179` model-family branches (Llama vs Qwen eps, Qwen2.5 QKV bias argument order). **medium**
- `protected.py:40,103` default profile names `vllm_d9105ea80_sm89_eager{,_qwen15}` (a vLLM commit, an sm_89 GPU, a model). **medium**
- `fold_compare.py:60` `HF_GLOB` = `models--HuggingFaceTB--SmolLM2-135M` snapshot path; `:58` default record. **high** (see SCRIPT/ENV/PATH)
- `commit_verdict.py:27-29` `REQUIRED_CLASSES_DEFAULT` includes `fa2_hidden_m1_stream`; `HIDDEN_CLASS_BY_FA` keyed by FlashAttention major version. **medium**
- `sampled_replay.py:73-158` `EVALUATORS`: per-family provenance prose including measurement claims ("pinned word for word on the H100 at every Qwen2.5-1.5B shape"), emitted into every report. **medium**
- `kernel_allowlist.py:14-28` allowlist qualified by "residue 0 on SmolLM2-135M and Qwen2.5-1.5B". **low**
- `poc_description.py:8-9` example with `H: 576, V: 49152` (SmolLM2). **low**

**SCRIPT/ENV/PATH**
- `__main__` + argparse in 19 of 36 modules: `adversarial, census, compiled_fx_kernels, difftest, fa2_attn_oracle, fold_compare, global_match, golden, holdout, kernel_identity, noninterference, operand_provenance, program_compare, protected, quarantine_lint, replay, stoch_recompute, twins, verdict`. Only seven are run by `ops/*.sh` with `-m` (`global_match, holdout, program_compare, protected, quarantine_lint, stoch_recompute, verdict`); `ops/row_pod.sh:558` reaches `sampled_replay.form_b_families` through an inline `python -c`. **medium**
- `fold_compare.py:58` `DEFAULT_RECORD = Path("/Users/danielreuter/projects/veritor/out/scale/e8/live/...")` (a laptop path in library code). **high**
- `fa2_attn_oracle.py:9-10` run instructions point at `out/gen/r8/fa2-sem/verity_attn_ref.py` and `/tmp/*.json`. **low**
- Environment variables that change behaviour: `global_match.py:2080` `MATCH_IMPL`, `global_match_fast.py:56,510,514` `MATCH_IMPL`/`MATCH_COMPACT`/`MATCH_WORKERS` (switches the operand representation of `program_compare.Prog`), `census.py:200-203` `VERITY_CENSUS_GPU_UTIL`, `stoch_recompute.py:721,724` `STOCH_EVALUATOR`/`STOCH_REFERENCE_ROWS`, `sampled_replay.py:2245-2251` `VERITY_REPLAY_DUMP_*`, `:2477` `VERITY_REPLAY_FORK_GC_FREEZE`, `kernel_identity.py:58,70` cache dirs, `twins.py:124,142` `CXX`, `fold_compare.py:69` `HF_HOME`. **medium**
- `Path(__file__).parents[2]` = `integrations/vllm` as `REPO` in `fold_compare:57`, `protected:26`, `golden:26`, `twins:50`, `adversarial:51`, `quarantine_lint:27`. **low**
- `twins.py:51-52` `sys.path.insert(REPO / "vllm-poc")`: the directory does not exist. **medium**
- `twins.py:124-152` compiles C++ with g++ (`subprocess.run`) at first use. **low**
- CWD-relative defaults: `noninterference.py:770,778`, `census.py:542,550,552` (`manifests/checkpoints.json`, `data/logs/m1.jsonl.gz`, `out/capture/reports/census_m1`). **medium**

**LAYERING**
- `adversarial.py:448-462` imports `tests.observe.test_fold_synthetic` and `tests.check.test_compare_synthetic` (private `_evaluate_program`, `_write_snapshots`), calls `tfs.install_stub_memory()` and overwrites the test modules' `SAMPLED`/`PROMPT` lists in place. **high**
- `relations.REGISTRY` is filled by `program/numerics/relations.py:494-509`, `rms_relation.py:166-181`, `fa2_relation.py:247-262` (`from verity_vllm.check import relations as R; R.register(...)`): program depends on check and check's registry depends on program being imported. **high**
- `oracle_compare.py:914-940` `committed_reader` reads the live committer's private `_layouts`, `_gpu_blocks` through `getattr`; `value_check.py:22` imports `acquire.native_host._mro_names`. **high**
- `global_match.py:2132` imports `harness.gc_tuning` (check -> harness). **low**
- `replay.py:71,75`, `fold_compare.py:46`, `twins.py:769,911,1038`, `difftest.py:148`, `program_compare.py:112`: private names imported across modules (`_field_intervals`, `_attach_specs`, `_component_ranges`, `_standalone`, `_replayer`, core `_spec_id`). **medium**
- Library reads top-level data dirs: `fold_compare.py:59` (`fixtures/B0-divergence-.../cos_sin_cache.npy`), `adversarial.py:523-525` (`data/logs/m1*`), `golden/corpus.json` -> `data/logs/`, `protected.py:58` (`manifests/checkpoints.json`). **medium**

**GOD-MODULE** (over ~800 lines; distinct jobs)
- `sampled_replay.py` (3149): (1) spec/static parsing (`prim_static`, `parse_struct`); (2) Program index + op-path/invocation resolution (`ProgramIndex`, `alias_table`); (3) committed-bytes store (`CommittedStore`); (4) the family evaluator ladder (`evaluate`, `padded_moe_block`, `moe_router_topk`, sampler replays); (5) MoE plane aliasing checks; (6) population accounting and why-classes (`population`, `query_population` 374 lines, `split_not_executed`, `executed_prefix_of_record`); (7) stratified sampling (`sample`, `challenge_seed`, `_catch_probability`); (8) row evaluation + debug dumps (`_evaluate_row`, `_dump_row_words`); (9) a fork-based process pool with prewarm and gc freeze (`_parallel_replay`, `_fork_worker`); (10) boundary and prescribed-input linkage; (11) engine facts and weights provider. **high**
- `global_match.py` (2206): workload/record loading and relocation, a mock global program (`mock_global_program`, `:167`), sampler geometry check, EOS/lag rows, engine facts, permutation matching, the 1,234-line `_check` (`:828-2062`), impl dispatch and banner, CLI. **high**
- `verdict.py` (1409): typed records, ~20 rule re-implementations, run aggregation and grouping, correspondence-of-build reading, record rebuild from a row directory, old->new name mapping table, CLI. **medium**
- `gates.py` (1397): frozen constants, `RunArtifacts` loader (165 lines), eight gate functions, diagnostics, the card, CLI-less API. **medium**
- `relations.py` (1344): error types, lazy inputs, the registry, ten op-type checkers, challenge, result types, `check` runner, linkage, domain checks, sample coverage, `draw_sample`, adjacent-pair checks. **high**
- `replay.py` (1178): `Replayer` (417-line class), four tiers, VU population, chain planning, evaluator selection, summary, CLI. **medium**
- `twins.py` (1054): C++ build/load, nine twin classes, SiLU table, twin registry, self-check against `evaluate_call`, log-driven family check, CLI. **medium**
- `oracle_compare.py` (953): `MatchOracle` (404-line class), producer facts, oracle compare, same-name invocation helpers, the committed reader. **medium**
- `fold_compare.py` (923): HF safetensors loading, snapshot store, weight source with per-family field maps (MoE, qk-norm, Gemma-2 norms, NeoX permute), four comparisons, CLI. **medium**
- `program_compare.py` (906): the registry importer, `Prog`, loaders for derived/oracle Programs, divergence report, step compare, canonical hashing, padding audit, CLI. **medium**
- `noninterference.py` (803): observer and hooks variants, per-family boundary rules (unfused norm, parallel residual), hashing, comparison and markdown, subprocess orchestration, CLI. **medium**

**DEAD** (searched: absolute and relative imports, `importlib`, `python -m` in `verity_vllm/ops/*.sh`, tests, `tests/dead_code_keep.json`)
- `poc_verify_bindings.py`: its stated consumer `check/poc_verify` + `verify.py` does not exist (`:1-4`); 19 of 21 functions have no caller; `dist_identity` is used by `observe/engine_profile.py:255`. high confidence. **medium**
- `poc_rows.py` (681) and `compiled_fx_kernels.py` (205): only importer is `poc_verify_bindings` (`:42`, `:72`), from functions nobody calls; `compiled_fx_kernels` has a CLI no script runs. high confidence. **medium**
- `adversarial.py`: no library or script caller; used by 3 tests. Test support in the library. high confidence. **low**
- `fa2_attn_oracle.py`: no importer; `tests/acquire/test_fa2_tap_geometry.py` loads it by file name (`dead_code_keep.json:29`). high confidence. **low**
- `global_match.py:167` `mock_global_program`: library-resident test double. medium confidence. **low**
- Stale references: `gates.py:3,9-31` and `kernel_allowlist.py:6` name `out/capture/decisions.md` (the only way to change the "FROZEN" gates) and `bench/run_config.py`, `bench.resolve_log`, `bench/verify_lane.sh`; none exists (`bench/` moved to `harness/` and `ops/`). **medium**

**NAMING**
- "oracle": the Match capture (`oracle_compare`), a numpy reference (`fa2_attn_oracle`), `evaluate_call` (`fa2_prototype/oracle`), the record Program (`program_compare.load_oracle`). **medium**
- "verdict": `commit_verdict` returns `(bool, str)`, `verdict.Verdict` is a record, `gates.verdict` is a string, `poc_rows.verdict` a `Verdict` named tuple. **medium**
- `EVALUATORS` means a provenance-prose dict (`sampled_replay.py:73`), a name -> job-function dict (`stoch_recompute.py:117`) and a CLI choice tuple (`replay.py:79`). **low**
- "twin" (`twins.py`) vs "derived rows" (`derived_rows.py`) for the same thing. **low**
- `replay.py` vs `sampled_replay.py` vs `stoch_recompute.py` vs `compiled_kernel_check.py`: all four are sampled exact replays. **low**

**DOCS**
- Lab-notebook docstrings dominate: `commit_verdict.py`, `verdict.py`, `sampled_replay.py`, `executed_prefix.py`, `oracle_compare.py`, `stoch_recompute.py` open with ruling/board ids (e.g. `executed_prefix.py:1` "R17-1 / F-moe-r17-03 (moe M-0283)"; `oracle_compare.py:1` "COORD R15 ruling M-0111 (2), lane manbind"). `executed_prefix.py:14` documents "the first record" with a UTC timestamp and lane hash. **medium**
- `adversarial.py:1` "lane ov-adversarial (Agent 10, swarm 2026-09-17)". **low**
- `poc_verify_bindings.py:1-4` points at `docs/vllm-poc/audit-compiled-pass.md` and "GUIDANCE-2026-09-07 §6". **low**

**FALLBACKS**
- `program_compare.py:63-81` `_registry()`: three `except Exception` blocks that print and continue, so a failed registry import makes some programs silently undecodable. **medium**
- `kernel_identity.py:65,124,158,203,209,240,256,324`: eight `except Exception` in an identity check. **medium**
- `sampled_replay.py` nine broad excepts; `evaluate` returns aliases (`{"0": out, "out": out}`, `{"0": out, "1": out, "out": out}` at `:779,789`) so the caller's member name always hits. **medium**
- `compiled_kernel_check.py:206` sample seed defaults to 0 when the caller passes none. **medium**
- `commit_verdict.py:107,152,353-354` decisions keyed on prose strings produced by other modules ("== sampled_replay.WHY_CLASSES_BY_NAME", "== the text sampled_replay.population() counts", "== sampled_replay.challenge_seed's source text"); changing a message changes a verdict. **high**
- `harness/commit_delta.py:2531` (outside slice) probes `inspect.signature(SR.sampled_replay)` to discover whether `executed_prefix=` is accepted. **low**

**OTHER-WEIRD**
- `global_match_fast.py:482-520` `install()` monkeypatches core `verity.ir.codec._spec_id` and `verity.ir.refs.runs`, plus `program_compare.Prog.canon`, `compare_steps`, `_canonical_hash`, `_canon_step_relative`, `batch_decomp.dag_hashes`, `live_cone`, `Projection`, `X09_LEGS`, and flips `program_compare.COMPACT_ARGS`, process-wide, when `MATCH_IMPL=fast` (the default). **high**
- `sampled_replay.py:2375-2376,2476,2494` module globals `_FORK_FN`, `_FORK_VUS`, `_FORK_STATS` for a fork pool; `:2235` `_DUMP_N = [0]` counter. **medium**
- `relations.py:131-134` + decorators at `:227-324`: module-level `REGISTRY` filled at import. **medium**
- `twins.py:116,136,463` lazily-built globals (`_TC_LIB`, `_SILU_TABLE`); `compiled_autotune.py:63` `global _AUT`. **low**
- `protected.py:128` runs a code string with `python -c` in a subprocess against the head checkout; `noninterference.py:729-752` orchestrates engine subprocesses from library code. **medium**
- `global_match.py:828` a 1,234-line function. **high**

<!-- SECTION-MAPS -->
