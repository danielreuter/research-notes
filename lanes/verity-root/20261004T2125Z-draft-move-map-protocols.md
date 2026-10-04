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

The owners' answers of 4 Oct are folded into the rows: compute-accounting's
(`note:compute-accounting/20261004T2247Z-draft-move-map-answers`, revised 23:09Z for Daniel's 4:06 PM ruling),
memory-accounting's (`note:memory-accounting/20261004T2245Z-report-move-map-pous-answers`), and network-accounting's and
lean's in the kickoff thread (1791150333.889129), with the captain's calls on them. They were checked against main
`9400e83d5`; where this fold rechecked a fact, it says at which commit. A resolved question reads "answered (OWNER, 4
Oct): …". Where two owners disagree, the row keeps the draft's destination and the disagreement is listed under
"Conflicts for the captain" at the end. The counts in "Counts by destination" are the draft's and were not recounted.

Python import names follow the new directories (Daniel, 4 Oct 3:50 PM PDT), and the move script carries a module map
beside its path map. In Lean, declaration names are kept, while proof modules move under a root of their own
(`PousProofs.*`, `PouwProofs.*`; lean, verity#1144); the umbrella module and any proof module that stays in a spec
package (PoUW's `Lifting` until the validator reports it, PoUS's `Sanity` and `Accounting/Numbers`) keep the spec's
root.

Daniel's 4:06 PM ruling, as the plan records it, changes PoUW's split: a claim about a computation is verified only by
a sampled proof over C-Flock with zero-knowledge, and a replay is a diagnostic that is never in `verity/`. Only `ncp-v2`
and `ncp-v2-shift24` run under sampled proofs today, so `verity/`'s PoUW registry is those two until Pearl-C's tile
check passes under sampled proofs. PoUS and the warden check physical facts, not computations, and keep their checks.

Daniel's 4:19 PM ruling, as the plan records it: only the prover's zero-knowledge layer is trusted, and every kernel
lives outside `verity/`, in a top-level `kernels/`. A destination written `verity/kernels/…` below reads `kernels/…`.

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

So its code is TCB. Its Lean is not in this package. It is `FlockSoundness.Audit.*` inside C-Flock's soundness (38
files, 26 at its top level and 12 under `Partitioning/`, and 120 pins; compute-accounting, 4 Oct), and S3.1 moves it
whole to `security_proofs/flock/` under its current names. A spec of its own, with its game folded into core's model,
is an S3.3 job. The plan names `Audit.Work.work_escape_le`, but the pin is `FlockSoundness.Audit.Law.work_escape_le`.

Sampled proofs' Python cites C-Flock audit-law pins: `one_stage/draw.py` cites `work_escape_le`, `one_stage/consumers.py`
cites `audit_exfiltration` and `card_admissible_le`, and PoUW's `circuit/plan.py` cites eight (compute-accounting §A1).
Whether the flock lock keeps them, or that code stops citing them, is proofs' and pouw-lock's call.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `verity_sampled_proofs/one_stage/audit.py` | `verity/protocols/verification/sampled_proofs/one_stage/audit.py` | P1: the audit record and its `IntegrityProfile` | high | answered (compute-accounting, 4 Oct): beside C-Flock under `verification/`. Daniel's ruling of 3 Oct ("PoUW's tile check is a sampled proof", `EDGES = {"pouw": {"sampled_proofs"}}` in `tests/test_protocol_boundaries.py`) makes it a verification protocol that the accounting protocols consume, and its Lean is C-Flock's `FlockSoundness.Audit.*`. |
| `one_stage/draw.py` | `verity/…/sampled_proofs/one_stage/draw.py` | P1, P5: the verifier's draw checks, its coins from `verity.randomness` | high | — |
| `one_stage/registration.py` | `verity/…/sampled_proofs/one_stage/registration.py` | P1: the record fixed before the draw | high | Correction (compute-accounting, 4 Oct): vLLM does not import it; `serving_rows.py` keeps its own `verity/one-stage/registration/v0`, and the only importers are `benchmarks/one_stage`. The destination stands. |
| `one_stage/registered.py` | `verity/…/sampled_proofs/one_stage/registered.py` | P1: registered values opened against their commitment | high | — |
| `one_stage/verdict.py` | `verity/…/sampled_proofs/one_stage/verdict.py` | P1 | high | — |
| `one_stage/consumers.py` | `experimental/sampled_proofs/consumers.py`, with `test_consumers.py` and the Lean difftest | AGENTS.md: consumers read the profile "with their own utilities; their readers stay out of core"; P9 | medium | answered (compute-accounting, 4 Oct): consumer code, until a consumer adopts it. Nothing imports it outside its tests and the README. It is the Python twin of `audit_exfiltration` and `card_admissible_le`, checked against `tests/fixtures/exfiltration_lean.json`, and `verity.claims` has no sampled-proofs id. |
| `one_stage/partition.py` | `verity/…/sampled_proofs/one_stage/partition.py`, whole | P1 | medium | answered (compute-accounting, 4 Oct): don't split it. `population_program` and `mixed_population_program` are two small builders (about 40 of 126 lines) that build the program shape the audit runs on and hold no data. Their users are the package's `test_one_stage.py`, `stratified_agree.py` and `benchmarks/one_stage/a0,a2,a3`; sending them to `examples/` would make `verity/`'s own test import `examples/`. |
| `law.py` (the two-stage law, `OwnRandomness`, `ru_key`/`vu_key`) | `experimental/sampled_proofs/law.py` while vLLM's `LEGACY` is true; promoted with the two-stage pins when decision 42 flips it | P9: no guarantee reads it today | medium | answered (compute-accounting, 4 Oct). The draft's evidence was inverted: vLLM's `commit/challenge.py:30` imports `ReplayUnit`, `Stage`, `TwoStageLaw`, `select_verification_units` and `vu_key` for the non-legacy draws, and line 33 sets `LEGACY = True`. That import is integration → experimental, which P6 allows, so nothing moves first. C-Flock's soundness pins `twoStage_exfiltration`, `twoStage_influence` and `flock_two_stage_exfiltration`, which no Python cites; `pouw/sp-layout-a` is live. Ordering: if decision 42 is close, `law.py` stays in `verity/` and skips the round trip (Daniel or the coordinator). |
| `plan.py` (`VerificationPlan`) | `experimental/sampled_proofs/plan.py`, with `law.py` | P8, P9: only its own test and vLLM's `test_running_example` use it, and it imports `.law` | medium | answered (compute-accounting, 4 Oct): not deleted. The README says the two-stage driver is "not built yet", and its approach is live. |
| `README.md` | `verity/…/sampled_proofs/README.md` | Conv: PROTOCOL.md (the short README stays) | high | — |
| `tests/` (suites) | `verity/…/sampled_proofs/tests/` | Conv: tests | high | — |
| `tests/lean/ExfiltrationVectors.lean`, `generate.sh`, `fixtures/exfiltration_lean.json` | `experimental/sampled_proofs/`, with `consumers.py`; the generate paths follow `FlockSoundness.Audit` to `security_proofs/flock/` | S3.1: difftest paths follow each move | medium | answered in part (compute-accounting, 4 Oct): they go with `consumers.py`. Still open for lean: which package the difftest builds against after S3.1. The audit fails closed on an unresolved `runs` path (lean, 4 Oct). |

## PoUS Python (`protocols/pous/`, memory-accounting)

These are the statuses the plan's step 2 gives:

- **Live:** `band-d12`, P2 v3 (`ec-p2-16448`, #1123) as the candidate, and P3, which has no certificate. Correction
  (memory-accounting, 4 Oct): P2 v2 is now `pous/p2-chacha8-keys`, superseded by `pous/ec-p2-16448`; its codec stays as
  the nonconforming `p2-16448/v2`, which the `p2-gpu` bench arm measures, so it goes to `experimental/pous/p2/` with v3.
- **Superseded:** `dense`, by band. Band and dense's ideal-model theorems still stay guarantees.
- **Killed:** the hardware reading of their deadlines (art:7617c801, #1122), `feistel-indifferentiability` (refuted), and
  TwoTierBandwidth (no host RAM).

From the registry: `miyaguchi-preneel-h` is killed, `sponge-h` and `ec-p2-5504` are superseded, and `ec-cuda-arx-p3` is
killed. memory-accounting registered more on 4 Oct: killed `pi2-wallclock-floor`, `feistel-indifferentiability`,
`two-tier-bandwidth`, `cost-rule-relaxations` and `erased-encode-secrets`; parked `keyed-page-fill-erasure`,
`symmetric-wide-final-step` and `p2-xor-reduce-compression`; live `p2-seqroot-cooperating-cores`; merged
`continuous-audit`, `rebuild-exclusion`, `continuous-time-average` and `continuous-complete`.

PoUS moves late in S5. It waits for #1123, #1096, #1086 and the root-floor recalibration. memory-accounting also has
P2's RTT allowance and root floor waiting on Daniel's window ruling; the plan records that ruling at 2:21 PM PDT (the
RTT allowance capped near 0.35 ms, Δ + RTT ≤ about 0.85 ms, and w stays 16,448), and the RTT-cap option is a draft on
`cursor/pous-p2-rtt-cap-3cf5`. The values follow the ruling when the P2 code moves.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `verity_pous/protocol.py` | `verity/…/pous/protocol.py` | P1: the `Scheme`/`Certificate`/`Verifier` interface | high | — |
| `verity_pous/codec.py` | `verity/…/pous/codec.py`, receiving `Encoding` from `scheme.py` | P1: the seam between a scheme and the audit | high | — |
| `verity_pous/band.py` | `verity/…/pous/band.py` | `band-d12` live; `BandMultiMeetsFamily` and its D2/D1/D0 forms stay guarantees (ideal-permutation model, #1122) | high | — |
| `verity_pous/dense.py` | Split: the overwrite chain band builds on (`DenseChain`) → a `verity/…/pous/` module of its own (e.g. `chain.py`); the dense scheme → `experimental/pous/dense/` | `dense` superseded by `band-d12`; P9 | high | answered (memory-accounting, 4 Oct). The chain extraction lands first and clears edge 1. `ChainDenseMeets64` then leaves the lock: no ledger row, published table, claim id or docs page relies on it (the lock-reduction draft `cursor/pous-lock-reduction-3cf5` checks this), and if a band statement reads it, it stays as a read, not an entry. The harness's `dense-chain/v1` arm (`band_gpu/harness.py`, `pod.sh SCHEME=`) moves with the scheme. |
| `verity_pous/scheme.py` | Split: `Encoding` → `verity/…/pous/codec.py`; the P3 scheme → `experimental/pous/p3/scheme.py` | P3 live, no certificate; `audit`, `setup` and `verifier` import `Encoding` | medium | answered (memory-accounting, 4 Oct): P3 is not under a guarantee until promotion. The `P3Concrete*` pins leave the lock, their statements stay as `def`s in `Guarantees(.P2).lean`, and their proofs keep building in `security_proofs/pous/`. |
| `verity_pous/params.py` | Split: `SALT_BITS`, `TAG_BITS` → `verity/…/pous/layout.py`; P3's `Params`, `OPERATING_POINT`, `LEAN_P3_MEETS` → `experimental/pous/p3/params.py` | P3 status; `labels`, `dense`, `setup` and `schemes/p2` read `SALT_BITS` | medium | memory-accounting: `labels.py` takes P3's `Params`. Is its layout generic over a band label width, or P3-only? |
| `verity_pous/labels.py` | `verity/…/pous/labels.py` | P1: Lean's `Bits` layout, read by `verifier`, `dense` and `primitives` | high | — |
| `verity_pous/primitives.py` | Split four ways. `pi2_keccak_f`, `OverwriteStepper`/`OverwriteChain` and `Feistel10`/`FeistelPi` → `verity/…/pous/primitives.py`. `KECCAK_F_NS = 50` and `pi2_call_ns`'s floor → `catalog/devices/`. `FeistelP`, `ArxButterfly`, `EvenMansourArx` and `heuristic_arx` → `experimental/pous/p3/`. `XorSponge`, `MiyaguchiPreneel`, `RandomOracleKey`, `IdealPermutation`, `IdealTweakablePermutation` and `ideal` → tests | Conv: tests (broken attack modes, the oracle); P3 ("PoUS's Keccak step"); the statuses above | medium | answered (memory-accounting, 4 Oct): no deployed path reads the ideal objects. `band.ideal` and `dense.ideal` are model constructors that only `test_pous_band`, `test_pous_dense` and `test_pous_scheme` call, so they move to the tests too; `band_gpu/codec.py` only names `XorSponge` in a docstring. |
| `verity_pous/oracle.py` | Split: `Prog`, `run`, `pure`, `Cost` and `Query` → `verity/…/pous/oracle.py`; what only the adversary and the model use → tests (`tests/pous_oracle.py`) | Conv: tests; P1 for the program types deployed code is written in | medium | answered (memory-accounting, 4 Oct): `Prog` and `run` are used by `scheme`, `protocol`, `audit` and `dense`; `pure` and `Cost` by `audit`; `Query` by `primitives` and `dense`. A split row, not a whole-file move. |
| `verity_pous/adversary.py` | tests (`tests/pous_adversary.py`) | Conv: tests | high | — |
| `verity_pous/audit.py` | Split: `TimedVerifier` and the spec and certificate parameters `AUDIT_CAP`, `LATE_ROUNDS`, `WORK` and `CHALLENGES` → `verity/…/pous/audit.py`, pinned to Lean; `CERTIFIED_ROUNDS` (D = 10, P3's certificate point) → `experimental/pous/p3/`; `DEADLINE_NS` (Δ), `RTT_ALLOWANCE_NS` and `CALL_NS` (the 242 µs floor) → `catalog/devices/`, with no default in `verity/`; `simulate` (the model's clock) → tests | P1 (the deployed verifier); P3 (device numbers) | medium | answered (memory-accounting, 4 Oct). Lean's `Accounting.Params` holds only ρ, δ, the 21/20 expansion and λ; `AUDIT_CAP` is `Pous.Rebuild.auditCap` (read by `BackgroundRebuildExcluded`), `LATE_ROUNDS` is `BandGradedMeetsFamily`'s `D_late ≤ 12`, `WORK` is Q, and `CHALLENGES` (k) is in practice each certificate's own k. The band's D comes from its certificate. Every wall-clock reading holds in the ideal-permutation model only (#1122). |
| `verity_pous/continuous.py` | `verity/…/pous/continuous.py` | P1: the `ContinuousAudit` verifier (ideal model only, #1122) | high | — |
| `verity_pous/layout.py` | `verity/…/pous/layout.py` | P1: vLLM's PoUS option reads it | high | — |
| `verity_pous/setup.py` | `verity/…/pous/setup.py` | P1 | high | — |
| `verity_pous/verifier.py` | `verity/…/pous/verifier.py` | P1: the vk, a SHA-256 RFC 6962 Merkle tree | high | answered (memory-accounting, 4 Oct): adopt the shared tree later, as a change of meaning with a bridge; the move stays pure. |
| `verity_pous/schemes/__init__.py` | `verity/…/pous/schemes/__init__.py`, without the `p2` and `p3` imports | P6, P9 | high | — |
| `verity_pous/schemes/band.py` | `verity/…/pous/schemes/band.py` | `band-chain/d12/v1`, certificate `BandMultiMeetsFamily` | high | — |
| `verity_pous/schemes/dense.py` | `experimental/pous/dense/` | `dense-chain/v1`; approach superseded; P9 | high | answered (memory-accounting, 4 Oct): with `dense.py`'s scheme; `ChainDenseMeets64` leaves the lock. |
| `verity_pous/schemes/p2.py` | Split: the scheme → `experimental/pous/p2/scheme.py`; `ROOT_CALL_NS = 2_900_000` → `catalog/devices/` | `p2-16448/v2` (ChaCha8, nonconforming, superseded), marked EXPERIMENTAL; v3 is the candidate | high | answered (memory-accounting, 4 Oct): P2 v3 does not promote when #1123 lands. The P2–M1-SGI instantiation assumption is not accepted (spec decision 8), the XOR-then-reduce compression attack is open, and the window and w are Daniel's. The six P2 pins leave the lock, their statements stay as `def`s, and promotion re-pins them with one statement review. #1123's `test_certificates_name_proved_guarantees` then exempts experimental schemes again. |
| `verity_pous/schemes/p3.py` | `experimental/pous/p3/scheme.py` | `p3/v1`, no certificate | high | — |
| `PROTOCOL.md` | retired: definitions to the Lean spec, parameters to `catalog/`, threat model and lifecycle to the README | Conv: PROTOCOL.md | high | — |
| `DISCREPANCIES.md` | `verity/…/pous/DISCREPANCIES.md` | an allowed current-truth file | high | answered (memory-accounting, 4 Oct): it stays. Its rows record where Python and Lean conform, which is current truth; B6's verdict is already registered as `pous/pi2-wallclock-floor` and `pous/feistel-indifferentiability` (both killed). |
| `README.md` | `verity/…/pous/README.md` | Conv: PROTOCOL.md | high | — |
| `tests/` (suites, `conftest.py`, `pous_state_game.py`, `pous_continuous_model.py`, `pous_vectors.py`, `pous_scheme_vectors.py`) | `verity/…/pous/tests/` | Conv: tests | high | — |
| `tests/fixtures/schemes/{band-chain-d12-v1,dense-chain-v1}.json` | `catalog/vectors/pous/` (the dense file with the dense scheme, if it goes to experimental) | P3: generated vectors; Conv: PROTOCOL.md (a vectors file is the spec where two implementations agree) | high | answered (memory-accounting, 4 Oct): they are the agreement between the reference codec and `benchmarks/pous/band_gpu/`'s kernels, which `bench.py` gates against them. There is no vLLM `engine.pous` on main. |
| `tests/fixtures/schemes/{p2-16448-v2,p3-v1}.json`, and #1123's `p2-16448-v3.json` and `tests/fixtures/p2-v1-keys.json` (the spec's key vectors) | `experimental/pous/{p2,p3}/` | P9 | high | Correction (memory-accounting, 4 Oct): #1123 adds the two P2 fixtures, and both go to `experimental/pous/p2/` with `p2-16448-v2.json`. |
| `tests/lean/*Check.lean` and their generate scripts | stay in the tests; generate paths updated at each move | S3.1 | medium | lean: does each check build against the spec package or the math package? |
| root `tests/test_pous_bench.py`, `tests/test_pous_harness.py` | tests: `benchmarks/pous/tests/` | Conv: tests (the root suite keeps only whole-tree invariants) | high | answered (memory-accounting, 4 Oct): they test `benchmarks/pous`'s dataset, implementation registry, certificate gate and `band_gpu/harness.py`, not `verity_pous`. |

## PoUS Lean (`protocols/pous/lean/`, memory-accounting; layout with lean)

`lean-audit.json` has `roots: ["Pous"]` and 104 pins. Its `layers` are `Pous.Protocol`, `.Game`, `.Model`, `.P2`,
`Pous.Assumptions(.P2)` and `Pous.Guarantees(.P2)`, and `reads` lists 34 modules. Its exempt entries are
`PousTargets`, `CheckAxioms`, `Grader` and `submissions`. S3.1 says PoUS's split already exists in the tree.

S3.1 also requires that `TRUSTED.sha256`, `CheckAxioms.lean` and `Grader/Registry.lean` update in the same PR that moves
the proofs. `TRUSTED.sha256` lists two `SecurityProofs` files, `Pous/SecurityProofs/Sanity.lean` and
`Pous/SecurityProofs/Accounting/Numbers.lean`. `grade.sh` lets submissions import those same two files beside the spec,
and builds them. So the same PR must either keep these two files in the spec package under their names (as PoUW's
`Lifting` stays), or change the grader's trusted set and `TRUSTED.sha256` together. answered (memory-accounting, 4 Oct):
keep them in the spec package under their names, with the spec's root `Pous`, so `TRUSTED.sha256` and `grade.sh`'s
import set don't change and the move stays pure. Every other proof module moves under `PousProofs.*` while its
declarations keep `namespace Pous.SecurityProofs` (verity#1144). Narrowing the trusted set is a separate, reviewed
change.

The lock (correction, memory-accounting, 4 Oct): "104 pins, about 73 after the reduction" was round 2's count. Under
Daniel's 2:03 PM guarantee ruling the lock-reduction draft (`cursor/pous-lock-reduction-3cf5`) keeps 15: 11 kept
(`BandMultiMeetsFamily` and its D2, D1 and D0 forms, `ChainDenseMeets64`, and six P2 pins, all read by code today) and 4
held (`DigestAU` and three `SecureErasureMeets*`, while #1096 and #1086 are open). At the Python move, dense and P2 leave
with their code, leaving the band's four plus whatever the erasure PRs settle.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `Pous/Protocol.lean`, `Pous/Protocol/Game/{Prob,Oracle}.lean` | spec | `layers` `Pous.Protocol`, `.Game`; in `reads` | high | — |
| `Pous/Protocol/Model/*` (21 files: band, dense, P3, M1/M1p, audit and erasure models) | spec | `layers` `Pous.Protocol.Model`; all 21 in `reads`; S3.1 names `Protocol/Model` spec | high at S3.1, medium after | answered (memory-accounting, 4 Oct): they all stay in the spec at S3.1, which is a pure move. Once the validator reports spec definitions no guarantee reads, a later consolidation moves `ColumnGame`, `M1` and `M1p` out; `P3Chain` stays anyway, because `BandChain` imports it. |
| `Pous/Protocol/Accounting/{EraseMeets,GradedMeets,LemmaA,Params,PubMeets,Rebuild}.lean` | spec | `meaning` includes `Pous.Protocol`; five in `reads`, `LemmaA` through `Pous.Assumptions` | high | — |
| `Pous/Protocol/P2/Cost.lean` | spec at S3.1 | `layers` `Pous.Protocol.P2`; read by the P2 pins | medium | answered (memory-accounting, 4 Oct): it stays at S3.1 and leaves in the later consolidation if the validator reports it unread once the P2 pins leave the lock. |
| `Pous/Assumptions.lean`, `Pous/Assumptions/P2.lean` | spec | `assumptions` | high | — |
| `Pous/Guarantees.lean`, `Pous/Guarantees/{P2,SecureErasure}.lean` | spec | `layers`; holds the 104 pinned statements, 15 locked after the reduction | high | answered (memory-accounting and lean, 4 Oct): the dropped statements stay as `def`s, so no record or digest changes; moving them out is later consolidation. lean: a `reads` record hashes only the definitions some guarantee reads, so an unread statement leaving would not change it either, except where a dropped guarantee was the only reader of something. |
| `Pous/SecurityProofs/**` except `Sanity.lean` and `Accounting/Numbers.lean` (56 files) | `security_proofs/pous/`, under the module root `PousProofs.*` with declarations in `namespace Pous.SecurityProofs` | P2; verity#1144 | high | — |
| `Pous/SecurityProofs/Sanity.lean`, `Pous/SecurityProofs/Accounting/Numbers.lean` | spec package, names and root `Pous` kept | both are in `TRUSTED.sha256` and in `grade.sh`'s allowed imports | high | answered (memory-accounting, 4 Oct): keep them in the spec package, as PoUW keeps `Lifting`; narrowing the grader's trusted set is a separate, reviewed change. |
| `Pous.lean` (umbrella) | `security_proofs/pous/` | S3.1: umbrellas move to the math package | high | — |
| `PousTargets.lean` (every pinned statement as a `sorry` stub; exempt) | `security_proofs/pous/` (exempt) | open targets | medium | answered (memory-accounting, 4 Oct): it stays, exempt, until the grader's registry lists every open target, then it retires. |
| `Grader/Registry.lean`, `Grader/Main.lean` | `tools/pous_grader/` | Layout ("PoUS's grader" under `tools/`) | medium | answered (memory-accounting, 4 Oct): `pinnedTargets` follows `Pous/Guarantees*`, not the lock; a target is any statement there and needn't be a guarantee. |
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

compute-accounting corrected this split (4 Oct, §A4–A6, revised 23:09Z for Daniel's 4:06 PM ruling):
- **`verity/`'s registry** is `circuit.SCHEMES` alone (`ncp-v2`, `ncp-v2-shift24`; `pouw/ncp-v2-circuit` is merged),
  since only those run under sampled proofs. `ncp-v1` and `pearl-c-sm120-v1-h2` (not `pearl-c-sm120-v1`, which is h0)
  sit beside their replay until their circuits run under sampled proofs, and Pearl-C's served verdict and the exhaustion
  audit are diagnostics until then. The γ statements carry over.
- **Experimental:** `pearl-c-sm120-v1` (h0) and `-v1-h1` (superseded, still building, so P8), the parked
  `pouw/pearl-c-sm120-unpromoted`, and the six the draft named.
- **Three registries today, not one:** `schemes.SCHEMES` (9 entries), `circuit.SCHEMES`, and vLLM's
  `protocol_options/pouw_pearl_c_device.py:108`, which builds its own over `(SM120,"h1")`, `(SM120_UNPROMOTED,"h1")` and
  `(SM120,"h2")`. vLLM's `scheme_of` (line 155) skips the protocol registry, `pouw.py` (line 99) unions all three, and
  `audit.Verifier` accepts any `PoUWScheme`. So the served `-sm120-v1-h1`/`-h2` and the unpromoted scheme are not in
  `SCHEMES`, and "parsing a name grants nothing" is false today. Each entry point (`Verifier`, `identifier`, vLLM's
  `scheme_of` and `EXECUTED`) must refuse a name outside `verity/`'s registry, and vLLM's `PPD.SCHEMES` must be derived
  from it. That is the vLLM PoUW option owner's change, together with whether `-h1` is still served on purpose.
- **The H100 defaults go:** H100 is the default device in `PearlC.__init__` (`pearl_c.py:387`, which also defaults
  `forming="v0"`), `pearl_c_debit.py` and `pearl_c_u.py`. Moving them with those defaults would make the experimental lane
  the default inside `verity/`.

compute-accounting's revision changes only its §C3, §C11, §C13–16, §D3 and §E4; its other answers stand as folded
below.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `verity_pouw/protocol.py` | `verity/…/pouw/protocol.py` | P1: the `PoUWScheme` interface | high | — |
| `verity_pouw/audit.py` | `verity/…/pouw/audit.py` | P1: the lifecycle and the work-weighted draw `WorkWeightedSampling` states | high | — |
| `verity_pouw/beacon.py` (drand quicknet) | `verity/primitives/crypto/beacon.py` | Layout: crypto (drand BLS) | high | — |
| `verity_pouw/bls12_381.py` | `verity/primitives/crypto/bls12_381.py` | Layout | high | — |
| `verity_pouw/identifier.py` | `verity/…/pouw/identifier.py`, looking schemes up only in `verity/`'s registry | P1: the proof's identifier v1 | medium | answered (compute-accounting, 4 Oct): two registries. If experimental work needs identifiers, `experimental/pouw/` calls the shared encoder with its own registry, explicitly. `identifier._name` refuses a name not in `SCHEMES`, nothing outside its tests imports it, and C-Flock's verifier compares `identifier_v1.json` byte for byte, so the encoding stays one. |
| `verity_pouw/serving.py` (`HASH_FORMATS`, the SchemeId grammar, `SCHEDULES`, `KernelVariant`) | `verity/…/pouw/serving.py`, whole | P1: vLLM's options parse it; it imports only the stdlib and `verity.commitments.blake3` | high | answered (compute-accounting, 4 Oct): whole, one `SchemeId` grammar (`_FP4` at line 61, `FP4_PRECISIONS` at line 58) whose docstring requires every name in use to round-trip. Correction: "parsing grants nothing" holds only once the entry points refuse, and the `-sm120-v1-h1`/`-h2` names are served, not only parsed. `ledger.py` and `price_twins.py` read `KernelVariant` and `GateRecord`, which may move to the kernel registry later. |
| `verity_pouw/schemes/__init__.py` (`SCHEMES`, `get`) | Split: no entry stays in `verity/`'s registry, which is `circuit.SCHEMES`; `ncp-v1`, `ncp-v1-shift24` and `pearl-c-sm120-v1-h2` sit beside their replay until their circuits run under sampled proofs; the other seven of today's nine (`pearl-c-sm120-v1` (h0) and the six the draft named) → `experimental/pouw/schemes.py`, which also takes the served `-h1` and the unpromoted scheme | Daniel's 4:06 PM ruling; P8, P9 | medium | answered (compute-accounting, 4 Oct, revised 23:09Z): two registries, the caller chooses, and nothing experimental fills. The directory for "beside their replay" isn't named; the plan puts PoUW's device-run replay in `benchmarks/pouw/`. |
| `verity_pouw/schemes/ncp.py` | `verity/…/pouw/schemes/ncp.py` | `ncp` live, `route-u` merged; `Theorem1` and `GammaFromTTNCP_U_v1` kept | high | — |
| `verity_pouw/schemes/pearl_kw.py` | Split: Pearl's shared pieces (`Reject`, `SIGMA_MIN`, `NOISE_NORM`, `R`, `TILE`, `WINDOW`; `f32_bits`, `f32_of_bits`, `f32`, `bf16_mul`, `bf16_to_f32`, `f32_to_bf16`, `f32_to_fp8`, `fp8_to_f32`; `hash_labelled`, `sample_line`) → `verity/…/pouw/schemes/pearl.py`; `Device`, `H100`, `B200`, `ADA`, `DEVICES`, `replay`, `device_dot`, `parse_row`, `open_row`, `exact_norms`, `noisy_quantize`, `Built` and `delta_consts` → `experimental/pouw/pearl_fp8_v4/` with the scheme | Layout: `pearl-fp8-v4` experimental | high | answered (compute-accounting, 4 Oct): the split stands, with the line drawn as listed. The shared pieces are used by `pearl_c`, `pearl_c_debit`, `pearl_c_work`, `circuit/pc8` and vLLM's `pouw_pearl_c_screen.py`. `pearl_kw`'s own device records (`pearl_kw.py:80-102`) are a second device set, whose only Pearl-C user is v0 (`pearl_c.py:503`). The 14 benchmark scripts that `import pearl_kw as P` need their imports updated. |
| `verity_pouw/schemes/pearl_c.py` (v0 and v1 formings; H100 and sm120 instances) | Split: a v1-only `PearlC` with no device default → `verity/…/pouw/schemes/pearl_c.py`, keeping `LABELS = pearl-c/v0/…` (wire constants v1 still uses); the v0 forming → `experimental/pouw/pearl_c_h100/` | Layout; P9 | medium | answered (compute-accounting, 4 Oct): split v0 out. Its branches sit inside `PearlC.__init__`, `_forming`, `credit_of`, `_side`, `admissible`, `useful`, `line_norm`, `peel_a`/`peel_b` and `NAME`, and the constructor defaults to `forming="v0"`, `device=H100`, so behind a refusal the default constructor would still build the superseded scheme. `tests/vectors/pearl_c.json` checks that no byte moved. |
| `verity_pouw/schemes/pearl_c_device.py` | Split: `Prices`, `Device` and the scheme and statement parameters `g`, `k_max`, `cap` and `standins` → `verity/…/pouw/schemes/pearl_c_device.py`; the measured `Prices` values, `atom` and `peel` (references to `verity.ml.tc.models`) for `SM120`, `SM120_UNPROMOTED`, `H100` → `catalog/devices/` | P3: device numbers | medium | answered (compute-accounting, 4 Oct): the scheme object carries its device. The registry entry builds it from catalog records (`_pearl_c(device=DEVICES[d])`, `schemes/__init__.py:27-28`), and every function takes the scheme or a `Device`, with no module-level import of a record and no default. The direct importers to change are `pearl_c.py:84`, `pearl_c_debit.py:41`, `pearl_c_u.py:52`, `pearl_c_work.py:76`, `circuit/pc8.py:63`, `circuit/rowk.py:54`, vLLM's `pouw_pearl_c_device.py` and about 13 benchmark scripts. Evidence correction: the certified γ reads Lean's `Sm120`, `DevicePricesLoop` and `devSm120v1`, not this record; the record's `SM120_PRICES.fadd = 8` is the credited price, while γ is stated at the loop price `1047/125`, which `pearl_c_work` substitutes. A test checks that the catalog's sm_120 record equals the Lean instance's numbers. |
| `verity_pouw/schemes/pearl_c_debit.py` | `verity/…/pouw/schemes/pearl_c_debit.py`, without its H100 default and module constants | P1: the debit the work law replays | high | answered (compute-accounting, 4 Oct): agreed. The H100 default goes, and with it `G = H100.g`, `ATOM`, `CAP = H100.cap`, `ATOM_UNITS` and `ELEMENT_UNITS` (lines 43-47). |
| `verity_pouw/schemes/pearl_c_work.py` | `verity/…/pouw/schemes/pearl_c_work.py`, taking its device as a parameter; `DRAW_WREF` → a catalog entry keyed by (device, prices, cap) | P1: Pearl-C's work law; vLLM's Pearl-C option uses it; P3 | high | answered (compute-accounting, 4 Oct): agreed, plus `DRAW_WREF`, which is built at import from `SM120` (lines 217-220) and names a pinned statement; its value is checked against the spec's `Prices.sm120Loop` and cast. It also cites `ServedMixedRev1Gamma`, `HonestTileCapRate` and the 20 `pearlCSampled…Cap1000_*` pins, which bears on the lock's size (see "Conflicts for the captain"). |
| `verity_pouw/schemes/pearl_c_u.py` | `experimental/pouw/pearl_c_h100/pearl_c_u.py` | Layout: the sm_90 entry's CPU twin; "CPU-pinned" to H100 | high | — |
| `verity_pouw/schemes/pearl_c4.py`, `pearl_c4_c_L.py` | `experimental/pouw/nvfp4/` | Layout: `pearl-c-nvfp4-v0` experimental | high | — |
| `verity_pouw/schemes/pearl_c4_replay.py` | `experimental/pouw/nvfp4/`, with Pearl-C4 | its own docstring: a development shortcut, never the protocol's verdict | high | answered (compute-accounting, 4 Oct): not deleted; it is live, since `benchmarks/pouw/pearl_c4/pearl_c4_arm.py:170` imports it (`write_dump`). |
| `verity_pouw/circuit/__init__.py` (`verify`) | `verity/…/pouw/circuit/__init__.py` | P1 | high | — |
| `verity_pouw/circuit/anchors.py` | `verity/…/pouw/circuit/anchors.py` | P1: vLLM's NCP option uses it | high | — |
| `verity_pouw/circuit/partition.py` | `verity/…/pouw/circuit/partition.py` | P1 | high | — |
| `verity_pouw/circuit/plan.py` (closure draws) | `verity/…/pouw/circuit/plan.py`, without its `pc4` and `pc8` imports | P1; P9 | high | answered (compute-accounting, 4 Oct): yes. `tile_layout(shape, w_ref)` imports `pc4`/`pc8` lazily and uses only `mod.units`, `mod.call` and `mod.weight`, so it takes that triple as an argument. It cites eight C-Flock audit-law pins (`work_escape_le`, `record_sizing`, `record_sizing_one_fewer`, `audit_work_floor`, `audit_work_whole_stratum`, `audit_window_split_of_record`, `covers_window`, `harm_le_unsoundWork`). |
| `verity_pouw/circuit/reference.py` (`ncp-v2`'s native reference) | `verity/…/pouw/circuit/reference.py` | P5: the reference a fast path is gated against | high | — |
| `verity_pouw/circuit/hashes.py` (SHA-512, SHAKE256, TurboSHAKE128 as word-level composites) | conflict (see "Conflicts for the captain"): compute-accounting splits it, SHA-512 and SHAKE256 (through `KeccakF1600`) → `verity/primitives/circuits/hashes.py` and TurboSHAKE128 with `KeccakP1600R12` on Pearl-C's tile-check path; circuits sends it whole wherever `words.py` goes | S5: one SHA-512 | low | compute-accounting (4 Oct): `ncp2` uses `sha512`, `shake256`, `sha_words` and `keccak_lanes` for the call key K and the noise rows (`ncp2.py:57`); TurboSHAKE128 serves only `leaves` and the parked `pouw/ncp-v2-lowbyte-leaf`, and since the 23:09Z revision it is not experimental. circuits (4 Oct): `Emit` builds `CompositeDefinition`s over PoUW's own word primitives (`W.PouwCh32`, `PouwMaj32`, `PouwXor32`, `PouwAdd64*`, `PouwRotl64*`), not gates, so in `verity/` it would import catalog-bound `words.py` (P6); "one SHA-512" is a vectors bridge to `ml/boolean/sha512`. |
| `verity_pouw/circuit/ncp2.py` (unit templates) | `verity/…/pouw/circuit/ncp2.py`, for now | the captain's call 5 (4 Oct): a builder the verifier runs at verification time is trusted code, whatever directory it sits in | medium | answered (compute-accounting, 4 Oct, against the draft and the catalog entry format's recommendation): it stays in `verity/`. `circuit.Traced` builds the Program for any (m, k, n), and `check_descriptor` refuses a descriptor whose digest differs (X-SPC-73), so catalog-by-digest would need a pinned digest per served shape, and m varies per call. Importers: vLLM's `check/replay/pouw_circuit.py`, `program/registry/pouw_rows.py` and `protocol_options/{pouw_circuit,pouw_device,pouw_native}.py`; the circuit package's `__init__`, `anchors`, `partition`, `plan` and `reference`; `circuit_check.targets`. Still open: whether parametric builders the verifier runs are trusted code (Daniel); top asked compute-accounting whether the verifier could pin each fixed-shape unit's digest per k and n, with m only setting the unit count. Its imports of the `ml.fp32` and `ml.prims` Definitions are core map split 10. |
| `verity_pouw/circuit/words.py`, `boolean.py` | conflict (see "Conflicts for the captain"): circuits sends both to `catalog/definitions/pouw/`; compute-accounting splits `words.py` (lines 44-209 with `ncp2`; the Pearl-C4 section, lines 210-245, with `pc4` to experimental; the Pearl-C section, lines 246-298, with `pc8`) and sends `boolean.py` with `pc8` | P3, P6 | low | circuits (4 Oct): `boolean.py` imports `ml.boolean.fp`, `forms` and `trace`, all `verity/` after the corrections, so P6 holds in the catalog. compute-accounting (4 Oct): `boolean.py` is "PoUW's own word primitives … Pearl-C4's (`pc4`) and Pearl-C's (`pc8`) row units call", imported by `test_circuit_boolean.py` and `circuit_check.targets`. |
| `verity_pouw/circuit/leaves.py` | with `pc8` on Pearl-C's tile-check path; the draft's `catalog/definitions/pouw/leaves.py` until the builder question for `pc8` is settled | P3; it imports `schemes.pearl_c` | medium | answered (compute-accounting, 4 Oct, revised 23:09Z): only `pc4` and `pc8` use it and no pin reads `TileCheck*`, but it is part of Pearl-C's only route to a verdict under the 4:06 PM ruling, so it is not experimental. |
| `verity_pouw/circuit/pc8.py` (the tile checks for h100-v1 and sm120-v1) | Pearl-C's tile-check path, not experimental: the draft's `catalog/definitions/pouw/pc8.py` (default 4), unless the call-5 decision makes builders the verifier runs `verity/` code; the device records it reads (`DEVICES`, lines 88, 159, 214, 290, 345-348) become parameters | P3; Daniel's 4:06 PM ruling | medium | answered (compute-accounting, 4 Oct, revised 23:09Z). Before the revision compute-accounting sent both checks together to experimental (`circuit.SCHEMES` refuses it, no vLLM option imports it, `pouw/circuit-pc8` is parked, and no pin reads `TileCheck8`); the revision makes it Pearl-C's only route to a verdict, to be promoted with a new or restated guarantee (the circuit's relation equals `TileGood`, plus sampled proofs' soundness as a named assumption) that needs Daniel's statement review. The draft split the H100 check off to `experimental/pouw/pearl_c_h100/`; compute-accounting did not split the module. |
| `verity_pouw/circuit/pc4.py` | `experimental/pouw/nvfp4/pc4.py` | Layout | high | compute-accounting agreed (4 Oct). |
| `verity_pouw/circuit/rowk.py` | with `pc8` on Pearl-C's tile-check path, without `pc4` and with its device as a parameter (`DEVICES` at line 323) | P3; Daniel's 4:06 PM ruling | medium | answered (compute-accounting, 4 Oct, revised 23:09Z): before the revision, experimental (`pouw/circuit-row-k` is parked and opt-in); after it, on Pearl-C's route to a verdict. |
| `PROTOCOL.md` | retired: per-scheme sections to the Lean spec and `catalog/` | Conv: PROTOCOL.md | high | — |
| `tests/` (suites, `circuit_fixtures.py`) | `verity/…/pouw/tests/`; the H100 and NVFP4 suites go with their code | Conv: tests | high | — |
| `tests/*_vectors.py`, `quicknet.py`, `pearl_vectors.rs`, `ncp_lean.py` | Split: `identifier_vectors.py`, `pouw_vectors.py`, `pouw_regions_vectors.py`, `ncp_lean.py`, `pearl_c_vectors.py` (v1; v0 cases go with v0) and `quicknet.py` stay with `verity/`'s tests; `pearl_vectors.py`/`.rs` (`pearl-fp8-v4`), `pearl_c_u_vectors.py` and `pearl_c4_vectors.py` go to experimental with their schemes; `pouw_rows_vectors.py` goes with `leaves` | Conv: tests: tests of the trusted code's wire formats, as core keeps `format_vectors.json` | medium | answered (compute-accounting, 4 Oct): not `tools/catalog/` builders. C-Flock's verifier compares `identifier_vectors.py`'s output byte for byte, `pouw_regions_vectors.py` is C-Flock's public-input regions, `ncp_lean.py` is a Python↔Lean difftest over `Pouw.Protocol.NCP.RouteU`, and `quicknet.py` is not a generator (it loads recorded drand rounds). |
| `tests/vectors/*.json` (`ncp`, `pearl_c`, `pearl_kw`, `pearl_c4`, `pearl_c_u`, `identifier_v1`, `quicknet`, `pouw_rows`, `pouw_regions`, `ncp_lean`, the skip vectors) | Split as the generators: `identifier_v1`, `ncp`, `ncp_lean`, `pouw_regions`, `pearl_c` and `quicknet` stay with `verity/`'s tests; `pearl_kw`, `pearl_c_u` and `pearl_c4` go to experimental; `pouw_rows` goes with `leaves`; the skip vectors go with whichever module reads them | Conv: tests | medium | answered (compute-accounting, 4 Oct). |

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

From the 4 Oct answers:
- **Module roots (lean, verity#1144):** the modules sent to `security_proofs/pouw/` take the `PouwProofs.*` root and keep
  their `Pouw.*` namespaces; spec modules keep `Pouw.*`, so the keys of `reads` don't change (compute-accounting §A7).
- **Slice 6 changes the certified γ's read records** (compute-accounting §D1): #1132 changes definitions it reads in
  `Defs`, `Device`, `DeviceRev1`, `FormingPDefs`, `Game`, `Instance` and `SaltDead`, so when it lands those records change
  and need a statement reviewer (Daniel's DM). The five pins' own signature records don't change.
- **The γ over a device (compute-accounting §A3, ruled 22:58Z on lean's answer):** γ is stated once, as a lemma in
  `security_proofs/pouw/`, for every device that satisfies the named device assumption, and the guarantee in the lock is
  its instance at `Sm120`, keeping the concrete prices, cap, cast, shape and literal γ. `--update --moved` must print it
  as the same statement; if it doesn't, the restatement waits for Daniel's review. `Sm120`, `DevicePricesLoop` and
  `devSm120v1` become catalog Lean whose entry `value` is the definition hash the lock's `reads` records, and lean's reads
  check (`cursor/lean-reads-owner-741b`) admits catalog reads. compute-accounting's §D1 ("all 33 stay spec") predates
  this ruling.
- **verity#1154** renames the certified γ's pin to `Pouw.SecurityProofs.PearlC.GammaSm120v1LoopCast8p72Rev1Cap1000_8192`.
- **The tile-check bridge (Daniel's 4:06 PM ruling, compute-accounting's revision):** the tile-check Lean (`TileCheck8`,
  `RowCircuit` and the rest) is the bridge a new guarantee needs: the circuit's relation equals `TileGood`, with sampled
  proofs' soundness as a named assumption. That guarantee is new or restated and needs Daniel's statement review.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| The 33 spec modules the five kept guarantees read. `Assumptions`: `Game`, `NCP.RouteUAssumptions`, `PearlC.TTOut`, `PearlC.TTOutRev1`. `Guarantees`: `Game`, `NCP`. `Protocol.Basic`: `Mat`, `Prob`, `QTree`. `Protocol`: `D1`, `Game.Defs`, `Game.Params`, `NCP.Defs`, `NCP.Protocol`, `NCP.RouteU`. `Protocol.Fp8Atom`: `Atom`, `E4M3`, `Fp32`. `Protocol.PearlC`: `Accum`, `Defs`, `Device`, `DeviceKernelWref`, `DevicePricesLoop`, `DeviceRev1`, `FormingPDefs`, `Game`, `Instance`, `PeelExact`, `PeelExactP`, `SaltDead`, `Skip`, `SkipP`, `Sm120` | spec, except `Sm120`, `DevicePricesLoop` and `devSm120v1` (split out of `Device.lean`), which become catalog Lean keyed by definition hash | P2: what the guarantees read; compute-accounting §A3 | high; medium for the catalog instances | answered (compute-accounting and lean, 4 Oct). `DeviceRev1` (121 lines) and `DeviceKernelWref` (55 lines) are generic over `d : PearlCDevice`, so they are protocol definitions (high). `Sm120` (read by 240 pins) and `DevicePricesLoop` (`Prices.sm120Loop := ⟨1047/125, 2, ⟨40, 2⟩⟩`, read by 161) are the instance the guarantee is about; under the 22:58Z ruling they become catalog Lean that the lock's `reads` names by definition hash. `Device.lean` (205 lines) mixes the generic `PearlCDevice` and `Prices` with instances (`Prices.h100`, `devH100`, `devSm120v1`, `devSm120v2`, `devAt`) and imports `Tile`: the generic part stays spec, `devSm120v1` goes with `Sm120`, and the other instances go with their pins. |
| `Pouw/SecurityProofs/Dimension/Lifting.lean` | spec package at the split, name kept; then `security_proofs/pouw/` under the proofs root, declarations' names kept | the plan (S1, S3.1); in `layers`; imports Mathlib only; no spec module imports it | high | answered (lean, 4 Oct): yes, once no guarantee reads it, on the validator's report of unread spec definitions (`cursor/lean-reads-owner-741b`). compute-accounting agrees: only `Pouw/SecurityProofs.lean:21` imports it, and it sits in the spec only because it is in `layers`. |
| Pearl-C tile-check modules no pin reads today: `Protocol.PearlC.{Tile, RowCircuit, TileCircuit, WholeCircuit, TileCheck, TileCheck8, RowSem, RowPrims}` | `Tile` stays spec through the import closure; the other seven go to `security_proofs/pouw/` under spec names until a guarantee reads them | P2: a spec definition stays only if a guarantee reads it (lean) | medium | answered (compute-accounting, 4 Oct): `EndToEnd` reads none of them, on main or on slice 6 (#1132's body: "No pin reads `TileCheck.Accepts`"). `Tile` is read by 189 pins, none of the five kept, so the draft's "no pin reads today" is wrong for it. Under the 4:06 PM ruling the seven are the bridge to a new tile-check guarantee; when it is pinned, with Daniel's review, the modules it reads return to the spec. |
| Theorems stated inside spec modules: `Protocol.PearlC.{Accum (7), RowCircuit (16), Row4Circuit (12), WholeCircuit (17), WholeCircuit4 (17), TileCircuit (2), Tile4Circuit (2), PeelExactP (4), Game (1), Instance (1)}` and `Protocol.Fp8Atom.H1T (1)` | Split: the theorems → `security_proofs/pouw/` in sibling modules; the definitions stay | P2: lemma statements leave `Protocol`. I count 80 theorems in 11 modules; the plan says about 41 | medium | answered (lean, 4 Oct): the module's record doesn't change. A `reads` record hashes only the definitions some guarantee reads (name, kind, content hash; `audit.py` `read_groups`), and an unread theorem isn't among them. A record changes only when a read definition changes, or when a dropped guarantee was the only reader of something. |
| Dimension and route-U pipe family: 25 `Assumptions.Dimension.*`, `Protocol.Dimension.{Causal, Defs, Lift}`, `Guarantees.Dimension` | `security_proofs/pouw/` under spec names, at S3.1 | P9: H100 lane experimental; the family leaves the lock | medium | answered (compute-accounting, 4 Oct): move it at S3.1. No kept pin reads it: `Protocol.Dimension.Defs` is read by 111 pins and `Guarantees.Dimension` by one (`A2WordsIff`), none in the kept reads' closure, and outside Lean only `PROTOCOL.md` names it. |
| H100 `-h1` family: `Protocol.Fp8Atom.{H1T, H1TCrossLate, H1TLemmas, H1TPinned}`, `Assumptions.Fp8Atom.{H1TAssumptions, H1TGamma, H1TRunningAssumptions, H1TTile, H1TTileAssumptions}` | `security_proofs/pouw/` under spec names | Layout: H100 `-h1` experimental; the 45 H100 γ pins leave the lock and keep building | medium | — |
| NVFP4 family: `Protocol.PearlC.{Fp4, Fp4Chain, Fp4Skip, DeviceFp4, DeviceFp4ChainOnly, DeviceFp4Hot, DeviceFp4Issue, Row4Circuit, Tile4Circuit, WholeCircuit4, TileCheck4}`, `Assumptions.PearlC.{TTOutFp4, TTOutFp4ChainOnly}` | `security_proofs/pouw/` under spec names | Layout: `pearl-c-nvfp4-v0` experimental | high | — |
| Pearl-C modules no kept guarantee reads: `Protocol.PearlC.{Completeness, Deadline, DeviceChainOnly, DevicePrices, Hidden, HiddenTileGame}`, `Assumptions.PearlC.{Deadline, DeviceChainCap, DeviceChainCapKernel, HiddenTile, HonestCap, RowSeedAssumptions, TTOutChainOnly, TTOutRowSeed, TTOutTileUOnly, TTOutUOnly}` | `security_proofs/pouw/` after the reduction, except the cap pins if the lock keeps them | P2, P9. `DevicePrices` holds 116 pins. The plan also drops the 104 γ pins that `harness/price_twins.json` names | medium | answered (compute-accounting, 4 Oct): not of `EndToEnd` or the certified γ. `Hidden`, `HiddenTile` and `HiddenTileGame` leave (`pouw/circuit-hidden-tile` is parked and nothing outside Lean cites them). `DeviceChainCap` (27 pins) and `DeviceChainCapKernel` (6) belong to the parked sm120 v2 chain cap and leave. `HonestCap` and `Completeness` are read by `completeSampledDevRev1K` and the two `pearlCCompleteSm120v1…` pins, and `pearl_c_work.py:214-215` cites `HonestTileCapRate`, so under the 2:03 ruling they are candidates to keep. Correction: `price_twins.json` is not an internal pricing table; `ledger.py` writes its γ into `kernel-attempt/v1` records that `panel.py` renders (see "Conflicts for the captain"). |
| NCP, Barrier, TileBound, M1, Witness and Deadline families: `Protocol.NCP.{ExtraIdentity, Pinned, Relation, Witness, Word}`, `Assumptions.NCP.{Assumptions, Chain, GamePinned, RouteUGame, RouteUWord}`, `Protocol.Barrier.*`, `Protocol.TileBound.*`, `Protocol.M1`, `Protocol.Witness.*`, `Protocol.Game.Deadline`, `Assumptions.{Deadline, Pinned}`, `Guarantees.{Barrier, Deadline}` | `security_proofs/pouw/` after the reduction, except the 15 closure modules in the next row | P2: lemma families; about 25 NCP and Barrier lemmas that `PROTOCOL.md` and `ncp.py` name keep building | medium | answered (compute-accounting, 4 Oct): `GammaFromTTNCP_U_v1` reads neither; it reads `Assumptions.NCP.RouteUAssumptions`, with `Guarantees.NCP`, `Basic.*`, `D1`, `Game.{Defs,Params}` and `NCP.{Defs,Protocol,RouteU}`. |
| New row (compute-accounting §D2): the import closure of the 33 read modules, 15 modules: `Assumptions.NCP.{Assumptions, Chain, GamePinned, RouteUGame, RouteUWord}`, `Assumptions.Pinned`, `Protocol.Barrier.Defs`, `Protocol.M1`, `Protocol.NCP.{Pinned, Relation, Witness, Word}`, `Protocol.PearlC.Tile`, `Protocol.Witness.{Copy, Model}` | spec until `Guarantees.Game`'s and `Guarantees.NCP`'s imports are trimmed to what the guarantees read; then `security_proofs/pouw/` | a spec module can't import the math package | high | Ordering constraint: the import trim lands first. `Guarantees.Game` imports `Assumptions.Pinned` (which imports `M1` and `Witness.*`); `Guarantees.NCP` imports `RouteUGame`, `RouteUWord`, `NCP.Pinned` and `NCP.Relation`, which pull in the rest and `Barrier.Defs`; `TTOut` and `Device` import `Tile` (from `reads` and the imports at `9400e83d5`). Whether an import-only change moves a record is lean's to confirm; by lean's rule above, only a change to a read definition or a dropped sole reader does. |
| Generated vectors: `Protocol.Fp8Atom.{Vectors, Vectors/* (5 files), H1TVectors, H1TVec}`, `H1TCoverage.json`, `Protocol.PearlC.{EncVectors, Fp4Vectors, PeelExactVectors, PeelFp4Vectors, RowPrimVectors, Sm120Vectors}` | `catalog/vectors/pouw/` (Lean) | P2: "its generated vectors go to the catalog" | medium | lean: `Pouw/Protocol.lean` imports every vector module, and `Fp8Atom.Pinned` and `H1TPinned` import vectors. The umbrella must stop importing them first. |
| `Protocol.Fp8Atom.Pinned` | `security_proofs/pouw/` | lemma statements over the vectors | medium | — |
| `Pouw/SecurityProofs/**` except `Dimension/Lifting.lean` (149 files) | `security_proofs/pouw/` | P2 | high | — |
| `Pouw.lean` (umbrella) | `security_proofs/pouw/` | S3.1 | high | — |
| `PouwBulk.lean` (exempt `runs`: fp8 conformance against `scripts/fp8atom_vectors.py`) | `security_proofs/pouw/` as a `lake exe` target that requires the spec, with its `runs` entry moving into that package's lock | lean's spec runners | high | answered (lean, 4 Oct): the math package. A runner needs no trust, since selected vectors are kernel-checked against the spec's definitions (`decide +kernel`). |
| `scripts/fp8atom_vectors.py`, `h1t_vectors.py`, `row_prims_vectors.py`, `fp8atom_cover.json` | each with what it generates: `fp8atom_*` wherever the `Fp8Atom` vector modules go; `h1t_vectors.py` to experimental with the H100 `-h1` family; `row_prims_vectors.py` with `RowPrims` and `pc8` (it imports `circuit.words`' Pearl-C section) | P3 | medium | answered (compute-accounting, 4 Oct). The kept pins read `Atom`, `E4M3` and `Fp32`, not the vector modules. |
| `lean-audit.json` | split: the spec keeps the five guarantees after the reduction, plus whatever the lock-size decision adds; `roots` (now the spec prefixes), `proved_in`, `layers` and `dependencies` divided | S3.1; verity#1144 | high | compute-accounting (4 Oct): five plus §A1, and pouw-lock keeps this package's `reads` by hand until the validator derives it. The lock's size is a decision for Daniel and pouw-lock (see "Conflicts for the captain"). |
| `lakefile.toml`, `lake-manifest.json`, `lean-toolchain`, `.gitignore` | the spec package; the math package requires the spec, Mathlib and core's math package (it uses `ProbBatchInduced` as a lemma) | S3.1 | high | — |

## The network warden (`protocols/network_warden/`, network-accounting)

The warden moves first in S5. Correction (network-accounting, 4 Oct): its lock keeps 4 of its 51 pins, not about 10:
`EncardDecodableLeConstantRate` and `EncardIngressObsDecodableLe`, each with its per-window form (draft #1142, under the
2:03 PM ruling; only `calibration.calibrate` reads a result, and the 4 records are byte-identical). The 23 lemma pins
and the 16 non-vacuity witnesses leave the lock, and the witnesses become checked tests in `security_proofs/warden/`.
network-accounting's dry-run move script follows these answers.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `verity_network_warden/grid.py` | `verity/…/warden/grid.py` | P1 | high | — |
| `verity_network_warden/schedule.py` | `verity/…/warden/schedule.py` | P1 | high | — |
| `verity_network_warden/audit.py` | `verity/…/warden/audit.py` | P1 | high | — |
| `verity_network_warden/commitment.py` | `verity/…/warden/commitment.py` | P1 | high | answered (network-accounting, 4 Oct): adopt the shared Merkle tree later, as a bridged change of meaning. The move stays pure and the record digests (`verity-network-warden/record/v1`) don't change, so the replay set's committed verdicts still reproduce bit for bit. The audit compares whole-window digests and never opens a frame, so a tree adds nothing until something needs per-frame openings. |
| `verity_network_warden/capacity.py` | Split: the counts and bounds → `verity/…/warden/capacity.py`, with `k_share(bits, k_bits)` taking K as a parameter; the value of `K_BITS = 9.12e7` → a catalog parameter entry | P3 | high | answered (network-accounting, 4 Oct): K is NCI's number, not the warden's: α·Γ, the inference-only policy's budget. Only `capacity.k_share` reads it, to report a bound as a share of K, and no pin or audit reads it. NCI's spec states the α·Γ it is, and the warden's lock doesn't change. |
| `verity_network_warden/calibration.py` (`network-warden-calibrate`) | Split: `choose_syncs` → `verity/…/warden/`, beside `schedule.py`; the sizing (`calibrate`, `size_ingress_ms`, `network-warden-calibrate`) → `tools/warden_calibrate/` | P1 for the honest prover's sync declaration; P3 for the sizing | high | Correction (network-accounting, 4 Oct): `choose_syncs` is the honest prover's sync declaration, not sizing. `replay.py`, `active_replay.py` and the live vLLM mode (#1125) call it, and a deployed prover would too. |
| `verity_network_warden/active.py` (the asyncio proxy) | `verity/…/warden/active.py` | Layout: the warden "with its active enforcer" | high | — |
| `verity_network_warden/__init__.py` | `verity/…/warden/__init__.py` | P1 | high | — |
| `PROTOCOL.md` | Split: retired except the wire format section → `verity/…/warden/PROTOCOL.md` | Conv: PROTOCOL.md | high | — |
| `README.md` | `verity/…/warden/README.md` | Conv: PROTOCOL.md | high | — |
| `tests/` (seven suites, with the Lean difftest) | `verity/…/warden/tests/`; the sizing tests go with `tools/warden_calibrate/`, and the tests of `choose_syncs` stay with it | Conv: tests | high | — |

## The network warden's Lean (`protocols/network_warden/lean/`, network-accounting; layout with lean)

`lean-audit.json` sets `layers` to `NetTiming.Protocol`, `Assumptions` and `Guarantees`, with 51 pins and 6 `reads`.
`CheckAxioms` and `NetTimingDifftest` are exempt; `NetTimingDifftest` `runs` against `scripts/difftest_vectors.py`.
It requires Mathlib only.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `NetTiming/Protocol.lean`, `NetTiming/Protocol/{Grid,Ingress,Run,Schedule}.lean` | spec | `layers` | high | — |
| `NetTiming/Assumptions.lean`, `NetTiming/Guarantees.lean` | spec | `layers` | high | — |
| `NetTiming/SecurityProofs.lean`, `NetTiming/SecurityProofs/{Advice,Counting,Ingress,Occupancy,PerWindow,Sanity,Schedule}.lean` | `security_proofs/warden/`, under a module root of its own with declaration names kept | P2; verity#1144; the 16 witnesses become its checked tests | high | — |
| `NetTiming/Difftest.lean` (imports only `Protocol`), `NetTimingDifftest.lean` | `security_proofs/warden/`, as a `lake exe` target that requires the spec; its `runs` entry moves from the spec's lock into that package's lock | lean's spec runners | high | answered (lean, 4 Oct): the math package. A runner needs no trust, since selected vectors are kernel-checked against the spec (`decide +kernel`). The audit already fails closed on a `runs` path that doesn't resolve (a missing runner module, a `generate` script that exits nonzero, a missing data file, a changed data hash), so the only quiet way out is deleting the entry. lean asked ci to let `move-check` move a `runs` entry between the two locks with only its `generate` path rewritten, and to refuse one that disappears from both. |
| `NetTiming.lean` (umbrella) | `security_proofs/warden/` | S3.1 | high | — |
| `CheckAxioms.lean` | retired | P2: the validator replaces it | high | — |
| `scripts/difftest_vectors.py` | beside the difftest, moving with `NetTimingDifftest` to `security_proofs/warden/`; the `runs` generate path changes in the same PR | S3.1 | high | answered (network-accounting, 4 Oct): not a `tools/` builder, because it has one consumer. |
| `lean-audit.json`, `lakefile.toml`, `lake-manifest.json`, `lean-toolchain`, `README.md` | the spec package; `lean-audit.json` split | S3.1 | high | — |

## NCI's Lean (`protocols/nci/lean/`, lean)

NCI has no Python, so its S5 train only moves the spec beside where its code will go. network-accounting (4 Oct): K,
the warden's `K_BITS`, is NCI's number (α·Γ, the inference-only policy's budget), so NCI's spec states it, and its value
is a catalog parameter entry. The package requires Mathlib and
core's `verity`. It has 8 pins: `Inference`, `ReadBound`, `Training`, `UpdatedMatMul`, `full_positions`, `iu_reads`,
`loomis_whitney` and `other_positions`. Lean proposes keeping `Inference` and `Training`.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `Nci/Protocol.lean`, `Nci/Assumptions.lean`, `Nci/Guarantees.lean` | spec; at S5 `verity/…/nci/lean/` | the four-name layout (`layers`) | high | — |
| `Nci/SecurityProofs.lean`, `Nci/SecurityProofs/{Chain,Inequalities,LoomisWhitney,Throttling}.lean` | `security_proofs/nci/`, under a module root of its own with declaration names kept | P2; verity#1144; it imports `Verity.SecurityProofs`, so the math package requires core's math package | high | — |
| the `upstream` watch entry `loomis-whitney` | `security_proofs/nci/`'s lock | S3.1; the lemma it watches is in the math | high | answered (lean, 4 Oct): it watches a hand-proved lemma (`Nci.SecurityProofs.loomis_whitney`), which moves with the math. A watch moves to a spec's lock only when it covers a named assumption. |
| `Nci.lean` (umbrella) | `security_proofs/nci/` | S3.1 | high | — |
| `lean-audit.json`, `lakefile.toml`, `lake-manifest.json`, `lean-toolchain` | the spec package; `lean-audit.json` split | S3.1 | high | — |

## `benchmarks/` (stays, minus kernels, calibration and frozen workloads)

`benchmarks/` stays, but P5 and P7 take the kernels a result rests on out of it. vLLM's `protocol_options/pouw.py` and
`pouw_pearl_c_device.py` load the sm_120 kernel directory from the run tree's `benchmarks/pouw/pearl_c_sm120`. Under P7
they load it from `verity/kernels/pearl-c-sm120/` instead. `tools/research/src/research/store/tools_registry.py` names
`benchmarks.pouw.tool`, so that path stays. Daniel's 4:06 PM ruling, as the plan records it, adds that PoUW's device-run
replay goes to `benchmarks/pouw/`: a replay is a diagnostic and never in `verity/`.

| Current path | Destination | Principle | Confidence | Question for the owner |
|---|---|---|---|---|
| `judge.py`, `latency_compare.py` | stays | run judges over `verity_numerical` | high | — |
| `commitments/` | stays | cost benchmarks | high | — |
| `dot_product/`, `ir_call/` (frozen D-SP1 workloads) | `archive/sp1/` with D-SP1 | S4: frozen backends to `archive/`, each with its record | medium | proofs (outside this map's owners): do they still build against the frozen backend? |
| `network_traces/record.py` (vLLM trace capture) | `tools/warden_capture/` | P3: capture is a tool; the traces are preserved inputs, never re-recorded | high | answered (network-accounting, 4 Oct): agreed. |
| `network_traces/replay.py`, `active_replay.py`, `run.sh`, `tests/` | stays | the warden's replay set (convert, calibrate, audit on preserved traces) | high | answered (network-accounting, 4 Oct): no guarantee rests on the conversion. The bit bounds are the Lean pins and the verdicts are `audit.py`'s; `replay.py` feeds the preserved traces through that code, and its result (5,289 of 5,290 honest windows accepted) is a benchmark result. It runs on the injected clock, so it is deterministic and can sit in the replay set's re-verify tier. |
| `one_stage/` | stays | runs the one-stage audit end to end with C-Flock's circuit prover; it imports the demo population programs | high | — |
| `private_circuit/` | stays | C-Flock ZK benchmark | high | — |
| `pous/{bench.py, pod.sh, weight_sets.json, side_by_side.py, explorer.py, README.md}` | stays | `bench.py` imports `dense` and `p2`, which is fine from `benchmarks/` | high | — |
| `pous/band_gpu/` (`codec.py`, `dense.py`, `harness.py`, `live.py`, `native.py`, `pous_native.cu`) | Split: the kernel → `verity/kernels/pous-band-<device>/`, consolidated with vLLM's `engine.pous` kernels; the harness stays; `codec.py`'s P3 import goes with P3 to experimental | P5 | medium | answered (memory-accounting, 4 Oct): there is one copy. It moved from the vLLM tree's `engine/pous`, and main has no `verity_vllm/engine/pous`; main's vLLM option uses the CPU reference codec, and the `vllm-gpu` bench arm reads an external pinned tree (`--impl-tree`). So the consolidation is moot. The band and dense scheme vectors are the agreement between the reference codec and these kernels (`bench.py` gates them), and the harness's `dense-chain/v1` arm moves with the dense scheme to experimental. |
| `pous/erase_calib/` (secure-erasure calibration, Triton fill kernels) | Split: the calibration → `tools/pous_erase_calib/` (it builds the erase-timing entry, P3); the fill kernels → `verity/kernels/` if the erasure audit runs them | P3, P5 | medium | memory-accounting: waits on #1096 and #1086 |
| `pous/hbm_audit/` (TwoTierBandwidth) | `experimental/pous/hbm_audit/` while it runs, else `archive/pous-hbm-audit/` | P8: TwoTierBandwidth killed (no host RAM; registered `pous/two-tier-bandwidth` killed, 4 Oct); the HBM sweep art:59c46dd8 isn't re-run | medium | memory-accounting: does it still run, and does it still teach? (not answered on 4 Oct) |
| `pous/p2_gpu/` (CGBN `p2dec.cu`, P2 v2) | `experimental/pous/p2/gpu/` | P2 v2 live, nonconforming | high | — |
| `pous/p2_v1/` (P2 v1 frozen spec, reference, kernel) | `experimental/pous/p2/v1/` | the plan: the frozen P2 spec goes to the store or beside its code in `experimental/pous/` | high | answered (memory-accounting, 4 Oct): the frozen v1 is already in the store, `art:a7a29e84eef9d2584482b7f3e9722af6b579e2984a9633352564c562ce9e2021`, with its timing evidence `art:23a323f313d2193873c59ee8ab59a0f1197167a0b4c6d008346d771c3e72de57` and the relays `note:20261004T2102Z-report-relay-p2-redteam-timing` and `…-deployment-decisions`. The spec goes beside `experimental/pous/p2/` when the code moves. |
| `pouw/pearl_c_sm120/` | Split: the kernel (`pearl_c_sm120.cu`, `mainloop_sm120.cuh`, `h2_rows_stats.cuh`, `build.sh`, `sass_gate.py`) → `verity/kernels/pearl-c-sm120/`; `run.py`, `pearlc_arm.py`, `fixture.py`, `verify.py` stay | P5, P7; `pearl-c-sm120-v1` in `verity/` | high | — |
| `pouw/pearl_c/` (H100) | Split: `hash.cuh`, `hash_h2.cuh`, `hash_sm120.cuh` (included by the sm_120 kernel) → `verity/kernels/pearl-c-sm120/`; the H100 kernel `pearl_c.cu`, `acc.h`, the h1 code, `ftz_gate.py`, `twin.py`, `simt_twin.py` and the rest → `experimental/pouw/pearl_c_h100/` | Layout: the H100 lane is experimental until a guarantee rests on it, then the sm_90 entry | high | — |
| `pouw/pouw_hash/` | Split: `pouw_hash.cuh` (included by the sm_120 kernel) → `verity/kernels/pearl-c-sm120/`; the bench and check stay | P5 | medium | — |
| `pouw/pearl_c4/` | `experimental/pouw/nvfp4/` | Layout | high | — |
| `pouw/nvfp4_sm120/` (`nvf4_plain.cu`, `fp8_bench`, `mainloop_nvf4.cuh`) | stays, whole, in `benchmarks/pouw/` | it is not Pearl-C4, which lives in `pearl_c4/` | high | answered (compute-accounting, 4 Oct): `harness/native/build.sh:29` builds `nvf4_plain.cu` with `mainloop_nvf4.cuh` into the harness's baseline registry (`cutlass_registry.cu`), `baselines.py:360` and `test_harness.py:844` rely on it, and `pouw/kernel-nvfp4-sm120-plain` is merged. Moving it would make the harness build from `experimental/`. |
| `pouw/harness/` | stays, except the FTZ/MUFU gate on timed binaries (`harness/sass_gate.py`, `sass_pins.json`, `ieee_pin.*`) → the `verity/kernels/` registry's build, with the harness calling it there; `price_twins.py`/`.json` stay in the harness | P5: the gate on every cache fill | medium | answered (compute-accounting, 4 Oct). There are two gates: the kernel build gate `pearl_c_sm120/sass_gate.py` goes with the kernel, and the FTZ/MUFU gate is what `bench.py` runs on every timed arm's binaries (lines 51, 917, 1278), whose version `ledger.py` records and which `tools/tc_probe_fp4` also uses. `price_twins` stays with its readers (`ledger.py`, `exhaustion/audit.py`); once `DevicePrices`' pins leave the lock, the ledger would publish staged γ unless it refuses them. Ordering: verity#1154 makes the pin's signature `X : G`, so `price_twins.py` must read γ from the `Guarantees` definition instead, settled with the lock's size. |
| `pouw/kernels/pouw_gemm.cu` (`ncp-v1` route-U, RTX 4090) | stays | not a registry entry | medium | answered (compute-accounting, 4 Oct). Evidence correction: `e2e_audit.py` is not its only user; `kernels/__init__.py`'s `load` is used by `check_route_u_sass.py`, `e2e_audit.py`, `gemm_bench.py`, `route_u_bench.py`, `ncp2_gpu_bench.py:391` and `tests/test_route_u_shift.py`, and `tools_registry` lists `benchmarks.pouw.tool`. No vLLM option loads it (there is no `route_u` in `integrations/vllm`), and `pouw/kernel-pouw-gemm-4090` is merged as a benchmark route. |
| `pouw/exhaustion/` (the salt-to-deadline window and its CPU audit) | stays | a timed run of `pearl-c-sm120-v1-h1` over the panel's kernel; its `check_tile` is a diagnostic under the 4:06 PM ruling | high | answered (compute-accounting, 4 Oct, revised 23:09Z): no cited result rests on it. Its γ is the kept pin, looked up through `price_twins.lookup`, each tile is checked by `audit.Verifier(...).check_tile`, nothing outside `benchmarks/pouw/` reads the certified fraction, and `pouw/pearl-c-sm120-window-60pct` was killed. |
| `pouw/pearl_c_vllm/` | stays | served runs | high | — |
| `pouw/{gamma.py, e2e_audit.py, gemm_bench.py, route_u_bench.py, vllm_bench.py, ncp2_gpu_bench.py, check_route_u_sass.py, run_result.py, tool.py, workloads.json, pearl_b200_setup.sh, README.md, tests/}` | stays | benchmarks | high | — |
| `pouw/pearl_calibration.py` (Pearl's B200 calibration) | stays in `benchmarks/pouw/` | a benchmark, not a calibration tool | medium | answered (compute-accounting, 4 Oct): it benchmarks Pearl's own miner against plain vLLM on a B200 (`r20260928-075340-f1bb`) in Pearl's environment, calibrates no parameter and builds no entry; `tool.py` registers it as `pouw_pearl_cal`. |

## Where `verity/` would import `catalog/`, `experimental/` or `benchmarks/`

P6 lets `verity/` import nothing else in the repository, and P9's boundary test fails closed. These are the edges the
destinations would create, and the split that must come first in each case.

### PoUS

1. `band.py` and `schemes/band.py` import `dense.DenseChain`. The dense scheme goes to experimental (memory-accounting,
   4 Oct), so the overwrite chain band builds on must first move into a `verity/` module of its own (e.g. `chain.py`).
2. `audit.py`, `setup.py` and `verifier.py` import `Encoding` from P3's `scheme.py`. `Encoding` must move into
   `codec.py` first.
3. `labels.py`, `dense.py`, `setup.py` and `schemes/p2.py` import `SALT_BITS` (and `labels.py` imports `Params`) from
   P3's `params.py`. The salt and tag widths must move to `layout.py`. `labels.py` must then take its widths as
   parameters.
4. `primitives.py` mixes four destinations. It must be split before anything moves. Its `pi2_call_ns` must take the
   Keccak-f step as a parameter rather than default to `KECCAK_F_NS`.
5. `oracle.py` is test-only by convention, but `dense`, `primitives`, `scheme` and `audit` import it. The types the
   deployed code uses (`Prog`, `run`, `pure`, `Cost`, `Query`; memory-accounting, 4 Oct) stay in `verity/`, and the
   rest goes to the tests.
6. `schemes/__init__.py` imports `p2` and `p3`. The registry must stop listing them, with experimental registering its
   schemes on its own side.
7. `audit.py`'s `DEADLINE_NS`, `RTT_ALLOWANCE_NS` and `CALL_NS`, and `schemes/p2.py`'s `ROOT_CALL_NS`, are device
   numbers. They must become values the verifier passes in from a catalog entry, with no default in `verity/` code
   (memory-accounting agreed, 4 Oct). `CERTIFIED_ROUNDS` goes with P3 to experimental.

### PoUW

1. `pearl_kw.py` holds Pearl's shared pieces, which `pearl_c`, `pearl_c_debit`, `pearl_c_work` and `circuit/pc8` import.
   They must be extracted into a `verity/` module before `pearl-fp8-v4` moves to experimental (the lists are in the
   `pearl_kw.py` row).
2. `pearl_c.py` holds the v0 forming (superseded) beside the v1 forming. v0 is split out (compute-accounting, 4 Oct),
   and the v1-only `PearlC` has no device default.
3. `pearl_c_device.py`'s records are device numbers bound for `catalog/devices/`. `pearl_c_work`, `pearl_c_debit`,
   `pearl_c_u`, `circuit/pc8` and `circuit/rowk` import them directly. `pearl_c_debit` already takes a device and only
   defaults to the H100. Each must take the device as a parameter with no default first: the scheme object carries its
   device, which the registry entry builds from catalog records (compute-accounting, 4 Oct).
   `Device` also reads `verity.ml.tc.models`' Hopper and Blackwell constants, which P3 sends to the catalog as hardware
   models. That is core's split (circuits with @architecture), but this module depends on it.
4. `schemes/__init__.py` (`SCHEMES`) and `identifier.py` list experimental schemes. Under the 4:06 PM ruling,
   `verity/`'s registry is `circuit.SCHEMES` (`ncp-v2`, `ncp-v2-shift24`); `schemes.SCHEMES`' entries leave it, with the
   experimental registry kept apart, before the H100 and NVFP4 code moves. Every entry point (`Verifier`, `identifier`,
   vLLM's `scheme_of` and `EXECUTED`) must refuse a name outside `verity/`'s registry, and vLLM's own registry in
   `pouw_pearl_c_device.py` must be derived from it (compute-accounting §A4).
5. `circuit/__init__.py` (`verify`), `partition.py`, `plan.py` and `reference.py` import `ncp2` and `words`. `ncp2` stays
   in `verity/` for now (the captain's call 5), so this edge holds only if `words.py`'s part that `ncp2` uses stays where
   `verity/` may import it. That is the `words.py` conflict (see "Conflicts for the captain"), and `ncp2`'s imports of the
   `ml.fp32` and `ml.prims` Definitions are core map split 10.
6. `circuit/plan.py` and `circuit/rowk.py` import `pc4`, the NVFP4 tile check bound for experimental. `plan` takes the
   (units, call, weight) triple as an argument instead (compute-accounting, 4 Oct), and `rowk` drops `pc4`.
7. In Lean, the certified γ reads `Pouw.Protocol.PearlC.Sm120`, `DeviceRev1` and the other device modules. Settled
   (compute-accounting's ruling of 22:58Z, on lean's answer): γ is a lemma over every device satisfying the named device
   assumption, the lock holds its instance at `Sm120` with the literal γ, and `Sm120`, `DevicePricesLoop` and
   `devSm120v1` become catalog Lean that the lock's `reads` names by definition hash, which lean's reads check admits.
   If `--update --moved` doesn't print the instance as the same statement, it waits for Daniel's review.
8. In Lean, `Pouw/Protocol.lean` imports every generated-vector module, and `Fp8Atom.Pinned` and `H1TPinned` import
   vectors. The umbrella must drop those imports, and the Pinned modules must move to `security_proofs/pouw/`, before the
   vectors go to `catalog/`.

### The warden and sampled proofs

1. `capacity.py`'s `K_BITS` must become a parameter before K becomes a catalog entry: `k_share(bits, k_bits)` takes K
   (network-accounting, 4 Oct). `calibration.py` splits: `choose_syncs` goes to `verity/` beside `schedule.py`, and the
   sizing to `tools/warden_calibrate/`.
2. `law.py` goes to experimental while vLLM's `LEGACY` is true. Correction (compute-accounting, 4 Oct): vLLM's
   `commit/challenge.py:30` imports it for the non-legacy draws, not the legacy ones. That edge is integration →
   experimental, which P6 allows, so nothing has to move first. No `one_stage/` module imports `law.py`; only `plan.py`
   does, and it goes to experimental with it.

### Integrations

vLLM's Pearl-C option loading its kernel from `benchmarks/pouw/pearl_c_sm120` is the one integration → benchmarks edge,
which P7 forbids. Moving the kernel into `verity/kernels/pearl-c-sm120/` removes it. That kernel includes
`../pearl_c/hash_h2.cuh` (which includes `hash_sm120.cuh` and then `hash.cuh`) and `../pouw_hash/pouw_hash.cuh`, so those
headers must move with it. Otherwise `verity/kernels/` would include from `experimental/` and `benchmarks/`.

## Open questions, by owner

Questions the owners answered on 4 Oct are kept here, marked answered, so their numbers stay stable.

### compute-accounting (PoUW, the sampled-proofs audit law)

1. The scheme registry. answered (compute-accounting, 4 Oct): two registries, the caller chooses explicitly, and
   nothing experimental fills. Under Daniel's 4:06 PM ruling `verity/`'s registry is `circuit.SCHEMES` alone. Still
   open for the vLLM PoUW option's owner: routing `pouw_pearl_c_device.SCHEMES` and `scheme_of` through it, moving the
   served `-h1` and `sm120-unpromoted` to the experimental registry or ceasing to serve them, and whether `-h1` is still
   served on purpose now that `pouw/pearl-c-hash-h1` is superseded.
2. The device record. answered (compute-accounting, 4 Oct, ruled 22:58Z on lean's answer): the scheme carries its
   device and the record splits; γ is a lemma over a device parameter, and its instance at `Sm120`, in catalog Lean
   keyed by definition hash, is the guarantee in the lock.
3. `ncp2`. answered (compute-accounting, 4 Oct; the captain's call 5): it stays in `verity/` for now. Still open:
   whether parametric builders the verifier runs are trusted code (Daniel), and top's question whether each fixed-shape
   unit's digest could be pinned per k and n.
4. Slice 6. answered (compute-accounting, 4 Oct): `EndToEnd` reads no tile-check module, and only `Tile` stays,
   through the closure. `Hidden*` aren't future reads; the cap pins are candidates to keep. Under the 4:06 PM ruling the
   tile-check Lean is the bridge to a new guarantee, which needs Daniel's statement review.
5. Sampled proofs. answered (compute-accounting, 4 Oct): under `verity/protocols/verification/`, beside C-Flock.
   `law.py` and `plan.py` go to experimental until decision 42, and neither is deleted. Still open for Daniel or the
   coordinator: decision 42's timing, since if the `LEGACY` flip is close both stay in `verity/`.
6. `pouw_gemm.cu` and the exhaustion audit. answered (compute-accounting, 4 Oct): `pouw_gemm.cu` is not a registry
   entry, and no cited result rests on `exhaustion/audit.py`, whose `check_tile` is a diagnostic.
7. New (compute-accounting, 4 Oct): lean, trim `Guarantees.Game`'s and `Guarantees.NCP`'s imports so the 15 closure
   modules can leave, and confirm that an import-only change moves no record.

### memory-accounting (PoUS)

1. Dense. answered (memory-accounting, 4 Oct): extract the overwrite chain into `verity/`, send the dense scheme and its
   harness arm to `experimental/pous/dense/`, and drop `ChainDenseMeets64` from the lock.
2. P2 and P3. answered (memory-accounting, 4 Oct): their pins leave the lock until promotion, with their statements
   kept as `def`s; P2 v3 does not promote when #1123 lands.
3. The grader. answered (memory-accounting, 4 Oct): keep `Sanity.lean` and `Accounting/Numbers.lean` in the spec
   package under their names and the root `Pous`.
4. `audit.py`'s counts. answered (memory-accounting, 4 Oct): `AUDIT_CAP`, `LATE_ROUNDS`, `WORK` and `CHALLENGES` are spec
   or certificate parameters in `verity/`; `CERTIFIED_ROUNDS` goes with P3; Δ, the RTT allowance, `CALL_NS` and
   `ROOT_CALL_NS` go to `catalog/devices/`. memory-accounting has P2's RTT allowance and root floor waiting on Daniel's
   window ruling, which the plan records at 2:21 PM PDT.
5. The band kernels. answered (memory-accounting, 4 Oct): `benchmarks/pous/band_gpu/` is the only copy, and the band
   and dense scheme vectors are its agreement with the reference codec.
6. Still open from the rows: whether `labels.py`'s layout is generic over a band label width or P3-only (the
   `params.py` row), and whether `hbm_audit/` still runs and teaches.

### network-accounting (the warden)

1. K. answered (network-accounting, 4 Oct): NCI's number (α·Γ); `k_share` takes it as a parameter, its value is a
   catalog parameter entry, and NCI's spec states it.
2. `replay.py`. answered (network-accounting, 4 Oct): no guarantee rests on it; it stays in `benchmarks/`.
3. `difftest_vectors.py`. answered (network-accounting and lean, 4 Oct): it stays beside the difftest and moves with
   `NetTimingDifftest` to `security_proofs/warden/`, its `runs` entry and generate path changing in the same PR; the audit
   fails closed on an unresolved `runs` path.

### lean (NCI and the Lean layout)

1. Lifting. answered (lean, 4 Oct): yes, to `security_proofs/pouw/` on the validator's unread-definitions report, under
   the proofs root with its declarations' names kept.
2. Moving a theorem out of a read spec module. answered (lean, 4 Oct): the module's record doesn't change, since a
   `reads` record hashes only the definitions some guarantee reads. A record changes only when a read definition changes
   or a dropped guarantee was the only reader of something, which lean checks on each lock reduction.
3. Spec runners. answered (lean, 4 Oct): the math package, as a `lake exe` target that requires the spec.
4. NCI's `loomis-whitney` watch. answered (lean, 4 Oct): `security_proofs/nci`'s lock.
5. Area names. answered (lean and network-accounting, 4 Oct): `core`, `flock`, `pous`, `pouw`, `warden`, `nci`.
6. Still open from the rows: which package the sampled-proofs exfiltration difftest and PoUS's `tests/lean/*Check.lean`
   build against after S3.1.

## Conflicts for the captain

1. **PoUW's `circuit/hashes.py`.** compute-accounting (§C11, 4 Oct) splits it: SHA-512 and SHAKE256, through
   `KeccakF1600`, go to `verity/primitives/circuits/hashes.py`, because `ncp2`, which stays in `verity/`, uses `sha512`,
   `shake256`, `sha_words` and `keccak_lanes` (`ncp2.py:57`); TurboSHAKE128 and `KeccakP1600R12` go with Pearl-C's tile
   check (since the 23:09Z revision, not experimental). circuits (row corrections, 4 Oct) sends the module whole wherever
   `words.py` goes, the catalog under the entry format: `Emit` builds `CompositeDefinition`s over PoUW's own word
   primitives (`PouwCh32`, `PouwMaj32`, `PouwXor32`, `PouwAdd64*`, `PouwRotl64*`), so in `verity/` it would import
   catalog-bound `words.py` against P6, and "one SHA-512" is a vectors bridge to `ml/boolean/sha512`. The row keeps the
   draft's open destination. Call 5 bears on it: if `ncp2` stays in `verity/`, the parts it uses can't be in the catalog.
2. **PoUW's `circuit/words.py` and `boolean.py`.** circuits (4 Oct) agrees with the draft's `catalog/definitions/pouw/`
   for both, since `boolean.py` imports only `verity/`-bound `ml.boolean.fp`, `forms` and `trace`. compute-accounting
   (§C13, 4 Oct) splits `words.py` by user: lines 44-209 (the 32-bit words, bytes and int7 entries, the accumulator,
   dequantization) with `ncp2` in `verity/`, the Pearl-C4 section (lines 210-245) with `pc4` to experimental, and the
   Pearl-C section (lines 246-298) with `pc8`; `boolean.py` goes with `pc8`. The same call-5 consequence applies: `ncp2`
   in `verity/` can't import a catalog `words.py`.
3. **Where Pearl-C's tile-check builders go (`pc8`, `rowk`, `leaves`).** compute-accounting's revision (23:09Z) takes
   them out of experimental, since under Daniel's 4:06 PM ruling they are Pearl-C's only route to a verdict, but doesn't
   name `verity/` or the catalog. Default 4 sends builders to the catalog; call 5 keeps `ncp2`, a builder the verifier
   runs, in `verity/` pending a decision that would decide these too. The rows keep the draft's catalog destination.
4. **The PoUW lock's size, against Daniel's 2:03 PM ruling.** The plan keeps five pins. compute-accounting (§A1, 4 Oct)
   shows code, ledger rows and a rendered table reading more: `pearl_c_work`'s `DRAW_WREF` names the 20
   `pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_*` pins and cites the served-layout γ and `HonestTileCapRate`;
   `ledger.py` writes γ from `price_twins.json`'s 104 twins into `kernel-attempt/v1` records that `panel.py` renders; and
   `plan.py`, `draw.py` and `consumers.py` cite about ten C-Flock audit-law pins. Either the lock keeps them, or that
   code cites only kept pins. compute-accounting brings it to Daniel with pouw-lock's report; proofs owns the C-Flock
   audit-law pins.
