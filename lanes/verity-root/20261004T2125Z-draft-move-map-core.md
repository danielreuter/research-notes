---
id: 20261004T2125Z-draft-move-map-core
campaign: verity
lane: verity-root
kind: draft
status: open
repo: danielreuter/verity
origin: worker of verity-top's repository-layout agent (bc-d6f8b221); for owners (proofs, circuits, compute-accounting) to correct
---

# Move map: core (`packages/verity/`), `census/`, `fixtures/` and the root `tests/`

This is a draft for owners to correct. It gives every module of the core distribution a destination in the layout of
`note:20261004T2058Z-draft-repo-organization-principles` (version 9), the principle that decides it, how sure the
decision is, who imports the module from outside core, and the question for its owner where the decision isn't
settled. Nothing has moved. The owners' answers of 4 Oct (proofs, circuits, compute-accounting, infra, memory-accounting,
and ci, lean and comms in the kickoff thread 1791150333.889129) and the captain's calls on them are folded into the rows;
a resolved question reads "answered (OWNER, 4 Oct): …", and where two owners disagree the row is listed under
"Conflicts for the captain" at the end.

Python import names follow the new directories (Daniel, 4 Oct 3:50 PM PDT): `verity/primitives/silicon/` imports as
`verity.primitives.silicon`, and the move script carries a module map beside its path map.

## How this was made

- The import graph is an AST walk over every tracked `.py` file (`git ls-files`). It records top-level and
  function-level (lazy) imports, and resolves `from verity.x import y` to the submodule `y` when one exists. Core has
  107 Python modules under `packages/verity/src/verity/`; paths in the tables are relative to `packages/verity/src/`.
- The "Imported by" column names the other top-level areas that import the module. Core's own modules and tests are
  left out of it; the core-internal edges that matter are in "Forbidden-import splits". A `*` marks an area whose code
  goes to `verity/` (C-Flock, PoUW, PoUS, the warden, sampled proofs), and a `†` marks one going to `archive/` (SP1,
  B-Ligero, A-GKR, VOLE). "tests only:" means only that area's tests import it. numerical is unmarked: the backend is
  frozen, but its bench spine is live (C-Flock and the table renderers use it).
- The Lean part comes from `packages/verity/lean/lean-audit.json` (its `roots`, `layers`, `guarantees` and `reads`) and
  the `import` lines of every `.lean` file in the repository.
- High confidence means the plan or a ruling names the destination and the imports agree. Medium means the principle
  decides it, but an owner could reasonably pick a sibling directory or a different split. Low means the principles
  pull different ways, or the module's status is the owner's call.
- Destinations are directories in the plan's layout. Several names below are this map's proposals, which the layout
  doesn't have yet: `verity/primitives/silicon/` (Daniel renamed the map's `verity/primitives/fp/`),
  `verity/primitives/circuits/boolean/`, `verity/primitives/commitments/gates/`, and the catalog's subdirectories
  (`definitions/`, `hardware/tc/`, `targets/`, `library/`, `annotations/`, `census/`, `input_sets/`). Owners should
  rename them freely.
- The map gives directories, and since Daniel's 3:50 PM PDT ruling each directory is also the import name: `verity.ir`
  becomes `verity.primitives.circuits`. No digest, Definition id or Lean pin contains a module path, so a rename costs
  edits and one cold `check`. The move script's module map rewrites imports, `import_module` strings, `module:attr`
  specs and module-keyed test data; Lean comments that name Python modules are left to a later Lean PR, so a Python move
  doesn't rerun the Lean audit. Where a row below names a module by its current import name (`verity.ir`, `verity.ml`),
  read it as the module now at that path.
- The counts in "Summary" are the draft's, taken before the 4 Oct answers, and were not recounted.

## Summary

- The 107 Python modules go to these destinations: verity: 53, catalog: 17, archive: 16, split: 8, tests: 5, dissolve: 3, experimental: 2, retire: 2, integrations: 1. A "split" module has one part for `verity/` and
  another for `catalog/`, and each split is listed under "Forbidden-import splits". "dissolve" is an empty package
  `__init__` (`verity.ml`, `verity.ml.boolean`, `verity.proofs`) and "retire" is a re-export shim.
- Confidence for the Python modules: 41 high, 59 medium and 7 low. The low ones are `verity.commitments.multiproof`, `verity.ir.annotations`, `verity.ml.boolean.fp4`, `verity.ml.boolean.universal`, `verity.ml.library`, `verity.ml.tc.relation`, `verity.proofs.query`.
- Lean: of 64 files, 16 spec modules and the root umbrella `Verity.lean` stay beside the code. The 43
  `Verity.SecurityProofs*` modules go to `security_proofs/core/`, and so do the four unread spec modules
  (`Protocol.Boolean`, `Fp32`, `Prims`, `Scalar`; lean and proofs, 4 Oct). Declaration names are kept, while the proof
  modules move under a root of their own (lean, verity#1144). The lock's `guarantees` and `reads` stay byte-identical.
- `census/` (13 files) goes to `catalog/census/`. `fixtures/` has 9 entries: four go to the catalog, four to the
  archive, and `artifacts.json` stays at the root. Core's 8 test directories follow their modules, and 4 of the 10
  root tests leave `tests/` for `benchmarks/pous/`.

## The map, by package

### `verity` top level

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/__init__.py` | `verity/__init__` (package root) | P1 | high | — |  |
| `verity/errors.py` | `verity/errors` | P1: the shared error classes every role raises | high | B-Ligero†, PoUW\*, SP1†, bench/ir_call, numerical, vLLM |  |
| `verity/claims/__init__.py` | `verity/claims` | P10, P1 | high | PoUS\*, numerical | answered (proofs, 4 Oct): it stays in `verity/claims`. Claim ids are vocabulary that results and code cite, not parameters a verifier chooses, and they enter no digest; PoUS and the docs site import them. comms takes the default. |

`proofs.codes`, the verdict codes beside `errors`, is listed with `proofs` below.

### `verity.ir` to `verity/primitives/circuits/`

Principle 4 makes the circuit format, its digests, evaluation and the queries over circuits the core primitive.
C-Flock, PoUW and sampled proofs, all bound for `verity/`, import `codec`, `defs`, `types`, `refs`, `program`,
`partition`, `partition_object` and `cut`. circuits settled the two uncertain ones on 4 Oct: `liveness` stays, and
`annotations` leaves for `tools/circuit_check/`, with its JSON going to the catalog.

The catalog's descriptor digest is `verity.ir.codec.program_digest` of the one-call Program at given statics, built by
the wrapper that `program_graph._encoded` builds today, lifted into this package (captain's call on circuits' answer,
4 Oct). None of the four existing `definition_digest` functions (`ir/annotations.py`, vLLM's `query/word.py`,
`pipeline/program_graph.py`, `torch_frontend.py`) is lifted.

`const` (the `Const<w>` family) joins this package from `ml.prims`, beside `boolean.constant` (circuits, 4 Oct; see the
`ml.prims` row).

`ir/PROTOCOL.md` retires under the Conventions: `tests/ir/format_vectors.json` already pins its rules, and its
definitions belong in the Lean spec (`Verity.Protocol.Circuit`). The six vectors files under `tests/ir/` stay beside
the reference as the spec where two implementations must agree. C-Flock's verifier agreement scripts (`qword_agree.py`,
`qcall_agree.py`, `qword_program_agree.py`, `template_query_agree.py`) read four of them, so those scripts' paths
must follow the move.

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/ir/__init__.py` | `verity/primitives/circuits/__init__` | P4: the format, its digests and the Boolean basis | high | vLLM ; tests only: PoUW\* |  |
| `verity/ir/annotations.py` | the validator to `tools/circuit_check/`; the annotation JSON files (`ml/annotations.json`, the vLLM registry's `annotations.json`) to the catalog beside their Definitions | P3: names and descriptions keyed by descriptor ids, never inside a digest, so not TCB | medium | tests only: circuit_check | answered (circuits, 4 Oct): circuit_check is its main user (`tools/circuit_check/tests/test_annotation_files.py`). Its `definition_digest` (line 60) is not the catalog digest. |
| `verity/ir/boolean.py` | `verity/primitives/circuits/boolean` | P4: the format, its digests and the Boolean basis | high | PoUW\*, circuit_check, vLLM ; tests only: C-Flock\* |  |
| `verity/ir/boundary.py` | `verity/primitives/circuits/boundary` | P4: queries over circuits (partitions, cuts, units) | high | vLLM |  |
| `verity/ir/codec.py` | `verity/primitives/circuits/codec` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, PoUW\*, bench/one_stage, bench/private_circuit, numerical, sampled-proofs\*, vLLM ; tests only: circuit_check |  |
| `verity/ir/constants.py` | `verity/primitives/circuits/constants` | P4: the format, its digests and the Boolean basis | high | vLLM ; tests only: circuit_check |  |
| `verity/ir/cut.py` | `verity/primitives/circuits/cut` | P4: queries over circuits (partitions, cuts, units) | high | C-Flock\*, PoUW\*, circuit_check, vLLM |  |
| `verity/ir/defs.py` | `verity/primitives/circuits/defs` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, PoUW\*, SP1†, bench/ir_call, bench/private_circuit, circuit_check, numerical, sampled-proofs\*, vLLM |  |
| `verity/ir/evaluate.py` | `verity/primitives/circuits/evaluate` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, SP1†, vLLM |  |
| `verity/ir/intervals.py` | `verity/primitives/circuits/intervals` | P4: queries over circuits (partitions, cuts, units) | high | — |  |
| `verity/ir/layout.py` | `verity/primitives/circuits/layout` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, sampled-proofs\*, vLLM |  |
| `verity/ir/liveness.py` | `verity/primitives/circuits/liveness` | P4: a generic query over circuits, stdlib, imports only `ir` | high | circuit_check, vLLM | answered (circuits, 4 Oct): it stays. The frontend (`frontend/derive.py`, `torch_frontend.py`), `program/boolean.py:352` and `circuit_check/checks.py:505` use it. |
| `verity/ir/partition.py` | `verity/primitives/circuits/partition` | P4: queries over circuits (partitions, cuts, units) | high | C-Flock\*, PoUW\*, sampled-proofs\*, vLLM ; tests only: circuit_check |  |
| `verity/ir/partition_object.py` | `verity/primitives/circuits/partition_object` | P4: queries over circuits (partitions, cuts, units) | high | C-Flock\*, PoUW\*, bench/private_circuit, sampled-proofs\*, vLLM ; tests only: circuit_check |  |
| `verity/ir/parts.py` | `verity/primitives/circuits/parts` | P4: queries over circuits (partitions, cuts, units) | high | vLLM |  |
| `verity/ir/program.py` | `verity/primitives/circuits/program` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, PoUW\*, bench/one_stage, bench/private_circuit, numerical, sampled-proofs\*, vLLM ; tests only: circuit_check |  |
| `verity/ir/query.py` | `verity/primitives/circuits/query` | P4: queries over circuits (partitions, cuts, units) | high | tests only: sampled-proofs\*, vLLM |  |
| `verity/ir/query_ast.py` | `verity/primitives/circuits/query_ast` | P4: queries over circuits (partitions, cuts, units) | high | vLLM |  |
| `verity/ir/query_codec.py` | `verity/primitives/circuits/query_codec` | P4: queries over circuits (partitions, cuts, units) | high | vLLM |  |
| `verity/ir/refs.py` | `verity/primitives/circuits/refs` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, PoUW\*, bench/private_circuit, sampled-proofs\*, vLLM ; tests only: SP1†, circuit_check |  |
| `verity/ir/types.py` | `verity/primitives/circuits/types` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, PoUW\*, SP1†, bench/private_circuit, circuit_check, sampled-proofs\*, vLLM |  |
| `verity/ir/units.py` | `verity/primitives/circuits/units` | P4: queries over circuits (partitions, cuts, units) | high | C-Flock\* |  |

### `verity.evaluation` and `verity.randomness`

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/evaluation/__init__.py` | `verity/primitives/circuits/evaluation/__init__` | P4 (evaluation), P5 (the reference every kernel is bit-exact with) | high | bench/private_circuit, circuit_check, numerical, vLLM ; tests only: C-Flock\*, PoUW\* |  |
| `verity/evaluation/batch.py` | `verity/primitives/circuits/evaluation/batch` (registry part: `verity/kernels/registry`) | P5 | medium | circuit_check, vLLM | compute-accounting answered (4 Oct) that PoUW has no stake: no PoUW code calls `register_kernel`, and its only caller outside core is vLLM's `kernel_registry.py`. circuits noted that `register_kernel` already takes a Definition id string, so the default (kernels register by id from `verity/kernels/`) needs no new API. Still open for circuits: does the registry part move to `verity/kernels/registry`? |
| `verity/evaluation/bits.py` | `verity/primitives/circuits/evaluation/bits` | P4 (evaluation), P5 (the reference every kernel is bit-exact with) | high | bench/private_circuit, circuit_check, vLLM ; tests only: PoUW\* |  |
| `verity/evaluation/reference.py` | `verity/primitives/circuits/evaluation/reference` | P4 (evaluation), P5 (the reference every kernel is bit-exact with) | high | C-Flock\*, SP1†, circuit_check, vLLM |  |
| `verity/randomness/__init__.py` | `verity/primitives/randomness` | P5: fast provers take their coins from it; P1 | high | C-Flock\*, PoUS\*, PoUW\*, bench/pous, bench/pouw, numerical, sampled-proofs\*, vLLM |  |

`randomness` stays stdlib-only and imports no other core module. Its `tests/randomness/vectors.json` pins its byte
formats and stays with its tests.

### `verity.commitments` to `verity/primitives/commitments/` (and `crypto/`)

`hm96` imports `vllm_v1`, which imports `leaves`. So `vllm_v1` and `leaves` stay in `verity/` whatever the answer to
"one Merkle tree, one SHA-512 row hash" turns out to be. Only the status of each framing (current or superseded)
depends on it.

proofs answered it on 4 Oct. The one framing is the one the verifier of record accepts and the only one a guarantee
reads: the `frame-v3-sha512` tree over verifier-derived domains (`merkle` plus `frame_v3`), with `hm96-sha512/v1` hiding
leaves (`hm96`), over the SHA-512 row digests `sha512/row/v1`, `sha512/row/v2` and `sha512/row-seg/v1` (`rowleaf`). That
is C-Flock's `SCHEME = "frame-v3-sha512/hm96-sha512"`. The superseded entries are `frame-v3` over SHA-256,
`sha256/row/v1`, `blake3-keyed/row/v2`, `hm96-sha256/v1`, the NVFP4 row schemas and `poseidon2-babybear-w24/row/v2h`.
They stay in their modules for now, marked superseded, so old records replay; splitting them out is step-5
consolidation, not a move. `vllm_v1` and `leaves` stay current, because vLLM's serving Commit emits them; moving serving
onto the one framing is circuits' and proofs' step-5 job.

The vectors JSON files beside the references (`frame_v3/vectors.json`, `vectors_sha512.json` and
`nvfp4_row_v1_vectors.json`, plus `hm96/` and `vllm_v1/`) are the agreement spec. C-Flock's Lean verifier
(`verifier/lean/Main.lean`) and the Rust in `backends/flock/live`, `ligero-verify` and `gkr` read them, so they stay
beside the references. Under the Conventions, the three `PROTOCOL.md` files (`frame_v3`, `hm96`, `vllm_v1`) retire
into those vectors and a short README.

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/commitments/__init__.py` | `verity/primitives/commitments/__init__` | P1 | high | A-GKR†, B-Ligero†, PoUW\*, bench/pouw, vLLM ; tests only: backends/shared | proofs: it re-exports `multiproof`, so the re-export has to go first (see the forbidden-import splits). |
| `verity/commitments/blake3.py` | `verity/primitives/crypto/blake3` | P1: a hash, not a commitment scheme: the Pearl-C schemes' BLAKE3 and `rowleaf`'s superseded BLAKE3 row | high | PoUW\*, bench/pouw | answered (proofs, 4 Oct): `primitives/crypto/`. |
| `verity/commitments/frame_v3/__init__.py` | `verity/primitives/commitments/frame_v3` | P1: C-Flock and PoUW import it | high | A-GKR†, B-Ligero†, C-Flock\*, PoUW\*, bench/commitments ; tests only: vLLM | answered (proofs, 4 Oct): the `frame-v3-sha512` tree is the one framing; `frame-v3` over SHA-256 stays in the module, marked superseded, so A-GKR's and B-Ligero's records replay. |
| `verity/commitments/frame_v3/vectors.py` | `packages/verity/tests/commitments` (generating test) | Tests convention: test-only code moves into tests | high | tests only: B-Ligero† | answered (proofs, 4 Oct): the generator becomes a generating test, and the JSON stays beside the reference. |
| `verity/commitments/frame_v3/vectors_sha512.py` | `packages/verity/tests/commitments` (generating test) | Tests convention: test-only code moves into tests | high | — | answered (proofs, 4 Oct): the generator becomes a generating test, and the JSON stays beside the reference. |
| `verity/commitments/hm96/__init__.py` | `verity/primitives/commitments/hm96` | P1: C-Flock's verifier of record and sampled proofs read it | high | C-Flock\*, PoUW\*, bench/commitments, sampled-proofs\*, vLLM |  |
| `verity/commitments/hm96/vectors.py` | `packages/verity/tests/commitments` (generating test) | Tests convention: test-only code moves into tests | high | tests only: vLLM | answered (proofs, 4 Oct): the generator becomes a generating test, and the JSON stays beside the reference. |
| `verity/commitments/identity.py` | `verity/primitives/commitments/identity` | P1: the commitment primitives every protocol uses | high | C-Flock\*, PoUS\*, bench/network_traces, bench/one_stage, bench/pous, sampled-proofs\*, vLLM, warden\* |  |
| `verity/commitments/indexed.py` | `verity/primitives/commitments/indexed` | P1: the commitment primitives every protocol uses | high | C-Flock\*, bench/commitments, bench/one_stage, sampled-proofs\*, vLLM |  |
| `verity/commitments/leaves.py` | `verity/primitives/commitments/leaves` | P1: `vllm_v1` imports it; vLLM's serving Commit emits `verity-vllm/leaf/v1` | high | SP1†, numerical, vLLM ; tests only: backends/shared | answered (proofs, 4 Oct): it stays current in `verity/` until serving moves onto the one framing in step 5. circuits (4 Oct): vLLM's `commit/merkle.py` duplicates this module and consolidates onto it. |
| `verity/commitments/limits.py` | `verity/primitives/commitments/limits` | P1: the commitment primitives every protocol uses | high | — |  |
| `verity/commitments/merkle.py` | `verity/primitives/commitments/merkle` | P1: the commitment primitives every protocol uses | high | A-GKR†, B-Ligero†, C-Flock\*, bench/commitments, bench/one_stage, bench/pouw, sampled-proofs\*, vLLM ; tests only: backends/shared |  |
| `verity/commitments/multiproof.py` | `experimental/commitments/multiproof` | P9: no guarantee depends on it; a generic algorithm that still runs and may serve batched Merkle openings | high | tests only: B-Ligero† | answered (proofs, 4 Oct): `experimental/commitments/`. Its two archive-bound `proofs` importers (`statement`, `transparent`) go to `archive/sp1`. |
| `verity/commitments/poseidon2_babybear.py` | `archive/direct` (B-Ligero) | P8: the hash of a frozen backend (B-Ligero's Table 2 cell); no live approach uses a field-native hash | high | B-Ligero† | answered (proofs, 4 Oct): `archive/direct`, together with `rowleaf`'s `v2h` schema. Ordering: the `v2h` schema is split out of `rowleaf` first. |
| `verity/commitments/rowleaf.py` | `verity/primitives/commitments/rowleaf` | P1: its SHA-512 row digests are the current row framing | high | A-GKR†, B-Ligero†, C-Flock\*, PoUW\*, bench/commitments, sampled-proofs\*, vLLM ; tests only: backends/shared | answered (proofs, 4 Oct): `sha512/row/v1`, `v2` and `row-seg/v1` are current; its other schemas stay marked superseded. Ordering: the `poseidon2-babybear-w24/row/v2h` schema leaves with `poseidon2_babybear` before this module moves. |
| `verity/commitments/scheme.py` | `verity/primitives/commitments/scheme` | P1: the commitment primitives every protocol uses | high | bench/commitments |  |
| `verity/commitments/turboshake.py` | `verity/primitives/crypto/turboshake` | P1: a hash (the Pearl-C schemes' TurboSHAKE128), not a commitment scheme | high | PoUW\*, bench/pouw | answered (proofs, 4 Oct): `primitives/crypto/`. |
| `verity/commitments/vllm_v1/__init__.py` | `verity/primitives/commitments/vllm_v1` | P1: `hm96` wraps a `VllmV1` base, and vLLM's serving Commit and `protocol_options/sampled_proofs.py` use it | high | A-GKR†, B-Ligero†, C-Flock\*, bench/commitments, vLLM ; tests only: backends/shared | answered (proofs, 4 Oct): it stays current in `verity/`; the one framing is `frame-v3-sha512` with `hm96-sha512/v1` leaves (see the section's introduction), and serving moves onto it in step 5. |
| `verity/commitments/vllm_v1/vectors.py` | `packages/verity/tests/commitments` (generating test) | Tests convention: test-only code moves into tests | high | tests only: vLLM | answered (proofs, 4 Oct): the generator becomes a generating test, and the JSON stays beside the reference. |
| `verity/commitments/vllm_v1/vectors_sha512.py` | `packages/verity/tests/commitments` (generating test) | Tests convention: test-only code moves into tests | high | — | answered (proofs, 4 Oct): the generator becomes a generating test, and the JSON stays beside the reference. |

### `verity.ml`, the word level

Principle 3 puts the word Definitions in the catalog: the builder is the source, and what's digest-addressed is its
descriptor at given statics. Four of these nine modules mix destinations and split (`prims`, `fp32`, `library`,
`kernels`); they are listed below the table. `operations` stays whole (captain's call, 4 Oct).

Two non-module files move too. `ml/tables/` (eight measured MUFU tables) goes to `catalog/hardware/sm89/mufu/`; proofs
(4 Oct) names these captures as the device assumption behind `ml.library`'s list. `ml.mufu` and `ml.boolean.mufu` find
it through `resources.files("verity.ml") / "tables"` (`ml/mufu.py:48`, `ml/boolean/mufu.py:116,463`), so that lookup
changes with it. `ml/annotations.json` goes to the catalog beside its Definitions (circuits, 4 Oct).

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/ml/__init__.py` | dissolves (package init) | the package dissolves | high | — |  |
| `verity/ml/prims.py` | `const` (the `Const<w>[0x..]_v1` family and its lazy family) to `verity/primitives/circuits/` (today's `verity.ir`), beside `boolean.constant`; the cast and dot Definitions to `catalog/definitions/prims` | P3 (Definitions), P4 (the constant family) | high | PoUW\*, circuit_check, numerical, vLLM ; tests only: C-Flock\*, SP1†, sampled-proofs\* | answered (circuits, 4 Oct): `const` goes to the stdlib-only circuits package, where w = 1 already delegates; `prims` re-exports it, so ids are unchanged. PoUW's `circuit/hashes.py`, five `ir` tests and at least seven registry modules (`b1`, `boolean_norms`, `fa2_check_inf`, `fa3_check_inf`, `fa2_softcap`, `pouw_rows`, `tables`) need it. `ncp2` also registers `F32ToBf16Rn_v1` from this module (`ncp2.py:52` at `9400e83d5`); see forbidden-import split 10. |
| `verity/ml/gemm.py` | `catalog/definitions/gemm` | P3: word Definitions | medium | C-Flock\*, circuit_check, numerical, vLLM |  |
| `verity/ml/scalar.py` | `catalog/definitions/scalar` | P3: word Definitions | medium | C-Flock\*, PoUW\*, vLLM ; tests only: sampled-proofs\* | resolved by other answers: at `9400e83d5` its importers outside core are PoUW's `pc4`, `pc8` and `rowk` and C-Flock's `ir_sampling` (lazily), and all four go to `experimental/` (compute-accounting and proofs, 4 Oct), so no `verity/` module imports it. The agreement script `qcall_agree.py:120` imports `I32Add` from it and switches to the same toy as `test_qcall_vectors` (circuits). |
| `verity/ml/fp32.py` | bit-level FP32/BF16 functions to `verity/primitives/silicon` (bridged with ml.tc.fp32); the F32*V2 Definitions to `catalog/definitions/fp32` | P3 (Definitions); step 5's one FP semantics (the bit functions) | medium | PoUW\*, vLLM ; tests only: C-Flock\* | answered (compute-accounting, 4 Oct): consolidate in step 5, bridged by vectors, not in the move train. `ncp2` registers `F32Mul_v2` and `Bf16Add_v1` from it (`ncp2.py:51`), and `pc4`/`pc8`/`rowk` use `F32*V2`, so the consolidation must keep the ncp-v2 Program's digest. With `ncp2` in `verity/`, its import of these Definitions is forbidden-import split 10. |
| `verity/ml/mufu.py` | `catalog/definitions/mufu` | P3: Definitions over measured tables; `tables/` goes to `catalog/hardware/sm89/mufu` | medium | C-Flock\*, vLLM |  |
| `verity/ml/library.py` | split: the mechanism (`Table`, `LABELS`, `table_label`, `definition_label`, `spec`, `digest`) to `verity/primitives/circuits/library`; the list of tables to a catalog entry (`catalog/library`). `Flock/Library.lean`'s `LIBRARY_TABLES` becomes a file generated from that entry, with a no-diff test | P3: which MUFU tables count as hardware semantics is a device assumption, chosen by the verifier rather than hard-coded | medium | C-Flock\* ; tests only: vLLM | answered (captain's call, 4 Oct, on proofs' design): split. circuits had argued to keep it whole because the Lean verifier compiles in the list; proofs' generated `LIBRARY_TABLES` (the `Vectors.lean` pattern; `test_table_library.py` already compares the two lists) answers that. Only the typed statement reads either part, and fail-closed refuses typed statements, so the list is off the accept path. Ordering: no move PR waits on it; the split lands after the moves. |
| `verity/ml/operations.py` | `verity/primitives/circuits/`, whole, beside `ir.constants` | P1: the no-data guard protects zero-knowledge; the list is zero-knowledge policy, not a parameter | high | tests only: circuit_check, vLLM | answered (circuits, 4 Oct; captain's call): it stays whole. `OPERATIONS` and `DERIVATIONS` are id strings resolved through `REGISTRY` at run time, so it imports no catalog module. |
| `verity/ml/kernels.py` | generic numpy kernels to `verity/kernels/tc`; the ScalarReference instances and _register_references to `catalog/hardware/tc/references` | P5 | high | B-Ligero†, bench/pouw, circuit_check, numerical, vLLM ; tests only: C-Flock\* | answered (compute-accounting, 4 Oct): yes. PoUW uses `f32_to_bf16_rn_batch` (vLLM's `pouw_native.py:35`), and the benchmark twins use `group_sum_total_batch`, `block_scaled_batch` and `chain_batch`. Each kernel's self-check against its Definition runs in the catalog's suite (the captain's revised default 3). |

### `verity.ml.tc`, split between `verity/primitives/silicon/` and `catalog/hardware/tc/`

Daniel renamed this map's `verity/primitives/fp/` to `verity/primitives/silicon/`, the bit-exact models of the
hardware's low-level ops. Whether `silicon/` itself stays in `verity/` or moves to `catalog/silicon/` is pending
Daniel's ruling; the rows below write `verity/primitives/silicon/` until then. The split itself is the captain's
default 2, and compute-accounting supports it (4 Oct): PoUW's trusted Python uses only the generic `ml.tc.fp32` and
`ml.tc.cast`, only `pearl_c_device.py:30` uses instances, and PoUW's Lean doesn't read core's TC spec.

This package decides the most. `ml.tc` is the exact tensor-core and FP semantics, stdlib only, and its Lean twin is
core's spec. Its `layers` entry says `Protocol.TC.Spec` transcribes `total.py`, `models.py` and `term.py`, and that
`Protocol.TC.Relation` transcribes `relation.py`. The lock's `reads` name both, for the 18 guarantees in `Guarantees.TC`.

The Lean already separates a model's shape from its instances. `Pipeline.lean` defines a generic `Pipeline` structure
and four device instances (`HOPPER_BF16_WGMMA_K16`, `HOPPER_BF16_M16N8K16`, `AMPERE_BF16_M16N8K16`,
`ADA_BF16_M16N8K16`), and `Spec.lean` is a generic interpreter (`tcDotTotal (p : Pipeline)`). Principle 3 says public
parameters are data, not code, so this map splits the Python the same way:
- the interpreter and format semantics go to `verity/primitives/silicon/`, beside the spec that describes them: `Model`,
  `GroupSum`, `BlockScaledAlignAdd`, `tc_dot`, the `term` decoders, the casts, FP32 arithmetic and the total rules;
- the instance constants go to `catalog/hardware/tc/`, with the instruction index: 17 public ones in `models`, plus
  the ones in `total` and `total_fp8`.

There is an alternative, which matches the plan's catalog list most literally ("hardware models: the tensor-core step,
FP32 and the FP formats"): put all of `ml.tc` in the catalog. Under it, every import of FP semantics from C-Flock and
PoUW would be forbidden:
- PoUW's four Pearl-C schemes import `ml.tc.fp32`, and its `circuit/words.py` imports `cast` and `fp32`;
- C-Flock's `lowering` and `instances` import `cast` and `models`.

It would also leave the generic kernels in `ml.kernels`, and the Lean TC spec, with no home in `verity/`. Whichever is
chosen, the Python and the Lean should move together.

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/ml/tc/__init__.py` | `verity/primitives/silicon/__init__` (re-exports narrowed to the generic semantics) | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data | medium | — | answered (captain's default 2, 4 Oct; compute-accounting agrees): the split, not all of `ml.tc` in the catalog. Where `silicon/` itself sits is pending Daniel. |
| `verity/ml/tc/cast.py` | `verity/primitives/silicon/cast` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data | medium | B-Ligero†, C-Flock\*, PoUW\*, SP1†, numerical, tc_probe ; tests only: vLLM | answered: the split (captain's default 2); `silicon/`'s own placement is pending Daniel. |
| `verity/ml/tc/errors.py` | retire (shim) | P8: superseded infrastructure (a shim re-exporting `verity.errors.InvalidArtifact`) | high | numerical, tc_probe_fp4 |  |
| `verity/ml/tc/fp32.py` | `verity/primitives/silicon/fp32` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data | medium | PoUW\*, bench/pouw | answered: the split (captain's default 2); `silicon/`'s own placement is pending Daniel. |
| `verity/ml/tc/instructions.py` | `catalog/hardware/tc/instructions` | P3: the PTX instruction-class index (model, status, evidence) is data | medium | numerical, tc_probe ; tests only: vLLM |  |
| `verity/ml/tc/models.py` | Model, GroupSum, BlockScaledAlignAdd, tc_dot to `verity/primitives/silicon/models`; the 17 public instance constants to `catalog/hardware/tc/instances` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data, so instances and interpreter split as in `Pipeline.lean` and `Spec.lean` | medium | A-GKR†, B-Ligero†, C-Flock\*, PoUW\*, bench/pouw, numerical, tc_probe, tc_probe_fp4 ; tests only: vLLM | answered: the split (captain's default 2); `silicon/`'s own placement is pending Daniel. |
| `verity/ml/tc/relation.py` | follows its Lean twin `Protocol.TC.Relation`: stays where it is until core's lock reduction decides; if the reduction makes the 18 `Guarantees.TC` step pins lemmas, `relation.py` goes to `experimental/` and the Lean to `security_proofs/core` with its names kept | not a cost model: `census()` only counts predicates | medium | numerical | answered (proofs, 4 Oct): nothing outside core's Lean package names the 18 step pins, no claim id names the relation, and its only Python users are core's tests and numerical's archive-bound red team (`redteam/campaign.py`, `forge.py`, `z3_relation.py`). Ordering: waits on core's lock reduction (proofs, `cursor/core-lock-reduction-95d4`) and its DM. |
| `verity/ml/tc/silicon.py` | retire (shim; importers move to models/total) | P8: superseded infrastructure (a shim re-exporting `term` and `models`); its importers switch to `models` in a prep PR | high | B-Ligero†, C-Flock\*, VOLE†, numerical, tc_probe, tc_probe_fp4, vLLM |  |
| `verity/ml/tc/term.py` | `verity/primitives/silicon/term` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data | medium | A-GKR†, B-Ligero†, PoUW\*, numerical, tc_probe_fp4 | answered: the split (captain's default 2); `silicon/`'s own placement is pending Daniel. |
| `verity/ml/tc/total.py` | generic total step to `verity/primitives/silicon/total`; its instance constants to `catalog/hardware/tc/instances` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data, so instances and interpreter split as in `Pipeline.lean` and `Spec.lean` | medium | C-Flock\*, numerical, tc_probe, vLLM | answered: the split (captain's default 2); `silicon/`'s own placement is pending Daniel. |
| `verity/ml/tc/total_fp8.py` | generic E4M3/E5M2 step to `verity/primitives/silicon/total_fp8`; HOPPER_E4M3_WGMMA_K32 to `catalog/hardware/tc/instances` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data, so instances and interpreter split as in `Pipeline.lean` and `Spec.lean` | medium | PoUW\* ; tests only: vLLM | answered: the split (captain's default 2); `silicon/`'s own placement is pending Daniel. |

### `verity.ml.boolean`

circuits' split decides most of these rows. The Boolean basis, the lowering, the evaluator, and SHA-512 and Merkle as
gates are TCB primitives; the word Definitions and their Boolean versions are catalog entries. `forms` is the GF(2)
builder under `trace`, and every Boolean module imports it. None of the verity-bound modules (`trace`, `forms`,
`gather`, `sha512`, `merkle`) imports a catalog-bound one, so this split is clean inside core.

circuits corrected the split on 4 Oct, and the captain placed the gadgets. `fp`, `tc_step`, `fp4` and `softmax` hold no
Definitions: they are lowering gadgets that C-Flock's lowering and `tail_pieces` import. `fp`, `tc_step` and `fp4` go to
`verity/primitives/silicon/`, beside the models they implement. The generic pieces `forms`, `gather`, `trace` and
`softmax` go to `verity/primitives/circuits/boolean/`; `softmax` composes the `fp` gadgets and models no single hardware
op. `scalar` and `mufu` split: their gadget halves (conversions and MUFU ops) go to `silicon/`, their Definitions to the
catalog. The catalog-bound `gemm` importing `fp4` is then an allowed `catalog/` → `verity/` edge. At `9400e83d5`,
`fp`, `tc_step`, `fp4` and `softmax` import only `forms`, one another and nothing else, so the corrected split is still
clean inside core.

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/ml/boolean/__init__.py` | dissolves (package init) | the package dissolves | high | — |  |
| `verity/ml/boolean/attention.py` | `catalog/definitions/boolean/attention` | P3: the Boolean versions of word Definitions | medium | circuit_check, vLLM |  |
| `verity/ml/boolean/cast.py` | `catalog/definitions/boolean/cast` | P3: the Boolean versions of word Definitions | medium | circuit_check |  |
| `verity/ml/boolean/elementwise.py` | `catalog/definitions/boolean/elementwise` | P3: the Boolean versions of word Definitions | medium | circuit_check, vLLM |  |
| `verity/ml/boolean/forms.py` | `verity/primitives/circuits/boolean/forms` | P3, circuits' split: the GF(2) builder under the lowering | high | C-Flock\*, PoUW\*, vLLM | answered (circuits, 4 Oct): yes, it is part of the lowering; `trace` and every gadget build on it, and it has no imports. |
| `verity/ml/boolean/fp.py` | `verity/primitives/silicon/` | a lowering gadget with zero Definitions (its docstring: "formerly C-Flock's `fp`"); it implements the silicon models | high | C-Flock\*, PoUW\*, vLLM | answered (circuits, 4 Oct; captain placed it in `silicon/`). |
| `verity/ml/boolean/fp4.py` | `verity/primitives/silicon/` | a gadget with zero Definitions, beside the FP4 models it implements | medium | C-Flock\* | captain placed it in `silicon/` (4 Oct). Still open: circuits' placement holds "unless NVFP4 is ruled experimental", and compute-accounting (4 Oct) answered that PoUW's NVFP4 is experimental but PoUW doesn't bind this module, so its fate is C-Flock's (proofs) and circuits' call. The importers are C-Flock's `unit_fp4`, `class_statement` and `pod/gemm_{fp,hill}.py`, core's tests and `circuit_check`. See open question 6. |
| `verity/ml/boolean/gather.py` | `verity/primitives/circuits/boolean/gather` | P4: a 30-line generic gadget that imports only `forms` and has no Definitions | high | vLLM | answered (circuits, 4 Oct): `verity/`. |
| `verity/ml/boolean/gemm.py` | `catalog/definitions/boolean/gemm` | P3: the Boolean versions of word Definitions | medium | circuit_check, vLLM ; tests only: C-Flock\* |  |
| `verity/ml/boolean/merkle.py` | `verity/primitives/commitments/gates/merkle` | P3, circuits' split: Merkle as gates is a TCB primitive | high | C-Flock\*, circuit_check |  |
| `verity/ml/boolean/mufu.py` | split: the gadget functions (MUFU ops) to `verity/primitives/silicon/`; the Definitions to `catalog/definitions/boolean/mufu` | P3; circuits' correction | medium | circuit_check, vLLM | answered (circuits, 4 Oct; captain's placement of the gadget half). |
| `verity/ml/boolean/scalar.py` | split: the gadget functions (conversions, `fmaxmin`) to `verity/primitives/silicon/`; the Definitions to `catalog/definitions/boolean/scalar` | P3; circuits' correction: C-Flock's `tail_pieces` imports `e4m3_to_f32`, `f32_to_e2m1_sat`, `f32_to_e4m3_sat` and `fmaxmin` from it | medium | C-Flock\*, circuit_check, vLLM | answered (circuits, 4 Oct; captain's placement of the gadget half). |
| `verity/ml/boolean/sha512.py` | `verity/primitives/commitments/gates/sha512` | P3, circuits' split: SHA-512 as gates is a TCB primitive; step 5 bridges it to commitments' SHA-512 by vectors | high | C-Flock\* |  |
| `verity/ml/boolean/softmax.py` | `verity/primitives/circuits/boolean/softmax` | a generic gadget with zero Definitions that composes the `fp` gadgets; C-Flock's `tail_pieces` and lowering import it | high | C-Flock\*, vLLM | answered (circuits, 4 Oct). |
| `verity/ml/boolean/tc_step.py` | `verity/primitives/silicon/` | a gadget with zero Definitions, beside the tensor-core model it implements | high | C-Flock\* | answered (circuits, 4 Oct; captain placed it in `silicon/`). |
| `verity/ml/boolean/trace.py` | `verity/primitives/circuits/boolean/trace` | P3, circuits' split: the lowering is a TCB primitive | high | PoUW\*, bench/private_circuit, circuit_check, vLLM ; tests only: C-Flock\* |  |
| `verity/ml/boolean/universal.py` | `experimental/private_circuits/universal` | P9: protocol 2 (private circuits, `UniversalUnit_v1`) has no guarantee yet | high | bench/private_circuit, circuit_check ; tests only: C-Flock\* | answered (circuits, 4 Oct): `experimental/`. Its users follow: `circuit_check/targets.py:53,350` takes its binding from `experimental/`, and `backends/flock/tests/test_wired_links.py` moves with it or switches to a toy unit. |

### `verity.proofs`

Most of `verity.proofs` is D-SP1's typed-obligation and lowering stack. SP1, `benchmarks/ir_call` and
`benchmarks/dot_product` use it, and it goes to `archive/sp1/`. Four modules are live:
- `profile` goes to `verity/` (a shared `verity/protocols/profile`, proofs);
- `codes` splits: the 12 codes live code uses go to `integrations/vllm/`, the rest to `archive/sp1` (proofs and
  circuits);
- `target` goes to the catalog;
- `query` is vLLM's, and moves into it (circuits).

Nothing may import archived code (principle 8). So before the stack moves, its live importers must split off or go to
the archive with it:
- numerical imports `packed`;
- `benchmarks/ir_call` imports `binding`, `codes`, `lowering`, `packed`, `reduce_mufu`, `typed_obligation` and
  `wire`;
- `benchmarks/dot_product` imports `binding`, `conformance` and `target`.

The map for backends, benchmarks and tools decides those.

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/proofs/__init__.py` | dissolves (package init) | the package dissolves | high | — |  |
| `verity/proofs/binding.py` | `archive/sp1/proofs/binding` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/dot_product, bench/ir_call |  |
| `verity/proofs/codes.py` | split: the 12 codes live code uses (`ACCEPTED`, `EXPECTATION_MISMATCH`, `INVALID_COMMITMENT`, `INVALID_OPENING`, `INVALID_VALUE`, `PUBLIC_IO_MISMATCH`, `CHECK_MISMATCH`, `CHALLENGE_MISMATCH`, `COVERAGE_MISMATCH`, `RELATION_REJECTED`, `INVALID_COMPILED_RESULT`, `MALFORMED_TRANSCRIPT`) to `integrations/vllm/`, values unchanged; the rest to `archive/sp1` with the `proof-format-v3` decoder | P7: all 12 are used only by vLLM's `check/` (`commit_rules`, `gates`, `result`); P8 | medium | bench/ir_call, vLLM | answered (proofs and circuits, 4 Oct): proofs said the 12 go to `verity/codes` if the Commit verdict is a verifier role and into `integrations/vllm` otherwise; circuits answered that it is not (backends map, circuits question 3). C-Flock, sampled proofs and PoUW import none of them. Daniel's 4:06 PM ruling, as the plan records it, ties the 12 to a narrower question that circuits and proofs decide: whether `check/`'s commitment and opening checks are protocol code because sampled proofs needs them (whatever recomputes opened values is a diagnostic). Until they decide, the destination stays `integrations/vllm/`. |
| `verity/proofs/conformance.py` | `archive/sp1/proofs/conformance` (test-only) | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | bench/dot_product | none: it is test-only apart from `benchmarks/dot_product/vector_run.py`, which goes to archive with it. |
| `verity/proofs/elem_bf16.py` | `archive/sp1/proofs/elem_bf16` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1† |  |
| `verity/proofs/families.py` | `archive/sp1/proofs/families` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1† |  |
| `verity/proofs/gateset.py` | `archive/sp1/proofs/gateset` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1† |  |
| `verity/proofs/int8.py` | `archive/sp1/proofs/int8` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | — |  |
| `verity/proofs/lowering.py` | `archive/sp1/proofs/lowering` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/ir_call ; tests only: vLLM | proofs: a vLLM test imports it. Does that test go to archive, or get dropped? |
| `verity/proofs/packed.py` | `archive/sp1/proofs/packed` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/ir_call, numerical | proofs: numerical (whose bench spine is live) and `benchmarks/ir_call` import it, and nothing imports archive code, so those importers have to split first. |
| `verity/proofs/profile.py` | `verity/protocols/profile` (shared) | P1: it records what any verifier established; PoUW reads it as well as sampled proofs | high | PoUW\*, sampled-proofs\* ; tests only: C-Flock\* | answered (proofs, 4 Oct): a shared `verity/protocols/profile`, not under `verification/`. |
| `verity/proofs/programs.py` | `archive/sp1/proofs/programs` (test-only), with its five target tests | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | high | — | answered (proofs, 4 Oct): the five tests regenerate SP1 guest digests, not catalog digests: `programs.py` builds `typed_obligation` subcircuits, and the digests it checks are `target.py`'s gate-set and family manifests, which only the SP1 guest reads. So they go to `archive/sp1` with it. |
| `verity/proofs/query.py` | `integrations/vllm/verity_vllm/query/`, under a vLLM name | P7: its only users are 4 vLLM modules and 11 vLLM tests | high | vLLM | answered (circuits, 4 Oct): it moves into vLLM (`query/required.py`'s `Q_module_body_v1`, `module_body.py`, `program_view.py`, `norm_scales.py` use it). It is not the same thing as `ir.query` or `partition_object`; superseding it later is a `circuits/<slug>` approach entry, not part of this move. |
| `verity/proofs/reduce_mufu.py` | `archive/sp1/proofs/reduce_mufu` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/ir_call |  |
| `verity/proofs/schema.py` | `archive/sp1/proofs/schema` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | — |  |
| `verity/proofs/statement.py` | `archive/sp1/proofs/statement` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | — |  |
| `verity/proofs/target.py` | `catalog/targets/target`, with its recorded digests as data | P3: the frozen first subcircuit is a public parameter | high | A-GKR†, B-Ligero†, C-Flock\*, SP1†, bench/dot_product, numerical, tc_probe | answered (proofs, 4 Oct). Ordering: `families`' name constants move into it first. Its live readers (`bench/contract.py`, `bench/drilldown.py`, `tools/tc_probe/trust.py`, `instances_hw.py`) read names, models and domains, never the SP1 digests. |
| `verity/proofs/transparent.py` | `archive/sp1/proofs/transparent` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | — |  |
| `verity/proofs/typed_obligation.py` | `archive/sp1/proofs/typed_obligation` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/ir_call |  |
| `verity/proofs/wire.py` | `archive/sp1/proofs/wire` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/ir_call |  |

## Lean: `packages/verity/lean/`

The step-3 pilot is a pure move: every spec module stays, every lemma and proof goes to `security_proofs/core/`, and no
declaration name changes. The `layers` column is the module's entry in `lean-audit.json` (its six `layers` keys are all
spec modules), and "read by a pin" means a guarantee's statement or the `reads` section names it.

Module names do change for the proofs (lean, verity#1144, 4 Oct). Lean resolves a module through the first search-path
package that has a directory for its root component, so with `Verity.Protocol` in the spec package and
`Verity.SecurityProofs.*` in `security_proofs/core`, `lake build` works but `lake env lean` can't load the proofs, and
the audit reads builds through `lake env lean`. So proof modules take a root of their own (for example `CoreProofs.*`)
while their declarations keep `namespace Verity.SecurityProofs`, and the umbrella module `Verity` stays with the spec.
ci's `move-check` (#1140, `da67f1f66`) certifies such a split as pure: `guarantees` and `reads` byte-identical, `roots`
and the new `proved_in` free to change, and imports rewritten module for module.

The rule behind lean's answers is that a spec definition stays in the spec package only if some guarantee, in any
package, reads it.

| Module(s) | Files | Layer | Read by a pin | Step 3 | Later | Confidence |
|---|---|---|---|---|---|---|
| `Verity.Assumptions` | 1 | `Verity.Assumptions` (the assumptions module) | yes: `GemmAmpereStep`, `GemmHopperStep`, `StepInputs` | spec, stays | the two device assumptions could go to catalog Lean with the tensor-core instances | high (step 3); medium (later) |
| `Verity.Guarantees`, `Guarantees/{Circuit, Game, TC}` | 4 | `Verity.Guarantees` | yes: the statements of all 29 guarantees | spec, stays | `Guarantees.TC` names the Ampere and Hopper instances, so it follows them if they move to catalog Lean. Core's lock reduction (proofs, `cursor/core-lock-reduction-95d4`) proposes the 18 `Guarantees.TC` step pins as lemmas unless the docs site cites them, since nothing outside core's Lean package names them | high |
| `Verity.Protocol` (umbrella) | 1 | `Verity.Protocol` | umbrella only | spec, stays | NCI's `Nci/Protocol.lean` imports this umbrella, so narrow that import to what NCI reads before any module leaves the umbrella. Ordering: that now applies at the first split that moves `Protocol.{Boolean, Fp32, Prims, Scalar}` out (the rows below) | high |
| `Protocol/{Circuit, Declaration, Game, Partition}` | 4 | `Verity.Protocol` | yes | spec, stays: core's one circuit and game model (principle 4) | none | high |
| `Protocol/TC.lean`, `TC/{Bridge, Gadgets, Pipeline, Relation, Spec}` | 6 | `Verity.Protocol`; `Pipeline`, `Spec` and `Relation` have layers of their own | yes | spec, stays | `Pipeline.lean`'s four instances to catalog Lean ("device instances in Lean"); the generic `Spec` stays beside `verity/primitives/silicon/` | high (step 3); medium (later) |
| `Protocol/Boolean` | 1 | `Verity.Protocol` | no | leaves the spec for `security_proofs/core`, unlocked, declarations keeping `Verity.Protocol.*` | answered (lean and proofs, 4 Oct): no guarantee in any package reads it (lean checked every lock's `reads`), so it leaves, against this map's recommendation to keep it. It returns by promotion, a module move with no rename, when a lowering guarantee reads it | high |
| `Protocol/{Fp32, Prims, Scalar}` | 3 | `Verity.Protocol` | no | leave the spec for `security_proofs/core`, unlocked, declarations keeping `Verity.Protocol.*` | answered (lean and proofs, 4 Oct): no guarantee reads them. The first likely reader is PoUW's `Pc4OpsAgree.le` through `Scalar.i32Le`, once it is proved for core's instance | high |
| `Verity.lean` (root umbrella) | 1 | `roots` | no | stays with the spec (lean, verity#1144: the umbrella module stays with the spec); today it imports `Verity.SecurityProofs` | none | medium |
| `Verity.SecurityProofs` and `SecurityProofs/*` | 43 | the math | the proofs of the 29 pins | `security_proofs/core/`; module names move under the proofs' own root, declaration names unchanged (verity#1144) | consolidated in step 3.3 | high |

The 43 math modules are `SecurityProofs.lean`, plus five at its top level (`Boolean`, `Circuit`, `Fp32`, `Game`,
`TC`), `Game/*` (12), `TC/*` (22: `Ampere.lean`, `AmpereSound`, `Boundary`, `Gadgets`, `Proofs.lean`, `Sound`,
`Vectors`, six under `Ampere/` and nine under `Proofs/`), and `Fp32/Vectors`, `Prims/Vectors` and `Scalar/Vectors`.

The lock splits only at package level, as the plan's step 3 says:
- `roots` goes from `["Verity"]` to the spec prefixes, and the lock gains `proved_in`, the path to the proofs package
  (lean, verity#1144).
- The six `layers` entries stay with the spec.
- The 29 `guarantees` (each `Verity.SecurityProofs.X : Verity.Guarantees.X`) and the 13 `reads` modules (all spec)
  stay byte-identical.
- `dependencies` (the Mathlib manifest and the toolchain) is copied to both packages, since both require Mathlib.

Each pin's proof name then points into the math package, which is what the validator change on the critical path
(item 3) handles.

Four of the math modules are generated vectors: `TC/Vectors.lean`, `Fp32/Vectors.lean`, `Scalar/Vectors.lean` and
`Prims/Vectors.lean`. Principle 2 sends generated vectors to the catalog, but step 3 moves them with the math, under
their declaration names. They are written and checked by `tests/ml/test_lean_vectors.py`, `test_lean_fp32_vectors.py`
and `test_lean_scalar_vectors.py`, which name the files by path (`packages/verity/lean/Verity/SecurityProofs/...`).
Those paths, and the verity suite's declared inputs, must change in the same commit as the move, or the Python half of
the check silently stops comparing.

After step 3 (lean and proofs, 4 Oct): the vector data goes to the catalog, and each `Vectors.lean` becomes a file in
`security_proofs/core` generated from the catalog JSON, with a test that regenerating it gives no diff. The Lean that
kernel-checks the definitions against the data stays beside them. Lean can't read the JSON at compile time, because the
audit forbids it.

Across packages: NCI's spec imports `Verity.Protocol`, and its `SecurityProofs` and `SecurityProofs/Chain` import
`Verity.SecurityProofs`. PoUW's `Protocol/PearlC/*` imports `Verity.Protocol.Partition` and `Verity.Protocol.Game`,
and its `SecurityProofs/PearlC/*` imports `Verity.SecurityProofs.{Game, Circuit, Game.Prob}`. No protocol's spec
imports core's math, so the split creates no forbidden Lean `require`. NCI's and PoUW's math packages will need
`security_proofs/core/`, which is moot once the proofs become one package.

## `census/`

| Current path | Destination | Principle | Confidence | Read by | Owner question |
|---|---|---|---|---|---|
| `census/{hardware, datatypes, networks, subcircuits, input_sets, workloads}.json` | `catalog/census/` | P3: the census is a catalog entry | high | read as files by `verity_numerical.bench.census`, the table renderer, benchmarks and the docs site; nothing imports it | answered (captain, with comms taking the default, 4 Oct): `catalog/census/` is its home, and a separate repository stays a later option. |
| `census/schemas/*.schema.json` (6) | `catalog/census/schemas/` | P3 | high | the same | none |
| `census/README.md` | `catalog/census/README.md` | P3 | high | none | none |

`test_core_never_reads_the_census` in core's `test_boundaries.py` becomes "`verity/` never reads `catalog/`", which
the merged boundary test checks (see "Tests").

## `fixtures/`

| Current path | Destination | Principle | Confidence | Read by | Owner question |
|---|---|---|---|---|---|
| `fixtures/artifacts.json` | stays at the root | the registry of every fixture's art id (store README §7.3) | high | `tools/research`, `tools/check`, `tests/test_repository.py`, several backends and vLLM | answered (infra and ci, 4 Oct): it stays at the root. `research data fetch-fixtures`, `test_repo_replicas.py` and the store README read it there. Any fixture that moves has its `artifacts.json` entry rewritten in the same PR (infra). |
| `fixtures/bench-instances/` (85 files) | with the suites that read them; `catalog/input_sets/` until a reader says otherwise | P3 | medium | `census/input_sets.json`, most backends, `benchmarks/`, vLLM, `tools/research`, `tools/tc_probe` | partly answered (4 Oct). ci: they go with the suites that read them. compute-accounting: no PoUW module, `benchmarks/pouw` script or vLLM PoUW option reads them. infra: no constraint beyond moving the `artifacts.json` entries in the same PR. Still open for proofs, whose readers (the backends and the tables) decide the home. |
| `fixtures/discrepancy_log.json` | `catalog/hardware/tc/` | P3: evidence for the device models | medium | core's `proofs/test_discrepancy_log.py`, numerical, `ligero-verify`, SP1, `tools/tc_probe` | none |
| `fixtures/hawkeye/` (1) | `catalog/hardware/tc/` | P3 | medium | core, numerical, `tools/tc_probe` | none |
| `fixtures/tc/` (13) | `catalog/hardware/tc/captures/` | P3 | medium | core's `ml` tests, numerical, B-Ligero, vLLM, PoUW, `tools/check`, `tools/tc_probe` | none |
| `fixtures/proof-format-v3/` (2) | `archive/sp1/` | P8 | medium | SP1; `proofs.codes` keeps its full enum for these | see `proofs.codes` |
| `fixtures/typed-obligation-v0/` (141) | `archive/sp1/` | P8 | medium | SP1, numerical, `benchmarks/dot_product`, `benchmarks/judge.py`, core's target tests | answered (proofs, 4 Oct): the target tests that read it go to `archive/sp1` with `proofs.programs`, so every reader is in the archive. |
| `fixtures/redteam/` (108), `redteam-3/` (16), `redteam-zk/` (4) | `archive/`, beside `backends/redteam` and the frozen backends | P8 | medium | B-Ligero, A-GKR, `ligero-verify`, numerical, `backends/redteam` | answered (4 Oct). proofs: `backends/redteam/` goes to the archive, since it attacks only A-GKR and B-Ligero and `check` runs none of it. ci: red-team fixtures go with the suites that read them, which are all archive-bound. infra: no constraint. |
| `packages/verity/tests/ml/fixtures/` (130: the `gemm-B1-…` capture with 117 files, `golden/`, `gpu-nan-…`, `tc-hopper-…`, four `tc-sm120-…` sets, a README) | the catalog's `hardware/tc` tests | P3 | medium | core's `ml` tests | partly answered (compute-accounting, 4 Oct): `gemm-B1` is not a served-row capture. It is 30 authenticated GEMM coordinates from the RTX 4090 eager vLLM port (`x.u16`, `w_row.u16`, `out_row.u16` and `fixture.json` each, 117 files, 718,696 bytes) without the Merkle openings, so it is already shrunk to what the coordinate relation reads and stays as a hardware-semantics fixture. Circuits' confirmation is still open. |

## Tests

### Core's tests (`packages/verity/tests/`)

| Current path | Destination | Principle | Confidence | Note |
|---|---|---|---|---|
| `tests/ir/` (17 tests, 6 vectors files) | verity's tests, beside `primitives/circuits/` | Tests convention | high | Seven of the 17 tests import `ml.prims` or `ml.scalar` to register Definitions before decoding: `test_annotations`, `test_codec`, `test_constants`, `test_partition_object`, `test_qcall_vectors`, `test_qword_vectors` and `test_units`. answered (circuits, 4 Oct): all seven switch to toy registrations, which needs `const` in the circuits package. The three pinned-vector tests (`test_partition_object`, `test_qword_vectors`, `test_qcall_vectors`) switch to toys with the same ids and signatures, so `partition_vectors.json`, `qword_vectors.json` and `qcall_vectors.json` stay byte-identical; the Lean verifier and `qword_agree.py --vectors` read them, and `qword_program_agree.py` imports `test_qword_vectors` by path. |
| `tests/evaluation/` (3) | verity's tests, except the kernel-specific tests, which go to the catalog's suite | Tests convention | medium | All three import catalog-bound modules. `test_bits` imports `ml.boolean`, and `test_evaluation` imports `ml.tc.models`, `total` and `total_fp8` for the self-check of every registered kernel that AGENTS.md requires. `test_registered_tables` is the third. answered (circuits, 4 Oct): `test_bits` and `test_registered_tables` switch to toys (the peak-bytes test uses a generated gate chain of the size of `ml.boolean.gemm`). In `test_evaluation`, the seven machinery tests switch to toys, and `SELF_CHECKED`, the completeness test, the kernel and statics tests and the capture replays (ampere, hopper, NVFP4, `gemm_coordinate`, `group_sum`) go to the catalog's suite. When the self-check list moves, its completeness filter (`test_evaluation.py:81`, which keeps only kernels whose `__module__` starts with `verity`) is keyed on `_KERNELS` minus an explicit allow-list instead, because today it fails open for a kernel under any other import name, and import names now change. |
| `tests/randomness/` (1 test, `vectors.json`) | verity's tests | Tests convention | high | none |
| `tests/claims/` (1) | verity's tests | Tests convention | medium | It follows `claims`. |
| `tests/commitments/` (16) | verity's tests; `test_poseidon2` to `archive/direct`, `test_multiproof` to `experimental/` | Tests convention | medium | The vectors generators become generating tests here. |
| `tests/proofs/` (13) | split. `test_profile` and `test_query` follow their modules. The five target tests (`test_target`, `test_bf16_hopper_target`, `test_fp8_targets`, `test_fp8_sm120_target`, `test_nvfp4_target`) go to `archive/sp1` with `proofs.programs`. `test_tc_probe_families` goes to `catalog/targets`. `test_discrepancy_log` goes to `catalog/hardware/tc`. `test_conformance`, `test_gateset`, `test_int8` and `test_reduce_mufu` go to `archive/sp1`. | Tests convention, P8 | medium | answered (proofs, 4 Oct): the five target tests regenerate SP1 guest digests, not catalog digests, so they go to the archive. answered (circuits, 4 Oct): `test_profile` imports `verity.ml` only to bind `gemm.Gemm` with `GEMM_AMPERE` for a Program with partition levels, and switches to a toy. |
| `tests/ml/` (29 tests, 130 fixture files) | split with their modules: semantics tests to the tests of `verity/primitives/silicon/`, Definition, instance and capture tests to the catalog | Tests convention | medium | `test_lean_vectors`, `test_lean_fp32_vectors` and `test_lean_scalar_vectors` follow the Lean move. |
| `tests/test_boundaries.py` | merges with the two root boundary tests | P6, P9 | medium | Its `ALLOWED`, `FORBIDDEN_EXTERNAL`, `NUMPY_FREE` and census rules are rewritten for the new layout. |

The verity suite's declared inputs read `census`, four `fixtures/` paths, `tools/tc_probe`,
`tools/tc_probe_fp4/probe.py` and five `backends/numerical` files. Under this map every test that reads them moves to
the catalog's or the archive's suite: `test_tc_probe_families`, `test_instructions`, `test_discrepancy_log`, the target
tests, `test_models`, `test_total_fp8` and `test_wgmma_bf16`. The verity suite would then read nothing outside
`verity/`, which makes its declared inputs a free check of principle 6. This is ci's answer to open question 5 (4 Oct):
core's suite stays self-contained, so a catalog change doesn't rerun it, and core's tests import no catalog module.

### The root `tests/`

| Current path | Destination | Principle | Confidence | Owner question |
|---|---|---|---|---|
| `test_repository.py`, `test_no_wall_clock.py`, `test_lean_packages.py`, `test_uv_pin.py` | stay in `tests/` | Tests convention: whole-tree invariants | high | none (`test_lean_packages.py` lists the Lake packages, so it changes with the Lean move) |
| `test_backend_boundaries.py`, `test_protocol_boundaries.py` | merge with core's `test_boundaries.py` into one boundary test in `tests/` | P6, P9 | medium | ci: the merged test would check four rules. `verity/` imports nothing else; `catalog/` imports only `verity/`; nothing in `verity/` imports `experimental/`; nothing imports `archive/`. partly answered (ci, 4 Oct): `test_boundaries.py` scans `src/` only, not `tests/`, and ci would keep it that way during the moves and decide the merge separately. Still open for ci: when to merge. |
| `test_pous_bench.py`, `test_pous_explorer.py`, `test_pous_harness.py`, `test_pous_p2v1.py` | `benchmarks/pous/tests/` | Tests convention: they load `benchmarks/pous/bench.py` and `explorer.py` by path, so they are that package's tests, not whole-tree invariants | high | answered (memory-accounting, 4 Oct): `benchmarks/pous/tests/`. |

## Forbidden-import splits

Under this map, these imports would point from `verity/` into `catalog/`, `experimental/` or `archive/`, or from
`catalog/` into `experimental/` or `archive/`. Each split must land before, or in the same commit as, the move that
would create the import.

Inside core, found by checking every core-to-core edge against the destinations:
1. `verity.commitments` (`__init__`) re-exports `multiproof`, which is bound for `experimental/`. Drop the re-export.
   B-Ligero's tests, its only outside users, can import `multiproof` directly.
2. `commitments.rowleaf` imports `poseidon2_babybear`, which is bound for the archive, for the
   `poseidon2-babybear-w24/row/v2h` schema (a B-Ligero Table 2 cell). Move that schema out with B-Ligero, and either
   have `rowleaf` take schemas by registration or drop that one.
3. `ml.kernels` imports instance constants: `tc.models`' `ADA_E4M3_M16N8K32`, `BLACKWELL_SM120_MXF4` and
   `BLACKWELL_SM120_NVF4`, `tc.total_fp8`'s `HOPPER_E4M3_WGMMA_K32`, and (lazily) `tc.cast`. Split
   `_register_references` and its `ScalarReference` instances (`HOPPER_E4M3_STEP`, `ADA_E4M3_STEP`, the NVFP4 and
   MXFP4 steps) into the catalog. The generic kernels then take the model as a parameter.
4. `ml.tc.models`, `total` and `total_fp8` each keep instance constants next to the interpreter. Split the instances
   into the catalog. `ml.tc`'s `__init__` re-exports `instructions` and the instances (through `silicon`), so it is
   narrowed to the generic semantics at the same time.
5. `proofs.target` imports four name constants from `proofs.families`, which is bound for the archive. Copy the names
   into `target` (they are names, not code). It also imports the `silicon` shim, which becomes `models`.
6. `ml.library` splits after the moves (the captain's call, 4 Oct): the mechanism stays in `verity/`, the table list
   becomes a catalog entry, and `Flock/Library.lean`'s `LIBRARY_TABLES` becomes a file generated from that entry with
   a no-diff test. No move PR waits on it. `ml.operations` stays whole in `verity/` (circuits): `OPERATIONS` and
   `DERIVATIONS` are id strings resolved through `REGISTRY` at run time. Its guard reads `library.TABLES`
   (`operations.py:37,57` at `9400e83d5`), so the library split also has to give the guard the table list without an
   import of the catalog entry. That is part of the split PR, not of the moves.
7. `ml.prims`: move `const` (the `Const<w>` family) to the circuits package (today's `verity.ir`), beside
   `ir.boolean.constant`, to which w=1 already delegates (circuits, 4 Oct). `prims` re-exports it, so the ids are
   unchanged. The Definitions stay in the catalog. Its importers are PoUW's `circuit/hashes.py`, five `ir` tests (once
   they switch to toys) and at least seven vLLM registry modules (`b1`, `boolean_norms`, `fa2_check_inf`,
   `fa3_check_inf`, `fa2_softcap`, `pouw_rows`, `tables`).
8. `ml.fp32`: move the bit-level FP32 and BF16 functions to `verity/primitives/silicon/`, bridged by vectors with
   `ml.tc.fp32`. The `F32*V2` Definitions stay in the catalog. answered (compute-accounting, 4 Oct): this is step-5
   consolidation, not part of the move train, and it must keep the ncp-v2 Program's digest.
9. Moot. It applied only if NVFP4 were ruled experimental, and the captain placed `ml.boolean.fp4` in
   `verity/primitives/silicon/` (open question 6 still decides the NVFP4 and MXFP4 coordinates in `ml.boolean.gemm`).
10. New, from the captain's call 5 (4 Oct): `ncp2` stays in `verity/` for now. At `9400e83d5` and `5049de02f` it
    imports `verity.ml.fp32` (to register `F32Mul_v2` and `Bf16Add_v1`) and `verity.ml.prims` (to register
    `F32ToBf16Rn_v1`) at `ncp2.py:51-52`, and both are catalog-bound Definitions. So either those three Definitions
    stay where `ncp2` can import them, or `ncp2` takes them as parameters. It needs a decision together with call 5.

From areas bound for `verity/` into catalog-bound core modules. The protocols map owns these, but they constrain core's
destinations:
- **C-Flock** (to `verity/protocols/verification/`):
  - `ml.library`: seven modules (`boolean_export`, `circuit_types`, `derive`, `ir_lower`, `layouts`, `type_trace`,
    `typed_statement`), plus the verifier's `circuit_type_agree.py` and `layout_agree.py`;
  - `ml.mufu`, `ml.boolean.scalar` and `ml.boolean.softmax`: `tail_pieces` and `boolean_export`;
  - `ml.boolean.fp`, `fp4` and `tc_step`: `fp`, `unit_fp4` and `unit`;
  - `ml.scalar` (`ir_sampling`) and `ml.gemm` (`pod/gemm_fp.py`);
  - the tensor-core instance constants: `lowering`, `unit_fp4_check` and `backend.py`;
  - `proofs.target`: `backend.py`. This is the Table 1 benchmark backend, which belongs in `benchmarks/` anyway.

  Its imports of `ml.boolean.forms`, `sha512` and `merkle` and of the generic `ml.tc` semantics are allowed.

  After the owners' answers (4 Oct), most of these edges go away because one side leaves `verity/`:
  - `ml.boolean.fp`, `tc_step`, `fp4`, `softmax` and the gadget halves of `ml.mufu` and `ml.boolean.scalar` are now
    `verity/` (the captain's placement), so `fp`, `unit_fp4`, `tail_pieces` and the lowering import them legally.
  - `ir_sampling` goes to `experimental/flock/`, and `unit`, `instances` and `backend.py` go to `archive/flock/`
    (proofs).
  - The per-Definition lowerings (`topp_word`, `gemm_coordinate`'s `circuit_lowering`) go to the catalog (default 4,
    proofs); `gemm_coordinate`'s lazy `instances.write_set` import is cut first. `unit_fp4_check` follows `lowering`.
  - `boolean_export` goes to `tools/` (circuits), where it may import anything.
  - The `ml.library` importers stay legal while `ml.library` is whole in `verity/`. The library split, after the moves,
    has to leave them free of a catalog import.
  - `pod/gemm_fp.py` and `class_statement` are placed in the backends map; `class_statement` waits on the catalog
    loader.
- **PoUW** (to `verity/protocols/accounting/work/`):
  - the Definitions in `ml.prims`, `ml.scalar` and `ml.fp32`: `circuit/pc4.py`, `pc8.py` and `rowk.py`;
  - `ml.prims.const`: `circuit/hashes.py`;
  - `ml.boolean.fp`: `circuit/boolean.py`;
  - the tensor-core instance constants: `schemes/pearl_c4.py`, `pearl_c_device.py` and `pearl_kw.py`.

  Its imports of `ml.boolean.forms` and `trace`, and of `ml.tc.fp32` and `cast`, are allowed under the split.

  After compute-accounting's answers (4 Oct, revised 23:09Z for Daniel's 4:06 PM ruling that a computation is verified
  only by a sampled proof): `pc4` goes to `experimental/pouw/nvfp4/`, and `pearl_kw`'s device records go with
  `pearl-fp8-v4` to experimental, so those edges are no longer from `verity/`. `pearl_c_device`'s instance references
  go to `catalog/devices/` with the record's measurements. `pc8`, `rowk`, `leaves`, `boolean.py`, Pearl-C's half of
  `words.py` and TurboSHAKE128 are Pearl-C's only route to a verdict under that ruling, so they are not experimental;
  their edges into the `ml.prims`, `ml.scalar`, `ml.fp32` and `ml.boolean.fp` Definitions remain, and whether they are
  `verity/` or catalog builders is in the protocols map's conflicts, with `hashes.py` and `words.py`. `ncp2` is split
  10, and `hashes.py`'s `const` is split 7.
  `lean/scripts/h1t_vectors.py` and `fp8atom_vectors.py` are vector generators, which are tools and may import
  anything.
- **Sampled proofs, PoUS and the warden**: none. Their source imports only `proofs.profile`, `claims`,
  `commitments.identity`, `randomness` and other verity-bound modules.

Most of the C-Flock and PoUW edges come from protocol code that builds a Program out of catalog Definitions (PoUW's
`circuit/`, C-Flock's lowering and units). Either that builder code goes to the catalog as the builders of
Definitions and Programs, or the protocol code takes the Definitions, models and tables as parameters chosen by the
verifier's side (principle 3). Open question 2 asked which. The captain's default 4 sends builders to the catalog, and
call 5 makes `ncp2` the exception for now.

### Test-only edges

Some core tests of verity-bound modules import catalog-bound ones, 11 edges in all (circuits, 4 Oct):
- seven `ir` tests (they register `ml.prims` and `ml.scalar` Definitions so the codec can decode);
- all three `evaluation` tests;
- `proofs/test_profile.py`.

Outside the tests, the agreement script `backends/flock/verifier/qcall_agree.py:120` imports `verity.ml.scalar.I32Add`
and needs the same toy as `test_qcall_vectors`.

Sampled proofs' tests import `ml.prims` and `ml.scalar` the same way. answered (ci and circuits, 4 Oct; open question
5): core's tests import no catalog module. The machinery tests switch to toy registrations, and the tests of
particular kernels and the capture replays move to the catalog's suite, as in the "Core's tests" table.

## Test-only code that moves into tests

- `commitments.indexed.domains_equal`: only `tests/commitments/test_indexed.py` uses it.
- `ir.program.is_registered`: only `tests/ir/test_constants.py` uses it.
- `proofs.gateset.decode_value`, `encode_value` and `union_gate_set`: only `tests/proofs/test_gateset.py` uses them.
  They go to the archive with `gateset`.
- `proofs.programs`: no source module imports it (`target` names it only in docstrings), and five target tests use it.
  It goes to `archive/sp1/` with `typed_obligation`, which it imports.
- `proofs.conformance`: only its test and `benchmarks/dot_product/vector_run.py` use it. It goes to the archive.
- The five commitment vectors generators (`frame_v3.vectors`, `frame_v3.vectors_sha512`, `hm96.vectors`,
  `vllm_v1.vectors`, `vllm_v1.vectors_sha512`) become generating tests. Only tests import them, from core, vLLM and
  B-Ligero.
- The four root `test_pous_*.py` files belong to `benchmarks/pous/`.

## Open questions, by owner

Questions the owners answered on 4 Oct are kept here, marked answered, so their numbers stay stable.

1. **captain, compute-accounting, circuits: where do the FP and tensor-core semantics live?** answered (captain's
   default 2, with compute-accounting's support, 4 Oct): split, as in the Lean. The generic interpreter goes to
   `verity/primitives/silicon/` (Daniel's rename of `fp/`), and the instances and the instruction index go to
   `catalog/hardware/tc/`. Whether `silicon/` stays in `verity/` or moves to `catalog/silicon/` is pending Daniel.
2. **circuits, compute-accounting: where does protocol code that builds Programs from catalog Definitions go?**
   Mostly answered (4 Oct). The captain's default 4 sends builders to the catalog, the catalog entry format has
   `verify` take a Program by digest, and proofs and circuits placed the C-Flock builders (see "Forbidden-import
   splits"). The exception is `ncp2`, which stays in `verity/` for now (the captain's call 5, after compute-accounting
   disagreed): a builder the verifier runs at verification time is trusted code, whatever directory it sits in. Still
   open: whether parametric builders the verifier runs are trusted code (Daniel), split 10's three Definitions, and
   top's question to compute-accounting (thread 1791150333.889129, 4 Oct) whether the verifier could pin the digest of
   each fixed-shape unit per k and n, with m only setting how many units there are, so that the builder could leave
   the TCB.
3. **proofs, circuits: is `ml.library` part of the verifier or a public parameter?** answered (captain's call 3, on
   proofs' design, 4 Oct): split after the moves. The mechanism stays in `verity/`, the table list becomes a catalog
   entry, and `LIBRARY_TABLES` becomes a generated Lean file with a no-diff test. Circuits' objection (the Lean
   verifier hard-codes the list) is met by the generated file.
4. **proofs: which commitment framing is the "one Merkle tree, one SHA-512 row hash"?** answered (proofs, 4 Oct):
   `frame-v3-sha512` over verifier-derived domains, with `hm96-sha512/v1` leaves over the SHA-512 row digests
   (C-Flock's `SCHEME`). `vllm_v1` and `leaves` stay current; `multiproof` goes to `experimental/`,
   `poseidon2_babybear` to `archive/direct`; `blake3` and `turboshake` go to `crypto/`.
5. **ci, circuits: may verity's tests import the catalog?** answered (ci and circuits, 4 Oct): no. The machinery tests
   switch to toys, three of them with the same ids so their vectors stay byte-identical, and the kernel-specific tests
   and capture replays move to the catalog's suite.
6. **compute-accounting: is NVFP4 catalog or experimental?** Still open. compute-accounting (4 Oct): PoUW doesn't bind
   `ml.boolean.fp4` or the NVFP4 and MXFP4 coordinates, and PoUW's own NVFP4 is experimental (`pouw/pearl-c4-nvfp4`
   parked, `pouw/pearl-c4-mxfp4` killed), so the call is C-Flock's and circuits'. proofs deferred to this question for
   `unit_fp4_check`. The captain placed the `fp4` gadget in `verity/primitives/silicon/` meanwhile; what remains open
   is the coordinates in `ml.boolean.gemm`, the FP4 instances in `models`, and C-Flock's `unit_fp4`.
7. **proofs: four smaller calls.** answered (proofs, 4 Oct). `ml.tc.relation` follows `Protocol.TC.Relation`, and both stay
   where they are until core's lock reduction decides: if the 18 `Guarantees.TC` step pins become lemmas,
   `relation.py` goes to `experimental/` and the Lean to `security_proofs/core`. It is not a cost model. Of
   `proofs.codes`, only the 12 live codes stay, in `integrations/vllm`. The target tests go to `archive/sp1`. `claims`
   stays in `verity/claims`.
8. **circuits: seven smaller calls.** answered (circuits, 4 Oct). `ir.liveness` stays; `ir.annotations`' validator goes
   to `tools/circuit_check/` and its JSON to the catalog; `proofs.query` goes to `integrations/vllm/verity_vllm/query/`;
   `boolean.universal` goes to `experimental/private_circuits/`; `boolean.gather` goes to `circuits/boolean/`; the
   `ml.operations` guard and list stay whole in `verity/`; `const` goes to the circuits package. Still open for
   circuits: whether `register_kernel`'s registry moves to `verity/kernels/registry` (the `batch.py` row), and
   confirmation of the `gemm-B1` fixture.
9. **lean, proofs: the unread spec modules.** answered (lean and proofs, 4 Oct): no guarantee reads `Protocol.Boolean`,
   `Fp32`, `Prims` or `Scalar`, so they go to `security_proofs/core`, unlocked, with their `Verity.Protocol.*` names.
   The four `Vectors.lean` files become files generated from catalog JSON with a no-diff test.
10. **infra, ci: fixtures.** Mostly answered (infra and ci, 4 Oct): `artifacts.json` stays at the root, and the
    red-team fixtures and `bench-instances` go with the suites that read them, their `artifacts.json` entries moving in
    the same PR. Still open for proofs: the home of `bench-instances`.
11. **captain, with the inventory worker: do Python import names follow directories?** answered (Daniel, 4 Oct 3:50 PM
    PDT): yes. The move script carries a module map beside its path map, and rewrites imports, `import_module`
    strings, `module:attr` specs and module-keyed test data. Lean comments that name Python modules are left to a
    later Lean PR.
12. **captain, comms: does the census still go to its own repository?** answered (captain, 4 Oct; comms takes the
    default): `catalog/census/` is its home, and a separate repository stays a later option.
13. **memory-accounting: where do the root `test_pous_*` files go?** answered (memory-accounting, 4 Oct):
    `benchmarks/pous/tests/`.

## Conflicts for the captain

No two owners disagree on a row of this map once the captain's calls of 4 Oct are applied: circuits' objections on
`ml.library` and on the placement of `fp4` were settled by calls 2 and 3. Two conflicts touch destinations in
`verity/primitives/circuits/`, PoUW's `circuit/hashes.py` and its `words.py` and `boolean.py`; they are rows of the
protocols map and are listed in its "Conflicts for the captain".
