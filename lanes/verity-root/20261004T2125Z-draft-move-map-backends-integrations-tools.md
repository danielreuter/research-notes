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

The owners' answers of 4 Oct are folded into the rows: proofs' (`note:proofs/20261004T2240Z-handoff-move-map-answers`),
circuits' (`note:circuits/20261004T2241Z-draft-move-map-answers`, with its rulings of 22:46–22:50Z), infra's
(`note:infra/20261004T2232Z-report-move-map-answers`), compute-accounting's §F
(`note:compute-accounting/20261004T2247Z-draft-move-map-answers`, revised 23:09Z), and ci's and lean's in the kickoff
thread (1791150333.889129), with the captain's calls on them. They were checked against main `9400e83d5` (infra's against
`16749a0ff`); where this fold rechecked a fact, it says at which commit. A resolved question reads "answered (OWNER, 4
Oct): …". Where two owners disagree, or an answer disagrees with the plan, the row follows the owner's evidence and the
disagreement is listed under "Conflicts for the captain" at the end. The counts in "Counts by destination" are the
draft's and were not recounted.

Python import names follow the new directories (Daniel, 4 Oct 3:50 PM PDT), and the move script carries a module map
beside its path map. It rewrites imports, `import_module` strings, `module:attr` specs and module-keyed test data; Lean
comments that name Python modules are left to a later Lean PR. In Lean, declaration names are kept, while proof modules
move under a root of their own (lean, verity#1144).

Two of Daniel's later rulings, as the plan records them, bear on this map. At 4:06 PM: a claim about a computation is
verified only by a sampled proof over C-Flock with zero-knowledge, and a replay is a diagnostic that is never in
`verity/`, so vLLM's `check/replay/` stays in the integration. At 4:19 PM: only the prover's zero-knowledge layer is
trusted, and every kernel lives outside `verity/`, in a top-level `kernels/`: the witness kernels and the prover's
arithmetic (most of C-Flock's CUDA prover), whose wrong outputs stay hidden under the pads. So a destination written
`verity/kernels/<entry>/` below reads `kernels/<entry>/`. proofs draws the ZK layer's line in C-Flock's code; the padded
encoding and the leaf hashing are its open edge.

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

Since the draft, the fold moved rows between destinations: the shims are kept and the quarantine goes to
`experimental/` (so nothing is deleted); `instances`, `backend` and `arch_proto/` go to `archive/`; `boolean_export` goes to
`tools/`, `bench/templates.py` to `benchmarks/`, and `conformance` stays in the integration. The table is the draft's.

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
| `tools/research/src/research/pods/nebius/vy-keeper-n1.service`, `vy-keeper-n2.service`, `vy-keeper.timer`, `sky/store_evict_src.conf` (new) | `infra/nebius/`, with their `deploy.toml` `src` values | Conv: node config | medium | answered by infra's rule for units, timers and sky YAML (section 5a): they may move |
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
- Its superseded statements go form by form to `archive/flock/` (the pure, chunk and vLLM-block forms) or to
  `experimental/flock/` (the frame-v3 IR forms, which teach lowerings M0 hasn't ported) (answered, proofs, 4 Oct).

The prover cannot move until five lazy-import blockers are cut (section 6, items 1 to 4): its reads of the vLLM registry,
vLLM's kernel relations, vLLM's pipeline, `verity_numerical.bench`, and B-Ligero. circuits (4 Oct) found a sixth:
`class_statement` and `partition_units` import `circuit_check.targets` lazily (section 6, item 3).

### 1a. Lean (`backends/flock/verifier/lean/`, 667 files)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `verifier/lean/Flock/` (45), `Main.lean` (`flock-verify`), `lakefile.toml`, `lean-toolchain`, `lake-manifest.json` | `verity/protocols/verification/flock/lean/` (the executable verifier, no dependencies) | P1, P2 (the only Lean in `verity/` besides specs), S3 | high | none |
| Superseded forms' parsers inside `Flock/`: after fail-closed, only PR #83's four tags (`verity/flock-netlist/v1`, `verity/flock-circuit@19c7269a`, `@fd02e847`, `@631567f7`) reach `Blake3Row` (whole), `RowLeaf`, `Stmt.setup`'s non-hm96 branch with its `Circuit.parse`, `Comp`'s BLAKE3 load (`D_b3`), `Public`'s SHA-256 frame-v3 roots and those four `Tags` records | frozen copies into `security_proofs/flock/superseded/`, unlocked (Daniel's 1:13 PM ruling); the refusal stays in the verifier as a name-to-reason list, the `refused: <form>` text that #1147's `replay_expect` matches, with the four `Tags` records removed | P9 (last bullet), S3 | high | answered (proofs, 4 Oct): the legacy forms (`pure_block`, `chunk`, `ir_frame`, `ir_sampling`, `vllm_block`) have no parser; Lean refuses them by statement id before anything parses (`Main.lean:320–321`, `Flock/Tags.lean:304–308`). On main the four #83 tags still accept, with no claim over them. *Ordering:* this waits on fail-closed landing (`ProvedScope.statementRules` refuses the four by their tag fields), since without that refusal it would change what the verifier accepts. The lock's `reads` name `Comp`, `Circuit`, `Public` and `RowLeaf`, so those four split rather than leave whole, after the flock-lock reduction (864 entries to about 9). The typed statement (`verity/flock-circuit/types`, §16.11) is unfinished, not superseded: it stays behind `ProvedScope`'s refusal with `CircuitType`, `Layout`, `Typed`, `Derive*` and `Library`, and the hm96 tags pass the statement rules. |
| `verifier/lean/FlockProofs/` (6; core-only lemmas about the executable) | `security_proofs/flock/` | P2 (every lemma in `security_proofs/`), S1's lock reduction (the verifier's 25 entries leave) | high | answered (proofs and lean, 4 Oct): it joins `security_proofs/flock/`, and its root moves there. 18 of the verifier's 25 pins are proved there; the other 7 proofs, now in `Flock/*.lean`, move there in the lock reduction. The verifier package stays dependency-free. |
| `FlockRows` (`flock-rows` exe) | stays with the verifier package | P1 | high | answered (proofs, 4 Oct): a test exe. It emits netlists from types JSON, which `test_flock_rows*.py` compares with Python's `derive_vectors.json`; no guarantee depends on it, and it builds from the verifier's modules. |
| `verifier/lean/lean-audit.json` | split: the verifier's and spec's lock stays with them, and `security_proofs/flock` validates against it | P2 (the lock), S3.1 | high | none |
| `verifier/lean/level3/` (24; `FlockLevel3`, requires Mathlib and the verifier by path `..`) | `security_proofs/flock/level3/`, whole | S3.1 | high | answered (lean, 4 Oct): its root `FlockLevel3` already satisfies verity#1144's module-root rule, so it moves whole with no rename; its `require` path changes |
| `verifier/lean/soundness/` (589; `FlockSoundness`, requires ArkLib and level3 by path; `ASSUMPTIONS.md`, `DESIGN.md`, `assumptions/*.md`) | `security_proofs/flock/soundness/`, whole; the spec is extracted later as C-Flock's spec package | S3.1, P2; P8 (a `DESIGN.md` holding reasoning stays) | high for the move, low for the spec's timing | proofs: which subset is the trusted spec? Pins read 285 of its 561 modules, and the spec must come out before S3.3 touches the math. lean (4 Oct): `FlockSoundness` has its own root, so the move needs no rename; `Flock` and `Main` stay with the executable verifier as its spec until proofs extracts it. |
| `soundness/…/Audit.*` (38 files, not 27, per compute-accounting at `9400e83d5`; the sampled-proofs audit law) | moves with soundness under current names; its own area is an S3.3 job | S3.1 | high | answered (compute-accounting, 4 Oct): nothing to decide for the move; the Python cites the pins its §A 1 lists |
| `tests/lean/RandomnessVectors.lean`, `tests/fixtures/randomness_lean.json` | stays beside the verifier's tests | Conv: tests | high | none |

### 1b. Python (`backends/flock/python/verity_flock/`, 42 files)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `circuit.py` (990, the M0 `verity/flock-circuit` staging), `typed_statement.py`, `type_trace.py`, `circuit_types.py`, `layouts.py`, `derive.py`, `tables.py`, `sha512_circuit.py`, `lowering.py` | `verity/protocols/verification/flock/` (reference prover) + `benchmarks/flock/` (`circuit.main`, the input-set CLI) | P1, P6 | high | answered (proofs, 4 Oct): yes, the reference prover is the Python statement staging (`circuit.py`, `typed_statement.py`, `ir_lower.py` and `class_statement.py`) together with the Rust CPU `flock-circuit`. Still open (proofs): `circuit.lowering_for_set` reads numerical's `lowerings` registry and `main` reads its `InputSet`; can the prover take a `Lowering` object instead (section 6, item 2)? |
| `ir_lower.py` (1091; imported at module level by `circuit.py` and `typed_statement.py`) | `verity/…/flock/` after a split: `silu_table` (reads `registry.prims`) and `write_tables` (reads `kernels.fa2_relation` and `rms_relation`'s MUFU tables) take their tables as parameters | P6; P3 (device tables are catalog entries) | medium | proofs and circuits: should the MUFU and SiLU tables become catalog device entries that the prover's caller passes in? |
| `tail.py`, `tail_pieces.py` | `verity/…/flock/` after the same split (`_fold_constant_mufu` reads `prims`, `_gelu_table` reads `dense`) | P6, P3 | medium | as for `ir_lower.py` |
| `class_statement.py` (1442) | `verity/…/flock/` after two cuts: `_encoded` lifts out of `verity_vllm.pipeline.program_graph` into `verity.ir`, and `circuit_check.targets`' `load_registries()` and `definition(spec)` become the catalog loader | P6 | medium | answered (circuits, 4 Oct, with the captain's call): lift `_encoded` only. No `definition_digest` is lifted; four exist, with three meanings (`ir/annotations.py:60`, `query/word.py:221`, `pipeline/program_graph.py:650`, `torch_frontend.py:1332`). The catalog entry pins `verity.ir.codec.program_digest` of the one-call Program at given statics, as a new field. `class_statement`'s check of a capture graph's `definitions_index` moves with `program_graph` and keeps its v0 digest until graphs are re-recorded, so no recorded digest changes. circuits also found the second blocker: lazy imports of `circuit_check.targets` at `class_statement.py:421` and `partition_units.py:233`. |
| `partition_units.py` | `verity/…/flock/`, with the B1 Program passed by its caller; `_program` goes to `benchmarks/flock/` with `partition_units.main` and `class_statement`'s CLI | P6 | high | answered (proofs, 4 Oct): `_program` is only a CLI default, so it goes with the CLIs, and the prover takes its Program from the caller. It is also blocked by `circuit_check.targets` (`partition_units.py:233`; see `class_statement.py`). |
| `topp_word.py` (module-level imports of `registry.topp_keep_builder` and `topp_word_gates`) | `catalog/definitions/` beside `topp_words`, as that Definition's C-Flock lowering | P6, default 4 | medium | answered (proofs, 4 Oct): per-Definition lowerings follow top's default 4 to the catalog |
| `ir_sampling.py` (526; reads `registry.sampling`, `prims`, `sampling_rows`) | `experimental/flock/` | P9 | high | answered (proofs, 4 Oct): not current. Its only routes are the Gumbel template's `frame_lowering` and the `flock-ir-sampling` bin, and Lean refuses that statement id. It teaches the Gumbel lowering M0 hasn't ported. |
| `ir_frame.py` (349) | split: `BINDING_TAG` and `OWNER`, which `circuit.py` reads, go to `verity/…/flock/`; the frame-v3 statement goes to `experimental/flock/` | P9 | high | answered (proofs, 4 Oct): frame-v3 is superseded for new statements; M0 reuses only `BINDING_TAG` and `OWNER` for its domains, and `ir_frame.stage` goes to `experimental/flock/` |
| `templates/` (8; per-template lowerings, located by `verity_numerical.bench.lowerings.DIRECTORIES`, a hard-coded path) | `gemm_coordinate.py`'s `circuit_lowering` (the only one, the M0 path) goes to `catalog/` beside its Definition, after its lazy `instances.write_set` import is cut; the six `frame_lowering`-only modules go to `experimental/flock/` | P9, P3, default 4 | medium | answered (proofs, 4 Oct): per-Definition lowerings follow default 4 to the catalog. The six frame lowerings teach the attention, RoPE, RMSNorm, SiLU and Gumbel lowerings that M0 hasn't ported. `DIRECTORIES` must still follow the move. |
| `boolean_export.py` (1577; reads the registry, `query.word`, `program_graph` and numerical's bench) | `tools/` | P6 | high | answered (circuits, 4 Oct): an exporter, not an integration adapter; its docstring calls it "the website visualizer's dataset; a derived format, not a statement" |
| `fp.py`, `gf2.py`, `unit.py`, `unit_fp4.py` (7-line re-exports of `verity.ml.boolean`) | kept until `boolean_export`'s patching is replaced; then deleted, and callers import the modules under their new names | P8 (superseded tooling goes) | medium | answered (circuits, 4 Oct): not deletable yet. `BX._patch()` (used by `type_trace.trace_types`) patches through them, and `ir_lower`, `tail`, `tail_pieces`, `lowering`, `class_statement`, `partition_units`, `sha512_circuit`, `ir_sampling` and `circuit_types` import through them. proofs' archive list also names a `unit.py` and a `gf2.py`; see "Conflicts for the captain". |
| `unit_fp4_check.py` | follows `lowering` to `catalog/` (default 4), or `experimental/` if NVFP4 is ruled experimental (core map, question 6) | P9, default 4 | medium | answered (proofs, 4 Oct) |
| `bench.py` (imports `ligero`), `ir_bench.py`, `circuit_bench.py`, `register.py`, `key_class_sets.py`, `lean_rows.py`, `class_sweep.py`, `negatives.py` | `benchmarks/flock/` (`key_class_sets` too, an orphan CLI), except: `ir_bench.py` → `experimental/flock/` with the frame-v3 forms; `negatives.py` and `bench.py`'s pure path → `archive/flock/`; `lean_rows` beside its pin test | Layout, P9 | medium | answered (proofs, 4 Oct): `lean_rows` generates the Lean RoPE data and belongs with its pin test |
| `instances.py` (imports `ligero` auth, relations, `fp4.chain`), `backend.py` (`FLOCK_FRAME_V3_BLAKE3`, `FLOCK_BLOCK`, `FLOCK_VLLM_V1`) | `archive/flock/`, each with its record and last-good commit | P8, S4 | high | answered (proofs, 4 Oct): archive. *Ordering:* `templates/gemm_coordinate.py`'s lazy `instances.write_set` import is cut first. |

### 1c. Rust (`backends/flock/live/`, 33 files; the `flock-live` crate dropped into upstream Flock `b684b12`)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `circuit.rs`, `typed.rs`, `lookup.rs`, `ir_block.rs` (shared: `circuit`, `typed` and `lookup` use it), `ir_tail.rs`, `tables.rs`, `glue.rs`, `sha512_native.rs`, `zk_hooks.rs`, `zk_veil.rs`, `coin_tree.rs`, `coin_seed.rs`, `lib.rs` (`unit_draw`, `replay_round`, the coin server), `bin/flock-circuit.rs`, `Cargo.toml` | `verity/protocols/verification/flock/prover/` (the CPU reference prover) | P1, P5 (coins from `verity.randomness`) | high | answered (proofs, 4 Oct): yes. `check_build.sh` checks and tests the CPU features (`sha512`, `glue`, `seed-injection`) and never `gpu`, and the GPU must match the CPU byte for byte (`gpu_proofs_match_cpu`, `flock-circuit.rs:3761`). `coin_seed.rs` reimplements `verity.randomness.derive`, pinned by the `matches_verity_randomness` KAT, which P5 accepts; the ZK path draws OS coins (`coin_tree.rs`). Under the 4:19 PM ruling the prover's ZK layer stays in `verity/` and its arithmetic goes to `kernels/`; the first gap the plan names is `zk_veil::prove_inner`, which sends `Y` without checking the batched constraint. proofs draws that line through these files. |
| `session_verify.rs` (upstream's `verify_ligerito_extra`, call for call, timed; `flock-circuit serve`'s verifier) | `benchmarks/flock/` as a `flock-serve` bin; until the crate split it stays in the prover crate, with one line in its doc saying it is not the verifier of record | P1 (not the verifier of record), P5 | high | answered (proofs, 4 Oct): a benchmark, neither TCB nor assurance. Lean's `flock-verify` is the verifier of record, the one-stage audit takes Lean's verdict (`a0.py`), and upstream's Rust verifier is already on the assurance list through lean-agreement. |
| `gpu_circuit.rs` (feature `gpu`), `cuda/prove_circuit.cuh`, `cuda/sha512.cuh`, `cuda/ligerito_zk.cuh`, `cuda_circuit_patch.py`, `cuda_sha512_patch.py`, `cuda_live_patch.py`, `flock-{glue,sha512,zk,vtime}-b684b12.patch` | `verity/kernels/flock-cuda/` (one entry: the `gpu` feature minus `gpu.rs`; build key the crate's source hash, `--features gpu`, `b684b12` and the toolkit; the SASS/FTZ gate), minus any part proofs keeps in the ZK layer (4:19 PM ruling) | P5 | medium | answered (proofs, 4 Oct): the `gpu` feature is the entry. `gpu.rs` serves only the superseded chunk, pure and vLLM bins, so it leaves with them. It stays a feature for now; `gpu_circuit` becomes its own crate only after the superseded modules leave `lib.rs` and `prove_circuit.cuh` stops being included after `prove_chunk.cuh`. |
| `pure_block.rs`, `chunk.rs`, `ir_frame.rs`, `ir_sampling.rs`, `vllm_block.rs`, `gpu.rs` (serves only those); bins `flock-pure`, `flock-pure-gpu`, `flock-link`, `flock-gpu-link`, `flock-live`, `flock-ir-block`, `flock-ir-frame`, `flock-ir-sampling`, `flock-vllm-v1`; `cuda/prove_chunk.cuh`, `cuda/pure_sha256.cuh`, `cuda_chunk_patch.py`, `flock-{link,gpu-link}-b684b12.patch`, `backends/flock/verity_unit.rs` | form by form. To `archive/flock/`, each with its record and last-good commit: the pure and chunk forms (`pure_block`, `chunk`, `gpu.rs`, bins `flock-pure`, `flock-pure-gpu`, `flock-link`, `flock-gpu-link`, `flock-live`, `verity_unit.rs`, `pure_sha256.cuh`, the chunk and link patches) and the vLLM block (`vllm_block`, `flock-vllm-v1`). To `experimental/flock/`: the frame-v3 IR forms (`ir_frame.rs`, `ir_sampling.rs`, `flock-ir-frame`, `flock-ir-sampling`). `prove_chunk.cuh` stays with the kernel entry while `prove_circuit.cuh` includes it | P8, P9 | high | answered (proofs, 4 Oct): none is built by `check`, and Lean has no parser for any; their replays re-verify at their own commits and expect "refused: <form>" at main. `ir_block.rs` and `ir_tail.rs` stay with the prover; the answer doesn't place the `flock-ir-block` bin. *Ordering:* the first PR is the crate split (`lib.rs` declares every module, so each form gets a feature or leaves the module list before any file moves), and `tool.py`'s `flock_pure` (pod `20-pure.sh`) and `tools_registry` change in the same PR. |
| `check_build.sh` (check's flock-rust step) | stays beside the prover crate | P5 (CI builds every kernel) | high | answered (ci, 4 Oct): `ci.toml` names it by path, a one-line update when the crate moves |
| `live/PROTOCOL.md` | retires; its definitions go to the Lean spec, its vectors stay | Conv: PROTOCOL.md | medium | proofs |

### 1d. Pod scripts, prototypes and tool declarations

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `pod/00-setup-cpu.sh`, `cpu-slices.sh`, `50-preflight.sh`, `60-circuit.sh`, `61-circuit-cell.sh`, `70-class-sweep.sh`, `71-gemm-slowdown.sh`, `72-host-unit-eval.sh`, `74-gemm-hill.sh`, `76-read-gadget.sh`, `gemm_hill.py`, `gemm_slowdown.py`, `gemm_fp.py`, `read_gadget.py`, `gemm-coordinates*.defs.json` | `benchmarks/flock/`, except `50-preflight.sh` → `archive/flock/` | Layout | medium | answered (proofs, 4 Oct): `50-preflight.sh` builds `flock-vllm-v1` and has no callers |
| `pod/10-link.sh`, `20-*.sh`, `21-*.sh`, `22-*.sh`, `23-*.sh`, `30-*.sh`, `31-*.sh`, `33-*.sh`, `34-*.sh`, `40-vllm-v1.sh`, `unit.py`, `gf2.py`, `export_unit.py` | `archive/flock/` (pods `10`–`31` and `40`, `unit.py`, `gf2.py`, `export_unit.py`), each with its record and last-good commit; pods `33` and `34` → `experimental/flock/` with the frame-v3 IR forms; their replays expect "refused: <form>" at main | P8, P9 | high | answered (proofs, 4 Oct) |
| `arch_proto/` (10; architecture study prototypes, at `backends/flock/arch_proto/`, not under `pod/`) | `archive/flock/` | P8 | high | answered (proofs, 4 Oct): nothing references it |
| `tool.py` (`flock_pure`, `flock_class_sweep`) | `benchmarks/flock/tool.py` | P6 (it imports `research`, so never `verity/`) | high | none; `research`'s `tools_registry.REGISTRY` dotted path updates in the same PR |

### 1e. Verifier scripts and data (`backends/flock/verifier/`, excluding `lean/`)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `agree.py`, `ci.py`, `ci-bundle.sh`, `ci-pod.sh`, `fuzz.py`, `transcript_check.py`, `zk_mutants.py`, `selftest_records.py`, `redigest.py`, `upstream.json`, `upstream-build.sh`, `tool.py` (`flock_agreement`) | `tools/lean_agreement/` (the assurance TCB's "upstream's Rust verifier through lean-agreement") | P1 (assurance list), P6 | high | answered (proofs and ci, 4 Oct): yes. They import `verity` and `research`, never the reverse. It is a pure move that updates `research.store.kinds`' paths (`upstream-build.sh`, `upstream.json`) and `ci.toml`'s step in the same PR; it counts as a `backends/flock/` change, so it needs a `check --record` with lean-agreement. |
| `circuit_type_agree.py`, `cut_check_agree.py`, `layout_agree.py`, `qcall_agree.py`, `qword_agree.py`, `qword_program_agree.py`, `template_query_agree.py`, `unit_cut_agree.py`, `stratified_agree.py` (imports `verity_sampled_proofs.one_stage`) | `tools/lean_agreement/` | P1 (assurance list) | high | answered, as the row above. circuits (4 Oct): `qcall_agree.py:120` imports `verity.ml.scalar.I32Add` and needs the same toy as `test_qcall_vectors`, and `qword_program_agree.py` imports `test_qword_vectors` by path. |
| `vectors.json`, `lookup_v2_vectors.json`, `circuit-vectors*.patch`, `netlist-vectors.patch` | split: the two vectors files stay beside the verifier in `verity/`; the `circuit-vectors*` and `netlist-vectors` patches go to `tools/lean_agreement/` | Conv: PROTOCOL.md | high | answered (proofs, 4 Oct): a vectors file is the spec where two implementations agree. `lookup_v2_vectors.json` is written from Lean and read by Rust (`lookup.rs:355`) and Python (`test_derive.py`); the verifier's tests cite `vectors.json`'s set ids, and `check.py`'s lean-agreement reads it. A catalog entry is a parameter with an assumption, and these are neither. |
| `verifier/PROTOCOL.md` | retires except §16.15; its deviation list becomes data that `agree.py` reads | Conv: PROTOCOL.md | high | none |
| `verifier/README.md` | a short README stays with the verifier | Conv: PROTOCOL.md | high | none |

### 1f. Tests (`backends/flock/tests/`, 52 files)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `test_lean_*` (verifier), prover tests, bench tests, frozen-form tests | each moves beside its code: the verifier's and prover's tests to `verity/…/flock/tests/`, the rest to `benchmarks/`, `experimental/` or `archive/` | Conv: tests | medium | answered (ci, 4 Oct): `test_boundaries.py` scans `src/` only, not `tests/`, so these tests' imports of `verity_numerical.bench.templates` and input sets (`test_circuit.py`, `test_typed_statement.py`, `test_ir_lowering.py`, `test_lean_verifier.py`, …) are no violation today. ci keeps it that way for the moves and decides separately. |

## 2. `backends/numerical/` (`verity_numerical`, 211 files; owner: proofs for the frozen parts, circuits for templates)

The README already calls everything except the bench spine frozen.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `bench/templates.py` (the subcircuit template catalogue: a named Definition family with typed parameters) | `benchmarks/` (with numerical's bench) | Layout | medium | answered (circuits, 4 Oct): not catalog. It binds templates to input-set ports and VU-export relation names, which are benchmark vocabulary, and it lazily imports `kernels.rows`. Its `kernel_registry` import then points at `kernels/`. |
| `bench/input_sets.py`, `generate.py`, `lowerings.py` (hard-codes C-Flock's `templates/` path), `census.py` (the census reader) | `benchmarks/numerical/` | Layout | medium | proofs: C-Flock's `circuit.py` reads `lowerings` and `InputSet` (section 6, item 2). |
| `bench/contract.py`, `tables.py`, `views.py`, `drilldown.py`, `store_tables.py`, `summary.py`, `switch.py`, `ledger_to_store.py`, `frozen.py`, `placement.py` (imports `research.pods`), `cell.py`, `instances.py`, headline, decision tables, latency and plots, drivers `a_route_a`, `b_interactive`, `c_interactive` | `benchmarks/numerical/` (the table renderer and the frozen-ledger readers) | Layout, P8 | medium | answered (ci, 4 Oct): `research` shells out to `python -m verity_numerical.bench.tables` and `.drilldown` (`notes.py`, `store/parity.py`), and `store/vocab.py` mirrors `contract.PROOF_CLASSES`; both update in the move PR, and `move-check` (#1140) puts them on its allowlist of path-only files. |
| `reference/hawkeye_close` (used by `tools/tc_probe` and `bench.instances`) | `tools/tc_probe/` (a catalog builder's reference) | Layout (catalog builders are tools) | medium | circuits: or is it a hardware-model entry for `catalog/`? |
| `checker/` (WP2), `security/` (A-GKR and B-Ligero calculators), `gkr_export/`, `explore/`, `redteam/` | `archive/numerical/`, with the frozen backends that use them | S4, P8 | high | answered (proofs, 4 Oct): yes. `frozen.py` imports only `functools` and `Path` and fetches the frozen ledger from the store, and neither `tables.py` nor `store_tables.py` imports `security/` or `checker/`. Their other importers are all archive-bound (A-GKR, B-Ligero, VOLE, `gkr_export`, `anchor_a100`'s report, numerical's `explore/` and `redteam/`). |
| `backends/numerical/tests/` | splits with its code | Conv: tests | medium | none |

## 3. Frozen backends (owner: proofs)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `backends/gkr/` (A-GKR, 282) | `archive/gkr/` with its record | S4 | high | none |
| `backends/direct/` (B-Ligero, Python `ligero`, 305) | `archive/direct/` | S4 | high | first C-Flock's `instances.py` and `bench.py` and numerical's tests and drivers must stop importing `ligero` (archive is imported by nothing) |
| `backends/ligero-verify/` (129), `backends/ligerito-verify/` (88) (Rust) | `archive/ligero-verify/`, `archive/ligerito-verify/` | S4 | high | none |
| `backends/sp1/` (D-SP1, 101) | `archive/sp1/` | S4 | high | first `benchmarks/dot_product` and `benchmarks/ir_call` (out of this map's scope) must drop `verity_sp1` or move with it |
| `backends/vole/` (13) | `archive/vole/` | S4 | high | none |
| `backends/redteam/` (7, Rust forgery harnesses) | `archive/redteam/` | S4 | high | answered (proofs, 4 Oct): no; they attack A-GKR and B-Ligero only, and `check` runs none of them |
| `backends/shared/hash_gpu` | `benchmarks/commitments/`, or `verity/kernels/` as a commitment kernel if a result rests on it | P5, S4 | medium | circuits: `benchmarks/commitments/commit_cost_gpu.py` imports it, so it can't go to `archive/` |
| `backends/shared/anchor_a100` | `archive/shared/` | S4 | high | answered (proofs, 4 Oct): only its own report reads it, through `frozen.path` |
| `backends/README.md`, `backends/AGENTS.md` (campaign policy, frozen tables, trust levels) | `archive/README.md`; any rule still live folds into AGENTS.md | S4 | high | answered (proofs, 4 Oct): as the map says |

For every frozen backend, these must change in the same PR:

- the root `pyproject.toml` workspace members and the `torch-cpu` conflicts list;
- `research`'s `tools_registry` (`bench_vu`, `ligero_verify_batch`, `a_gpu_prove`, `bench_vu_fp8`, `bench_vu_fp4`);
- `research`'s `store/vocab.py` mentions.

## 4. `integrations/vllm/` (`verity_vllm`, 1523 files; owner: circuits)

Most of the integration stays; the plan places the frontend, capture, capture maps, κ profiles, the fold and Match there.
The Commit verdict stays too: circuits answered (4 Oct) that it is not a verifier role (section 7, circuits question 3).
Four areas leave or split:

- the registry's Definitions to `catalog/`;
- `program/kernels`' registry and row kernels to `verity/kernels/`;
- PoUW's device code to `verity/kernels/`;
- the commit layer's duplicates of core, which consolidate onto `verity.commitments.leaves`.

### 4a. Subpackages and data

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `engine/` (135), `acquire/` (42), `observe/` (38), `collectives/` (4), `linear/` (3), `predict/` (6), `ops/` (18, with `known_roots.json`), `config.py`, `target_family.py` | stays | P7 | high | none |
| `pipeline/` (80) | stays; `program_graph._encoded` lifts into `verity.ir`, and `program_graph`'s v0 digest stays with it until graphs are re-recorded (section 6, item 3) | P7, P6 | high | none |
| `pipeline/research_tools.py`, `pipeline/research.py`, `source_identity.py` | stays (research job declarations, `vllm.build` … `vllm.replay`) | P6 (allowed: an integration may import tools) | high | none |
| `query/` (18) | stays; `call_scope.py` and `cross_call.py` ("what `query.word` and `query.cross_call` share beyond core's `verity.ir.cut`") are candidates to move into `verity/primitives/circuits/` | P4 (queries over circuits are core) | medium | circuits: is the cross-Call partition invariant generic core query logic? |
| `correspondence/` (7) | stays | P7 | high | none |
| `properties/` (16, difftest harnesses) | stays; the plan's "one difftest harness" consolidation comes later | P7, S5 | high | none |
| `check/` (63): `match/` (20), `fold_compare.py`, `gates.py`, `poc_*`, `program_ops.py`, … | stays (the fold and Match are integration per circuits) | P7 | high | none |
| `check/verdict.py`, `commit_rules.py`, `result.py`, `replay/` (19: `sample.py`, `opening.py`, `stoch_recompute.py`, `pouw_circuit.py`, …) | stays, except the linkage from a run's public ends to its roots (`replay/linkage.py`'s `boundary_linkage` and `prescribed_input_linkage`, and `commit_tokens.py:191`'s `link_to_commit_account`, at `5049de02f`), which moves to `verity_sampled_proofs.one_stage`, restated over the registered roots, with vLLM supplying the positions | P7 ("they never talk to the verifier"); the 4:06 PM ruling (a replay is a diagnostic) | high | answered (circuits, 4 Oct): the VERDICT (`vllm-verdict/v1`) is the integration's row evidence, evaluated from v1's `commit_rules`, not a verifier role. proofs (at `5049de02f`, as the plan records under the 4:06 PM ruling): the commitment and opening checks verify reads against `vllm-v1`, the record the replay reads, not the `frame-v3-sha512` roots sampled proofs registers, so they stay with the replay, and the 12 codes stay as `check/`'s report vocabulary. The linkage recomputes nothing and is what an accepted sampled proof lacks to show the committed units are what was served. *Ordering:* proofs writes its rule after the move maps. |
| `commit/challenge.py` (every draw over committed values; legacy Fiat–Shamir forms, and new forms from a beacon or auditor key via `verity.randomness` and `verity_sampled_proofs.law`) | stays as an adapter: its non-legacy forms already draw through `verity.randomness.derive` and `verity_sampled_proofs.law`; the legacy Fiat–Shamir forms stay for replay until decision 42 | P7, P5 | medium | answered (circuits and compute-accounting, 4 Oct): the non-legacy forms are the verifier's draws, or public coins anyone recomputes (`derive` from a beacon round published after the run root was registered, or from an auditor key), and `replay_key` is sampled proofs' `vu_key`/`select_verification_units`. Those go with sampled proofs, so `law.py` becomes trusted code when `LEGACY` flips. The legacy forms are Fiat–Shamir over the prover's own commitment. *Ordering:* decision 42. |
| `commit/merkle.py`, `commit/hashing.py` (a second `vllm-v1` Merkle implementation, specified in core's `verity/commitments/vllm_v1/PROTOCOL.md`) | the duplicated pieces (`path_shape`, `tree_depth`, `verify_opening`, `MerkleTree`) consolidate onto `verity.commitments.leaves` (`LeafTree`, `levels`, `open_path`), bridged by vectors; `RangeOpening`, `fold_range` and `verify_range_opening` stay in vLLM until a verifier reads them, then go to core; a thin adapter stays | Layout, S5 (consolidation adds, bridges, supersedes) | high | answered (circuits, 4 Oct): `merkle.py` duplicates `leaves` (the `verity-vllm/leaf/v1` contract), not `vllm_v1`'s chunked framing, and `hashing.py` already imports H and the tags from `leaves` |
| `commit/hiding.py`, `commit/scheme.py` (thin adapters over `verity.commitments`) | stays | P7 | high | none |
| `commit/committer/` CUDA sources: `native_leafhash.cu`, `native_tree.cu`, `native_gather.cu`, `hidden_gpu_src/hidden_gpu_tree.cu`, `native_plans.h`, `native_collect.cpp` | stay for now; later the leaf-hash and tree kernels become a kernel entry (`verity/kernels/commitments-gpu/`, references `vllm_v1.pos_leaf` and `fold`); the collector stays | P5 | medium | answered (circuits, 4 Oct): no soundness result rests on them, because the verifier recomputes leaves from the opened bytes; only completeness does. The Python host side (`native_host`, `native_collect`, `leafhash`) imports `acquire`, `engine` and `pipeline`, so only the `.cu` files and a JIT shim could move. |
| `commit/` other modules: `binding`, `capture_map`, `identity`, `native_ranges`, `opened`, `padding_steps`, `partition`, `serving_rows`, `store_dump`, `hidden_stream` | stays | P7 | high | none |
| `protocol_options/interface.py`, `pous.py`, `pouw.py`, `pouw_circuit.py`, `sampled_proofs.py` | stays (protocol adapters) | P7 | high | none |
| `protocol_options/pouw_native.py` (`ncp-v2`'s committed values natively, from numpy and hashlib) | a numpy kernel entry in `verity/kernels/`, with `test_pouw_native.py`; the reference is the Program plus `circuit/reference.py` | P5 | medium-high | answered (compute-accounting, 4 Oct): yes, leaf for leaf (`pouw_device.first_difference` gates each build against it: `test_pouw_device.py:54`, `:136`, `:146`), but it is itself a fast path; `test_pouw_native.py` checks it against the Programs through `verity.evaluation.evaluate` and `circuit.reference` |
| `protocol_options/pouw_device.py`, `pouw_cuda/` (`ncp2*.cu`, `.cuh`, `ncp2_host.cpp`) | `verity/kernels/ncp-v2-cuda/` | P5; `ncp-v2` and `ncp-v2-shift24` are what `verity/`'s PoUW registry holds (4:06 PM ruling) | medium | answered (compute-accounting, 4 Oct): agreed, split first. `pouw_device.py:29-30` imports `pouw_circuit` (`unit_leaf`) and `pouw_native`, so the unit-leaf functions move with the kernel entry. |
| `protocol_options/pouw_pearl_c_{device,graphs,host,screen,triton,whole}.py` (Pearl-C on sm_120) | `verity/kernels/pearl-c-sm120/` for the kernel pipeline, the screen as an honest-prover kernel entry; the vLLM `quant_method.apply` hook stays | P5; under the 4:06 PM ruling Pearl-C's served verdict is a diagnostic until its tile check passes under sampled proofs | medium | answered (compute-accounting, 4 Oct): not for soundness. `screen` only pre-filters rows, and the band's rows are decided exactly by `pearl_c.live_row` (`screen.py:77-83`); the verifier's `PearlC.admissible` (`pearl_c.py:516-522`) recomputes the noise floor and `live_row` on every opened tile. A wrong screen changes the honest prover's records, not what the verifier accepts, and P5's "torch is a container only" applies to trusted code, which this is not. Still open (compute-accounting's decision 8, for the vLLM PoUW option's owner): `pouw_pearl_c_device.SCHEMES` and `scheme_of` go through `verity/`'s registry; the served `-h1` and `sm120-unpromoted` move to the experimental registry or stop being served; and is `-h1` still served on purpose, now that `pouw/pearl-c-hash-h1` is superseded? |
| `program/frontend/` (47: `rules/`, `rules/vllm_bindings/`, `torch_frontend`, `triton_capture`, `target_profile`, `registration`, `derive`, …) | stays (rules and vocabulary) | P7, P3 (circuits' "integration" list) | high | none |
| `program/lifting/` (3; promoted from veritor, single consumer) | stays | P7 | high | none |
| `program/boolean.py` (each Definition's Boolean version, and how far a Program is from bits) | stays (`lift`, `purity`, `dry_run`, `derived`: the Program-on-bits analysis, which imports `frontend.derive`, `torch_frontend` and `config`); only the `boolean_version()` lookup goes to the catalog's loader | P7, P3 | high | answered (circuits, 4 Oct): there is no link table. The Definition-to-Boolean link is each Boolean Definition's own `word` (`verity.ml.boolean.trace.word_of`), and `boolean_version()` just scans modules. |
| `program/compact.py`, `descriptor_equivalence.py`, `profile_descriptor.py`, `instances_form.py`, `replay.py`, `sampling_event.py`, `workload.py`, `model.py` | stays; `profile_descriptor.py` could become a tool | P7 | high | none |
| `program/dtypes.py` (numpy BF16↔f32) | stays; consolidate onto core's FP semantics later | S5 (one FP semantics) | medium | circuits |
| `program/registry/` (55 modules) | see 4b | P3, S5 | n/a | n/a |
| `program/registry/quarantine/` (6 subpackages, 39 `.py`) | `experimental/` (consolidate, don't delete); a deletion is first a `circuits/<slug>` superseded entry | P9, P8, S5 | medium | answered (circuits, 4 Oct): it is live. `gen_ov_sampling_patterns.py`, `gen_dense_softcap_patterns.py`, `gen_ln_patterns.py`, `gen_ov_moe_patterns.py`, `gen_dense_gemma2_patterns.py` and `generic.py:354/356` import it at module level, and gate G4 (`check/gates.py:716`, `observe/fold/resolver.py`, `resolve_log.py`) finds it by the `.quarantine.` path, which must still match after the move. The plan's "8 modules" was its superseded first draft; the tree's 6 subpackages and 39 files are the record. |
| `program/kernels/` (37) | see 4c | P5 | n/a | n/a |
| `data/` (16), `docs/` (34, `ref-prims` data), `manifests/` (8: capture maps, semantic profiles, `checkpoints.json`), `workloads/` (160, 6.8 MB), `fixtures/` (7) | stays (capture maps and κ profiles are integration) | P7, P3 | high | answered (circuits, 4 Oct): representative statics come from circuit-check's bindings, which are being split per Definition module, not from these files |
| `tests/` (615; `program/` 148) | splits with its code: registry tests go to `catalog/tests/`, kernel tests to `verity/kernels/`; each kernel's self-check against its Definition runs in the catalog's suite (revised default 3) | Conv: tests | medium | circuits |

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
| `targets` | Vocab (target-keyed bindings: which Definition variant a launch binds to) | stays in `integrations/vllm/` (circuits, 4 Oct) | none | high |
| `gemm_targets` | Vocab (GEMM target specialisations, read through `TargetProfile`) | stays in `integrations/vllm/` (circuits, 4 Oct) | `frontend.target_profile`* | high |
| `conformance` | Record (each Definition's status, `current`/`superseded`, with qualifications) | stays in `integrations/vllm/` with its B1/B0 data (`DIVERGENCES`, `INPUT_QUALIFICATIONS`, `NAN_CANONICALISATION`) and its CLI; the catalog index derives each entry's status and conformance kind from the Definition's `conformance=` (`ir/defs.py:78`) (circuits, 4 Oct) | `config` (only for the CLI's `option`) | high |
| `sampling_rows` | Twin (vectorised exact twins of `GumbelTopPTokenSelect_v1`) | `verity/kernels/`, because default 3 puts every kernel there (circuits, 4 Oct: not on the VERDICT's account) | `kernels.derived_rows` (module level) | medium |
| `serve3_reference` | Twin (vectorised reference evaluator of Serve@3's padding layer) | `verity/kernels/` (default 3, as `sampling_rows`) | none | medium |
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
- **The conformance record (1)** stays in the integration; the catalog index derives status from each Definition
  (circuits, 4 Oct).
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

Answered (circuits, 4 Oct): the classes are right, with three corrections.
- The row kernels need twin helpers and constants moved, not only ids: they import `fp8.np_f32_to_e4m3_sat`,
  `MIN_SCALE_BITS`, `dense.softcap_mul_bits` and `fp8_moe.check_act_st…`, and they `bind` Definitions.
- The quarantine goes to `experimental/`, not deletion.
- No registry module calls `register_kernel`, so moving the registry moves no kernel registration.

`lifted`'s split is the right order for freeing `moe_pad`: `moe_pad` imports `lifted` at module level, and nothing else
holds it. The 59 modules at the next tip and the six module-level external importers match an AST scan of origin/main.
The plan's "43" was its superseded first draft; the plan now cites the scan (59 modules, 53 importing nothing outside the
registry, `verity` and numpy).

### 4c. `program/kernels/` (37 files)

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `_jit.py`, `kernel_registry.py`, `__init__.py` | `verity/kernels/` (the registry), under a new import name | P5 | medium | answered (circuits, 4 Oct, and Daniel's 3:50 PM ruling): a rename plus an import-name change. `verity_vllm` is not a namespace package, so about 94 importer files change (86 in vLLM), and `program/kernels` takes its new import name when it moves. Section 6, item 11 is answered by revised default 3. |
| `cpp/` (`fa2_model.cpp`, `k16_chain.cpp`, `rms_triton_model.cpp`, `tc_model.cpp`) with `fa2_model.py`, `fa3_model.py`, `rms_triton_model.py`, `cpu_model.py`, `mma.py` (imports only `verity.ml.tc`) | `verity/kernels/` (C++ twins of vLLM's attention, GEMM and RMS kernels) | P5 | medium | moot: circuits answered (4 Oct) that the VERDICT is not a verifier role, and the 4:19 PM ruling puts every kernel outside `verity/` whether or not a result rests on it |
| `rows.py`, `ir_rows.py`, `dense_rows.py`, `act_rows.py`, `softcap_rows.py`, `value_rows.py`, `moe_router_rows.py`, `fp8_moe_rows.py`, `derived_rows.py` (numpy row kernels, `register_kernel`ed and `self_check`ed) | `verity/kernels/cpu/` | P5 | medium | answered (captain's revised default 3, and circuits, 4 Oct): they register by Definition id (`register_kernel` already takes an id string), each self-check runs in the catalog's suite, and the twin helpers and constants they import move with them. Under the 4:19 PM ruling they sit in the top-level `kernels/`, which P6 lets import `catalog/`. |
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
| `pods/nebius/` units and timers (`infra-pool-publish`, `n2-custody`, `vy-lean-cache-daily`: 3 `.service`, 3 `.timer`), `user-cpuset.conf`, `deploy.toml`, `dispatch-n1.env`, `weights.tsv` | units, timers, `user-cpuset.conf` and `dispatch-n1.env` → `infra/nebius/`, each with its `deploy.toml` `src` value rewritten in the same commit; `deploy.toml` and `weights.tsv` stay | Conv: node config | medium | answered (infra, 4 Oct): the nodes run `research` from a tool snapshot (`/workspace/research/tool/<sha>`, `remote.tool_tarball`) that carries only `tools/research/src/research/`, so the four files the package opens by a package-relative path stay beside their readers: `deploy.toml` (`deploy.MANIFEST`), `weights.tsv` (`prefetch.TSV`), `monitoring/lanes.tsv` (`alert_sink.host_context`) and `store.pod.toml` (`store.remote.POD_CONFIG`). `MANIFEST` needs no change: `install --ref` takes each `src` from that ref at the path the manifest names, so a ref from before a move fails with the file missing and installs nothing (fail closed); deploy from a commit after the move. Each move PR also re-greps `Path(__file__)` reads under `pods/`. infra would rather leave `pods/nebius/` whole but takes the default. See "Conflicts for the captain". |
| `pods/nebius/monitoring/` YAML and JSON (`alerting`, `exporter`, `grafana`, `nebius-overview.json`, `lanes.tsv`), `pods/nebius/sky/*.yaml`, `sky/jobs/*.yaml`, `kueue*.yaml`, `sky-config.yaml` | `infra/nebius/`, with their `deploy.toml` `src` values, except `monitoring/lanes.tsv`, which stays | Conv: node config | medium | answered (infra, 4 Oct): nothing in the package opens them by path; `research deploy` reads them from a git ref |
| `pods/nebius/` scripts (28 `.sh`, 21 `.py`: `dispatch`, `fill_runner`, `pool_n1`, `n1_lease`, `node_ops`, `lean_sandbox`, `vm_setup.sh`, …), `monitoring/*.py`, `sky/*.sh` and `*.py`, `pods/sh/` (`lease.sh`, `gpu_lease.sh`, `pod_guard.sh`) | stays in `tools/research/` (code) | Conv: node config (data only) | high | answered (infra, 4 Oct): code. They ship in the snapshot, `deploy.toml` installs them from a git ref, and tests import them. The pinned `research` on the nodes never reads `infra/` from a checkout; node scripts that read `$SRC/<path>` read the tree their own run shipped. |
| `console/` (`verity_console.py` and friends) | stays (its units are already in `infra/nebius/`) | Conv: node config | high | none |
| `control/` (control-pod scripts) | stays; `steward-run.sh` goes later | Layout | high | answered (infra, 4 Oct): `steward-run.sh` belongs to the retired resource steward and goes when the steward's old project writes its final note (infra checks at 23:30Z) |
| `store.pod.toml` | stays | Conv: node config | high | answered (infra, 4 Oct): it is `POD_CONFIG`, read at `parents[3]` from a checkout |
| `store/tools_registry.py` (`REGISTRY`: tool name → dotted repo path, for example `backends.flock.tool:FLOCK_PURE`) | stays, and every move PR updates its entries | S5 (each move updates its paths) | high | answered (ci, 4 Oct): agreed; `move-check` (#1140) adds it to its allowlist of path-only files |

### 5b. Other tools

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `tools/cluster/src/` (stdlib, imports neither `verity` nor `research`) | stays | Layout | high | none |
| `tools/cluster/descriptions/nebius.toml`, `kinds/*.toml` | stays | Conv: node config | high | answered (infra, 4 Oct): `cli.py` defaults to `parents[2]/descriptions`, and `vy-cluster-agent.service` names `@SOURCE@/tools/cluster/descriptions/nebius.toml`; moving them changes both for no gain |
| `tools/cluster/vy-cluster-agent.service`, `shadow-node2.sh` | `infra/nebius/`, with their `deploy.toml` entries | Conv: node config | medium | answered (infra, 4 Oct): they may move |
| `tools/check/` (`check.py`, `suites.py`, `slot.py`, `lean_slot.py`, `lean_audit.py`, `verdicts.py`, `guard/`, `train.sh`, `post_train.py`, …) | stays (check's gates are on the assurance list) | P1 (assurance list) | high | none |
| `tools/check/ci.toml`, `queue.toml`, `lean-deps.json` | stays (check's own data) | P1 | medium | ci |
| `tools/check/pod_setup.sh` | stays in `tools/check/` | Conv: node config | high | answered (ci, 4 Oct) |
| `tools/lean/` (`audit.py`, `Facts.lean`, `Replay.lean`, `Upstream.lean`, `sandbox.sh`, `setup.sh`, `cache.py`, `merge.py`, `upstream.py`, `run_daily.py`, `tool.py`) | stays (the validator is on the assurance list) | P1 | high | none |
| `tools/circuit_check/src/circuit_check/` code (`checks.py`, `cli.py`, `cache.py`, `vectors.py`, `known.py`) | stays | Layout | high | none |
| `tools/circuit_check/…/targets.py` (684 lines of per-Definition bindings) | split per Definition module first (S5). A binding that names only a Definition, its statics and its pins moves beside the Definition in `catalog/`; anything needing `frontend.rules`, `target_profile`, `program.boolean`, `kernels`, `query`, `verity_pouw.circuit.*` or `verity_numerical.bench` stays in the tool | S5, P6 | medium | circuits: a binding in `catalog/` may import only `catalog/` and `verity/` |
| `tools/circuit_check/…/pins.json` (definitions 224, pieces 100, units 8) | `catalog/definitions/`, split per Definition module | P3 (circuits' catalog list), S5 | medium | circuits |
| `tools/agent-guard/` | stays | Layout | high | none |
| `tools/tc_probe/` (`tc_probe.py`, `trust.py`, `canary.py`, `instances_hw.py`, `mma_tiles.cu`, `wgmma_tiles.cu`, `tiles_common.cuh`, `tool.py`) | stays (a catalog builder) | P3, Layout | high | none; it imports `verity_numerical.bench` and `reference`, which become `benchmarks/` and `tools/` |
| `tools/tc_probe_fp4/` probes (`probe.py`, `cast.py`, `k32.py`, `sparse.py`, `recheck.py`, `meta_rule.py`, `t1_merged.py`, `model5.py`, `stage0_sm100.py`, `stage0_sm120.py`, `*.cu`, `rows_fp4.cuh`, `nvf4_step.cuh`, `fp4_emulation_1ad1aaa2.py`, `tool.py`) | stays (a catalog builder) | P3, Layout | medium | none |
| `tools/tc_probe_fp4/lean_vectors.py` | stays (a builder), and its output becomes `catalog/vectors/` | P3 | medium | none |
| `tools/tc_probe_fp4/` PoUW experiments (`f1_rates.py`, `f2_strassen.{py,cu}`, `f3_lut.{py,cu}`, `w1_price.{py,cu}`) | stays in `tools/tc_probe_fp4/` | P3 (capture is a tool) | low-medium | answered (compute-accounting, 4 Oct): measurement tools, not schemes. F1 rates, F2 Strassen and F3 LUT-GEMM search for attacker shortcuts on NVFP4, and W1 measures prices. Core's `pyproject.toml:30` lists `tools/tc_probe_fp4/probe.py` as a test input, `ml/tc/models.py:810` and `:875` cite its runs, and `tools_registry` names `tc_probe_fp4` and `tc_price_fp4`. No approach is registered for F1–F3 or W1, so live or killed is unconfirmed; their consumer, Pearl-C4, is parked. |
| `tools/native_peak/` (`measure.py`, `mma_peak_fp4.cu`, `tool.py`) | stays (a catalog builder of device peak numbers) | P3 | high | none |

### 5c. `infra/`, `.agents/` and the root

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `infra/nebius/verity-console.service`, `verity-console.timer` | stays | Conv: node config | high | none |
| `.agents/` (skills, `using-slack/registry.json`) | stays (the plan keeps `registry.json` in place); skills update with each move | S5 | high | none |
| `pyproject.toml` (workspace members), `uv.lock` | stays; members change with each move | Conv: packaging | high | answered (ci, 4 Oct): the 8 `tools/` distributions stay separate (section 7, ci question 1) |
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

   Answered (proofs, 4 Oct): `ir_sampling` goes to `experimental/flock/` and `partition_units._program` to
   `benchmarks/flock/`, and the per-Definition lowerings (`topp_word`, `gemm_coordinate`'s `circuit_lowering`) go to the
   catalog under default 4. Still open (proofs and circuits): the MUFU, SiLU and GELU tables as catalog device entries.
2. **C-Flock's prover would import benchmarks.** `circuit.lowering_for_set` reads `verity_numerical.bench.lowerings`, and
   `circuit.main` reads `bench.input_sets.InputSet`. `lean_rows`, `register`, `key_class_sets`, `ir_bench` and
   `circuit_bench` read `bench` as well.

   *Split first:* `main` and every input-set path move to `benchmarks/flock/`, and the prover takes a `Lowering`.
   Numerical's `lowerings.DIRECTORIES` hard-codes C-Flock's `templates/` path. Still open (proofs); circuits (4 Oct) puts
   `bench/templates.py` in `benchmarks/` as well.
3. **C-Flock's prover would import the integration's pipeline.** `class_statement.distinct_calls` imports
   `program_graph._encoded` and `definition_digest`.

   *Split first (answered, circuits with the captain's call, 4 Oct):* lift `_encoded` only. No `definition_digest` is
   lifted: the catalog entry pins `verity.ir.codec.program_digest` of the one-call Program at given statics, and
   `class_statement`'s `definitions_index` check moves with `program_graph`, keeping its v0 digest until graphs are
   re-recorded. circuits found a second blocker: `class_statement.py:421` and `partition_units.py:233` import
   `circuit_check.targets` lazily, so `load_registries()` and `definition(spec)` must become the catalog loader first.
4. **Two kinds of C-Flock code must stay out of `verity/`.**
   - `boolean_export`, which imports the registry, `query.word`, `program_graph` and numerical's bench.
   - `tool.py` and `verifier/tool.py`, which import `research`.

   `instances.py` and `bench.py`'s flock-pure path import `ligero`. Since `archive/` is imported by nothing, those go to
   `archive/` too, or drop `ligero`.

   Answered (4 Oct): `boolean_export` goes to `tools/` (circuits), and `instances.py` and `bench.py`'s pure path go to
   `archive/flock/` (proofs).
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
   Definition module (S5). `conformance` now stays in the integration (circuits, 4 Oct), so its `config` import is no
   longer a catalog edge.
6. **The registry in `catalog/` would import `protocols/` until PoUW moves.** `pouw_rows` imports
   `verity_pouw.circuit.ncp2`. That becomes `verity/` after PoUW's Python move, so PoUW's move lands before this module's;
   the plan's order already puts PoUW first. `ncp2` stays in `verity/` for now, pending a decision on whether parametric
   builders the verifier runs are trusted code (captain's call).
7. **`catalog/definitions/templates.py` would import the integration's kernel registry.** Numerical's `bench/templates.py`
   imports `verity_vllm.program.kernels.kernel_registry`.

   *Split first:* point it at `verity/kernels/`. Its other registry imports become catalog-internal once the registry moves.

   Moot (circuits, 4 Oct): `bench/templates.py` goes to `benchmarks/`, not the catalog; its `kernel_registry` import then
   points at `kernels/`.
8. **`program/boolean.py` in `catalog/` would import the frontend.** It imports `frontend.derive`, `torch_frontend` and
   `config`.

   Moot (circuits, 4 Oct): there is no link table. Only `boolean_version()`'s lookup goes to the catalog's loader, and
   nothing that imports the frontend moves.
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

    Under the 4:19 PM ruling these go to the top-level `kernels/`, not `verity/`. The plan doesn't say whether `kernels/`
    may import `integrations/`, so the splits stand. `pouw_device`'s split is agreed (compute-accounting, 4 Oct).
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

    Answered by revised default 3 (captain, 4 Oct): kernels register by Definition id, each kernel's self-check against
    its Definition runs in the catalog's suite, and core's tests import no catalog module. `register_kernel` already
    takes an id string, so this needs no new API (circuits). The row kernels' twin helpers and constants move with them
    (circuits), and C-Flock's Definition-specific lowerings go to the catalog under default 4 (proofs). Since the 4:19 PM
    ruling the kernels sit in the top-level `kernels/`, which P6 lets import `catalog/`; registration by id still keeps
    `verity/` free of catalog imports.
12. **Live benchmarks would import `archive/`.**
    - `benchmarks/commitments/commit_cost_gpu.py` imports `backends/shared/hash_gpu`.
    - `benchmarks/dot_product` and `benchmarks/ir_call` import `verity_sp1`.

    These aren't `verity/` or `catalog/` imports, but they break "nothing imports `archive/`".

    *Split first:* `hash_gpu` leaves `shared/` before `shared/` is archived, and the two benchmarks move to `archive/`
    with SP1 or drop it.

## 7. Open questions by owner

**proofs (C-Flock)**

1. Superseded-form parsers: answered (proofs, 4 Oct): after fail-closed, only PR #83's four tags reach `Blake3Row`,
   `RowLeaf`, `Stmt.setup`'s non-hm96 branch, `Comp`'s `D_b3`, `Public`'s SHA-256 roots and four `Tags` records; frozen
   copies go to `security_proofs/flock/superseded/`, and the refusal stays as a name-to-reason list (section 1a).
2. The reference prover: answered (proofs, 4 Oct): yes, the Python staging with `class_statement.py` and the Rust CPU
   `flock-circuit`; the `gpu` feature minus `gpu.rs` is the `flock-cuda` entry, and it becomes its own crate only after
   the superseded modules leave `lib.rs` (section 1c).
3. `session_verify.rs`: answered (proofs, 4 Oct): a benchmark, to `benchmarks/flock/` as a `flock-serve` bin.
4. The superseded statements: answered (proofs, 4 Oct): the pure, chunk and vLLM-block forms to `archive/flock/`, the
   frame-v3 IR forms to `experimental/flock/`, form by form (sections 1b to 1d).
5. Agreement scripts and vectors: answered (proofs and ci, 4 Oct): the scripts, `upstream.json`, `upstream-build.sh` and
   the vectors patches to `tools/lean_agreement/`; `vectors.json` and `lookup_v2_vectors.json` stay beside the verifier.
6. numerical's `security/` and `checker/`: answered (proofs, 4 Oct): `archive/numerical/`; the frozen rows render only
   from the store.

Still open for proofs: whether the prover can take a `Lowering` object (section 6, item 2); the MUFU, SiLU and GELU
tables as catalog device entries (with circuits); the subset of `soundness/` that is the trusted spec; `live/PROTOCOL.md`'s
retirement; and where the ZK layer ends in C-Flock's code (the 4:19 PM ruling).

**circuits (vLLM registry, Definitions, circuit_check)**

1. Kernels of catalog Definitions: answered by revised default 3 (section 6, item 11).
2. The registry classes: answered (circuits, 4 Oct): agreed, with three corrections (section 4b).
3. The Commit VERDICT: answered (circuits, 4 Oct): not a verifier role; `challenge.py` is an adapter.
4. Conformance and targets: answered (circuits, 4 Oct): the index derives status from each Definition's `conformance`,
   and `targets` and `gemm_targets` are integration vocabulary.
5. `commit/merkle.py` and the committer kernels: answered (circuits, 4 Oct): consolidate onto `verity.commitments.leaves`;
   the `.cu` kernels stay for now and become a kernel entry later.
6. `bench/templates.py`, `program/boolean.py`, `boolean_export.py`: answered (circuits, 4 Oct): `benchmarks/`, no link
   table, and `tools/`.
7. The counts: answered (circuits, 4 Oct): the AST scan is the record (59 modules; 39 quarantine files in 6
   subpackages); the plan's 43 was its superseded first draft.

Still open for circuits: `reference/hawkeye_close` (section 2); `backends/shared/hash_gpu` (section 3); `query/call_scope`
and `cross_call` as core query logic; `twins.py`, `libdevice_sampling` and `kernel_zoo` (section 4c); `mla.py`; and
the shims' replacement with `boolean_export`'s patching.

**compute-accounting**

Answered (4 Oct): `challenge.py`'s draws, `pouw_native`, `pouw_device`'s split, the Pearl-C screen, `Audit.*`'s count
and `tc_probe_fp4`'s experiments (sections 1a, 4a and 5b). Still open, for the vLLM PoUW option's owner: its decision 8
(`pouw_pearl_c_device.SCHEMES` through `verity/`'s registry, and the served `-h1` and `sm120-unpromoted`).

**infra (tools/research, pods, cluster)**

1. Node-side scripts: answered (infra, 4 Oct): code; they stay in `tools/research/`.
2. `MANIFEST` and `manifest_at(ref)`: answered (infra, 4 Oct): no change, because `deploy.toml` stays; `install --ref`
   fails closed on a ref from before a move, and the pinned `research` never reads `infra/` from a checkout.
3. `tools/cluster`'s `descriptions/` and `kinds/`: answered (infra, 4 Oct): they stay.
4. `store.pod.toml` and `control/`: answered (infra, 4 Oct): both stay; `steward-run.sh` goes later.

**ci (tools/check)**

1. Distributions: answered (ci, 4 Oct): keep the 8; the convention now reads "`tools/` holds one distribution per tool".
2. What each move PR updates: answered (ci, 4 Oct): this map's list, plus `[tool.verity.tests] inputs`,
   `tools/check/ci.toml` and `tests/test_lean_packages.py`; `move-check` (#1140) puts the path-only files on its
   allowlist.
3. `check_build.sh`, `pod_setup.sh` and the boundary test: answered (ci, 4 Oct): both scripts stay, and
   `test_boundaries.py` keeps scanning `src/` only during the moves.

**lean (tools/lean)**

1. `FlockProofs`: answered (lean and proofs, 4 Oct): it joins `security_proofs/flock/`.
2. C-Flock's three packages: answered (lean, 4 Oct): yes. `level3` (`FlockLevel3`) and `soundness` (`FlockSoundness`)
   have roots of their own and move whole with no rename; `FlockProofs`' root moves too; `Flock` and `Main` stay with
   the executable verifier as its spec until proofs extracts it.

## Conflicts for the captain

1. **`deploy.toml` and the plan's node-configuration convention.** The plan's Conventions say "The systemd units,
   cpusets and `deploy.toml` leave the research package for `infra/`". infra (4 Oct) answers that `deploy.toml`,
   `weights.tsv`, `monitoring/lanes.tsv` and `store.pod.toml` must stay, because the nodes' tool snapshot carries only
   `tools/research/src/research/`, and that it would rather leave `pods/nebius/` whole, though it takes the default for
   the units. This map follows infra's evidence (section 5a); the plan's line needs the captain's edit.
2. **`unit.py` and `gf2.py`: two files of each name.** proofs' archive list names Python `unit.py`, `gf2.py` and
   `export_unit.py`. At `5049de02f`, `unit.py` and `gf2.py` exist both as `backends/flock/pod/` scripts and as the
   `python/verity_flock/` shims that circuits keeps while `BX._patch()` patches through them. This map reads proofs' list
   as the `pod/` files (section 1d), which leaves no conflict, but proofs should confirm.
