---
id: 20261004T2125Z-draft-move-map-backends-integrations-tools
campaign: verity
lane: verity-root
kind: draft
status: open
repo: danielreuter/verity
origin: worker of verity-top's repository-layout agent (bc-d6f8b221); for owners (proofs, circuits, infra, ci, lean) to correct
---

# Move map: `backends/`, `integrations/vllm/`, `tools/`, `infra/` and the root

This draft maps every package and subpackage in scope to its destination in the layout of
note:20261004T2058Z-draft-repo-organization-principles ("the plan"). It was made read-only against
`3504da27e9b66416dee9453ed7f0912bb476eecf`, the layout agent's branch `cursor/migration-rulings-c3b2`. That commit is
`main`'s merge `75976b4f2` ("Merge 26 PRs") plus one friction-note commit, so the code is `75976b4f2`'s. The section
"Changes at the next tip" lists what `be2452acd` (the next tip, merged into #1127 while this draft was written) changes in
scope. The map was made from the tree, the imports (an AST walk of every
module, distinguishing module-level from function-level imports) and each module's docstring. No repository code was
executed, only read-only scans, and nothing under `/workspace` was changed. Every row is a proposal for its owner to
correct.

The scope is `backends/` (all), `integrations/vllm/`, `tools/`, `infra/`, `.agents/` and the root files. There is no
top-level `pods/`: the pod and node files AGENTS.md calls `pods/nebius/…` are `tools/research/src/research/pods/`, and they are
mapped under `tools/research`.

## How to read the tables

Each table has the columns *current path*, *destination*, *principle*, *confidence* and *question for the owner*. The
principle column cites the plan's numbered principles (P1 to P10), its conventions ("Conv: tests", "Conv: packaging",
"Conv: PROTOCOL.md", "Conv: node config"), its layout section ("Layout") and its plan steps (S3 is the Lean move, S4 the
frozen backends, S5 the Python moves). A destination written as `A + B` means the path must be split first, and the row
says along which line. "Stays" means the path keeps its directory. File counts are tracked files (`git ls-files`).

Destination names used below:

- `verity/protocols/verification/flock/`: C-Flock's executable Lean verifier and its reference prover (P1, Layout).
- `verity/kernels/<entry>/`: a kernel registry entry (P5), for example `flock-cuda` or `pearl-c-sm120`.
- `verity/primitives/{circuits,commitments}/`: core's circuit and commitment primitives.
- `catalog/definitions/`, `catalog/devices/`, `catalog/vectors/`: Definitions with their builders, device numbers and
  tables, and generated vectors (P3).
- `security_proofs/flock/`: C-Flock's lemmas and proofs (S3).
- `experimental/<area>/`, `archive/<name>/`, `benchmarks/<area>/`, `tools/<tool>/` and `infra/nebius/`.

## Counts by destination

These are the rows of the tables in sections 1 to 5, counted by the main destination each row names. A split row counts
once, under its main destination. Section 4b's per-module registry table is counted separately, after this table. There
are 117 rows, plus two pointer rows (`program/registry/` and `program/kernels/`).

| Destination | Rows | Main contents |
|---|---|---|
| `verity/` (protocols, primitives, kernels) | 28 | C-Flock's executable verifier, its Python and Rust reference prover, and its CUDA prover (`flock-cuda`); vLLM's kernel registry, C++ twins and row kernels; PoUW's `ncp-v2` and Pearl-C device code; consolidated commitments; the committer's GPU hash kernels |
| `catalog/` | 8 | numerical's subcircuit templates; `pins.json` and the data half of circuit-check's bindings; the Definition-to-Boolean link table; device models and evidence (`libdevice_sampling`, `kernel_zoo`); `topp_word`'s lowering; registry tests |
| `security_proofs/` | 5 | `level3/`, `soundness/` (with the `Audit.*` law), `FlockProofs/`, frozen copies of superseded-form parsers |
| `experimental/` | 5 | C-Flock's superseded Rust statements, frame-v3 Python (`instances`, `backend`), `arch_proto/`, `unit_fp4_check`; PoUW's FP4 pricing experiments |
| `archive/` | 10 | A-GKR, B-Ligero (`direct`, `ligero-verify`, `ligerito-verify`), D-SP1, VOLE, `redteam/`, `shared/anchor_a100`, numerical's frozen subpackages, C-Flock's oldest pod scripts, `backends/README.md` and `AGENTS.md` |
| `benchmarks/` | 8 | C-Flock's bench drivers, current pod scripts, `tool.py` and `session_verify.rs`; numerical's input sets and table renderer; `shared/hash_gpu` |
| `integrations/vllm/` (stays) | 20 | frontend, engine, acquire, observe, pipeline, query, correspondence, check and Match, commit adapters, protocol adapters, data; plus C-Flock's `boolean_export` |
| `tools/` | 20 | 16 that stay (research, check, lean, circuit_check, cluster, agent-guard, probes); 4 coming in (lean-agreement scripts, `hawkeye_close`, vLLM's capture probes) |
| `infra/` | 5 | systemd units and timers, the cpuset, `deploy.toml`, env and TSV data, monitoring and sky YAML, `store.pod.toml`, cluster descriptions and unit |
| deleted (P8, superseded tooling) | 2 | C-Flock's four 7-line shims; vLLM's `registry/quarantine/` with its deleted versions |
| retired documents | 2 | `verifier/PROTOCOL.md` (except §16.15), `live/PROTOCOL.md` |
| unchanged (root, `.agents/`, `infra/`) | 4 | `pyproject.toml` and `uv.lock`, `AGENTS.md` and `README.md`, `.agents/`, `infra/nebius/verity-console.*` |

Section 4b's 55 registry modules split as follows:

- 44 go to `catalog/` in whole or in part: 34 pure Definition modules, the Definition halves of the 5 Definition-plus-twin
  and the 4 Definition-plus-vocabulary modules, and the conformance record.
- 7 twins go to `verity/kernels/` or stay: the 5 split twins and 2 twin-only modules.
- 6 vocabulary pieces stay in the integration: 4 split from Definition modules and 2 vocabulary-only modules.
- 5 harnesses go to the integration's tests.
- 2 loaders split.

## Changes at the next tip (`be2452acd`)

These are the in-scope additions and renames between `3504da27e` and `be2452acd`. Modified files keep the rows they
already have.

| Path at `be2452acd` | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `program/registry/mla.py` (new; DeepSeek-V2 MLA decode kernels on bits; imports only `boolean_attention`) | `catalog/` (pure Definition), or `experimental/` until the plan's bridge to the row lane's word twins lands | P3, S5 (the MLA Booleans are bridged by vectors) | medium | circuits |
| `program/registry/mla_capture.py` (new; captures of vLLM's Triton MLA decode; `config` at module level, torch lazily) | stays in `integrations/vllm/` (capture) | P7 | high | none |
| `program/registry/mla_check.py` (new; word-for-word checks of the MLA captures against numpy kernel models; imports `program.kernels` and `libdevice_sampling` at module level) | stays in `integrations/vllm/` (check); its numpy models go to `verity/kernels/` under section 6, item 11's ruling | P7, P5 | medium | circuits |
| `program/registry/rope_gptj_difftest.py` (new; difftest adapter for `RoPEGptJ_v2` against vLLM's CUDA rotary embedding) | `integrations/vllm/` tests or `properties/` (harness) | P7 | high | none |
| `tools/check/{lean-deps.json, lean_audit.py, lean_changed.py}` → `tools/lean/` (renamed, #1085) | stays in `tools/lean/` (the validator, on the assurance list) | P1 | high | none; section 5b's `tools/check` rows predate this rename |
| `tools/research/src/research/pods/nebius/vy-keeper-n1.service`, `vy-keeper-n2.service`, `vy-keeper.timer`, `sky/store_evict_src.conf` (new) | `infra/nebius/` | Conv: node config | medium | infra |
| `tools/research/src/research/{doctor,jobuser,keeper}.py`, `pods/nebius/keeper.py`, `tools/cluster/src/cluster/policy.py` (new code) | stays | Layout | high | none |

At `be2452acd` the registry has 59 modules: 35 pure Definitions (with `mla`), the same 5 Definition-plus-twin and 6
vocabulary pieces, 2 twin-only modules plus `mla_check`, 7 harnesses (with `mla_capture` and `rope_gptj_difftest`), the
record and 2 loaders. Of the 59, 53 import nothing outside the registry, `verity` and numpy at module level. The six that
do are `conformance`, `rmsnorm_fused_sweep` and `mla_capture` (all through `config`), `sampling_rows` and `mla_check`
(through `program.kernels`), and `pouw_rows` (through `verity_pouw.circuit.ncp2`).

## 1. C-Flock (`backends/flock/`, 893 files; owner: proofs)

C-Flock splits five ways:

- Its executable Lean verifier and its reference prover (the Python statement staging and the Rust CPU path) go to
  `verity/`.
- Its CUDA prover becomes one kernel registry entry.
- Its Lean proofs go to `security_proofs/flock/`.
- Its benchmarks go to `benchmarks/flock/`.
- Its superseded statements go to `experimental/flock/` while they build and teach, then to `archive/`.

The prover cannot move until five lazy-import blockers are cut (section 6, items 1 to 4): its reads of the vLLM registry,
vLLM's kernel relations, vLLM's pipeline, `verity_numerical.bench`, and B-Ligero.

### 1a. Lean (`backends/flock/verifier/lean/`, 667 files)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `verifier/lean/Flock/` (45), `Main.lean` (`flock-verify`), `lakefile.toml`, `lean-toolchain`, `lake-manifest.json` | `verity/protocols/verification/flock/lean/` (the executable verifier, no dependencies) | P1, P2 (the only Lean in `verity/` besides specs), S3 | high | none |
| Superseded forms' parsers inside `Flock/` (reachable only to refuse) | frozen copies into `security_proofs/flock/` beside their proofs; the refusal list stays in the verifier | P9 (last bullet), S3 | medium | proofs: which `Flock/` modules are superseded-form parsers today, and does each form's refusal stay in the verifier while its parser copy leaves? |
| `verifier/lean/FlockProofs/` (6; core-only lemmas about the executable) | `security_proofs/flock/` | P2 (every lemma in `security_proofs/`), S1's lock reduction (the verifier's 25 entries leave) | medium | lean and proofs: today it is a no-dependency library inside the verifier's package. Should it join the single `security_proofs` package (which requires Mathlib), or stay a separate no-dependency library? |
| `FlockRows` (`flock-rows` exe) | stays with the verifier package, or `tools/` | P1 | medium | proofs: is `flock-rows` part of what a guarantee depends on, or a developer tool? |
| `verifier/lean/lean-audit.json` | split: the verifier's and spec's lock stays with them, and `security_proofs/flock` validates against it | P2 (the lock), S3.1 | high | none |
| `verifier/lean/level3/` (24; `FlockLevel3`, requires Mathlib and the verifier by path `..`) | `security_proofs/flock/level3/`, whole | S3.1 | high | none; its `require` path changes |
| `verifier/lean/soundness/` (589; `FlockSoundness`, requires ArkLib and level3 by path; `ASSUMPTIONS.md`, `DESIGN.md`, `assumptions/*.md`) | `security_proofs/flock/soundness/`, whole; the spec is extracted later as C-Flock's spec package | S3.1, P2; P8 (a `DESIGN.md` holding reasoning stays) | high for the move, low for the spec's timing | proofs: which subset is the trusted spec? Pins read 285 of its 561 modules, and the spec must come out before S3.3 touches the math. |
| `soundness/…/Audit.*` (27; the sampled-proofs audit law) | moves with soundness under current names; its own area is an S3.3 job | S3.1 | high | compute-accounting and proofs: none for the move |
| `tests/lean/RandomnessVectors.lean`, `tests/fixtures/randomness_lean.json` | stays beside the verifier's tests | Conv: tests | high | none |

### 1b. Python (`backends/flock/python/verity_flock/`, 42 files)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `circuit.py` (990, the M0 `verity/flock-circuit` staging), `typed_statement.py`, `type_trace.py`, `circuit_types.py`, `layouts.py`, `derive.py`, `tables.py`, `sha512_circuit.py`, `lowering.py` | `verity/protocols/verification/flock/` (reference prover) + `benchmarks/flock/` (`circuit.main`, the input-set CLI) | P1, P6 | medium | proofs: is this statement staging, together with the Rust `flock-circuit` CPU path, "the reference prover"? `circuit.lowering_for_set` reads numerical's `lowerings` registry and `main` reads its `InputSet`. Can the prover take a `Lowering` object instead? |
| `ir_lower.py` (1091; imported at module level by `circuit.py` and `typed_statement.py`) | `verity/…/flock/` after a split: `silu_table` (reads `registry.prims`) and `write_tables` (reads `kernels.fa2_relation` and `rms_relation`'s MUFU tables) take their tables as parameters | P6; P3 (device tables are catalog entries) | medium | proofs and circuits: should the MUFU and SiLU tables become catalog device entries that the prover's caller passes in? |
| `tail.py`, `tail_pieces.py` | `verity/…/flock/` after the same split (`_fold_constant_mufu` reads `prims`, `_gelu_table` reads `dense`) | P6, P3 | medium | as for `ir_lower.py` |
| `class_statement.py` (1442) | `verity/…/flock/` after lifting `_encoded` and `definition_digest` out of `verity_vllm.pipeline.program_graph` into `verity.ir` (both are pure `verity.ir.codec` helpers) | P6 | medium | circuits: can those two helpers move into `verity.ir`? `definition_digest` is SHA-256 of canonical JSON, a second digest beside the program's SHA-512. |
| `partition_units.py` | `verity/…/flock/`, with the B1 Program passed by its caller instead of `_program` importing `registry.b1` | P6 | medium | proofs: is `_program` only a test and bench fixture? |
| `topp_word.py` (module-level imports of `registry.topp_keep_builder` and `topp_word_gates`) | `catalog/definitions/` beside `topp_words`, as that Definition's C-Flock lowering, or `verity/` with its constants passed in | P6 | low | proofs and circuits: where does a lowering specific to one Definition live, with the prover (`verity/`) or with the Definition (`catalog/`)? |
| `ir_sampling.py` (526; reads `registry.sampling`, `prims`, `sampling_rows`) | `verity/…/flock/` if the sampler statement is current, else `experimental/flock/`; it splits either way, like `topp_word.py` | P6, P9 | low | proofs: is the sampling-row statement current? Its only in-tree caller is the gumbel template's `frame_lowering` (frame-v3). |
| `ir_frame.py` (349) | split: `BINDING_TAG` and `OWNER`, which `circuit.py` reads, go to `verity/…/flock/`; the frame-v3 statement goes to `experimental/flock/` | P9 | medium | proofs: confirm frame-v3 is superseded for new statements |
| `templates/` (8; per-template lowerings, located by `verity_numerical.bench.lowerings.DIRECTORIES`, a hard-coded path) | `gemm_coordinate.py` (the only one with `circuit_lowering`, the M0 path) goes with the prover or into `catalog/` beside its template; the six `frame_lowering`-only modules go to `experimental/flock/` | P9, P3 | low | proofs and circuits: is a template's C-Flock lowering prover code or catalog data keyed by template? `DIRECTORIES` must follow the move. |
| `boolean_export.py` (1577; reads the registry, `query.word`, `program_graph` and numerical's bench) | `integrations/vllm/` (it exports the served Program's Boolean circuit), or `tools/` | P7, P6 | medium | circuits: integration or tool? |
| `fp.py`, `gf2.py`, `unit.py`, `unit_fp4.py` (7-line re-exports of `verity.ml.boolean`) | deleted; callers import `verity.ml.boolean` | P8 (superseded tooling goes) | high | none |
| `unit_fp4_check.py` | `experimental/flock/`, or with Pearl-C4's FP4 work in `experimental/pouw/` | P9 | medium | proofs |
| `bench.py` (imports `ligero`), `ir_bench.py`, `circuit_bench.py`, `register.py`, `key_class_sets.py`, `lean_rows.py`, `class_sweep.py`, `negatives.py` | `benchmarks/flock/`; `bench.py`'s flock-pure path goes to `archive/` with B-Ligero | Layout, P9 | medium | proofs: is any of these a test helper that belongs in `tests/`? |
| `instances.py` (imports `ligero` auth, relations, `fp4.chain`), `backend.py` (`FLOCK_FRAME_V3_BLAKE3`, `FLOCK_BLOCK`, `FLOCK_VLLM_V1`) | `experimental/flock/` while it builds, or `archive/flock/` | P8, S4 | medium | proofs: `templates/gemm_coordinate.py` imports `instances` (`write_set`) lazily, so it moves after that template's split. Keep or archive? |

### 1c. Rust (`backends/flock/live/`, 33 files; the `flock-live` crate dropped into upstream Flock `b684b12`)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `circuit.rs`, `typed.rs`, `lookup.rs`, `ir_block.rs` (shared: `circuit`, `typed` and `lookup` use it), `ir_tail.rs`, `tables.rs`, `glue.rs`, `sha512_native.rs`, `zk_hooks.rs`, `zk_veil.rs`, `coin_tree.rs`, `coin_seed.rs`, `lib.rs` (`unit_draw`, `replay_round`, the coin server), `bin/flock-circuit.rs`, `Cargo.toml` | `verity/protocols/verification/flock/prover/` (the CPU reference prover) | P1, P5 (coins from `verity.randomness`) | medium | proofs: is the Rust CPU path the reference, and the GPU feature the kernel? |
| `session_verify.rs` (upstream's `verify_ligerito_extra`, call for call, timed; `flock-circuit serve`'s verifier) | `benchmarks/flock/` (it times the verifier), or the assurance list beside lean-agreement | P1 (not the verifier of record), P5 | low | proofs: is it TCB, a benchmark, or assurance? |
| `gpu_circuit.rs` (feature `gpu`), `cuda/prove_circuit.cuh`, `cuda/sha512.cuh`, `cuda/ligerito_zk.cuh`, `cuda_circuit_patch.py`, `cuda_sha512_patch.py`, `cuda_live_patch.py`, `flock-{glue,sha512,zk,vtime}-b684b12.patch` | `verity/kernels/flock-cuda/` (one entry: a Rust+CUDA crate with patches, build key `b684b12` + toolkit, the SASS/FTZ gate) | P5 | medium | proofs: today this is one cargo package with a `gpu` feature. Does the registry entry point at that feature, or does `gpu_circuit` become its own crate? `prove_circuit.cuh` is included after `prove_chunk.cuh` in upstream's `prove_ffi.cu`, so the chunk header can't leave first. |
| `pure_block.rs`, `chunk.rs`, `ir_frame.rs`, `ir_sampling.rs`, `vllm_block.rs`, `gpu.rs` (serves only those); bins `flock-pure`, `flock-pure-gpu`, `flock-link`, `flock-gpu-link`, `flock-live`, `flock-ir-block`, `flock-ir-frame`, `flock-ir-sampling`, `flock-vllm-v1`; `cuda/prove_chunk.cuh`, `cuda/pure_sha256.cuh`, `cuda_chunk_patch.py`, `flock-{link,gpu-link}-b684b12.patch`, `backends/flock/verity_unit.rs` | `experimental/flock/` while each builds and teaches, then `archive/flock/` with its record | P8, P9 | medium | proofs: each is a superseded statement form. Experimental or archive, form by form? `lib.rs` declares every module, so the crate must split before any leaves. |
| `check_build.sh` (check's flock-rust step) | with the prover crate | P5 (CI builds every kernel) | medium | ci: should it stay beside the crate, or move into `tools/check/`? |
| `live/PROTOCOL.md` | retires; its definitions go to the Lean spec, its vectors stay | Conv: PROTOCOL.md | medium | proofs |

### 1d. Pod scripts, prototypes and tool declarations

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `pod/00-setup-cpu.sh`, `cpu-slices.sh`, `50-preflight.sh`, `60-circuit.sh`, `61-circuit-cell.sh`, `70-class-sweep.sh`, `71-gemm-slowdown.sh`, `72-host-unit-eval.sh`, `74-gemm-hill.sh`, `76-read-gadget.sh`, `gemm_hill.py`, `gemm_slowdown.py`, `gemm_fp.py`, `read_gadget.py`, `gemm-coordinates*.defs.json` | `benchmarks/flock/` | Layout | medium | proofs: is `50-preflight.sh` current? |
| `pod/10-link.sh`, `20-*.sh`, `21-*.sh`, `22-*.sh`, `23-*.sh`, `30-*.sh`, `31-*.sh`, `33-*.sh`, `34-*.sh`, `40-vllm-v1.sh`, `unit.py`, `gf2.py`, `export_unit.py` | `archive/flock/` (or `experimental/flock/`) with the superseded statements; their replays expect "refused: <form>" at main | P8 | medium | proofs |
| `arch_proto/` (10; architecture study prototypes) | `experimental/flock/` | P9 | medium | proofs: does it still teach something, or should it go to archive? |
| `tool.py` (`flock_pure`, `flock_class_sweep`) | `benchmarks/flock/tool.py` | P6 (it imports `research`, so never `verity/`) | high | none; `research`'s `tools_registry.REGISTRY` dotted path updates in the same PR |

### 1e. Verifier scripts and data (`backends/flock/verifier/`, excluding `lean/`)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `agree.py`, `ci.py`, `ci-bundle.sh`, `ci-pod.sh`, `fuzz.py`, `transcript_check.py`, `zk_mutants.py`, `selftest_records.py`, `redigest.py`, `upstream.json`, `upstream-build.sh`, `tool.py` (`flock_agreement`) | `tools/lean_agreement/` (the assurance TCB's "upstream's Rust verifier through lean-agreement") | P1 (assurance list), P6 | medium | proofs and ci: does this move into `tools/`, or stay beside the verifier but outside `verity/`'s import closure? `research.store.kinds` names `upstream-build.sh` and `upstream.json` by path. |
| `circuit_type_agree.py`, `cut_check_agree.py`, `layout_agree.py`, `qcall_agree.py`, `qword_agree.py`, `qword_program_agree.py`, `template_query_agree.py`, `unit_cut_agree.py`, `stratified_agree.py` (imports `verity_sampled_proofs.one_stage`) | `tools/lean_agreement/` | P1 (assurance list) | medium | same as the row above |
| `vectors.json`, `lookup_v2_vectors.json`, `circuit-vectors*.patch`, `netlist-vectors.patch` | beside the verifier in `verity/` (a vectors file is the spec where two implementations agree), or `catalog/vectors/` | Conv: PROTOCOL.md, P3 | medium | proofs: beside the verifier, or in the catalog? |
| `verifier/PROTOCOL.md` | retires except §16.15; its deviation list becomes data that `agree.py` reads | Conv: PROTOCOL.md | high | none |
| `verifier/README.md` | a short README stays with the verifier | Conv: PROTOCOL.md | high | none |

### 1f. Tests (`backends/flock/tests/`, 52 files)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `test_lean_*` (verifier), prover tests, bench tests, frozen-form tests | each moves beside its code: the verifier's and prover's tests to `verity/…/flock/tests/`, the rest to `benchmarks/`, `experimental/` or `archive/` | Conv: tests | medium | ci: several of these tests import `verity_numerical.bench.templates` and input sets (`test_circuit.py`, `test_typed_statement.py`, `test_ir_lowering.py`, `test_lean_verifier.py`, …). Does the boundary test cover `tests/`? If it does, these become catalog-side or benchmark-side tests. |

## 2. `backends/numerical/` (`verity_numerical`, 211 files; owner: proofs for the frozen parts, circuits for templates)

The README already calls everything except the bench spine frozen.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `bench/templates.py` (the subcircuit template catalogue: a named Definition family with typed parameters) | `catalog/definitions/templates.py` | P3 | medium | circuits: its registry imports (`b1`, `hopper`, `moe`, `fp8`, all lazy) become catalog-internal once the registry moves, and its `kernel_registry` import must point at `verity/kernels`. Confirm it's catalog. |
| `bench/input_sets.py`, `generate.py`, `lowerings.py` (hard-codes C-Flock's `templates/` path), `census.py` (the census reader) | `benchmarks/numerical/` | Layout | medium | proofs: C-Flock's `circuit.py` reads `lowerings` and `InputSet` (section 6, item 2). |
| `bench/contract.py`, `tables.py`, `views.py`, `drilldown.py`, `store_tables.py`, `summary.py`, `switch.py`, `ledger_to_store.py`, `frozen.py`, `placement.py` (imports `research.pods`), `cell.py`, `instances.py`, headline, decision tables, latency and plots, drivers `a_route_a`, `b_interactive`, `c_interactive` | `benchmarks/numerical/` (the table renderer and the frozen-ledger readers) | Layout, P8 | medium | ci: `research` shells out to `python -m verity_numerical.bench.tables` and `.drilldown` (`notes.py`, `store/parity.py`), and `store/vocab.py` mirrors `contract.PROOF_CLASSES`. Both update in the move PR. |
| `reference/hawkeye_close` (used by `tools/tc_probe` and `bench.instances`) | `tools/tc_probe/` (a catalog builder's reference) | Layout (catalog builders are tools) | medium | circuits: or is it a hardware-model entry for `catalog/`? |
| `checker/` (WP2), `security/` (A-GKR and B-Ligero calculators), `gkr_export/`, `explore/`, `redteam/` | `archive/numerical/`, with the frozen backends that use them | S4, P8 | medium | proofs: do the frozen table rows render only from the store (`frozen.py`), so that nothing live reads `security/`? |
| `backends/numerical/tests/` | splits with its code | Conv: tests | medium | none |

## 3. Frozen backends (owner: proofs)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `backends/gkr/` (A-GKR, 282) | `archive/gkr/` with its record | S4 | high | none |
| `backends/direct/` (B-Ligero, Python `ligero`, 305) | `archive/direct/` | S4 | high | first C-Flock's `instances.py` and `bench.py` and numerical's tests and drivers must stop importing `ligero` (archive is imported by nothing) |
| `backends/ligero-verify/` (129), `backends/ligerito-verify/` (88) (Rust) | `archive/ligero-verify/`, `archive/ligerito-verify/` | S4 | high | none |
| `backends/sp1/` (D-SP1, 101) | `archive/sp1/` | S4 | high | first `benchmarks/dot_product` and `benchmarks/ir_call` (out of this map's scope) must drop `verity_sp1` or move with it |
| `backends/vole/` (13) | `archive/vole/` | S4 | high | none |
| `backends/redteam/` (7, Rust forgery harnesses) | `archive/redteam/` | S4 | medium | proofs: do these harnesses still attack a live backend? |
| `backends/shared/hash_gpu` | `benchmarks/commitments/`, or `verity/kernels/` as a commitment kernel if a result rests on it | P5, S4 | medium | circuits: `benchmarks/commitments/commit_cost_gpu.py` imports it, so it can't go to `archive/` |
| `backends/shared/anchor_a100` | `archive/shared/`, or `catalog/devices/` as A100 evidence | P3, S4 | low | proofs and circuits: does any live result read it? |
| `backends/README.md`, `backends/AGENTS.md` (campaign policy, frozen tables, trust levels) | `archive/README.md`; any rule still live folds into AGENTS.md | S4 | medium | proofs |

For every frozen backend, these must change in the same PR:

- the root `pyproject.toml` workspace members and the `torch-cpu` conflicts list;
- `research`'s `tools_registry` (`bench_vu`, `ligero_verify_batch`, `a_gpu_prove`, `bench_vu_fp8`, `bench_vu_fp4`);
- `research`'s `store/vocab.py` mentions.

## 4. `integrations/vllm/` (`verity_vllm`, 1523 files; owner: circuits)

Most of the integration stays; the plan places the frontend, capture, capture maps, κ profiles, the fold and Match there.
Five areas leave or split:

- the registry's Definitions to `catalog/`;
- `program/kernels`' registry and row kernels to `verity/kernels/`;
- PoUW's device code to `verity/kernels/`;
- the commit layer's duplicates of core, which consolidate onto `verity.commitments`;
- possibly the Commit verdict, if it is a verifier role (section 7, circuits question 3).

### 4a. Subpackages and data

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `engine/` (135), `acquire/` (42), `observe/` (38), `collectives/` (4), `linear/` (3), `predict/` (6), `ops/` (18, with `known_roots.json`), `config.py`, `target_family.py` | stays | P7 | high | none |
| `pipeline/` (80) | stays; `program_graph._encoded` and `definition_digest` lift into `verity.ir` (section 6, item 3) | P7, P6 | high | none |
| `pipeline/research_tools.py`, `pipeline/research.py`, `source_identity.py` | stays (research job declarations, `vllm.build` … `vllm.replay`) | P6 (allowed: an integration may import tools) | high | none |
| `query/` (18) | stays; `call_scope.py` and `cross_call.py` ("what `query.word` and `query.cross_call` share beyond core's `verity.ir.cut`") are candidates to move into `verity/primitives/circuits/` | P4 (queries over circuits are core) | medium | circuits: is the cross-Call partition invariant generic core query logic? |
| `correspondence/` (7) | stays | P7 | high | none |
| `properties/` (16, difftest harnesses) | stays; the plan's "one difftest harness" consolidation comes later | P7, S5 | high | none |
| `check/` (63): `match/` (20), `fold_compare.py`, `gates.py`, `poc_*`, `program_ops.py`, … | stays (the fold and Match are integration per circuits) | P7 | high | none |
| `check/verdict.py`, `commit_rules.py`, `result.py`, `replay/` (19: `sample.py`, `opening.py`, `stoch_recompute.py`, `pouw_circuit.py`, …) | stays, or the deciding logic moves into `verity/protocols/` if the Commit verdict is a verifier | P7 ("they never talk to the verifier") | low | circuits and proofs: is the Commit VERDICT the verifier's decision, or the integration's own self-check before handing off? |
| `commit/challenge.py` (every draw over committed values; legacy Fiat–Shamir forms, and new forms from a beacon or auditor key via `verity.randomness` and `verity_sampled_proofs.law`) | the verifier-side draws move to `verity/protocols/` (sampled proofs); the legacy forms stay for replay | P7, P5 | low | circuits and compute-accounting: who runs these draws, the verifier or the prover? |
| `commit/merkle.py`, `commit/hashing.py` (a second `vllm-v1` Merkle implementation, specified in core's `verity/commitments/vllm_v1/PROTOCOL.md`) | consolidate onto `verity/primitives/commitments/` ("one Merkle tree"), with a bridge by vectors; a thin adapter stays | Layout, S5 (consolidation adds, bridges, supersedes) | medium | circuits |
| `commit/hiding.py`, `commit/scheme.py` (thin adapters over `verity.commitments`) | stays | P7 | high | none |
| `commit/committer/` CUDA sources: `native_leafhash.cu`, `native_tree.cu`, `native_gather.cu`, `hidden_gpu_src/hidden_gpu_tree.cu`, `native_plans.h`, `native_collect.cpp` | the leaf-hash and tree kernels go to `verity/kernels/commitments-gpu/` (reference: `verity.commitments`); the collector stays | P5 | low | circuits: does a result rest on these device hashes? The Python host side (`native_host`, `native_collect`, `leafhash`) imports `acquire`, `engine` and `pipeline`, so only the `.cu` files and a JIT shim could move. |
| `commit/` other modules: `binding`, `capture_map`, `identity`, `native_ranges`, `opened`, `padding_steps`, `partition`, `serving_rows`, `store_dump`, `hidden_stream` | stays | P7 | high | none |
| `protocol_options/interface.py`, `pous.py`, `pouw.py`, `pouw_circuit.py`, `sampled_proofs.py` | stays (protocol adapters) | P7 | high | none |
| `protocol_options/pouw_native.py` (`ncp-v2`'s committed values natively, from numpy and hashlib) | `verity/protocols/accounting/pouw/` (the reference for the device path) | P5 | medium | compute-accounting: is this the reference that `pouw_device` is gated against, leaf for leaf? |
| `protocol_options/pouw_device.py`, `pouw_cuda/` (`ncp2*.cu`, `.cuh`, `ncp2_host.cpp`) | `verity/kernels/ncp-v2-cuda/` | P5; the plan's `ncp-v1`/`-shift24` in `verity/` | medium | compute-accounting: both modules import the integration's `protocol_options` interface, so split that first |
| `protocol_options/pouw_pearl_c_{device,graphs,host,screen,triton,whole}.py` (Pearl-C on sm_120) | `verity/kernels/pearl-c-sm120/` for the kernel pipeline; the vLLM `quant_method.apply` hook stays | P5, the plan's `pearl-c-sm120-v1` | medium | compute-accounting: the liveness screen is torch plus Triton. P5 says torch is a container only, so does the screen's math sit on a path a result rests on? |
| `program/frontend/` (47: `rules/`, `rules/vllm_bindings/`, `torch_frontend`, `triton_capture`, `target_profile`, `registration`, `derive`, …) | stays (rules and vocabulary) | P7, P3 (circuits' "integration" list) | high | none |
| `program/lifting/` (3; promoted from veritor, single consumer) | stays | P7 | high | none |
| `program/boolean.py` (each Definition's Boolean version, and how far a Program is from bits) | split: the Definition-to-Boolean link table goes to `catalog/definitions/`; the Program-on-bits analysis (imports `frontend.derive`, `torch_frontend`, `config`) stays | P3 (circuits: "the word Definitions and their Boolean versions") | medium | circuits |
| `program/compact.py`, `descriptor_equivalence.py`, `profile_descriptor.py`, `instances_form.py`, `replay.py`, `sampling_event.py`, `workload.py`, `model.py` | stays; `profile_descriptor.py` could become a tool | P7 | high | none |
| `program/dtypes.py` (numpy BF16↔f32) | stays; consolidate onto core's FP semantics later | S5 (one FP semantics) | medium | circuits |
| `program/registry/` (55 modules) | see 4b | P3, S5 | n/a | n/a |
| `program/registry/quarantine/` (6 subpackages, 39 `.py`) | deleted with the deleted versions' targets | S5 | medium | circuits: the plan says "8 modules", but the tree has 6 subpackages (`act`, `collective`, `dense`, `ln`, `ov_moe`, `ov_sampling`) holding 39 files. `value_inputs.py` says `LayerNormAten_v2` stays in `quarantine.ln`. Do the kept Programs or records name any of them? |
| `program/kernels/` (37) | see 4c | P5 | n/a | n/a |
| `data/` (16), `docs/` (34, `ref-prims` data), `manifests/` (8: capture maps, semantic profiles, `checkpoints.json`), `workloads/` (160, 6.8 MB), `fixtures/` (7) | stays (capture maps and κ profiles are integration) | P7, P3 | medium | circuits: do any kept Programs' representative statics belong in `catalog/` as entries? |
| `tests/` (615; `program/` 148) | splits with its code: registry tests go to `catalog/tests/`, kernel tests to `verity/kernels/` | Conv: tests | medium | circuits |

### 4b. `program/registry/`: each of the 55 modules

Classes:

- *Def*: Definitions, or helpers only Definitions use. These move to `catalog/` as they are once their siblings do.
- *Def+twin*: Definitions with a numpy or C++ twin, or a hook into a kernel model, beside them. The twin splits out.
- *Def+vocab*: Definitions with model configurations, target bindings or integration code beside them. The vocabulary
  splits out.
- *Vocab*: bindings only; they stay in the integration.
- *Record*: the conformance record.
- *Twin*: a twin with no Definitions.
- *Harness*: a difftest or sweep.
- *Loader*: modules that load the registry.

Imports are direct imports, from the AST. "Siblings" are other registry modules; `*` marks a function-level import.

| Module | Class | Destination | Imports outside the registry, and the split needed | Confidence |
|---|---|---|---|---|
| `act` | Def | `catalog/` | none (siblings: `prims`) | high |
| `boolean_activation` | Def | `catalog/` | none | high |
| `boolean_attention` | Def | `catalog/` | none | high |
| `boolean_dense` | Def | `catalog/` | none | high |
| `boolean_dense_norm` | Def | `catalog/` | none | high |
| `boolean_fp8` | Def | `catalog/` | none | high |
| `boolean_fp8_moe` | Def | `catalog/` | none | high |
| `boolean_gather` | Def | `catalog/` | none | high |
| `boolean_moe` | Def | `catalog/` | none | high |
| `boolean_norms` | Def | `catalog/` | none (imports `sampling`, which splits) | high |
| `boolean_rope` | Def | `catalog/` | none | high |
| `boolean_silu` | Def | `catalog/` | none | high |
| `boolean_softcap` | Def | `catalog/` | none | high |
| `dense` | Def | `catalog/` | none | high |
| `fa2_check_inf` | Def | `catalog/` | none | high |
| `fa2_softcap` | Def | `catalog/` | none | high |
| `fa3_check_inf` | Def | `catalog/` | none | high |
| `fp8_moe` | Def | `catalog/` | none | high |
| `gemm_bias` | Def | `catalog/` | none | high |
| `gumbel_boolean` | Def | `catalog/` | none | high |
| `moe` | Def | `catalog/` | none (imports `ref_prims`, which splits) | high |
| `moe_pad` | Def | `catalog/` | none directly, but it imports `lifted` at module level, so it waits for `lifted`'s split | medium |
| `nvfp4` | Def | `catalog/`, or `experimental/` if its conformance status is not current | none | medium |
| `operand_widths` | Def (helper of `lifted`'s strict lift) | `catalog/` | none | high |
| `pad_prims` | Def | `catalog/` | none | high |
| `pouw_rows` | Def | `catalog/` | `verity_pouw.circuit.ncp2` (`protocols/`), which is `verity/` after PoUW's Python move; land that first | medium |
| `sampling_boolean` | Def | `catalog/` | none | high |
| `serve3` | Def (Serve@3, the padded serving circuit) | `catalog/` | none | medium |
| `spec` | Def (speculative-decoding composites and programs) | `catalog/` | none | medium |
| `tables` | Def (tables as registered values) | `catalog/` | none | high |
| `topp_keep_builder` | Def (the top-p keep word's builder) | `catalog/` | none (imports `topp_split`* lazily, which splits) | medium |
| `topp_word_gates` | Def | `catalog/` | none (imports `sampling`*) | high |
| `topp_words` | Def | `catalog/` | none (imports `sampling`*) | high |
| `value_inputs` | Def | `catalog/` | none | high |
| `prims` | Def+twin | `catalog/` + `verity/kernels/` | the `_fa2()` and `_rms()` hooks import `kernels.fa2_model`*, `fa2_relation`*, `rms_relation`* and `rms_triton_model`*; only `kernels/twins.py` and `check/replay/driver.py` call them, no Definition does. Move the hooks to the kernels. | medium |
| `fp8` | Def+twin | `catalog/` + `verity/kernels/` | the numpy twins (`np_f32_to_e4m3_sat`, `np_e4m3_to_f32`, …) split from the Definitions | medium |
| `ref_prims` | Def+twin | `catalog/` + `verity/kernels/` | about 20 numpy functions, a torch import, and `kernels.derived_rows`*; the reference kinds' Definitions go to the catalog, the twins to the kernels. It's also S5's FP-semantics consolidation target. | medium |
| `sampling` | Def+twin | `catalog/` + `verity/kernels/` | numpy row paths, and `topp_split`* | medium |
| `topp_split` | Def+twin | `catalog/` (its one Definition) + `verity/kernels/` (the exact-fp32 numpy model of vLLM's split top-p) | kernels* (the same four as `prims`) | medium |
| `b1` | Def+vocab | `catalog/` (composites) + `integrations/vllm/` (vocabulary) | `B1_CONFIG`, `B0_CONFIG`, `SMOL360_CONFIG`, `QWEN05_CONFIG`, `FUSED_RMS_BLOCK`, the FA2 kernel source strings, `SERVE_FAMILIES`, `GEMM_AMPERE` and `ATTENTION_FA2` sit beside the composites | medium |
| `b1_tp2` | Def+vocab | `catalog/` + `integrations/vllm/` | `B1_TP2_CONFIG` (a model's TP=2 configuration) beside the TP compositions | medium |
| `hopper` | Def+vocab | `catalog/` (the Hopper Definitions) + `integrations/vllm/` (`bindings()`, `GEMM_HOPPER`, the re-instantiation of B1) | none outside the registry | medium |
| `lifted` (2368 lines) | Def+vocab (integration code) | `catalog/` (the ⊥-lifted Definitions) + `integrations/vllm/` | `pipeline.global_program`*, `program.workload`* and `query.query_artifact`* must leave the Definition module; this split also frees `moe_pad` | medium |
| `targets` | Vocab (target-keyed bindings: which Definition variant a launch binds to) | stays in `integrations/vllm/` | none | medium |
| `gemm_targets` | Vocab (GEMM target specialisations, read through `TargetProfile`) | stays in `integrations/vllm/` | `frontend.target_profile`* | medium |
| `conformance` | Record (each Definition's status, `current`/`superseded`, with qualifications) | `catalog/` as each entry's status; its CLI stays in the integration | `config` (only for the CLI's `option`) | medium |
| `sampling_rows` | Twin (vectorised exact twins of `GumbelTopPTokenSelect_v1`) | `verity/kernels/`, or stays if the replay isn't a verifier | `kernels.derived_rows` (module level) | medium |
| `serve3_reference` | Twin (vectorised reference evaluator of Serve@3's padding layer) | `verity/kernels/`, or stays | none | medium |
| `collectives_difftest` | Harness (torch, NCCL) | `integrations/vllm/` tests or `properties/` | torch | high |
| `moe_difftest` | Harness | `integrations/vllm/` tests or `properties/` | `engine.hooks`*, `frontend.target_profile`* | high |
| `rope_difftest` | Harness | `integrations/vllm/` tests or `properties/` | torch | high |
| `sampling_topp_difftest` | Harness | `integrations/vllm/` tests or `properties/` | torch | high |
| `rmsnorm_fused_sweep` | Harness | `integrations/vllm/` tests or `properties/` | `config` (`ROOT`, `option`) | high |
| `__init__` | Loader (registers lazy families via makers that import `b1`, `prims`, `sampling`, `lifted` and `topp_word_gates`) | `catalog/` once the makers are catalog-local | its "all" closure reaches `pipeline`, `query` and `workload` through `lifted` | medium |
| `catalog` | Loader (loads every module) | the Definition loader goes to `catalog/`; the integration keeps a loader that adds its vocabulary | none | medium |

The counts by what each module needs:

- **Pure Definition: 34.** `act`, the 12 `boolean_*`, `dense`, `fa2_check_inf`, `fa2_softcap`, `fa3_check_inf`, `fp8_moe`,
  `gemm_bias`, `gumbel_boolean`, `moe`, `moe_pad`, `nvfp4`, `operand_widths`, `pad_prims`, `pouw_rows`, `sampling_boolean`,
  `serve3`, `spec`, `tables`, `topp_keep_builder`, `topp_word_gates`, `topp_words`, `value_inputs`. Two of them wait on
  something: `moe_pad` on `lifted`'s split, and `pouw_rows` on PoUW's move.
- **Definition with a twin to split: 5.** `prims`, `fp8`, `ref_prims`, `sampling`, `topp_split`. Two more modules are
  twins alone: `sampling_rows` and `serve3_reference`.
- **Vocabulary: 6.** Four are Definition plus vocabulary (`b1`, `b1_tp2`, `hopper`, `lifted`), and two are vocabulary
  only (`targets`, `gemm_targets`).
- **The conformance record (1)** goes to the catalog as status metadata.
- **Harnesses (5)** go to the integration's tests.
- **Loaders (2)** split.

The total is 34 + 5 + 2 + 6 + 1 + 5 + 2 = 55.

The plan says "43 of vLLM's 55 registry modules import `verity_vllm`". At this commit, 51 of the 55 do, counting relative
imports. Counting only absolute `verity_vllm` import lines gives 49, and counting only module-level ones gives 45. Only
`catalog`, `operand_widths`, `pouw_rows` and `serve3_reference` have none. Nearly all of these imports are siblings
inside the registry, which move together.

Counted by module-level imports only, 51 of the 55 import nothing outside the registry, `verity` and numpy. Three reach
the integration at module level: `sampling_rows` (through `kernels.derived_rows`), and `conformance` and
`rmsnorm_fused_sweep` (through `config`). `pouw_rows` reaches `verity_pouw.circuit.ncp2`. The other blockers (`prims`,
`topp_split`, `ref_prims`, `gemm_targets`, `lifted`, `moe_difftest`) are each one or a few function-level imports. The registry's split is therefore
mostly separating twin and vocabulary *content* from the Definitions, not cutting a dense import graph.

### 4c. `program/kernels/` (37 files)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `_jit.py`, `kernel_registry.py`, `__init__.py` | `verity/kernels/` (the registry; the plan calls it "mostly a rename") | P5 | medium | circuits: see section 6, item 11 (the registry can't import catalog Definitions) |
| `cpp/` (`fa2_model.cpp`, `k16_chain.cpp`, `rms_triton_model.cpp`, `tc_model.cpp`) with `fa2_model.py`, `fa3_model.py`, `rms_triton_model.py`, `cpu_model.py`, `mma.py` (imports only `verity.ml.tc`) | `verity/kernels/` (C++ twins of vLLM's attention, GEMM and RMS kernels) | P5 | medium | circuits: does any result rest on them (the replay verdict), or do they only predict? |
| `rows.py`, `ir_rows.py`, `dense_rows.py`, `act_rows.py`, `softcap_rows.py`, `value_rows.py`, `moe_router_rows.py`, `fp8_moe_rows.py`, `derived_rows.py` (numpy row kernels, `register_kernel`ed and `self_check`ed) | `verity/kernels/cpu/` | P5 | medium | circuits: each imports `verity_vllm.program.registry` to reach its Definition, which would become `verity` importing `catalog` |
| `twins.py` | `verity/kernels/`, after its split | P5, P6 | medium | circuits: it imports `check.fold_compare` and `config` |
| `libdevice_sampling.py` (bit-exact transcription of libdevice `__nv_logf` and `__nv_log1pf`, FTZ) | `catalog/devices/` (a device math model), or `verity/kernels/` | P3, P5 | low | circuits: it imports `config` and `registry.sampling` |
| `relations.py` (the relation registry and the `check` runner), `gemm_relation.py`, `fa2_relation.py`, `rms_relation.py` | stays in `integrations/vllm/` (check); the MUFU tables that C-Flock's `ir_lower` reads from `fa2_relation` and `rms_relation` go to `catalog/devices/` | P7, P3 | medium | circuits |
| `compiled_relations.py`, `compiled_norm_literal.py` (torch and Triton), `gemm_target_correspondence.py` (torch) | stays in `integrations/vllm/` | P5 (torch is a container only; trusted code never uses its math) | high | none |
| `kernel_zoo.py` (resolved A100 GEMM launch signatures and their bit-exact CPU models) | `catalog/devices/` as evidence, or stays | P3 | low | circuits |
| `sampling_rng.py` (torch-free recomputation of the Gumbel noise; imports `check`, `observe`, `config`) | stays in `integrations/vllm/` (check) | P7 | medium | circuits |
| `cuda/` (`fa2_softmax_probe.cu`, `mma_tiles_sm80.cu`, `mufu_probe.cu`, `rms_probe.cu`, `tanh_probe.cu`) | `tools/` (catalog builders: capture probes); S5's "one GPU capture harness" | Layout | high | none |

## 5. `tools/`, `infra/`, `.agents/` and the root

### 5a. `tools/research/` (290 files; owner: infra)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `src/research/` code (`approaches`, `cli`, `deploy`, `gates`, `merge`, `notes*`, `queue`, `runs`, `steward`, `store/`, `jobs/`, `telemetry/`, `pods/*.py`) | stays; its own distribution | Conv: packaging | high | none |
| `pods/nebius/` units and timers (`infra-pool-publish`, `n2-custody`, `vy-lean-cache-daily`: 3 `.service`, 3 `.timer`), `user-cpuset.conf`, `deploy.toml`, `dispatch-n1.env`, `weights.tsv` | `infra/nebius/` | Conv: node config | medium | infra: `deploy.py` sets `MANIFEST` beside itself, and `manifest_at(ref)` reads a ref's copy at that same path, so a ref from before the move falls back to the checkout's manifest. Is that acceptable, or should it try both paths? `prefetch.py` reads `weights.tsv` beside itself. |
| `pods/nebius/monitoring/` YAML and JSON (`alerting`, `exporter`, `grafana`, `nebius-overview.json`, `lanes.tsv`), `pods/nebius/sky/*.yaml`, `sky/jobs/*.yaml`, `kueue*.yaml`, `sky-config.yaml` | `infra/nebius/` | Conv: node config | medium | infra |
| `pods/nebius/` scripts (28 `.sh`, 21 `.py`: `dispatch`, `fill_runner`, `pool_n1`, `n1_lease`, `node_ops`, `lean_sandbox`, `vm_setup.sh`, …), `monitoring/*.py`, `sky/*.sh` and `*.py`, `pods/sh/` (`lease.sh`, `gpu_lease.sh`, `pod_guard.sh`) | stays in `tools/research/` (code), or `infra/nebius/` | Conv: node config (data only) | low | infra: are node-side scripts code (tools) or node configuration (infra)? `deploy.toml` names 47 sources under `tools/research` and 21 entries installed `by` a script, and `research deploy drift` keys on those paths. |
| `console/` (`verity_console.py` and friends) | stays (its units are already in `infra/nebius/`) | Conv: node config | high | none |
| `control/` (control-pod scripts) | stays | Layout | medium | infra |
| `store.pod.toml` | `infra/`, or stays | Conv: node config | low | infra |
| `store/tools_registry.py` (`REGISTRY`: tool name → dotted repo path, for example `backends.flock.tool:FLOCK_PURE`) | stays, and every move PR updates its entries | S5 (each move updates its paths) | high | ci: add it to S5's list of what each move PR updates |

### 5b. Other tools

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `tools/cluster/src/` (stdlib, imports neither `verity` nor `research`) | stays | Layout | high | none |
| `tools/cluster/descriptions/nebius.toml`, `kinds/*.toml` | `infra/cluster/`, or stays | Conv: node config | medium | infra: `cli.py` defaults to `Path(__file__).parents[2]/"descriptions"`, and `kinds` sit "beside the descriptions" |
| `tools/cluster/vy-cluster-agent.service`, `shadow-node2.sh` | `infra/nebius/` | Conv: node config | medium | infra |
| `tools/check/` (`check.py`, `suites.py`, `slot.py`, `lean_slot.py`, `lean_audit.py`, `verdicts.py`, `guard/`, `train.sh`, `post_train.py`, …) | stays (check's gates are on the assurance list) | P1 (assurance list) | high | none |
| `tools/check/ci.toml`, `queue.toml`, `lean-deps.json` | stays (check's own data) | P1 | medium | ci |
| `tools/check/pod_setup.sh` | stays, or `infra/` | Conv: node config | low | ci |
| `tools/lean/` (`audit.py`, `Facts.lean`, `Replay.lean`, `Upstream.lean`, `sandbox.sh`, `setup.sh`, `cache.py`, `merge.py`, `upstream.py`, `run_daily.py`, `tool.py`) | stays (the validator is on the assurance list) | P1 | high | none |
| `tools/circuit_check/src/circuit_check/` code (`checks.py`, `cli.py`, `cache.py`, `vectors.py`, `known.py`) | stays | Layout | high | none |
| `tools/circuit_check/…/targets.py` (684 lines of per-Definition bindings) | split per Definition module first (S5). A binding that names only a Definition, its statics and its pins moves beside the Definition in `catalog/`; anything needing `frontend.rules`, `target_profile`, `program.boolean`, `kernels`, `query`, `verity_pouw.circuit.*` or `verity_numerical.bench` stays in the tool | S5, P6 | medium | circuits: a binding in `catalog/` may import only `catalog/` and `verity/` |
| `tools/circuit_check/…/pins.json` (definitions 224, pieces 100, units 8) | `catalog/definitions/`, split per Definition module | P3 (circuits' catalog list), S5 | medium | circuits |
| `tools/agent-guard/` | stays | Layout | high | none |
| `tools/tc_probe/` (`tc_probe.py`, `trust.py`, `canary.py`, `instances_hw.py`, `mma_tiles.cu`, `wgmma_tiles.cu`, `tiles_common.cuh`, `tool.py`) | stays (a catalog builder) | P3, Layout | high | none; it imports `verity_numerical.bench` and `reference`, which become `benchmarks/` and `tools/` |
| `tools/tc_probe_fp4/` probes (`probe.py`, `cast.py`, `k32.py`, `sparse.py`, `recheck.py`, `meta_rule.py`, `t1_merged.py`, `model5.py`, `stage0_sm100.py`, `stage0_sm120.py`, `*.cu`, `rows_fp4.cuh`, `nvf4_step.cuh`, `fp4_emulation_1ad1aaa2.py`, `tool.py`) | stays (a catalog builder) | P3, Layout | medium | none |
| `tools/tc_probe_fp4/lean_vectors.py` | stays (a builder), and its output becomes `catalog/vectors/` | P3 | medium | none |
| `tools/tc_probe_fp4/` PoUW experiments (`f1_rates.py`, `f2_strassen.{py,cu}`, `f3_lut.{py,cu}`, `w1_price.{py,cu}`) | `experimental/pouw/` | P9 | medium | compute-accounting: are these live approaches, or killed? `tc_price_fp4` in `tools_registry` points at this `tool.py`. |
| `tools/native_peak/` (`measure.py`, `mma_peak_fp4.cu`, `tool.py`) | stays (a catalog builder of device peak numbers) | P3 | high | none |

### 5c. `infra/`, `.agents/` and the root

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `infra/nebius/verity-console.service`, `verity-console.timer` | stays | Conv: node config | high | none |
| `.agents/` (skills, `using-slack/registry.json`) | stays (the plan keeps `registry.json` in place); skills update with each move | S5 | high | none |
| `pyproject.toml` (workspace members), `uv.lock` | stays; members change with each move | Conv: packaging | high | ci: see the packaging question in section 7 |
| `AGENTS.md`, `README.md` | stay; the map in AGENTS.md updates with each move, and the README is rewritten in S6 | S5, S6 | high | none |

## 6. Destinations that would make `verity/` or `catalog/` import `integrations/`, `experimental/`, `benchmarks/` or `tools/`

Each item names the import that would cross the boundary, and the split that must land first. Under P6, `verity/` may
import nothing else in the repository, *including `catalog/`*. Several items exist only because of that second half.

1. **C-Flock's prover in `verity/` would import the vLLM registry (`catalog/`) and vLLM's kernel relations (the
   integration).** The function-level imports are:
   - `ir_lower.silu_table` → `registry.prims`
   - `ir_lower.write_tables` → `kernels.fa2_relation` and `rms_relation`
   - `tail._fold_constant_mufu` → `prims`
   - `tail_pieces._gelu_table` → `dense`
   - `ir_sampling` (four functions) → `sampling`, `sampling_rows`, `prims`
   - `partition_units._program` → `b1`

   `topp_word` imports `topp_keep_builder` and `topp_word_gates` at module level.

   *Split first:*
   - The MUFU, SiLU and GELU tables become `catalog/devices/` entries that the caller passes to the prover.
   - Lowerings specific to one Definition (`topp_word`, the sampler rows) move beside their Definitions in `catalog/`
     and register with the prover through a parameter.
   - The B1 Program comes from the caller.
2. **C-Flock's prover would import benchmarks.** `circuit.lowering_for_set` reads `verity_numerical.bench.lowerings`, and
   `circuit.main` reads `bench.input_sets.InputSet`. `lean_rows`, `register`, `key_class_sets`, `ir_bench` and
   `circuit_bench` read `bench` as well.

   *Split first:* `main` and every input-set path move to `benchmarks/flock/`, and the prover takes a `Lowering`.
   Numerical's `lowerings.DIRECTORIES` hard-codes C-Flock's `templates/` path.
3. **C-Flock's prover would import the integration's pipeline.** `class_statement.distinct_calls` imports
   `program_graph._encoded` and `definition_digest`.

   *Split first:* lift both into `verity.ir`. They are pure codec helpers.
4. **Two kinds of C-Flock code must stay out of `verity/`.**
   - `boolean_export`, which imports the registry, `query.word`, `program_graph` and numerical's bench.
   - `tool.py` and `verifier/tool.py`, which import `research`.

   `instances.py` and `bench.py`'s flock-pure path import `ligero`. Since `archive/` is imported by nothing, those go to
   `archive/` too, or drop `ligero`.
5. **The vLLM registry in `catalog/` would import the integration.** The imports:
   - `prims` → kernel models*
   - `ref_prims` → `kernels.derived_rows`*
   - `sampling_rows` → `kernels.derived_rows` (module level)
   - `topp_split` → kernel models*
   - `conformance` and `rmsnorm_fused_sweep` → `config`
   - `gemm_targets` → `frontend.target_profile`*
   - `lifted` → `pipeline.global_program`*, `program.workload`*, `query.query_artifact`*
   - `moe_difftest` → `engine.hooks`*, `target_profile`*
   - `__init__`'s lazy family makers reach `pipeline`, `query` and `workload` through `lifted`

   *Split first:* the per-module splits in 4b, one family per PR, after circuit-check's bindings and pins are split per
   Definition module (S5).
6. **The registry in `catalog/` would import `protocols/` until PoUW moves.** `pouw_rows` imports
   `verity_pouw.circuit.ncp2`. That becomes `verity/` after PoUW's Python move, so PoUW's move lands before this module's;
   the plan's order already puts PoUW first.
7. **`catalog/definitions/templates.py` would import the integration's kernel registry.** Numerical's `bench/templates.py`
   imports `verity_vllm.program.kernels.kernel_registry`.

   *Split first:* point it at `verity/kernels/`. Its other registry imports become catalog-internal once the registry moves.
8. **`program/boolean.py` in `catalog/` would import the frontend.** It imports `frontend.derive`, `torch_frontend` and
   `config`.

   *Split first:* only the Definition-to-Boolean link table moves.
9. **circuit-check's per-Definition bindings beside their Definitions in `catalog/` would import tools, the integration
   and benchmarks.** `targets.py` imports `frontend.rules`, `frontend.target_profile`, `program.boolean`,
   `program.kernels`, `query`, `verity_pouw.circuit.*` and `verity_numerical.bench`.

   *Split first:* a catalog binding is data (Definition id, statics, pins); the checks that read the frontend, target
   profile or query stay in `tools/circuit_check/`.
10. **vLLM's kernels in `verity/kernels/` would import the integration.**
    - `twins.py` imports `check.fold_compare` and `config`.
    - `libdevice_sampling.py` imports `config`.
    - `pouw_device.py` and `pouw_native.py` import `verity_vllm.protocol_options`.
    - The committer's host code imports `acquire`, `engine` and `pipeline`.

    *Split first:* only the device sources and the pure twins move; the integration keeps the hooks.
11. **vLLM's kernels in `verity/kernels/` would import `catalog/`.** This is the structural one.
    - The row kernels (`rows`, `ir_rows`, `dense_rows`, `twins`, `derived_rows`) import `verity_vllm.program.registry` to
      reach the Definition each kernel computes.
    - `libdevice_sampling` imports `registry.sampling`.

    Once the registry is in `catalog/`, that is `verity` importing `catalog`, which P6 forbids. It needs one of two
    rulings:
    - kernels register against Definition ids as strings, and a catalog-side test binds and self-checks them (the ids
      are name-keyed, so moves don't change them); or
    - kernels of catalog Definitions sit in `catalog/` beside their Definitions, and `verity/kernels/` holds only
      kernels of core's own Definitions (C-Flock's CUDA prover, Pearl-C, commitments).

    The same question applies to C-Flock's Definition-specific lowerings in item 1.
12. **Live benchmarks would import `archive/`.**
    - `benchmarks/commitments/commit_cost_gpu.py` imports `backends/shared/hash_gpu`.
    - `benchmarks/dot_product` and `benchmarks/ir_call` import `verity_sp1`.

    These aren't `verity/` or `catalog/` imports, but they break "nothing imports `archive/`".

    *Split first:* `hash_gpu` leaves `shared/` before `shared/` is archived, and the two benchmarks move to `archive/`
    with SP1 or drop it.

## 7. Open questions by owner

**proofs (C-Flock)**

1. Which modules of the Lean `Flock/` are superseded-form parsers to copy into `security_proofs/flock/`, and does each
   refusal stay in the verifier?
2. Is the reference prover the Python statement staging (`circuit.py`, `typed_statement.py`, `ir_lower.py`) together
   with the Rust CPU path of `flock-circuit`? Is the `gpu` feature (`gpu_circuit.rs`, `cuda/`, patches) the
   `flock-cuda` kernel entry? Should that feature become its own crate?
3. Where does `session_verify.rs`, a timed Rust mirror of upstream's verifier inside `flock-circuit serve`, belong: in
   `verity/`, in `benchmarks/`, or on the assurance list?
4. Do the superseded statements go to `experimental/flock/` or `archive/flock/`, form by form? These are the Rust
   `pure_block`, `chunk`, `ir_frame`, `ir_sampling` and `vllm_block` with nine bins, the frame-v3 Python and its six
   template lowerings, and the pod scripts `10`–`40`. `prove_circuit.cuh` still includes after `prove_chunk.cuh`.
5. Do the agreement scripts and `upstream.json` move to `tools/lean_agreement/`, and do the vectors files sit beside the
   verifier or in `catalog/vectors/`? (With ci.)
6. Do numerical's `security/` and `checker/` go to `archive/`, with the frozen tables rendering only from the store?

**circuits (vLLM registry, Definitions, circuit_check)**

1. Which of section 6, item 11's two rulings for kernels of catalog Definitions? This decides where 5 twins, 2 twin-only
   modules, 9 row kernels and C-Flock's Definition-specific lowerings go. It probably needs @architecture.
2. Do you agree with the registry classes in 4b: 34 pure, 5 Definition plus twin, 2 twin-only, 6 vocabulary, 1 record,
   5 harnesses, 2 loaders? Is `lifted`'s split (pipeline, workload and query helpers out) the order in which `moe_pad`
   frees?
3. Is the Commit VERDICT, with `check/replay/` and `commit/challenge.py`, a verifier role (P7)? If yes, its deciding logic
   and the row kernels it uses move inward. If no, they stay, and the row kernels need no `verity/` home.
4. Is the conformance record the catalog's status field for each entry? Are `targets` and `gemm_targets` integration
   vocabulary, or the source of "each target's representative statics"?
5. Do `commit/merkle.py` and `hashing.py` consolidate onto `verity.commitments` (`vllm_v1`)? Are the committer's
   `.cu` leaf-hash and tree kernels a `verity/kernels/` entry?
6. Do `bench/templates.py` and `program/boolean.py`'s link table go into `catalog/`? Does `boolean_export.py` go to the
   integration or to tools?
7. The quarantine is 6 subpackages and 39 files, not the plan's 8 modules. The registry count is 51 of 55, not 43 (49
   counting absolute import lines only). Which method did the plan use?

**infra (tools/research, pods, cluster)**

1. Are the node-side scripts in `pods/nebius/` and `pods/sh/` (49 files) code that stays in `tools/research/`, or node
   configuration for `infra/`? This draft moves only units, timers, cpusets, `deploy.toml`, env, TSV and YAML.
2. `deploy.py`'s `MANIFEST` and `manifest_at(ref)` key on the manifest's path. How should refs from before the move
   resolve, and does the separately pinned `research` read `infra/` from a checkout on the nodes?
3. Do `tools/cluster`'s `descriptions/` and `kinds/` go to `infra/cluster/`, given `cli.py`'s default path?
4. Where do `store.pod.toml` and `tools/research/control/` go?

**ci (tools/check)**

1. The conventions say "one distribution per top-level directory", except `research`. `tools/` holds 8 distributions
   today. Do the other 7 merge into one `tools` distribution, given that `cluster` is stdlib-only, deployed on the nodes
   and boundary-tested on its own? I recommend exempting `cluster` like `research`.
2. Each move PR's list of what it updates should add `research`'s `tools_registry.REGISTRY`, `deploy.toml`'s sources,
   numerical's `lowerings.DIRECTORIES`, the `python -m verity_numerical.bench.*` strings in `research`, and
   `store/vocab.py`'s mirror of `PROOF_CLASSES`.
3. Do `check_build.sh` and `pod_setup.sh` stay where they are? Does the Python boundary test cover `tests/`? C-Flock's
   tests import numerical's templates and input sets.

**lean (tools/lean)**

1. Does `FlockProofs` (core-only lemmas, no dependencies) join the single `security_proofs` package, and so require
   Mathlib, or stay a separate no-dependency library?
2. C-Flock's three packages: the executable verifier in `verity/`, its spec, and `security_proofs/flock/` with `level3`
   and `soundness`. `level3` requires the verifier by path `..`. The path `require`s, the lock's package sections and
   `tests/test_lean_packages.py` change together. Is that one train?
