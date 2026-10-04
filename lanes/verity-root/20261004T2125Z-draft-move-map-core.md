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
settled. Nothing has moved, and nothing in this map has been agreed by an owner.

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
  doesn't have yet: `verity/primitives/fp/`, `verity/primitives/circuits/boolean/`,
  `verity/primitives/commitments/gates/`, and the catalog's subdirectories (`definitions/`, `hardware/tc/`, `targets/`,
  `library/`, `annotations/`, `cost_models/`, `census/`, `input_sets/`). Owners should rename them freely.
- The map gives directories only. Whether a Python import name such as `verity.ir` stays the same when its directory
  moves, the way Lean module names do, is the inventory worker's question for the captain. Nothing here depends on the
  answer, except whether a step-5 move can be a pure move.

## Summary

- The 107 Python modules go to these destinations: verity: 53, catalog: 17, archive: 16, split: 8, tests: 5, dissolve: 3, experimental: 2, retire: 2, integrations: 1. A "split" module has one part for `verity/` and
  another for `catalog/`, and each split is listed under "Forbidden-import splits". "dissolve" is an empty package
  `__init__` (`verity.ml`, `verity.ml.boolean`, `verity.proofs`) and "retire" is a re-export shim.
- Confidence for the Python modules: 41 high, 59 medium and 7 low. The low ones are `verity.commitments.multiproof`, `verity.ir.annotations`, `verity.ml.boolean.fp4`, `verity.ml.boolean.universal`, `verity.ml.library`, `verity.ml.tc.relation`, `verity.proofs.query`.
- Lean: of 64 files, the 20 spec modules stay beside the code. The 43 `Verity.SecurityProofs*` modules and the root
  umbrella `Verity.lean` (44 files) go to `security_proofs/core/` under unchanged names, and the lock stays
  byte-identical.
- `census/` (13 files) goes to `catalog/census/`. `fixtures/` has 9 entries: four go to the catalog, four to the
  archive, and `artifacts.json` stays at the root. Core's 8 test directories follow their modules, and 4 of the 10
  root tests leave `tests/` for `benchmarks/pous/`.

## The map, by package

### `verity` top level

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/__init__.py` | `verity/__init__` (package root) | P1 | high | — |  |
| `verity/errors.py` | `verity/errors` | P1: the shared error classes every role raises | high | B-Ligero†, PoUW\*, SP1†, bench/ir_call, numerical, vLLM |  |
| `verity/claims/__init__.py` | `verity/claims` | P10, P1 | medium | PoUS\*, numerical | proofs (with comms): claim ids are what each result cites for its trust, and PoUS imports them at runtime, so the catalog is ruled out (it would be a forbidden import). Is `verity/claims` right, or are they catalog data that verity code looks up by id? Recommend `verity/claims`. |

`proofs.codes`, the verdict codes beside `errors`, is listed with `proofs` below.

### `verity.ir` to `verity/primitives/circuits/`

Principle 4 makes the circuit format, its digests, evaluation and the queries over circuits the core primitive.
C-Flock, PoUW and sampled proofs, all bound for `verity/`, import `codec`, `defs`, `types`, `refs`, `program`,
`partition`, `partition_object` and `cut`. Two modules are less certain: `liveness` (no guarantee reads it) and
`annotations` (metadata that never enters a digest).

`ir/PROTOCOL.md` retires under the Conventions: `tests/ir/format_vectors.json` already pins its rules, and its
definitions belong in the Lean spec (`Verity.Protocol.Circuit`). The six vectors files under `tests/ir/` stay beside
the reference as the spec where two implementations must agree. C-Flock's verifier agreement scripts (`qword_agree.py`,
`qcall_agree.py`, `qword_program_agree.py`, `template_query_agree.py`) read four of them, so those scripts' paths
must follow the move.

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/ir/__init__.py` | `verity/primitives/circuits/__init__` | P4: the format, its digests and the Boolean basis | high | vLLM ; tests only: PoUW\* |  |
| `verity/ir/annotations.py` | `catalog/annotations` | P3: names and descriptions keyed by descriptor ids, never inside a digest | low | tests only: circuit_check | circuits: it is metadata about catalog entries and only `circuit_check`'s tests read it. Should it go to `catalog/annotations` (with `ml/annotations.json`) or to `tools/circuit_check`? |
| `verity/ir/boolean.py` | `verity/primitives/circuits/boolean` | P4: the format, its digests and the Boolean basis | high | PoUW\*, circuit_check, vLLM ; tests only: C-Flock\* |  |
| `verity/ir/boundary.py` | `verity/primitives/circuits/boundary` | P4: queries over circuits (partitions, cuts, units) | high | vLLM |  |
| `verity/ir/codec.py` | `verity/primitives/circuits/codec` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, PoUW\*, bench/one_stage, bench/private_circuit, numerical, sampled-proofs\*, vLLM ; tests only: circuit_check |  |
| `verity/ir/constants.py` | `verity/primitives/circuits/constants` | P4: the format, its digests and the Boolean basis | high | vLLM ; tests only: circuit_check |  |
| `verity/ir/cut.py` | `verity/primitives/circuits/cut` | P4: queries over circuits (partitions, cuts, units) | high | C-Flock\*, PoUW\*, circuit_check, vLLM |  |
| `verity/ir/defs.py` | `verity/primitives/circuits/defs` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, PoUW\*, SP1†, bench/ir_call, bench/private_circuit, circuit_check, numerical, sampled-proofs\*, vLLM |  |
| `verity/ir/evaluate.py` | `verity/primitives/circuits/evaluate` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, SP1†, vLLM |  |
| `verity/ir/intervals.py` | `verity/primitives/circuits/intervals` | P4: queries over circuits (partitions, cuts, units) | high | — |  |
| `verity/ir/layout.py` | `verity/primitives/circuits/layout` | P4: the format, its digests and the Boolean basis | high | C-Flock\*, sampled-proofs\*, vLLM |  |
| `verity/ir/liveness.py` | `verity/primitives/circuits/liveness` | P4 | medium | circuit_check, vLLM | circuits: the dead-gate analysis is used only by `circuit_check` and vLLM's frontend, and no guarantee reads it. Does it stay in `verity/` (the frontend rulings make dead gates legal, so a verifier may come to depend on it), or move to `tools/circuit_check`? |
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
| `verity/evaluation/batch.py` | `verity/primitives/circuits/evaluation/batch` (registry part: `verity/kernels/registry`) | P5 | medium | circuit_check, vLLM | circuits and compute-accounting: `evaluate_batch` is evaluation, but `register_kernel` is the kernel registry that P5 keys by op and device. Should the registry part move to `verity/kernels/registry`? |
| `verity/evaluation/bits.py` | `verity/primitives/circuits/evaluation/bits` | P4 (evaluation), P5 (the reference every kernel is bit-exact with) | high | bench/private_circuit, circuit_check, vLLM ; tests only: PoUW\* |  |
| `verity/evaluation/reference.py` | `verity/primitives/circuits/evaluation/reference` | P4 (evaluation), P5 (the reference every kernel is bit-exact with) | high | C-Flock\*, SP1†, circuit_check, vLLM |  |
| `verity/randomness/__init__.py` | `verity/primitives/randomness` | P5: fast provers take their coins from it; P1 | high | C-Flock\*, PoUS\*, PoUW\*, bench/pous, bench/pouw, numerical, sampled-proofs\*, vLLM |  |

`randomness` stays stdlib-only and imports no other core module. Its `tests/randomness/vectors.json` pins its byte
formats and stays with its tests.

### `verity.commitments` to `verity/primitives/commitments/` (and `crypto/`)

`hm96` imports `vllm_v1`, which imports `leaves`. So `vllm_v1` and `leaves` stay in `verity/` whatever the answer to
"one Merkle tree, one SHA-512 row hash" turns out to be. Only the status of each framing (current or superseded)
depends on it.

The vectors JSON files beside the references (`frame_v3/vectors.json`, `vectors_sha512.json` and
`nvfp4_row_v1_vectors.json`, plus `hm96/` and `vllm_v1/`) are the agreement spec. C-Flock's Lean verifier
(`verifier/lean/Main.lean`) and the Rust in `backends/flock/live`, `ligero-verify` and `gkr` read them, so they stay
beside the references. Under the Conventions, the three `PROTOCOL.md` files (`frame_v3`, `hm96`, `vllm_v1`) retire
into those vectors and a short README.

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/commitments/__init__.py` | `verity/primitives/commitments/__init__` | P1 | high | A-GKR†, B-Ligero†, PoUW\*, bench/pouw, vLLM ; tests only: backends/shared | proofs: it re-exports `multiproof`, so the re-export has to go first (see the forbidden-import splits). |
| `verity/commitments/blake3.py` | `verity/primitives/crypto/blake3` | P1: `merkle`, `rowleaf` and `scheme` import it | medium | PoUW\*, bench/pouw | proofs: does it go to `primitives/crypto/` beside drand BLS, or stay inside `commitments/`, whose modules are its only core users? |
| `verity/commitments/frame_v3/__init__.py` | `verity/primitives/commitments/frame_v3` | P1: C-Flock and PoUW import it | medium | A-GKR†, B-Ligero†, C-Flock\*, PoUW\*, bench/commitments ; tests only: vLLM | proofs: same question as for `vllm_v1`. Is `frame_v3` the one framing, or a superseded one that is kept so A-GKR's and B-Ligero's records replay? |
| `verity/commitments/frame_v3/vectors.py` | `packages/verity/tests/commitments` (generating test) | Tests convention: test-only code moves into tests | medium | tests only: B-Ligero† | proofs: the generator becomes a generating test. The JSON it writes stays beside the reference as the agreement spec, because C-Flock's Lean verifier and the Rust verifiers read it. vLLM's and B-Ligero's tests import some generators today, and would read the JSON instead. |
| `verity/commitments/frame_v3/vectors_sha512.py` | `packages/verity/tests/commitments` (generating test) | Tests convention: test-only code moves into tests | medium | — | proofs: the generator becomes a generating test. The JSON it writes stays beside the reference as the agreement spec, because C-Flock's Lean verifier and the Rust verifiers read it. vLLM's and B-Ligero's tests import some generators today, and would read the JSON instead. |
| `verity/commitments/hm96/__init__.py` | `verity/primitives/commitments/hm96` | P1: C-Flock's verifier of record and sampled proofs read it | high | C-Flock\*, PoUW\*, bench/commitments, sampled-proofs\*, vLLM |  |
| `verity/commitments/hm96/vectors.py` | `packages/verity/tests/commitments` (generating test) | Tests convention: test-only code moves into tests | medium | tests only: vLLM | proofs: the generator becomes a generating test. The JSON it writes stays beside the reference as the agreement spec, because C-Flock's Lean verifier and the Rust verifiers read it. vLLM's and B-Ligero's tests import some generators today, and would read the JSON instead. |
| `verity/commitments/identity.py` | `verity/primitives/commitments/identity` | P1: the commitment primitives every protocol uses | high | C-Flock\*, PoUS\*, bench/network_traces, bench/one_stage, bench/pous, sampled-proofs\*, vLLM, warden\* |  |
| `verity/commitments/indexed.py` | `verity/primitives/commitments/indexed` | P1: the commitment primitives every protocol uses | high | C-Flock\*, bench/commitments, bench/one_stage, sampled-proofs\*, vLLM |  |
| `verity/commitments/leaves.py` | `verity/primitives/commitments/leaves` | P1: `vllm_v1` imports it | medium | SP1†, numerical, vLLM ; tests only: backends/shared | proofs: same question as for `vllm_v1`: is `verity-vllm/leaf/v1` the current row framing? |
| `verity/commitments/limits.py` | `verity/primitives/commitments/limits` | P1: the commitment primitives every protocol uses | high | — |  |
| `verity/commitments/merkle.py` | `verity/primitives/commitments/merkle` | P1: the commitment primitives every protocol uses | high | A-GKR†, B-Ligero†, C-Flock\*, bench/commitments, bench/one_stage, bench/pouw, sampled-proofs\*, vLLM ; tests only: backends/shared |  |
| `verity/commitments/multiproof.py` | `experimental/commitments/multiproof` | P9: no guarantee depends on it | low | tests only: B-Ligero† | proofs: only B-Ligero's tests import it from outside core, plus two archive-bound `proofs` modules. Should it go to `experimental/` (it still runs) or to `archive/` with B-Ligero? |
| `verity/commitments/poseidon2_babybear.py` | `archive/direct` (B-Ligero) | P8: the hash of a frozen backend (B-Ligero's Table 2 cell) | medium | B-Ligero† | proofs: should it go to `archive/` with B-Ligero, or to `experimental/` in case a field-native proof system needs it? |
| `verity/commitments/rowleaf.py` | `verity/primitives/commitments/rowleaf` | P1 | medium | A-GKR†, B-Ligero†, C-Flock\*, PoUW\*, bench/commitments, sampled-proofs\*, vLLM ; tests only: backends/shared | proofs: its `poseidon2-babybear-w24/row/v2h` schema imports the archive-bound `poseidon2_babybear`, so that schema has to be split out first. |
| `verity/commitments/scheme.py` | `verity/primitives/commitments/scheme` | P1: the commitment primitives every protocol uses | high | bench/commitments |  |
| `verity/commitments/turboshake.py` | `verity/primitives/crypto/turboshake` | P1: PoUW imports it | medium | PoUW\*, bench/pouw | proofs: same question as for `blake3`. |
| `verity/commitments/vllm_v1/__init__.py` | `verity/primitives/commitments/vllm_v1` | P1: `hm96` imports it, so it goes wherever `hm96` goes | medium | A-GKR†, B-Ligero†, C-Flock\*, bench/commitments, vLLM ; tests only: backends/shared | proofs: the layout keeps one Merkle tree and one SHA-512 row hash. Which framing is the current one, and which become superseded entries? |
| `verity/commitments/vllm_v1/vectors.py` | `packages/verity/tests/commitments` (generating test) | Tests convention: test-only code moves into tests | medium | tests only: vLLM | proofs: the generator becomes a generating test. The JSON it writes stays beside the reference as the agreement spec, because C-Flock's Lean verifier and the Rust verifiers read it. vLLM's and B-Ligero's tests import some generators today, and would read the JSON instead. |
| `verity/commitments/vllm_v1/vectors_sha512.py` | `packages/verity/tests/commitments` (generating test) | Tests convention: test-only code moves into tests | medium | — | proofs: the generator becomes a generating test. The JSON it writes stays beside the reference as the agreement spec, because C-Flock's Lean verifier and the Rust verifiers read it. vLLM's and B-Ligero's tests import some generators today, and would read the JSON instead. |

### `verity.ml`, the word level

Principle 3 puts the word Definitions in the catalog: the builder is the source, and what's digest-addressed is its
descriptor at given statics. Five of these nine modules mix destinations and split; they are listed below the table.

Two non-module files move too. `ml/tables/` (eight measured MUFU tables) goes to `catalog/hardware/sm89/mufu/`.
`ml.mufu` and `ml.boolean.mufu` find it through `resources.files("verity.ml") / "tables"`, so that lookup changes with
it. `ml/annotations.json` goes to `catalog/annotations/`.

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/ml/__init__.py` | dissolves (package init) | the package dissolves | high | — |  |
| `verity/ml/prims.py` | const (Const<w> family) to `verity/primitives/circuits`; the cast and dot Definitions to `catalog/definitions/prims` | P3 (Definitions), P4 (the constant family) | medium | PoUW\*, circuit_check, numerical, vLLM ; tests only: C-Flock\*, SP1†, sampled-proofs\* | circuits: is `const` (the `Const<w>` family, which delegates w = 1 to `ir.boolean.constant`) a Boolean-basis primitive? PoUW's `circuit/hashes.py` imports it. |
| `verity/ml/gemm.py` | `catalog/definitions/gemm` | P3: word Definitions | medium | C-Flock\*, circuit_check, numerical, vLLM |  |
| `verity/ml/scalar.py` | `catalog/definitions/scalar` | P3: word Definitions | medium | C-Flock\*, PoUW\*, vLLM ; tests only: sampled-proofs\* | circuits: PoUW's circuit builders and C-Flock's `ir_sampling` import it at module level, which is a forbidden import once they are in `verity/` (see the forbidden-import splits). |
| `verity/ml/fp32.py` | bit-level FP32/BF16 functions to `verity/primitives/fp` (bridged with ml.tc.fp32); the F32*V2 Definitions to `catalog/definitions/fp32` | P3 (Definitions); step 5's one FP semantics (the bit functions) | medium | PoUW\*, vLLM ; tests only: C-Flock\* | compute-accounting: its bit functions duplicate `ml.tc.fp32`. Should they be bridged by vectors and consolidated in step 5, or now? |
| `verity/ml/mufu.py` | `catalog/definitions/mufu` | P3: Definitions over measured tables; `tables/` goes to `catalog/hardware/sm89/mufu` | medium | C-Flock\*, vLLM |  |
| `verity/ml/library.py` | Table/table/digest mechanism to `verity/primitives/circuits/library`; LIBRARY/PROGRAM/LABELS entries to `catalog/library` | P3 or P1 | low | C-Flock\* ; tests only: vLLM | proofs and circuits: seven C-Flock modules and two of its verifier agreement scripts bind the library's digest. Is the list of tables a public parameter that the verifier chooses (catalog), or part of the verifier (TCB)? Recommend splitting the mechanism from the list. |
| `verity/ml/operations.py` | the no-data guard to `verity/primitives/circuits/constants` (beside ir.constants); the pinned operation list to `catalog/definitions/operations` | P1 (the no-data guard protects zero-knowledge), P3 (the pinned list) | medium | tests only: circuit_check, vLLM | circuits: should the guard go beside `ir.constants`, which already takes the list as a parameter? |
| `verity/ml/kernels.py` | generic numpy kernels to `verity/kernels/tc`; the ScalarReference instances and _register_references to `catalog/hardware/tc/references` | P5 | medium | B-Ligero†, bench/pouw, circuit_check, numerical, vLLM ; tests only: C-Flock\* | compute-accounting and circuits: should the generic numpy kernels be the `tc` entries of `verity/kernels/`, with the instance references registered from the catalog? |

### `verity.ml.tc`, split between `verity/primitives/fp/` and `catalog/hardware/tc/`

This package decides the most. `ml.tc` is the exact tensor-core and FP semantics, stdlib only, and its Lean twin is
core's spec. Its `layers` entry says `Protocol.TC.Spec` transcribes `total.py`, `models.py` and `term.py`, and that
`Protocol.TC.Relation` transcribes `relation.py`. The lock's `reads` name both, for the 18 guarantees in `Guarantees.TC`.

The Lean already separates a model's shape from its instances. `Pipeline.lean` defines a generic `Pipeline` structure
and four device instances (`HOPPER_BF16_WGMMA_K16`, `HOPPER_BF16_M16N8K16`, `AMPERE_BF16_M16N8K16`,
`ADA_BF16_M16N8K16`), and `Spec.lean` is a generic interpreter (`tcDotTotal (p : Pipeline)`). Principle 3 says public
parameters are data, not code, so this map splits the Python the same way:
- the interpreter and format semantics go to `verity/primitives/fp/`, beside the spec that describes them: `Model`,
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
| `verity/ml/tc/__init__.py` | `verity/primitives/fp/__init__` (re-exports narrowed to the generic semantics) | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data | medium | — | captain, compute-accounting and circuits: `verity/primitives/fp/` is not in the layout. Should it be added, or should all of `ml.tc` go to `catalog/hardware/tc`, with protocols taking models as parameters? See open question 1. |
| `verity/ml/tc/cast.py` | `verity/primitives/fp/cast` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data | medium | B-Ligero†, C-Flock\*, PoUW\*, SP1†, numerical, tc_probe ; tests only: vLLM | See open question 1. |
| `verity/ml/tc/errors.py` | retire (shim) | P8: superseded infrastructure (a shim re-exporting `verity.errors.InvalidArtifact`) | high | numerical, tc_probe_fp4 |  |
| `verity/ml/tc/fp32.py` | `verity/primitives/fp/fp32` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data | medium | PoUW\*, bench/pouw | See open question 1. |
| `verity/ml/tc/instructions.py` | `catalog/hardware/tc/instructions` | P3: the PTX instruction-class index (model, status, evidence) is data | medium | numerical, tc_probe ; tests only: vLLM |  |
| `verity/ml/tc/models.py` | Model, GroupSum, BlockScaledAlignAdd, tc_dot to `verity/primitives/fp/models`; the 17 public instance constants to `catalog/hardware/tc/instances` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data, so instances and interpreter split as in `Pipeline.lean` and `Spec.lean` | medium | A-GKR†, B-Ligero†, C-Flock\*, PoUW\*, bench/pouw, numerical, tc_probe, tc_probe_fp4 ; tests only: vLLM | See open question 1. |
| `verity/ml/tc/relation.py` | `catalog/cost_models/tc_relation` | P3: cost models | low | numerical | proofs: its Lean twin `Protocol.TC.Relation` is spec that the step guarantees read, but no running code uses the Python, only numerical's census. Is it spec-side code (`verity/`), a cost model (`catalog/`), or `experimental/`? |
| `verity/ml/tc/silicon.py` | retire (shim; importers move to models/total) | P8: superseded infrastructure (a shim re-exporting `term` and `models`); its importers switch to `models` in a prep PR | high | B-Ligero†, C-Flock\*, VOLE†, numerical, tc_probe, tc_probe_fp4, vLLM |  |
| `verity/ml/tc/term.py` | `verity/primitives/fp/term` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data | medium | A-GKR†, B-Ligero†, PoUW\*, numerical, tc_probe_fp4 | See open question 1. |
| `verity/ml/tc/total.py` | generic total step to `verity/primitives/fp/total`; its instance constants to `catalog/hardware/tc/instances` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data, so instances and interpreter split as in `Pipeline.lean` and `Spec.lean` | medium | C-Flock\*, numerical, tc_probe, vLLM | See open question 1. |
| `verity/ml/tc/total_fp8.py` | generic E4M3/E5M2 step to `verity/primitives/fp/total_fp8`; HOPPER_E4M3_WGMMA_K32 to `catalog/hardware/tc/instances` | P2: its Lean twin `Protocol.TC.Spec` is core spec, read by the TC guarantees; P3: the instances are data, so instances and interpreter split as in `Pipeline.lean` and `Spec.lean` | medium | PoUW\* ; tests only: vLLM | See open question 1. |

### `verity.ml.boolean`

circuits' split decides most of these rows. The Boolean basis, the lowering, the evaluator, and SHA-512 and Merkle as
gates are TCB primitives; the word Definitions and their Boolean versions are catalog entries. `forms` is the GF(2)
builder under `trace`, and every Boolean module imports it. None of the verity-bound modules (`trace`, `forms`,
`gather`, `sha512`, `merkle`) imports a catalog-bound one, so this split is clean inside core.

| Current path | Destination | Principle | Confidence | Imported by (other areas) | Owner question |
|---|---|---|---|---|---|
| `verity/ml/boolean/__init__.py` | dissolves (package init) | the package dissolves | high | — |  |
| `verity/ml/boolean/attention.py` | `catalog/definitions/boolean/attention` | P3: the Boolean versions of word Definitions | medium | circuit_check, vLLM |  |
| `verity/ml/boolean/cast.py` | `catalog/definitions/boolean/cast` | P3: the Boolean versions of word Definitions | medium | circuit_check |  |
| `verity/ml/boolean/elementwise.py` | `catalog/definitions/boolean/elementwise` | P3: the Boolean versions of word Definitions | medium | circuit_check, vLLM |  |
| `verity/ml/boolean/forms.py` | `verity/primitives/circuits/boolean/forms` | P3, circuits' split: the GF(2) builder under the lowering | medium | C-Flock\*, PoUW\*, vLLM | circuits: `trace` and every Boolean Definition build on it. Does "the lowering" in your split include it? |
| `verity/ml/boolean/fp.py` | `catalog/definitions/boolean/fp` | P3: the Boolean versions of word Definitions | medium | C-Flock\*, PoUW\*, vLLM |  |
| `verity/ml/boolean/fp4.py` | `catalog/definitions/boolean/fp4` (or `experimental/nvfp4`) | P3, or P9 if NVFP4 is experimental | low | C-Flock\* | compute-accounting: the plan lists `pearl-c-nvfp4-v0` under `experimental/`, but C-Flock's `unit_fp4` imports this module, and `boolean.gemm`'s NVFP4 and MXFP4 coordinates import it too. If it is experimental, those coordinates have to split out with it. |
| `verity/ml/boolean/gather.py` | `verity/primitives/circuits/boolean/gather` | P4: a generic gadget | medium | vLLM | circuits: only `universal` and vLLM import it. Does it go to `verity/`, or to the catalog as a piece? |
| `verity/ml/boolean/gemm.py` | `catalog/definitions/boolean/gemm` | P3: the Boolean versions of word Definitions | medium | circuit_check, vLLM ; tests only: C-Flock\* |  |
| `verity/ml/boolean/merkle.py` | `verity/primitives/commitments/gates/merkle` | P3, circuits' split: Merkle as gates is a TCB primitive | high | C-Flock\*, circuit_check |  |
| `verity/ml/boolean/mufu.py` | `catalog/definitions/boolean/mufu` | P3: the Boolean versions of word Definitions | medium | circuit_check, vLLM |  |
| `verity/ml/boolean/scalar.py` | `catalog/definitions/boolean/scalar` | P3: the Boolean versions of word Definitions | medium | C-Flock\*, circuit_check, vLLM |  |
| `verity/ml/boolean/sha512.py` | `verity/primitives/commitments/gates/sha512` | P3, circuits' split: SHA-512 as gates is a TCB primitive; step 5 bridges it to commitments' SHA-512 by vectors | high | C-Flock\* |  |
| `verity/ml/boolean/softmax.py` | `catalog/definitions/boolean/softmax` | P3: the Boolean versions of word Definitions | medium | C-Flock\*, vLLM |  |
| `verity/ml/boolean/tc_step.py` | `catalog/definitions/boolean/tc_step` | P3: the Boolean versions of word Definitions | medium | C-Flock\* |  |
| `verity/ml/boolean/trace.py` | `verity/primitives/circuits/boolean/trace` | P3, circuits' split: the lowering is a TCB primitive | high | PoUW\*, bench/private_circuit, circuit_check, vLLM ; tests only: C-Flock\* |  |
| `verity/ml/boolean/universal.py` | `experimental/private_circuits/universal` | P9: protocol 2 (private circuits) has no guarantee yet | low | bench/private_circuit, circuit_check ; tests only: C-Flock\* | circuits and proofs: should it go to `experimental/`, or to the catalog as a Definition? |

### `verity.proofs`

Most of `verity.proofs` is D-SP1's typed-obligation and lowering stack. SP1, `benchmarks/ir_call` and
`benchmarks/dot_product` use it, and it goes to `archive/sp1/`. Four modules are live:
- `profile` goes to `verity/`;
- `codes` goes to `verity/`;
- `target` goes to the catalog;
- `query` is vLLM's.

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
| `verity/proofs/codes.py` | `verity/codes` (beside errors) | P1: wire constants beside `errors` | medium | bench/ir_call, vLLM | proofs: should it keep the full veritor enum, which exists only so `fixtures/proof-format-v3` (an SP1 fixture) decodes, or move the SP1-only codes to `archive/sp1`? |
| `verity/proofs/conformance.py` | `archive/sp1/proofs/conformance` (test-only) | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | bench/dot_product | proofs: it is test-only apart from `benchmarks/dot_product/vector_run.py`, which goes to archive with it. |
| `verity/proofs/elem_bf16.py` | `archive/sp1/proofs/elem_bf16` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1† |  |
| `verity/proofs/families.py` | `archive/sp1/proofs/families` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1† |  |
| `verity/proofs/gateset.py` | `archive/sp1/proofs/gateset` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1† |  |
| `verity/proofs/int8.py` | `archive/sp1/proofs/int8` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | — |  |
| `verity/proofs/lowering.py` | `archive/sp1/proofs/lowering` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/ir_call ; tests only: vLLM | proofs: a vLLM test imports it. Does that test go to archive, or get dropped? |
| `verity/proofs/packed.py` | `archive/sp1/proofs/packed` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/ir_call, numerical | proofs: numerical (whose bench spine is live) and `benchmarks/ir_call` import it, and nothing imports archive code, so those importers have to split first. |
| `verity/proofs/profile.py` | `verity/protocols/verification/profile` | P1: sampled proofs and PoUW read the audit's output | medium | PoUW\*, sampled-proofs\* ; tests only: C-Flock\* | proofs: should it sit beside sampled proofs under `verification/`, or in a shared `verity/protocols/` module? |
| `verity/proofs/programs.py` | `archive/sp1/proofs/programs` (test-only) | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | — | proofs: five catalog-bound target tests build Programs with it. Do those tests go to `archive/sp1` (they check the targets against SP1's obligations)? |
| `verity/proofs/query.py` | `integrations/vllm` (or fold into `verity/primitives/circuits/query`) | P7: only vLLM uses it (15 files) | low | vLLM | circuits: it is the Draft 3.1 query over Programs, and `ir.query` and `ir.partition_object` are the current ones. Should vLLM migrate to those and this one be superseded, or should it move into vLLM? |
| `verity/proofs/reduce_mufu.py` | `archive/sp1/proofs/reduce_mufu` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/ir_call |  |
| `verity/proofs/schema.py` | `archive/sp1/proofs/schema` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | — |  |
| `verity/proofs/statement.py` | `archive/sp1/proofs/statement` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | — |  |
| `verity/proofs/target.py` | `catalog/targets/target` | P3: the frozen first subcircuit is a public parameter | medium | A-GKR†, B-Ligero†, C-Flock\*, SP1†, bench/dot_product, numerical, tc_probe | proofs: it imports name constants from the archive-bound `families`, so those have to move into it first. |
| `verity/proofs/transparent.py` | `archive/sp1/proofs/transparent` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | — |  |
| `verity/proofs/typed_obligation.py` | `archive/sp1/proofs/typed_obligation` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/ir_call |  |
| `verity/proofs/wire.py` | `archive/sp1/proofs/wire` | P8: D-SP1's obligation and lowering stack; D-SP1 is frozen | medium | SP1†, bench/ir_call |  |

## Lean: `packages/verity/lean/`

The step-3 pilot is a pure move: every spec module stays, every lemma and proof goes to `security_proofs/core/`, and no
module name changes. The `layers` column is the module's entry in `lean-audit.json` (its six `layers` keys are all
spec modules), and "read by a pin" means a guarantee's statement or the `reads` section names it.

| Module(s) | Files | Layer | Read by a pin | Step 3 | Later | Confidence |
|---|---|---|---|---|---|---|
| `Verity.Assumptions` | 1 | `Verity.Assumptions` (the assumptions module) | yes: `GemmAmpereStep`, `GemmHopperStep`, `StepInputs` | spec, stays | the two device assumptions could go to catalog Lean with the tensor-core instances | high (step 3); medium (later) |
| `Verity.Guarantees`, `Guarantees/{Circuit, Game, TC}` | 4 | `Verity.Guarantees` | yes: the statements of all 29 guarantees | spec, stays | `Guarantees.TC` names the Ampere and Hopper instances, so it follows them if they move to catalog Lean | high |
| `Verity.Protocol` (umbrella) | 1 | `Verity.Protocol` | umbrella only | spec, stays | NCI's `Nci/Protocol.lean` imports this umbrella, so narrow that import to what NCI reads before any module leaves the umbrella | high |
| `Protocol/{Circuit, Declaration, Game, Partition}` | 4 | `Verity.Protocol` | yes | spec, stays: core's one circuit and game model (principle 4) | none | high |
| `Protocol/TC.lean`, `TC/{Bridge, Gadgets, Pipeline, Relation, Spec}` | 6 | `Verity.Protocol`; `Pipeline`, `Spec` and `Relation` have layers of their own | yes | spec, stays | `Pipeline.lean`'s four instances to catalog Lean ("device instances in Lean"); the generic `Spec` stays beside `verity/primitives/fp/` | high (step 3); medium (later) |
| `Protocol/Boolean` | 1 | `Verity.Protocol` | no | spec, stays | the validator will report it as unread. It is the spec of the Boolean basis, which circuits calls TCB, so recommend keeping it and having a guarantee about the lowering read it | medium |
| `Protocol/{Fp32, Prims, Scalar}` | 3 | `Verity.Protocol` | no | spec, stays (a pure move) | transcriptions of catalog Definitions (`ml.fp32`, the casts in `ml.prims`, `ml.scalar`) that no pin reads. PoUW's `RowOps` (in PoUW's own `Protocol`) takes such operations as fields and doesn't import these modules. Candidates for catalog Lean or `security_proofs/` | low |
| `Verity.lean` (root umbrella) | 1 | `roots` | no | `security_proofs/core/`, as its umbrella: it imports `Verity.SecurityProofs` | none | high |
| `Verity.SecurityProofs` and `SecurityProofs/*` | 43 | the math | the proofs of the 29 pins | `security_proofs/core/`, names unchanged | consolidated in step 3.3 | high |

The 43 math modules are `SecurityProofs.lean`, plus five at its top level (`Boolean`, `Circuit`, `Fp32`, `Game`,
`TC`), `Game/*` (12), `TC/*` (22: `Ampere.lean`, `AmpereSound`, `Boundary`, `Gadgets`, `Proofs.lean`, `Sound`,
`Vectors`, six under `Ampere/` and nine under `Proofs/`), and `Fp32/Vectors`, `Prims/Vectors` and `Scalar/Vectors`.

The lock splits only at package level, as the plan's step 3 says:
- `roots` goes from `["Verity"]` to the spec's three meaning modules on the spec side, and to the `Verity` umbrella on
  the math side.
- The six `layers` entries stay with the spec.
- The 29 `guarantees` (each `Verity.SecurityProofs.X : Verity.Guarantees.X`) and the 13 `reads` modules (all spec)
  stay byte-identical.
- `dependencies` (the Mathlib manifest and the toolchain) is copied to both packages, since both require Mathlib.

Each pin's proof name then points into the math package, which is what the validator change on the critical path
(item 3) handles.

Four of the math modules are generated vectors: `TC/Vectors.lean`, `Fp32/Vectors.lean`, `Scalar/Vectors.lean` and
`Prims/Vectors.lean`. Principle 2 sends generated vectors to the catalog, but step 3 moves them with the math, under
their names. They are written and checked by `tests/ml/test_lean_vectors.py`, `test_lean_fp32_vectors.py` and
`test_lean_scalar_vectors.py`, which name the files by path (`packages/verity/lean/Verity/SecurityProofs/...`). Those
paths, and the verity suite's declared inputs, must change in the same commit as the move, or the Python half of the
check silently stops comparing.

Across packages: NCI's spec imports `Verity.Protocol`, and its `SecurityProofs` and `SecurityProofs/Chain` import
`Verity.SecurityProofs`. PoUW's `Protocol/PearlC/*` imports `Verity.Protocol.Partition` and `Verity.Protocol.Game`,
and its `SecurityProofs/PearlC/*` imports `Verity.SecurityProofs.{Game, Circuit, Game.Prob}`. No protocol's spec
imports core's math, so the split creates no forbidden Lean `require`. NCI's and PoUW's math packages will need
`security_proofs/core/`, which is moot once the proofs become one package.

## `census/`

| Current path | Destination | Principle | Confidence | Read by | Owner question |
|---|---|---|---|---|---|
| `census/{hardware, datatypes, networks, subcircuits, input_sets, workloads}.json` | `catalog/census/` | P3: the census is a catalog entry | high | read as files by `verity_numerical.bench.census`, the table renderer, benchmarks and the docs site; nothing imports it | captain and comms: AGENTS.md says the census is meant to move to its own repository. Is `catalog/census/` the step before that, or does it replace it? |
| `census/schemas/*.schema.json` (6) | `catalog/census/schemas/` | P3 | high | the same | none |
| `census/README.md` | `catalog/census/README.md` | P3 | high | none | none |

`test_core_never_reads_the_census` in core's `test_boundaries.py` becomes "`verity/` never reads `catalog/`", which
the merged boundary test checks (see "Tests").

## `fixtures/`

| Current path | Destination | Principle | Confidence | Read by | Owner question |
|---|---|---|---|---|---|
| `fixtures/artifacts.json` | stays at the root | the registry of every fixture's art id (store README §7.3) | low | `tools/research`, `tools/check`, `tests/test_repository.py`, several backends and vLLM | infra and ci: should it stay at the root, or go to `catalog/`, since its entries are digest-addressed? |
| `fixtures/bench-instances/` (85 files) | `catalog/input_sets/` | P3 | medium | `census/input_sets.json`, most backends, `benchmarks/`, vLLM, `tools/research`, `tools/tc_probe` | compute-accounting and infra: should these go to the catalog, or to `benchmarks/`, since the benchmark tables are their readers? |
| `fixtures/discrepancy_log.json` | `catalog/hardware/tc/` | P3: evidence for the device models | medium | core's `proofs/test_discrepancy_log.py`, numerical, `ligero-verify`, SP1, `tools/tc_probe` | none |
| `fixtures/hawkeye/` (1) | `catalog/hardware/tc/` | P3 | medium | core, numerical, `tools/tc_probe` | none |
| `fixtures/tc/` (13) | `catalog/hardware/tc/captures/` | P3 | medium | core's `ml` tests, numerical, B-Ligero, vLLM, PoUW, `tools/check`, `tools/tc_probe` | none |
| `fixtures/proof-format-v3/` (2) | `archive/sp1/` | P8 | medium | SP1; `proofs.codes` keeps its full enum for these | see `proofs.codes` |
| `fixtures/typed-obligation-v0/` (141) | `archive/sp1/` | P8 | medium | SP1, numerical, `benchmarks/dot_product`, `benchmarks/judge.py`, core's target tests | proofs: catalog-bound target tests read it, which is the same question as for `proofs.programs` |
| `fixtures/redteam/` (108), `redteam-3/` (16), `redteam-zk/` (4) | `archive/`, beside `backends/redteam` and the frozen backends | P8 | low | B-Ligero, A-GKR, `ligero-verify`, numerical, `backends/redteam` | proofs and infra: should they be archived with the frozen backends, or kept in `experimental/`, since red-team verdicts are labels that tables read? |
| `packages/verity/tests/ml/fixtures/` (130: the `gemm-B1-…` capture with 117 files, `golden/`, `gpu-nan-…`, `tc-hopper-…`, four `tc-sm120-…` sets, a README) | the catalog's `hardware/tc` tests | P3 | medium | core's `ml` tests | compute-accounting and circuits: is the 117-file `gemm-B1` capture a row capture under Daniel's 1:30 PM PDT ruling (not stored, or shrunk to what Match reads)? |

## Tests

### Core's tests (`packages/verity/tests/`)

| Current path | Destination | Principle | Confidence | Note |
|---|---|---|---|---|
| `tests/ir/` (17 tests, 6 vectors files) | verity's tests, beside `primitives/circuits/` | Tests convention | high | Seven of the 17 tests import `ml.prims` or `ml.scalar` to register Definitions before decoding: `test_annotations`, `test_codec`, `test_constants`, `test_partition_object`, `test_qcall_vectors`, `test_qword_vectors` and `test_units`. See "Test-only edges". |
| `tests/evaluation/` (3) | verity's tests | Tests convention | medium | All three import catalog-bound modules. `test_bits` imports `ml.boolean`, and `test_evaluation` imports `ml.tc.models`, `total` and `total_fp8` for the self-check of every registered kernel that AGENTS.md requires. `test_registered_tables` is the third. |
| `tests/randomness/` (1 test, `vectors.json`) | verity's tests | Tests convention | high | none |
| `tests/claims/` (1) | verity's tests | Tests convention | medium | It follows `claims`. |
| `tests/commitments/` (16) | verity's tests; `test_poseidon2` to `archive/direct`, `test_multiproof` to `experimental/` | Tests convention | medium | The vectors generators become generating tests here. |
| `tests/proofs/` (13) | split. `test_profile` and `test_query` follow their modules. The five target tests (`test_target`, `test_bf16_hopper_target`, `test_fp8_targets`, `test_fp8_sm120_target`, `test_nvfp4_target`) and `test_tc_probe_families` go to `catalog/targets`. `test_discrepancy_log` goes to `catalog/hardware/tc`. `test_conformance`, `test_gateset`, `test_int8` and `test_reduce_mufu` go to `archive/sp1`. | Tests convention, P8 | medium | `test_profile` imports `verity.ml`. |
| `tests/ml/` (29 tests, 130 fixture files) | split with their modules: semantics tests to the tests of `verity/primitives/fp/`, Definition, instance and capture tests to the catalog | Tests convention | medium | `test_lean_vectors`, `test_lean_fp32_vectors` and `test_lean_scalar_vectors` follow the Lean move. |
| `tests/test_boundaries.py` | merges with the two root boundary tests | P6, P9 | medium | Its `ALLOWED`, `FORBIDDEN_EXTERNAL`, `NUMPY_FREE` and census rules are rewritten for the new layout. |

The verity suite's declared inputs read `census`, four `fixtures/` paths, `tools/tc_probe`,
`tools/tc_probe_fp4/probe.py` and five `backends/numerical` files. Under this map every test that reads them moves to
the catalog's or the archive's suite: `test_tc_probe_families`, `test_instructions`, `test_discrepancy_log`, the target
tests, `test_models`, `test_total_fp8` and `test_wgmma_bf16`. The verity suite would then read nothing outside
`verity/`, which makes its declared inputs a free check of principle 6.

### The root `tests/`

| Current path | Destination | Principle | Confidence | Owner question |
|---|---|---|---|---|
| `test_repository.py`, `test_no_wall_clock.py`, `test_lean_packages.py`, `test_uv_pin.py` | stay in `tests/` | Tests convention: whole-tree invariants | high | none (`test_lean_packages.py` lists the Lake packages, so it changes with the Lean move) |
| `test_backend_boundaries.py`, `test_protocol_boundaries.py` | merge with core's `test_boundaries.py` into one boundary test in `tests/` | P6, P9 | medium | ci: the merged test would check four rules. `verity/` imports nothing else; `catalog/` imports only `verity/`; nothing in `verity/` imports `experimental/`; nothing imports `archive/`. |
| `test_pous_bench.py`, `test_pous_explorer.py`, `test_pous_harness.py`, `test_pous_p2v1.py` | `benchmarks/pous/tests/` | Tests convention: they load `benchmarks/pous/bench.py` and `explorer.py` by path, so they are that package's tests, not whole-tree invariants | medium | memory-accounting: should they go to `benchmarks/pous/tests/`, or to PoUS's own tests? |

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
6. `ml.operations`' guard imports `ml.library`'s table list. Split it: the guard goes to `verity/` and the pinned list
   to the catalog, and the same goes for `ml.library` itself (mechanism to `verity/`, entries to the catalog).
7. `ml.prims`: move `const` (the `Const<w>` family) to `verity/` beside `ir.boolean.constant`. The Definitions stay
   in the catalog. PoUW's `circuit/hashes.py` is the importer that needs this.
8. `ml.fp32`: move the bit-level FP32 and BF16 functions to `verity/primitives/fp/`, bridged by vectors with
   `ml.tc.fp32`. The `F32*V2` Definitions stay in the catalog.
9. This one applies only if NVFP4 is ruled experimental. `ml.boolean.gemm` (catalog) imports `ml.boolean.fp4`, so the
   NVFP4 and MXFP4 coordinates (`GemmCoordinateNvf4_v2`, `GemmCoordinateMxf4_v2`) split out with `fp4`.

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
- **PoUW** (to `verity/protocols/accounting/work/`):
  - the Definitions in `ml.prims`, `ml.scalar` and `ml.fp32`: `circuit/pc4.py`, `pc8.py` and `rowk.py`;
  - `ml.prims.const`: `circuit/hashes.py`;
  - `ml.boolean.fp`: `circuit/boolean.py`;
  - the tensor-core instance constants: `schemes/pearl_c4.py`, `pearl_c_device.py` and `pearl_kw.py`.

  Its imports of `ml.boolean.forms` and `trace`, and of `ml.tc.fp32` and `cast`, are allowed under the split.
  `lean/scripts/h1t_vectors.py` and `fp8atom_vectors.py` are vector generators, which are tools and may import
  anything.
- **Sampled proofs, PoUS and the warden**: none. Their source imports only `proofs.profile`, `claims`,
  `commitments.identity`, `randomness` and other verity-bound modules.

Most of the C-Flock and PoUW edges come from protocol code that builds a Program out of catalog Definitions (PoUW's
`circuit/`, C-Flock's lowering and units). Either that builder code goes to the catalog as the builders of
Definitions and Programs, or the protocol code takes the Definitions, models and tables as parameters chosen by the
verifier's side (principle 3). Open question 2 asks which.

### Test-only edges

Some core tests of verity-bound modules import catalog-bound ones:
- seven `ir` tests (they register `ml.prims` and `ml.scalar` Definitions so the codec can decode);
- all three `evaluation` tests;
- `proofs/test_profile.py`.

Sampled proofs' tests import `ml.prims` and `ml.scalar` the same way. If the boundary test covers tests, these either
move to the catalog's suite (and the registered-kernel self-check list in `test_evaluation.py` becomes the catalog's),
or verity's tests register a toy Definition instead. Open question 5.

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

1. **captain, compute-accounting, circuits: where do the FP and tensor-core semantics live?** The recommendation is
   to split, as in the Lean: the generic interpreter goes to a new `verity/primitives/fp/`, and the instances and the
   instruction index go to `catalog/hardware/tc/`. The alternative puts all of `ml.tc` in the catalog. That keeps the
   layout as written, but then C-Flock, PoUW and `ml.kernels` must take every model as a parameter, and the Lean TC
   spec has to move to catalog Lean with it.
2. **circuits, compute-accounting: where does protocol code that builds Programs from catalog Definitions go?** This
   covers PoUW's `circuit/` and C-Flock's `unit`, `unit_fp4`, `fp`, `tail_pieces`, `boolean_export`, `ir_sampling`
   and `lowering`. It decides most of the forbidden imports from outside core. The recommendation is that builders go
   to the catalog, and the protocol code in `verity/` takes a Program or a Definition by digest.
3. **proofs, circuits: is `ml.library` part of the verifier or a public parameter?** C-Flock binds its digest in
   seven modules. The recommendation is to split the mechanism from the list of tables.
4. **proofs: which commitment framing is the "one Merkle tree, one SHA-512 row hash"?** That is `frame_v3`,
   `vllm_v1`/`leaves` or `rowleaf`. Do `multiproof` and `poseidon2_babybear` go to `experimental/` or `archive/`?
   `blake3` and `turboshake`: `crypto/` or `commitments/`?
5. **ci, circuits: may verity's tests import the catalog?** If not, the seven `ir` tests, the three `evaluation`
   tests and `test_profile` move to the catalog's suite or switch to a toy registration.
6. **compute-accounting: is NVFP4 catalog or experimental?** It involves `ml.boolean.fp4`, `boolean.gemm`'s NVFP4 and
   MXFP4 coordinates, and the FP4 instances in `models`. C-Flock's `unit_fp4` imports it today.
7. **proofs: four smaller calls.** Is `ml.tc.relation` spec-side code, a cost model or experimental? Should
   `proofs.codes` keep the full veritor enum? Do the target tests that use `proofs.programs` go to the archive? And
   `claims`: `verity/` or catalog data?
8. **circuits: seven smaller calls.** `ir.liveness` (verity or `tools/circuit_check`), `ir.annotations` (catalog or
   tools), `proofs.query` (supersede with `ir.query` or move to vLLM), `boolean.universal` (experimental),
   `boolean.gather`, the `ml.operations` guard, and `ml.prims.const`.
9. **lean, proofs: the unread spec modules.** Do `Protocol.Boolean`, `Fp32`, `Prims` and `Scalar` stay in the spec?
   Where do the four `Vectors.lean` files go after step 3 (the catalog, per principle 2)?
10. **infra, ci: fixtures.** Where do `fixtures/artifacts.json`, the red-team fixtures and `bench-instances` go?
11. **captain, with the inventory worker: do Python import names follow directories?** For example, does
    `verity.ir` become `verity.primitives.circuits`? If they don't, every step-5 move can be a pure move, as the Lean
    ones are.
12. **captain, comms: does the census still go to its own repository,** or is `catalog/census/` its home?
13. **memory-accounting: where do the root `test_pous_*` files go?** The options are `benchmarks/pous/tests/` and
    PoUS's own tests.
