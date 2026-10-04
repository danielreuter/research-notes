---
id: 20261004T2125Z-draft-move-map-protocols
campaign: verity
lane: verity-root
kind: draft
status: open
repo: danielreuter/verity
origin: worker of verity-top's repository-layout agent (bc-d6f8b221); for owners (compute-, memory-, network-accounting, lean) to correct
---

# Move map: `protocols/` and `benchmarks/`

This draft maps every module in `protocols/` (sampled proofs, PoUS, PoUW, the network warden and NCI, Python and each
`lean/` package) and in `benchmarks/` to its destination in the layout of
note:20261004T2058Z-draft-repo-organization-principles ("the plan"). It was made read-only. The survey was done at `main`
`3504da27e`. The claims were then rechecked against `origin/main` `16749a0ff` (4 Oct, "Merge 12 PRs"). In scope since
then, #1122 qualified every Π₂ wall-clock citation as holding in the ideal-permutation model only and marked
`feistel-indifferentiability` refuted. #1110 put every PoUS timed verifier on an injected clock (`tests/conftest.py`). A
PR also changed `circuit/rowk.py`, which still imports `pc4`. None of these changes a destination. Nothing was run and
nothing under `/workspace` was changed. Every row is a proposal for its owner to correct.

Approach statuses come from the rendered registries (`campaigns/pouw/APPROACHES.md` and `campaigns/pous/APPROACHES.md`,
rendered 29 Sep), overridden where the plan's 4 Oct text says otherwise:

- the Layout section's PoUW split (compute-accounting);
- step 2's PoUS statuses (memory-accounting).

`research notes approaches --campaign pous --refresh` timed out after five minutes with no output, so no status was read
live. The store's catalog has the approach ids but almost no labels.

## How to read the tables

Each table has the columns *current path*, *destination*, *principle*, *confidence* and *question for the owner*.

- **Principle column:** it cites the plan's principles (P1 to P10), its conventions ("Conv: tests", "Conv: PROTOCOL.md"),
  its Layout section ("Layout") and its plan steps. S3 is the Lean split and S5 the Python moves.
- **Split rows:** a destination that begins "Split:" means the module must be divided before it moves, along the line the
  row gives.
- **Paths:** each table gives current paths relative to its package.
- **"Spec":** a Lean module that stays in its package with the lock at S3 and moves beside its Python into `verity/` at S5.

Destination names follow the Layout and the sibling map (note:20261004T2125Z-draft-move-map-backends-integrations-tools):

- `verity/…/sampled_proofs/` is `verity/protocols/verification/sampled_proofs/`.
- `verity/…/pous/` is `verity/protocols/accounting/space/pous/`.
- `verity/…/pouw/` is `verity/protocols/accounting/work/pouw/`.
- `verity/…/warden/` is `verity/protocols/accounting/communication/warden/`.
- `verity/…/nci/` is `verity/protocols/compliance/nci/`.

The Layout writes `work/pouw` and `space/pous`, while the sibling map writes `verity/protocols/accounting/pouw/`. The
coordinator should pick one form.

The other destinations:

- `verity/kernels/<entry>/` is a kernel registry entry (P5).
- `verity/primitives/{circuits,crypto,commitments,physical}/` are the primitives the Layout lists.
- `catalog/{definitions,devices,parameters,vectors}/` hold Definitions with their builders, device numbers, calibrated
  parameters and generated vectors (P3). The entry format is still @architecture's open question, so these
  subdirectories are placeholders.
- `security_proofs/<area>/` is an area's math package. It follows the plan's `security_proofs/flock/`, so the areas here
  are `pous`, `pouw`, `warden` and `nci`.
- The rest are `experimental/<area>/`, `tools/<tool>/`, `archive/<name>/`, `examples/<area>/` and
  `benchmarks/<area>/` ("stays").

## Counts by destination

These are the rows of the tables below, counted by the first destination each row names. A split row counts once,
under its main destination, and the split rows are also counted on their own. A Lean row is a family of modules, so the
Lean file counts follow the table.

| Destination | Python rows | Lean rows | `benchmarks/` rows | Total |
|---|---|---|---|---|
| `verity/` (protocol code, primitives, kernels) | 54 | — | 5 | 59 |
| Lean spec (stays with the lock, then into `verity/`) | — | 20 | — | 20 |
| `security_proofs/` | — | 19 | — | 19 |
| `catalog/` | 7 | 1 | — | 8 |
| `experimental/` | 8 | — | 5 | 13 |
| tests (beside the package) | 9 | 1 | — | 10 |
| `tools/` | 2 | 3 | 3 | 8 |
| `archive/` | — | — | 1 | 1 |
| `benchmarks/` (stays) | — | — | 10 | 10 |
| retired (three `PROTOCOL.md`s, two `CheckAxioms.lean`s, `check.sh`) | 3 | 3 | — | 6 |
| Total | 83 | 47 | 24 | 154 |
| of which split rows | 13 | 3 | 5 | 21 |

The 21 split rows send code to:

- `verity/` (15 rows);
- `experimental/` (9);
- `catalog/` (6);
- tests (2);
- `security_proofs/` (1);
- `tools/` (1);
- `examples/` (1, the demo population programs).

The Lean files fall as follows at `16749a0ff`:

- **PoUS:** the spec is 36 files (`Pous/Protocol*`, `Assumptions*`, `Guarantees*`). `security_proofs/pous/` takes the 58
  `SecurityProofs` files, the umbrella and `PousTargets.lean`. The grader's 4 files go to `tools/`.
- **PoUW:** 150 files sit under `Pouw/Protocol*`, `Assumptions*` and `Guarantees*` (149 modules and one JSON), and
  `Pouw.SecurityProofs.Dimension.Lifting` joins them at S3.1. They divide as follows:
  - 33 modules are read by the five guarantees the reduction keeps;
  - 8 tile-check modules stay as future reads of `EndToEnd`;
  - the 3 umbrellas stay;
  - 15 generated-vector files go to `catalog/`;
  - about 90 go to `security_proofs/pouw/` as the validator reports them unread.

  `security_proofs/pouw/` also takes the 149 other `SecurityProofs` files and the umbrella.
- **The warden:** the spec is 7 files, plus the two difftest runners proposed to stay with it. `security_proofs/warden/`
  takes 8 files and the umbrella.
- **NCI:** the spec is 3 files; `security_proofs/nci/` takes 5 and the umbrella.

## sampled_proofs (`protocols/sampled_proofs/`, compute-accounting)

The one-stage audit is what C-Flock's audit-law guarantees describe:

- `Audit.Work.work_escape_le` and `Audit.Partition.audit_exfiltration`;
- the stratified-miss and influence bounds the plan keeps.

So its code is TCB. Its Lean is not in this package. It is `FlockSoundness.Audit.*` inside C-Flock's soundness (27
files, 120 pins), and S3.1 moves it whole to `security_proofs/flock/` under its current names. A spec of its own, with
its game folded into core's model, is an S3.3 job.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `verity_sampled_proofs/one_stage/audit.py` | `verity/…/sampled_proofs/one_stage/audit.py` | P1: the audit record and its `IntegrityProfile` | medium | compute-accounting: the Layout lists only C-Flock under `verification/`. Is sampled proofs a protocol beside C-Flock there, or its own `verity/protocols/sampled_proofs/`? |
| `one_stage/draw.py` | `verity/…/sampled_proofs/one_stage/draw.py` | P1, P5: the verifier's draw checks, its coins from `verity.randomness` | high | — |
| `one_stage/registration.py` | `verity/…/sampled_proofs/one_stage/registration.py` | P1: the record fixed before the draw; vLLM imports it | high | — |
| `one_stage/registered.py` | `verity/…/sampled_proofs/one_stage/registered.py` | P1: registered values opened against their commitment | high | — |
| `one_stage/verdict.py` | `verity/…/sampled_proofs/one_stage/verdict.py` | P1 | high | — |
| `one_stage/consumers.py` | `verity/…/sampled_proofs/one_stage/consumers.py` | P1, but AGENTS.md says consumers read the profile "with their own utilities" | medium | compute-accounting: are these weightings part of a cited result, or application code for its consumer (vLLM)? |
| `one_stage/partition.py` | Split: the template queries → `verity/…/sampled_proofs/one_stage/partition.py`; `population_program` and `mixed_population_program` → `examples/sampled_proofs/` | P1 for the queries; the demo programs are imported by `benchmarks/one_stage/a0,a2,a3.py` and `backends/flock/verifier/stratified_agree.py` | medium | compute-accounting: are the demo programs `examples/` or a shared test fixture? |
| `law.py` (the two-stage law, `OwnRandomness`, `ru_key`/`vu_key`) | `verity/…/sampled_proofs/law.py` | P1 if a guarantee reads it; vLLM's `commit/challenge.py` takes `ru_key`/`vu_key` "only for vLLM's LEGACY challenge" | low | compute-accounting: none of the kept audit-law bounds is the two-stage law. If no guarantee reads it, does it go to `experimental/sampled_proofs/` with vLLM's legacy challenge dropping its import first? |
| `plan.py` (`VerificationPlan`) | `experimental/sampled_proofs/plan.py` | P9: only its own test and vLLM's `test_running_example` use it | medium | compute-accounting: is it superseded infrastructure that P8 simply deletes? |
| `README.md` | `verity/…/sampled_proofs/README.md` | Conv: PROTOCOL.md (the short README stays) | high | — |
| `tests/` (suites) | `verity/…/sampled_proofs/tests/` | Conv: tests | high | — |
| `tests/lean/ExfiltrationVectors.lean`, `generate.sh`, `fixtures/exfiltration_lean.json` | stay in the tests; the generate paths follow `FlockSoundness.Audit` to `security_proofs/flock/` | S3.1: difftest paths follow each move | medium | lean: which package does the difftest build against after S3.1? |

## PoUS Python (`protocols/pous/`, memory-accounting)

These are the statuses the plan's step 2 gives:

- **Live:** `band-d12`, P2 v3 (`ec-p2-16448`, #1123) as the candidate, P2 v2 (ChaCha8 keys, nonconforming), and P3, which
  has no certificate.
- **Superseded:** `dense`, by band. Band and dense's ideal-model theorems still stay guarantees.
- **Killed:** the hardware reading of their deadlines (art:7617c801, #1122), `feistel-indifferentiability` (refuted), and
  TwoTierBandwidth (no host RAM).

From the registry: `miyaguchi-preneel-h` is killed, `sponge-h` and `ec-p2-5504` are superseded, and `ec-cuda-arx-p3` is
killed. PoUS moves late in S5. It waits for #1123, #1096, #1086, the root-floor recalibration, and Daniel's ruling on the
P2 window and w.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `verity_pous/protocol.py` | `verity/…/pous/protocol.py` | P1: the `Scheme`/`Certificate`/`Verifier` interface | high | — |
| `verity_pous/codec.py` | `verity/…/pous/codec.py`, receiving `Encoding` from `scheme.py` | P1: the seam between a scheme and the audit | high | — |
| `verity_pous/band.py` | `verity/…/pous/band.py` | `band-d12` live; `BandMultiMeetsFamily` and its D2/D1/D0 forms stay guarantees (ideal-permutation model, #1122) | high | — |
| `verity_pous/dense.py` | `verity/…/pous/dense.py` | `dense` superseded, but `band.py` builds on its `DenseChain` and `ChainDenseMeets64` stays a guarantee | medium | memory-accounting: keep `dense.py` whole in `verity/`, or extract the overwrite chain band needs into its own module and send the dense scheme to `experimental/pous/dense/`? |
| `verity_pous/scheme.py` | Split: `Encoding` → `verity/…/pous/codec.py`; the P3 scheme → `experimental/pous/p3/scheme.py` | P3 live, no certificate; `audit`, `setup` and `verifier` import `Encoding` | medium | memory-accounting: the `P3Concrete*` statements are proposed to stay locked while P3's code is experimental. Is P3 under a guarantee or not? |
| `verity_pous/params.py` | Split: `SALT_BITS`, `TAG_BITS` → `verity/…/pous/layout.py`; P3's `Params`, `OPERATING_POINT`, `LEAN_P3_MEETS` → `experimental/pous/p3/params.py` | P3 status; `labels`, `dense`, `setup` and `schemes/p2` read `SALT_BITS` | medium | memory-accounting: `labels.py` takes P3's `Params`. Is its layout generic over a band label width, or P3-only? |
| `verity_pous/labels.py` | `verity/…/pous/labels.py` | P1: Lean's `Bits` layout, read by `verifier`, `dense` and `primitives` | high | — |
| `verity_pous/primitives.py` | Split four ways. `pi2_keccak_f`, `OverwriteStepper`/`OverwriteChain` and `Feistel10`/`FeistelPi` → `verity/…/pous/primitives.py`. `KECCAK_F_NS = 50` and `pi2_call_ns`'s floor → `catalog/devices/`. `FeistelP`, `ArxButterfly`, `EvenMansourArx` and `heuristic_arx` → `experimental/pous/p3/`. `XorSponge`, `MiyaguchiPreneel`, `RandomOracleKey`, `IdealPermutation`, `IdealTweakablePermutation` and `ideal` → tests | Conv: tests (broken attack modes, the oracle); P3 ("PoUS's Keccak step"); the statuses above | medium | memory-accounting: does any deployed path read the ideal objects, for example the band margins? |
| `verity_pous/oracle.py` | tests (`tests/pous_oracle.py`) | Conv: tests names it; `dense`, `primitives`, `scheme` and `audit` import its `Prog`, `Cost` and query types | medium | memory-accounting: which of these types does deployed code use (those stay in `verity/`), and which only the model? |
| `verity_pous/adversary.py` | tests (`tests/pous_adversary.py`) | Conv: tests | high | — |
| `verity_pous/audit.py` | Split: `TimedVerifier` and the protocol's counts (`CHALLENGES`, `CERTIFIED_ROUNDS`, `WORK`, `LATE_ROUNDS`, `AUDIT_CAP`) → `verity/…/pous/audit.py`; `DEADLINE_NS`, `RTT_ALLOWANCE_NS` and `CALL_NS` → `catalog/devices/`; `simulate` (the model's clock) → tests | P1 (the deployed verifier); P3 (device numbers, the RTT allowance named) | medium | memory-accounting: which counts are spec parameters (Lean `Accounting.Params`) and which are calibrated? The RTT allowance waits on Daniel's window ruling. |
| `verity_pous/continuous.py` | `verity/…/pous/continuous.py` | P1: the `ContinuousAudit` verifier (ideal model only, #1122) | high | — |
| `verity_pous/layout.py` | `verity/…/pous/layout.py` | P1: vLLM's PoUS option reads it | high | — |
| `verity_pous/setup.py` | `verity/…/pous/setup.py` | P1 | high | — |
| `verity_pous/verifier.py` | `verity/…/pous/verifier.py` | P1: the vk, a SHA-256 RFC 6962 Merkle tree | medium | memory-accounting: adopt the primitives' one Merkle tree at the move, or later as a change of meaning with a bridge (S5's shared pieces)? |
| `verity_pous/schemes/__init__.py` | `verity/…/pous/schemes/__init__.py`, without the `p2` and `p3` imports | P6, P9 | high | — |
| `verity_pous/schemes/band.py` | `verity/…/pous/schemes/band.py` | `band-chain/d12/v1`, certificate `BandMultiMeetsFamily` | high | — |
| `verity_pous/schemes/dense.py` | `verity/…/pous/schemes/dense.py` | `dense-chain/v1`, certificate `ChainDenseMeets64` stays locked; approach superseded | medium | memory-accounting: same question as `dense.py`. If the dense scheme goes to experimental, `ChainDenseMeets64` leaves the lock. |
| `verity_pous/schemes/p2.py` | Split: the scheme → `experimental/pous/p2/scheme.py`; `ROOT_CALL_NS = 2_900_000` → `catalog/devices/` | `p2-16448/v2` (ChaCha8, nonconforming), marked EXPERIMENTAL; v3 is the candidate | high | memory-accounting: six P2 pins are proposed to stay locked. Does P2 promote with v3, or do those pins leave the lock until it does? |
| `verity_pous/schemes/p3.py` | `experimental/pous/p3/scheme.py` | `p3/v1`, no certificate | high | — |
| `PROTOCOL.md` | retired: definitions to the Lean spec, parameters to `catalog/`, threat model and lifecycle to the README | Conv: PROTOCOL.md | high | — |
| `DISCREPANCIES.md` | `verity/…/pous/DISCREPANCIES.md` | an allowed current-truth file | medium | memory-accounting: do its B1–B5 rows become approaches in the registry instead? |
| `README.md` | `verity/…/pous/README.md` | Conv: PROTOCOL.md | high | — |
| `tests/` (suites, `conftest.py`, `pous_state_game.py`, `pous_continuous_model.py`, `pous_vectors.py`, `pous_scheme_vectors.py`) | `verity/…/pous/tests/` | Conv: tests | high | — |
| `tests/fixtures/schemes/{band-chain-d12-v1,dense-chain-v1}.json` | `catalog/vectors/pous/` | P3: generated vectors; Conv: PROTOCOL.md (a vectors file is the spec where two implementations agree) | medium | memory-accounting: are these vectors the agreement with vLLM's `engine.pous` kernels, or only test fixtures? |
| `tests/fixtures/schemes/{p2-16448-v2,p3-v1}.json` | `experimental/pous/{p2,p3}/` | P9 | high | — |
| `tests/lean/*Check.lean` and their generate scripts | stay in the tests; generate paths updated at each move | S3.1 | medium | lean: does each check build against the spec package or the math package? |
| root `tests/test_pous_bench.py`, `tests/test_pous_harness.py` | tests: `benchmarks/pous/tests/` | Conv: tests (the root suite keeps only whole-tree invariants) | high | — |

## PoUS Lean (`protocols/pous/lean/`, memory-accounting; layout with lean)

`lean-audit.json` has `roots: ["Pous"]` and 104 pins. Its `layers` are `Pous.Protocol`, `.Game`, `.Model`, `.P2`,
`Pous.Assumptions(.P2)` and `Pous.Guarantees(.P2)`, and `reads` lists 34 modules. Its exempt entries are
`PousTargets`, `CheckAxioms`, `Grader` and `submissions`. S3.1 says PoUS's split already exists in the tree.

S3.1 also requires that `TRUSTED.sha256`, `CheckAxioms.lean` and `Grader/Registry.lean` update in the same PR that moves
the proofs. `TRUSTED.sha256` lists two `SecurityProofs` files, `Pous/SecurityProofs/Sanity.lean` and
`Pous/SecurityProofs/Accounting/Numbers.lean`. `grade.sh` lets submissions import those same two files beside the spec,
and builds them. So the same PR must either keep these two files in the spec package under their names (as PoUW's
`Lifting` stays), or change the grader's trusted set and `TRUSTED.sha256` together.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `Pous/Protocol.lean`, `Pous/Protocol/Game/{Prob,Oracle}.lean` | spec | `layers` `Pous.Protocol`, `.Game`; in `reads` | high | — |
| `Pous/Protocol/Model/*` (21 files: band, dense, P3, M1/M1p, audit and erasure models) | spec | `layers` `Pous.Protocol.Model`; all 21 in `reads`; S3.1 names `Protocol/Model` spec | high at S3.1, medium after | memory-accounting: once P2's and P3's code is experimental, do `P3Chain`, `ColumnGame`, `M1` and `M1p` stay in the spec? `BandChain` imports `P3Chain`, so `P3Chain` stays while band's statements read it. |
| `Pous/Protocol/Accounting/{EraseMeets,GradedMeets,LemmaA,Params,PubMeets,Rebuild}.lean` | spec | `meaning` includes `Pous.Protocol`; five in `reads`, `LemmaA` through `Pous.Assumptions` | high | — |
| `Pous/Protocol/P2/Cost.lean` | spec | `layers` `Pous.Protocol.P2`; read by the P2 pins | medium | memory-accounting: the P2 promotion question above |
| `Pous/Assumptions.lean`, `Pous/Assumptions/P2.lean` | spec | `assumptions` | high | — |
| `Pous/Guarantees.lean`, `Pous/Guarantees/{P2,SecureErasure}.lean` | spec | `layers`; holds the 104 pinned statements, about 73 after the reduction | high | memory-accounting with lean: do the ~31 dropped statements stay as `def`s in `Guarantees.lean` (no record changes), or move out (changes the module's `digest` in `reads`)? |
| `Pous/SecurityProofs/**` except `Sanity.lean` and `Accounting/Numbers.lean` (56 files) | `security_proofs/pous/` | P2 | high | — |
| `Pous/SecurityProofs/Sanity.lean`, `Pous/SecurityProofs/Accounting/Numbers.lean` | `security_proofs/pous/` | P2; but both are in `TRUSTED.sha256` and in `grade.sh`'s allowed imports | medium | memory-accounting: keep them in the spec package under their names, or narrow the grader's trusted set in the same PR? |
| `Pous.lean` (umbrella) | `security_proofs/pous/` | S3.1: umbrellas move to the math package | high | — |
| `PousTargets.lean` (every pinned statement as a `sorry` stub; exempt) | `security_proofs/pous/` (exempt) | open targets | medium | memory-accounting: is it still needed once the grader holds the targets? |
| `Grader/Registry.lean`, `Grader/Main.lean` | `tools/pous_grader/` | Layout ("PoUS's grader" under `tools/`) | medium | memory-accounting: `pinnedTargets` lists 62+ `Pous.Guarantees.*` names. Does it follow the reduced lock, or keep grading dropped targets? |
| `grade.sh`, `submissions/reference.lean` | `tools/pous_grader/` | Layout | medium | — |
| `TRUSTED.sha256` | spec, rewritten in the same PR | S3.1 | high | — |
| `CheckAxioms.lean` | retired; S3.1 updates it, and the validator replaces it when the proofs become one package | P2 | high | — |
| `check.sh` | retired into `check` and `tools/pous_grader/` | it runs `audit.py` and the grader's controls | medium | memory-accounting |
| `lean-audit.json` | split: `roots`, `layers` and `dependencies` divided between the spec and math packages | S3.1 | high | — |
| `README.md`, `lakefile.toml`, `lake-manifest.json`, `lean-toolchain` | the spec package; the math package gets its own `require` of the spec | S3.1 | high | — |

## PoUW Python (`protocols/pouw/`, compute-accounting)

The plan's Layout gives compute-accounting's split:

- **`verity/`:** `pearl-c-sm120-v1` (and `-h2`), `ncp-v1` and `ncp-v1-shift24`.
- **`experimental/`, as live approaches:** the H100 `-v1`, `-h1` and `-h2`, `pearl-c-nvfp4-v0` and `pearl-fp8-v4`.
- **Superseded:** `pearl-c-h100-v0`. It still builds, so it is experimental under P8, not archive.

On main, `SCHEMES` holds `pearl-c-h100-v1-h1` and `-h2`. The `-sm120-v1-h1`/`-h2` names that the benchmarks use are only
parsed by `serving.py`'s grammar. The status field on `SCHEMES` is on hold, since experimental schemes move to
`experimental/pouw/` instead. The vLLM PoUW options use:

- for NCP, `circuit` (`ncp2`, `partition`, `plan`, `anchors`, `reference`);
- for Pearl-C, `pearl_c`, `pearl_c_work`, `DEVICES`, `SM120` and `serving`.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `verity_pouw/protocol.py` | `verity/…/pouw/protocol.py` | P1: the `PoUWScheme` interface | high | — |
| `verity_pouw/audit.py` | `verity/…/pouw/audit.py` | P1: the lifecycle and the work-weighted draw `WorkWeightedSampling` states | high | — |
| `verity_pouw/beacon.py` (drand quicknet) | `verity/primitives/crypto/beacon.py` | Layout: crypto (drand BLS) | high | — |
| `verity_pouw/bls12_381.py` | `verity/primitives/crypto/bls12_381.py` | Layout | high | — |
| `verity_pouw/identifier.py` | `verity/…/pouw/identifier.py`, looking schemes up in a registry passed to it | P1: the proof's identifier v1; it imports `SCHEMES` | medium | compute-accounting: one registry that experimental code adds to, or two registries and an explicit choice by the caller? |
| `verity_pouw/serving.py` (`HASH_FORMATS`, the SchemeId grammar, `SCHEDULES`, `KernelVariant`) | `verity/…/pouw/serving.py`, whole | P1: vLLM's options parse it. Parsing a name grants nothing, since the lookup in `SCHEMES` fails closed | medium | compute-accounting: does Pearl-C4's part of the grammar stay with the rest? |
| `verity_pouw/schemes/__init__.py` (`SCHEMES`, `get`) | Split: `verity/…/pouw/schemes/__init__.py` with `ncp-v1`, `ncp-v1-shift24`, `pearl-c-sm120-v1`; the other six entries → `experimental/pouw/schemes.py` | Layout; P9: no forgotten label puts an experimental scheme under a guarantee | high | compute-accounting: the same registry question as `identifier.py`. A hook that experimental fills would let an audit accept an experimental scheme. |
| `verity_pouw/schemes/ncp.py` | `verity/…/pouw/schemes/ncp.py` | `ncp` live, `route-u` merged; `Theorem1` and `GammaFromTTNCP_U_v1` kept | high | — |
| `verity_pouw/schemes/pearl_kw.py` | Split: Pearl's shared pieces (imported by `pearl_c`, `pearl_c_debit`, `pearl_c_work`, `pearl_c4`, `circuit/pc8`) → `verity/…/pouw/schemes/pearl.py`; the `pearl-fp8-v4` scheme → `experimental/pouw/pearl_fp8_v4/` | Layout: `pearl-fp8-v4` experimental | high | — |
| `verity_pouw/schemes/pearl_c.py` (v0 and v1 formings; H100 and sm120 instances) | Split: the v1 forming → `verity/…/pouw/schemes/pearl_c.py`; the v0 forming → `experimental/pouw/pearl_c_h100/` | Layout; the scheme is generic over device, so H100 is a `SCHEMES` entry plus a catalog device record | medium | compute-accounting: split v0 out, or keep it in place behind a fail-closed refusal (P9)? |
| `verity_pouw/schemes/pearl_c_device.py` | Split: `Prices`, `Device` → `verity/…/pouw/schemes/pearl_c_device.py`; the records `SM120_PRICES`, `SM120`, `SM120_UNPROMOTED`, `H100_PRICES`, `H100`, `DEVICES` → `catalog/devices/` | P3: device numbers; the certified γ `pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_8192` reads the SM120 record | medium | compute-accounting: `pearl_c_work`, `pearl_c_debit`, `pearl_c_u`, `circuit/pc8` and `circuit/rowk` import the records directly. Who passes the chosen device in? |
| `verity_pouw/schemes/pearl_c_debit.py` | `verity/…/pouw/schemes/pearl_c_debit.py`, without its H100 default | P1: the debit the work law replays. It already takes the scheme's device, "the H100 by default", and its module constants are the H100's | high | — |
| `verity_pouw/schemes/pearl_c_work.py` | `verity/…/pouw/schemes/pearl_c_work.py`, taking its device as a parameter | P1: Pearl-C's work law; vLLM's Pearl-C option uses it | high | — |
| `verity_pouw/schemes/pearl_c_u.py` | `experimental/pouw/pearl_c_h100/pearl_c_u.py` | Layout: the sm_90 entry's CPU twin; "CPU-pinned" to H100 | high | — |
| `verity_pouw/schemes/pearl_c4.py`, `pearl_c4_c_L.py` | `experimental/pouw/nvfp4/` | Layout: `pearl-c-nvfp4-v0` experimental | high | — |
| `verity_pouw/schemes/pearl_c4_replay.py` | `experimental/pouw/nvfp4/` | its own docstring: a development shortcut, never the protocol's verdict | medium | compute-accounting: superseded tooling to delete under P8? |
| `verity_pouw/circuit/__init__.py` (`verify`) | `verity/…/pouw/circuit/__init__.py` | P1 | high | — |
| `verity_pouw/circuit/anchors.py` | `verity/…/pouw/circuit/anchors.py` | P1: vLLM's NCP option uses it | high | — |
| `verity_pouw/circuit/partition.py` | `verity/…/pouw/circuit/partition.py` | P1 | high | — |
| `verity_pouw/circuit/plan.py` (closure draws) | `verity/…/pouw/circuit/plan.py`, without its `pc4` import | P1; P9 | medium | compute-accounting: can `plan` take the tile-check templates as data, so it needs neither `pc4` nor `pc8`? |
| `verity_pouw/circuit/reference.py` (`ncp-v2`'s native reference) | `verity/…/pouw/circuit/reference.py` | P5: the reference a fast path is gated against | high | — |
| `verity_pouw/circuit/hashes.py` (SHA-512, SHAKE256, TurboSHAKE128 in gates) | `verity/primitives/circuits/hashes.py` | P3: SHA-512 and Merkle as gates are TCB primitives; S5: one SHA-512 | medium | compute-accounting with circuits: do SHAKE256 and TurboSHAKE128 go with SHA-512, or to `catalog/definitions/`? |
| `verity_pouw/circuit/ncp2.py` (unit templates) | `catalog/definitions/pouw/ncp2.py` | P3: a Definition is a builder in the catalog | medium | compute-accounting: `verify`, `partition`, `plan` and `reference` import it. Does the guarantee's circuit stay in `verity/`, or does `verify` take it from a catalog entry? |
| `verity_pouw/circuit/words.py`, `boolean.py` | `catalog/definitions/pouw/` | P3 | medium | circuits: the catalog entry format |
| `verity_pouw/circuit/leaves.py` | `catalog/definitions/pouw/leaves.py` | P3; it imports `schemes.pearl_c` | medium | — |
| `verity_pouw/circuit/pc8.py` (the tile checks for h100-v1 and sm120-v1) | Split: the sm120 check → `catalog/definitions/pouw/pc8.py`; the H100 check → `experimental/pouw/pearl_c_h100/` | P3, Layout; it reads the device dots `BlackwellE4m3QmmaDot32` and `HopperBF16WgmmaDot16` | medium | — |
| `verity_pouw/circuit/pc4.py` | `experimental/pouw/nvfp4/pc4.py` | Layout | high | — |
| `verity_pouw/circuit/rowk.py` | `catalog/definitions/pouw/rowk.py`, without `pc4` | P3; it imports `pc4`, `pc8` and `DEVICES` | medium | — |
| `PROTOCOL.md` | retired: per-scheme sections to the Lean spec and `catalog/` | Conv: PROTOCOL.md | high | — |
| `tests/` (suites, `circuit_fixtures.py`) | `verity/…/pouw/tests/`; the H100 and NVFP4 suites go with their code | Conv: tests | high | — |
| `tests/*_vectors.py`, `quicknet.py`, `pearl_vectors.rs`, `ncp_lean.py` (vector generators) | `tools/catalog/pouw/` | P3: code that builds an entry is a tool | medium | compute-accounting |
| `tests/vectors/*.json` (`ncp`, `pearl_c`, `pearl_kw`, `pearl_c4`, `pearl_c_u`, `identifier_v1`, `quicknet`, `pouw_rows`, `pouw_regions`, `ncp_lean`, the skip vectors) | `catalog/vectors/pouw/`, with the experimental schemes' vectors in `experimental/pouw/` | P3; Conv: PROTOCOL.md | medium | — |

## PoUW Lean (`protocols/pouw/lean/`, compute-accounting; layout with lean)

`lean-audit.json` has `roots: ["Pouw"]` and 24 assumption modules. Its `meaning` is `Pouw.Protocol`/`Assumptions`/
`Guarantees` and `Verity.Protocol`. Its `layers` are `Pouw.Assumptions`, `Pouw.Guarantees`, `Pouw.Protocol` (except
`PearlC.Defs`), `Pouw.Protocol.Basic`, `Pouw.Protocol.PearlC.Defs` and `Pouw.SecurityProofs.Dimension.Lifting`. It holds
800 pins (793 by the plan's count), and `reads` lists 128 modules. The lakefile requires Mathlib and core's `verity`
package by path.

The plan keeps five pins:

- `EndToEnd`, `WorkWeightedSampling` and `Theorem1`, in `SecurityProofs/Game.lean`;
- `GammaFromTTNCP_U_v1`, in `SecurityProofs/NCP.lean`;
- the certified γ `pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_8192`, inline in `SecurityProofs/PearlC/DeviceCapRev1Gamma.lean`.

The certified γ is lifted into `Guarantees` in prep. S3.1 keeps `Pouw.SecurityProofs.Dimension.Lifting` with the spec
under its name, and PoUW's split runs after l3-tilecheck's slice 6.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| The 33 spec modules the five kept guarantees read. `Assumptions`: `Game`, `NCP.RouteUAssumptions`, `PearlC.TTOut`, `PearlC.TTOutRev1`. `Guarantees`: `Game`, `NCP`. `Protocol.Basic`: `Mat`, `Prob`, `QTree`. `Protocol`: `D1`, `Game.Defs`, `Game.Params`, `NCP.Defs`, `NCP.Protocol`, `NCP.RouteU`. `Protocol.Fp8Atom`: `Atom`, `E4M3`, `Fp32`. `Protocol.PearlC`: `Accum`, `Defs`, `Device`, `DeviceKernelWref`, `DevicePricesLoop`, `DeviceRev1`, `FormingPDefs`, `Game`, `Instance`, `PeelExact`, `PeelExactP`, `SaltDead`, `Skip`, `SkipP`, `Sm120` | spec | P2: what the guarantees read | high; low for the device instances (`Sm120`, `DeviceRev1`, `Device`, `DevicePricesLoop`, `DeviceKernelWref`) | compute-accounting with lean: the Layout puts "device instances in Lean" in `catalog/`, but the certified γ reads them. See the flags. |
| `Pouw/SecurityProofs/Dimension/Lifting.lean` | spec package at the split, name kept | the plan (S1, S3.1); in `layers`; imports Mathlib only; no spec module imports it | high at S3.1, low after | lean: after the reduction drops the Dimension family's four pins, no guarantee reads it and it is not in `reads`. Does it return to `security_proofs/pouw/` on the validator's report of unread spec definitions? |
| Pearl-C tile-check modules no pin reads today: `Protocol.PearlC.{Tile, RowCircuit, TileCircuit, WholeCircuit, TileCheck, TileCheck8, RowSem, RowPrims}` | spec | the plan: tonight's L3 pins enter as reads of `EndToEnd`'s tile check | medium | compute-accounting: which of these does `EndToEnd` read after slice 6? The rest go with the lemmas. |
| Theorems stated inside spec modules: `Protocol.PearlC.{Accum (7), RowCircuit (16), Row4Circuit (12), WholeCircuit (17), WholeCircuit4 (17), TileCircuit (2), Tile4Circuit (2), PeelExactP (4), Game (1), Instance (1)}` and `Protocol.Fp8Atom.H1T (1)` | Split: the theorems → `security_proofs/pouw/` in sibling modules; the definitions stay | P2: lemma statements leave `Protocol`. I count 80 theorems in 11 modules; the plan says about 41 | medium | lean: `Accum`, `PeelExactP`, `Game` and `Instance` are read modules. Does moving a theorem out of one change its record (the module `digest` in `reads`), or only the definitions' hashes? |
| Dimension and route-U pipe family: 25 `Assumptions.Dimension.*`, `Protocol.Dimension.{Causal, Defs, Lift}`, `Guarantees.Dimension` | `security_proofs/pouw/` under spec names, after the reduction | P9: H100 lane experimental; the family leaves the lock | medium | compute-accounting: does it stay spec through S3.1 and move only on the validator's report? |
| H100 `-h1` family: `Protocol.Fp8Atom.{H1T, H1TCrossLate, H1TLemmas, H1TPinned}`, `Assumptions.Fp8Atom.{H1TAssumptions, H1TGamma, H1TRunningAssumptions, H1TTile, H1TTileAssumptions}` | `security_proofs/pouw/` under spec names | Layout: H100 `-h1` experimental; the 45 H100 γ pins leave the lock and keep building | medium | — |
| NVFP4 family: `Protocol.PearlC.{Fp4, Fp4Chain, Fp4Skip, DeviceFp4, DeviceFp4ChainOnly, DeviceFp4Hot, DeviceFp4Issue, Row4Circuit, Tile4Circuit, WholeCircuit4, TileCheck4}`, `Assumptions.PearlC.{TTOutFp4, TTOutFp4ChainOnly}` | `security_proofs/pouw/` under spec names | Layout: `pearl-c-nvfp4-v0` experimental | high | — |
| Pearl-C modules no kept guarantee reads: `Protocol.PearlC.{Completeness, Deadline, DeviceChainOnly, DevicePrices, Hidden, HiddenTileGame}`, `Assumptions.PearlC.{Deadline, DeviceChainCap, DeviceChainCapKernel, HiddenTile, HonestCap, RowSeedAssumptions, TTOutChainOnly, TTOutRowSeed, TTOutTileUOnly, TTOutUOnly}` | `security_proofs/pouw/` after the reduction | P2, P9. `DevicePrices` holds 116 pins. The plan also drops the 104 γ pins that `harness/price_twins.json`, an internal pricing table, names | medium | compute-accounting: are hidden-zk's `Hidden*` and the cap assumptions future reads of the certified γ or of `EndToEnd`? |
| NCP, Barrier, TileBound, M1, Witness and Deadline families: `Protocol.NCP.{ExtraIdentity, Pinned, Relation, Witness, Word}`, `Assumptions.NCP.{Assumptions, Chain, GamePinned, RouteUGame, RouteUWord}`, `Protocol.Barrier.*`, `Protocol.TileBound.*`, `Protocol.M1`, `Protocol.Witness.*`, `Protocol.Game.Deadline`, `Assumptions.{Deadline, Pinned}`, `Guarantees.{Barrier, Deadline}` | `security_proofs/pouw/` after the reduction | P2: lemma families; about 25 NCP and Barrier lemmas that `PROTOCOL.md` and `ncp.py` name keep building | medium | compute-accounting: does `GammaFromTTNCP_U_v1` read `Assumptions.NCP.Assumptions` or `RouteUGame`? |
| Generated vectors: `Protocol.Fp8Atom.{Vectors, Vectors/* (5 files), H1TVectors, H1TVec}`, `H1TCoverage.json`, `Protocol.PearlC.{EncVectors, Fp4Vectors, PeelExactVectors, PeelFp4Vectors, RowPrimVectors, Sm120Vectors}` | `catalog/vectors/pouw/` (Lean) | P2: "its generated vectors go to the catalog" | medium | lean: `Pouw/Protocol.lean` imports every vector module, and `Fp8Atom.Pinned` and `H1TPinned` import vectors. The umbrella must stop importing them first. |
| `Protocol.Fp8Atom.Pinned` | `security_proofs/pouw/` | lemma statements over the vectors | medium | — |
| `Pouw/SecurityProofs/**` except `Dimension/Lifting.lean` (149 files) | `security_proofs/pouw/` | P2 | high | — |
| `Pouw.lean` (umbrella) | `security_proofs/pouw/` | S3.1 | high | — |
| `PouwBulk.lean` (exempt `runs`: fp8 conformance against `scripts/fp8atom_vectors.py`) | `security_proofs/pouw/` as a `runs` target | conformance replay | medium | lean: or a catalog test, once the vectors are catalog entries? |
| `scripts/fp8atom_vectors.py`, `h1t_vectors.py`, `row_prims_vectors.py`, `fp8atom_cover.json` | `tools/catalog/pouw/` | P3 | medium | compute-accounting |
| `lean-audit.json` | split: the spec keeps the five guarantees after the reduction; `roots`, `layers` and `dependencies` divided | S3.1 | high | — |
| `lakefile.toml`, `lake-manifest.json`, `lean-toolchain`, `.gitignore` | the spec package; the math package requires the spec, Mathlib and core's math package (it uses `ProbBatchInduced` as a lemma) | S3.1 | high | — |

## The network warden (`protocols/network_warden/`, network-accounting)

The warden moves first in S5. The plan keeps about 10 of its 51 pins: the egress and ingress bounds that the K charge
and the bit bounds read. Its 16 non-vacuity witnesses become checked tests in `security_proofs/warden/`.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `verity_network_warden/grid.py` | `verity/…/warden/grid.py` | P1 | high | — |
| `verity_network_warden/schedule.py` | `verity/…/warden/schedule.py` | P1 | high | — |
| `verity_network_warden/audit.py` | `verity/…/warden/audit.py` | P1 | high | — |
| `verity_network_warden/commitment.py` | `verity/…/warden/commitment.py` | P1 | medium | network-accounting: adopt the primitives' one Merkle tree at the move, or later as a bridged change of meaning? |
| `verity_network_warden/capacity.py` | Split: the counts and bounds → `verity/…/warden/capacity.py`; `K_BITS = 9.12e7` → `catalog/parameters/` | P3: K is the inference-only policy's budget (α·Γ), a parameter | medium | network-accounting: is K a catalog parameter, or NCI's policy constant, stated in its spec? |
| `verity_network_warden/calibration.py` (`network-warden-calibrate`) | `tools/warden_calibrate/` | P3: code that builds a catalog entry (r, B, τ, Σ_sync) is a tool; no `verity/` module imports it | high | — |
| `verity_network_warden/active.py` (the asyncio proxy) | `verity/…/warden/active.py` | Layout: the warden "with its active enforcer" | high | — |
| `verity_network_warden/__init__.py` | `verity/…/warden/__init__.py` | P1 | high | — |
| `PROTOCOL.md` | Split: retired except the wire format section → `verity/…/warden/PROTOCOL.md` | Conv: PROTOCOL.md | high | — |
| `README.md` | `verity/…/warden/README.md` | Conv: PROTOCOL.md | high | — |
| `tests/` (seven suites, with the Lean difftest) | `verity/…/warden/tests/`; the calibration suite goes with `tools/` | Conv: tests | high | — |

## The network warden's Lean (`protocols/network_warden/lean/`, network-accounting; layout with lean)

`lean-audit.json` sets `layers` to `NetTiming.Protocol`, `Assumptions` and `Guarantees`, with 51 pins and 6 `reads`.
`CheckAxioms` and `NetTimingDifftest` are exempt; `NetTimingDifftest` `runs` against `scripts/difftest_vectors.py`.
It requires Mathlib only.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `NetTiming/Protocol.lean`, `NetTiming/Protocol/{Grid,Ingress,Run,Schedule}.lean` | spec | `layers` | high | — |
| `NetTiming/Assumptions.lean`, `NetTiming/Guarantees.lean` | spec | `layers` | high | — |
| `NetTiming/SecurityProofs.lean`, `NetTiming/SecurityProofs/{Advice,Counting,Ingress,Occupancy,PerWindow,Sanity,Schedule}.lean` | `security_proofs/warden/` | P2; the 16 witnesses become its checked tests | high | — |
| `NetTiming/Difftest.lean` (imports only `Protocol`), `NetTimingDifftest.lean` | spec | lean's "spec runner": the spec, executed against Python's vectors | medium | lean: do spec runners live in the spec package or the math package? |
| `NetTiming.lean` (umbrella) | `security_proofs/warden/` | S3.1 | high | — |
| `CheckAxioms.lean` | retired | P2: the validator replaces it | high | — |
| `scripts/difftest_vectors.py` | stays with the difftest's tests | S3.1: the difftest's `runs` generate paths and lean-deps follow each move, or the Lean half silently stops running | medium | network-accounting with ci: a `tools/` vector builder instead? |
| `lean-audit.json`, `lakefile.toml`, `lake-manifest.json`, `lean-toolchain`, `README.md` | the spec package; `lean-audit.json` split | S3.1 | high | — |

## NCI's Lean (`protocols/nci/lean/`, lean)

NCI has no Python, so its S5 train only moves the spec beside where its code will go. The package requires Mathlib and
core's `verity`. It has 8 pins: `Inference`, `ReadBound`, `Training`, `UpdatedMatMul`, `full_positions`, `iu_reads`,
`loomis_whitney` and `other_positions`. Lean proposes keeping `Inference` and `Training`.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `Nci/Protocol.lean`, `Nci/Assumptions.lean`, `Nci/Guarantees.lean` | spec; at S5 `verity/…/nci/lean/` | the four-name layout (`layers`) | high | — |
| `Nci/SecurityProofs.lean`, `Nci/SecurityProofs/{Chain,Inequalities,LoomisWhitney,Throttling}.lean` | `security_proofs/nci/` | P2; it imports `Verity.SecurityProofs`, so the math package requires core's math package | high | — |
| the `upstream` watch entry `loomis-whitney` | with the math, in `security_proofs/nci/`'s policy | S3.1; the lemma it watches is in the math | medium | lean: does the validator read `upstream` from the math package's policy, or from the spec's lock? |
| `Nci.lean` (umbrella) | `security_proofs/nci/` | S3.1 | high | — |
| `lean-audit.json`, `lakefile.toml`, `lake-manifest.json`, `lean-toolchain` | the spec package; `lean-audit.json` split | S3.1 | high | — |

## `benchmarks/` (stays, minus kernels, calibration and frozen workloads)

`benchmarks/` stays, but P5 and P7 take the kernels a result rests on out of it. vLLM's `protocol_options/pouw.py` and
`pouw_pearl_c_device.py` load the sm_120 kernel directory from the run tree's `benchmarks/pouw/pearl_c_sm120`. Under P7
they load it from `verity/kernels/pearl-c-sm120/` instead. `tools/research/src/research/store/tools_registry.py` names
`benchmarks.pouw.tool`, so that path stays.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `judge.py`, `latency_compare.py` | stays | run judges over `verity_numerical` | high | — |
| `commitments/` | stays | cost benchmarks | high | — |
| `dot_product/`, `ir_call/` (frozen D-SP1 workloads) | `archive/sp1/` with D-SP1 | S4: frozen backends to `archive/`, each with its record | medium | proofs (outside this map's owners): do they still build against the frozen backend? |
| `network_traces/record.py` (vLLM trace capture) | `tools/warden_capture/` | P3: capture is a tool; the traces are preserved inputs, never re-recorded | medium | network-accounting |
| `network_traces/replay.py`, `active_replay.py`, `run.sh`, `tests/` | stays | the warden's replay set (convert, calibrate, audit on preserved traces) | medium | network-accounting: is `replay.py`'s conversion part of the audit a result rests on, which would put it in `verity/`? |
| `one_stage/` | stays | runs the one-stage audit end to end with C-Flock's circuit prover; it imports the demo population programs | high | — |
| `private_circuit/` | stays | C-Flock ZK benchmark | high | — |
| `pous/{bench.py, pod.sh, weight_sets.json, side_by_side.py, explorer.py, README.md}` | stays | `bench.py` imports `dense` and `p2`, which is fine from `benchmarks/` | high | — |
| `pous/band_gpu/` (`codec.py`, `dense.py`, `harness.py`, `live.py`, `native.py`, `pous_native.cu`) | Split: the kernel → `verity/kernels/pous-band-<device>/`, consolidated with vLLM's `engine.pous` kernels; the harness stays; `codec.py`'s P3 import goes with P3 to experimental | P5, P8 (consolidate) | low | memory-accounting: does a result rest on these kernels, or on vLLM's copies? Which copy is kept? |
| `pous/erase_calib/` (secure-erasure calibration, Triton fill kernels) | Split: the calibration → `tools/pous_erase_calib/` (it builds the erase-timing entry, P3); the fill kernels → `verity/kernels/` if the erasure audit runs them | P3, P5 | medium | memory-accounting: waits on #1096 and #1086 |
| `pous/hbm_audit/` (TwoTierBandwidth) | `experimental/pous/hbm_audit/` while it runs, else `archive/pous-hbm-audit/` | P8: TwoTierBandwidth killed (no host RAM); the HBM sweep art:59c46dd8 isn't re-run | medium | memory-accounting: does it still run, and does it still teach? |
| `pous/p2_gpu/` (CGBN `p2dec.cu`, P2 v2) | `experimental/pous/p2/gpu/` | P2 v2 live, nonconforming | high | — |
| `pous/p2_v1/` (P2 v1 frozen spec, reference, kernel) | `experimental/pous/p2/v1/` | the plan: the frozen P2 spec goes to the store or beside its code in `experimental/pous/` | medium | memory-accounting: the store, or beside its code? |
| `pouw/pearl_c_sm120/` | Split: the kernel (`pearl_c_sm120.cu`, `mainloop_sm120.cuh`, `h2_rows_stats.cuh`, `build.sh`, `sass_gate.py`) → `verity/kernels/pearl-c-sm120/`; `run.py`, `pearlc_arm.py`, `fixture.py`, `verify.py` stay | P5, P7; `pearl-c-sm120-v1` in `verity/` | high | — |
| `pouw/pearl_c/` (H100) | Split: `hash.cuh`, `hash_h2.cuh`, `hash_sm120.cuh` (included by the sm_120 kernel) → `verity/kernels/pearl-c-sm120/`; the H100 kernel `pearl_c.cu`, `acc.h`, the h1 code, `ftz_gate.py`, `twin.py`, `simt_twin.py` and the rest → `experimental/pouw/pearl_c_h100/` | Layout: the H100 lane is experimental until a guarantee rests on it, then the sm_90 entry | high | — |
| `pouw/pouw_hash/` | Split: `pouw_hash.cuh` (included by the sm_120 kernel) → `verity/kernels/pearl-c-sm120/`; the bench and check stay | P5 | medium | — |
| `pouw/pearl_c4/` | `experimental/pouw/nvfp4/` | Layout | high | — |
| `pouw/nvfp4_sm120/` (`nvf4_plain.cu`, `fp8_bench`, `mainloop_nvf4.cuh`) | `experimental/pouw/nvfp4/` | Layout | medium | compute-accounting: the plain FP8 baseline could stay in `benchmarks/` |
| `pouw/harness/` | stays, except `sass_gate.py`, `sass_pins.json`, `ieee_pin.*` → `verity/kernels/` build (P5: the gate on every cache fill) | P5 | medium | compute-accounting: does the gate sit in the registry's build or in `tools/`? Where do `price_twins.py`/`.json` go once `DevicePrices` leaves the lock? |
| `pouw/kernels/pouw_gemm.cu` (`ncp-v1` route-U, RTX 4090) | `verity/kernels/ncp-route-u-sm89/` if a result rests on it, else stays | P5; `ncp-v1` in `verity/` | medium | compute-accounting: `e2e_audit.py` is its only user. Is it a registry entry? |
| `pouw/exhaustion/` (the salt-to-deadline window and its CPU audit) | stays | a timed run of `pearl-c-sm120-v1-h1` over the panel's kernel | medium | compute-accounting: does a cited result rest on `exhaustion/audit.py`'s certified fraction? If so, that audit belongs in `verity/…/pouw/`. |
| `pouw/pearl_c_vllm/` | stays | served runs | high | — |
| `pouw/{gamma.py, e2e_audit.py, gemm_bench.py, route_u_bench.py, vllm_bench.py, ncp2_gpu_bench.py, check_route_u_sass.py, run_result.py, tool.py, workloads.json, pearl_b200_setup.sh, README.md, tests/}` | stays | benchmarks | high | — |
| `pouw/pearl_calibration.py` (Pearl's B200 calibration) | `tools/pouw_calibrate/` | P3 | medium | compute-accounting |

## Where `verity/` would import `catalog/`, `experimental/` or `benchmarks/`

P6 lets `verity/` import nothing else in the repository, and P9's boundary test fails closed. These are the edges the
destinations would create, and the split that must come first in each case.

### PoUS

1. `band.py` and `schemes/band.py` import `dense.DenseChain`. If the dense scheme goes to experimental, the overwrite
   chain band builds on must first move into a `verity/` module of its own.
2. `audit.py`, `setup.py` and `verifier.py` import `Encoding` from P3's `scheme.py`. `Encoding` must move into
   `codec.py` first.
3. `labels.py`, `dense.py`, `setup.py` and `schemes/p2.py` import `SALT_BITS` (and `labels.py` imports `Params`) from
   P3's `params.py`. The salt and tag widths must move to `layout.py`. `labels.py` must then take its widths as
   parameters.
4. `primitives.py` mixes four destinations. It must be split before anything moves. Its `pi2_call_ns` must take the
   Keccak-f step as a parameter rather than default to `KECCAK_F_NS`.
5. `oracle.py` is test-only by convention, but `dense`, `primitives`, `scheme` and `audit` import it. The types the
   deployed code uses must be separated from the model's first.
6. `schemes/__init__.py` imports `p2` and `p3`. The registry must stop listing them, with experimental registering its
   schemes on its own side.
7. `audit.py`'s `DEADLINE_NS`, `RTT_ALLOWANCE_NS` and `CALL_NS`, and `schemes/p2.py`'s `ROOT_CALL_NS`, are device
   numbers. They must become values the verifier passes in from a catalog entry, with no default in `verity/` code.

### PoUW

1. `pearl_kw.py` holds Pearl's shared pieces, which `pearl_c`, `pearl_c_debit`, `pearl_c_work` and `circuit/pc8` import.
   They must be extracted into a `verity/` module before `pearl-fp8-v4` moves to experimental.
2. `pearl_c.py` holds the v0 forming (superseded) beside the v1 forming. v0 must be split out, or kept behind a
   fail-closed refusal.
3. `pearl_c_device.py`'s records are device numbers bound for `catalog/devices/`. `pearl_c_work`, `pearl_c_debit`,
   `pearl_c_u`, `circuit/pc8` and `circuit/rowk` import them directly. `pearl_c_debit` already takes a device and only
   defaults to the H100. Each must take the device as a parameter with no default first.
   `Device` also reads `verity.ml.tc.models`' Hopper and Blackwell constants, which P3 sends to the catalog as hardware
   models. That is core's split (circuits with @architecture), but this module depends on it.
4. `schemes/__init__.py` (`SCHEMES`) and `identifier.py` list the six experimental schemes. They must shrink to the three
   `verity/` entries, with the experimental registry kept apart, before the H100 and NVFP4 code moves.
5. `circuit/__init__.py` (`verify`), `partition.py`, `plan.py` and `reference.py` import `ncp2` and `words`, which P3
   sends to `catalog/definitions/`. Either the guarantee's circuit stays in `verity/`, or `verify` takes its Definition
   from the catalog entry the verifier chooses. This waits on @architecture's catalog entry format.
6. `circuit/plan.py` and `circuit/rowk.py` import `pc4`, the NVFP4 tile check bound for experimental. Its templates must
   become data they're given first.
7. In Lean, the certified γ reads `Pouw.Protocol.PearlC.Sm120`, `DeviceRev1` and the other device modules. The Layout puts
   Lean device instances in `catalog/`, which would make the spec `require` the catalog. Either the guarantee is restated
   over a device parameter with a named device assumption (a change of meaning, with Daniel's DM), and each result names
   the catalog instance it used (P10). Or the instance the guarantee is about stays in the spec.
8. In Lean, `Pouw/Protocol.lean` imports every generated-vector module, and `Fp8Atom.Pinned` and `H1TPinned` import
   vectors. The umbrella must drop those imports, and the Pinned modules must move to `security_proofs/pouw/`, before the
   vectors go to `catalog/`.

### The warden and sampled proofs

1. `capacity.py`'s `K_BITS` must become a parameter before K becomes a catalog entry. No `verity/` module imports
   `calibration.py`, so it moves to `tools/` without a split.
2. If `law.py` goes to experimental, vLLM's legacy challenge must stop importing `ru_key`/`vu_key` first. That edge is
   integration → experimental, which P6 allows, but it would keep a legacy path alive. No `one_stage/` module imports
   `law.py`; only `plan.py` does.

### Integrations

vLLM's Pearl-C option loading its kernel from `benchmarks/pouw/pearl_c_sm120` is the one integration → benchmarks edge,
which P7 forbids. Moving the kernel into `verity/kernels/pearl-c-sm120/` removes it. That kernel includes
`../pearl_c/hash_h2.cuh` (which includes `hash_sm120.cuh` and then `hash.cuh`) and `../pouw_hash/pouw_hash.cuh`, so those
headers must move with it. Otherwise `verity/kernels/` would include from `experimental/` and `benchmarks/`.

## Open questions, by owner

### compute-accounting (PoUW, the sampled-proofs audit law)

1. The scheme registry: one `SCHEMES` that experimental code adds to, or two registries and an explicit choice by the
   caller? A hook that experimental fills would let an audit accept an experimental scheme, against P9's fail-closed
   boundary.
2. Who passes the chosen device record into `pearl_c_work`, `pearl_c_debit`, `pc8` and `rowk` once the records are
   catalog entries? And does the certified γ restate over a device parameter, or does `Sm120` stay in the spec?
3. Do `ncp-v2`'s templates (`ncp2`) stay in `verity/` as the guarantee's circuit, or does `verify` take them from a
   catalog entry? This waits on @architecture's entry format.
4. Which of the unpinned Pearl-C tile-check modules does `EndToEnd` read after slice 6? Are `Hidden*` and the cap
   assumptions future reads?
5. Is sampled proofs under `verity/protocols/verification/` beside C-Flock, or its own protocol? Is the two-stage law
   (`law.py`) under any guarantee, and is `plan.py` superseded infrastructure to delete?
6. Is `pouw_gemm.cu` a registry entry? Does a cited result rest on `exhaustion/audit.py`?

### memory-accounting (PoUS)

1. Dense: keep `dense.py` and `schemes/dense.py` in `verity/` while `ChainDenseMeets64` is locked, or extract the
   overwrite chain and send the dense scheme to experimental, dropping that pin?
2. P2 and P3: their code is experimental while six P2 pins and the `P3Concrete*` statements are proposed to stay locked.
   P9 has no locked guarantee whose only code is experimental. Do the pins leave until promotion, or does P2 v3 promote
   when #1123 lands?
3. The grader: keep `Sanity.lean` and `Accounting/Numbers.lean` in the spec package under their names, or narrow the
   grader's trusted import set, `TRUSTED.sha256` and `Grader/Registry.lean` in the same PR as the proofs' move?
4. Which of `audit.py`'s counts are spec parameters and which are calibrated device numbers? The RTT allowance also waits
   on Daniel's window ruling.
5. Which copy of the band kernels is kept, `benchmarks/pous/band_gpu/` or vLLM's `engine.pous`? Are the band and dense
   scheme vectors the agreement between them?

### network-accounting (the warden)

1. Is K (`K_BITS`) a catalog parameter, or NCI's policy constant stated in a spec?
2. Is `benchmarks/network_traces/replay.py`'s conversion part of the audit a result rests on?
3. Does `scripts/difftest_vectors.py` stay with the difftest's tests or become a `tools/` builder? Either way, its `runs`
   generate path must follow each move (with ci).

### lean (NCI and the Lean layout)

1. Lifting: after the reduction no guarantee reads it. Does it go back to `security_proofs/pouw/` on the validator's
   report?
2. Does moving a theorem out of a read spec module (PoUW's `Accum`, `PeelExactP`, `Game`, `Instance`; PoUS's dropped
   `Guarantees.lean` statements) change that module's record through its `reads` digest, or does the validator compare
   definition hashes only?
3. Spec runners (`NetTiming/Difftest.lean`, `PouwBulk.lean`): spec package or math package?
4. NCI's `upstream` watch entry (`loomis-whitney`): which package's policy carries it after the split?
5. The area names under `security_proofs/`: `pous`, `pouw`, `warden` and `nci`, following `flock`?
