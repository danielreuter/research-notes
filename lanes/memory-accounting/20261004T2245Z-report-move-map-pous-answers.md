---
id: 20261004T2245Z-report-move-map-pous-answers
campaign: pous
lane: memory-accounting
kind: report
status: open
repo: danielreuter/verity
origin: memory-accounting (bc-15ada664), answering top's move maps (Slack 1791152743.071189): core Q13 and protocols memory-accounting Q1–5, plus PoUS row corrections
---

# PoUS: answers to the move maps' questions, and row corrections

I checked these against `origin/main` `9400e83d5`. They answer `note:20261004T2125Z-draft-move-map-protocols` ("memory-accounting (PoUS)" Q1–5 and the PoUS rows' questions) and `note:20261004T2125Z-draft-move-map-core` Q13.

## Core Q13: the root `test_pous_*` files

They go to `benchmarks/pous/tests/`. `tests/test_pous_bench.py` tests `benchmarks/pous`'s dataset, implementation registry and certificate gate. `tests/test_pous_harness.py` tests `benchmarks/pous/band_gpu/harness.py` on CPU. Neither one tests `verity_pous`.

## Protocols, memory-accounting

1. **Dense: send the scheme to `experimental/pous/dense/`, and extract the overwrite chain first.**
   - `dense` is superseded by `band-d12` in the registry.
   - Band builds on `dense.DenseChain`, so before the move that chain goes into a `verity/…/pous/` module of its own (e.g. `chain.py`). That clears the map's import edge 1.
   - `ChainDenseMeets64` then leaves the lock. Its scheme's code would be experimental (P9), and no ledger row, published table, claim id or docs page relies on it. The lock-reduction draft (`cursor/pous-lock-reduction-3cf5`, in progress) checks this.
   - If a band guarantee's statement reads it, it stays as a read, not an entry.
   - The harness's `dense-chain/v1` arm (`band_gpu/harness.py`, `pod.sh SCHEME=`) moves with the scheme.
2. **P2 and P3: their pins leave the lock until promotion. P2 v3 does not promote when #1123 lands.**
   - P2 stays experimental: the P2–M1-SGI instantiation assumption is not accepted (spec decision 8), the XOR-then-reduce compression attack is open (`approach:pous/p2-xor-reduce-compression`), and the window and w are Daniel's call.
   - Under P9 the six P2 pins and `P3Concrete*` leave the lock. Their statements stay as `def`s in `Guarantees(.P2).lean`, so no digest in `reads` changes, and their proofs keep building in `security_proofs/pous/`. `approach:pous/ec-p2-16448` and `approach:pous/p3` cite the commit.
   - Promotion re-pins them with one statement review.
   - #1123's `test_certificates_name_proved_guarantees` then exempts experimental schemes again (it checks 7 certificates today).
   - `Protocol/P2/Cost.lean`, `M1`, `M1p`, `ColumnGame` and `P3Chain` stay in the spec at S3.1, which is a pure move. Once the validator reports spec definitions that no guarantee reads, a later consolidation moves those out. `P3Chain` stays anyway, because `BandChain` imports it.
3. **The grader: keep `Pous/SecurityProofs/Sanity.lean` and `Pous/SecurityProofs/Accounting/Numbers.lean` in the spec package under their names**, as PoUW keeps `Lifting`.
   - Then `TRUSTED.sha256` and `grade.sh`'s import set don't change in the move, and the move stays pure.
   - This holds under @lean's split constraint (verity#1144): those two modules keep the spec's root `Pous`, and every other proof module moves under a new root (`PousProofs.*`) while its declarations keep `namespace Pous.SecurityProofs`.
   - Narrowing the trusted set is a separate, reviewed change.
4. **`audit.py`: which counts are spec and certificate parameters, and which are calibrated device numbers.** Lean's `Accounting.Params` holds only ρ, δ, the 21/20 expansion and λ.
   - *Spec and certificate parameters* stay with the verifier in `verity/` and are pinned to Lean:
     - `AUDIT_CAP` (`Pous.Rebuild.auditCap`, which `BackgroundRebuildExcluded` reads);
     - `LATE_ROUNDS` (`BandGradedMeetsFamily`'s `D_late ≤ 12`);
     - `WORK` (Q);
     - `CHALLENGES` (k), which in practice is each certificate's own k.
   - `CERTIFIED_ROUNDS` (D = 10) is P3's certificate point, so it goes with P3 to `experimental/pous/p3/`. The band's D comes from its certificate.
   - *Calibrated device numbers* go to `catalog/devices/`, with no default in `verity/`:
     - `DEADLINE_NS` (Δ);
     - `RTT_ALLOWANCE_NS`;
     - `CALL_NS` (the 242 µs floor);
     - P2's `ROOT_CALL_NS`.
   - Every wall-clock reading of these counts holds in the ideal-permutation model only (#1122). P2's RTT allowance and root floor wait on Daniel's window ruling. The RTT-cap option is a draft proposal on `cursor/pous-p2-rtt-cap-3cf5`, set against a wider w.
5. **There is one copy of the band kernels: `benchmarks/pous/band_gpu/`.**
   - It moved from the vLLM tree's `engine/pous` (its `__init__` docstring), and main has no `verity_vllm/engine/pous`. Main's vLLM option (`protocol_options/pous.py`) uses the CPU reference codec, and the `vllm-gpu` bench arm reads an external pinned tree (`--impl-tree`).
   - The band and dense scheme vectors are the agreement between the reference codec and those kernels: `bench.py` gates the kernels against them. So `catalog/vectors/pous/` is right for them.

## The PoUS rows' other questions

- **`primitives.py`'s ideal objects:** no deployed path reads them. `band.ideal` and `dense.ideal` are model constructors that only `test_pous_band`, `test_pous_dense` and `test_pous_scheme` call, so they move to the tests with the ideal objects. `band_gpu/codec.py` only mentions `XorSponge` in a docstring.
- **`oracle.py`:** deployed code is written in its program types. `Prog` and `run` are used by `scheme`, `protocol`, `audit` and `dense`; `pure` and `Cost` by `audit`; `Query` by `primitives` and `dense`. So those stay in `verity/`, and only what the adversary and the model alone use moves to the tests. A split row, not a whole-file move.
- **`verifier.py`'s Merkle tree:** adopt the shared one later, as a change of meaning with a bridge. A move stays pure.
- **`DISCREPANCIES.md`:** it stays. Its rows record where Python and Lean conform, which is current truth, not candidates. B6's verdict (the Π₂ break) is already registered as `pous/pi2-wallclock-floor` and `pous/feistel-indifferentiability` (both killed).
- **Dropped statements in `Guarantees.lean`:** they stay as `def`s, so there are no record or digest changes. Moving them out is later consolidation.
- **`PousTargets.lean`:** it stays, exempt, until the grader's registry lists every open target. Then it retires.
- **The grader's `pinnedTargets`:** it follows `Pous/Guarantees*`, not the lock. A target is any statement there, and needn't be a guarantee.

## Corrections to the rows

- **Statuses (registry since 4 Oct, owner memory-accounting; `campaigns/pous/APPROACHES.md` renders them):**
  - "P2 v2 (ChaCha8 keys) live" is now `pous/p2-chacha8-keys`, **superseded** by `pous/ec-p2-16448`. Its codec stays as the nonconforming `p2-16448/v2`, which the `p2-gpu` bench arm measures, so it goes to `experimental/pous/p2/` with v3.
  - Also registered:
    - killed: `pi2-wallclock-floor`, `feistel-indifferentiability`, `two-tier-bandwidth`, `cost-rule-relaxations` and `erased-encode-secrets`;
    - parked: `keyed-page-fill-erasure`, `symmetric-wide-final-step` and `p2-xor-reduce-compression`;
    - live: `p2-seqroot-cooperating-cores`;
    - merged: `continuous-audit`, `rebuild-exclusion`, `continuous-time-average` and `continuous-complete`.
- **P2 fixtures:** #1123 adds `tests/fixtures/schemes/p2-16448-v3.json` and `tests/fixtures/p2-v1-keys.json` (the spec's key vectors). Both go to `experimental/pous/p2/` with `p2-16448-v2.json`.
- **The P2 spec:** the frozen v1 is `art:a7a29e84eef9d2584482b7f3e9722af6b579e2984a9633352564c562ce9e2021`. Its timing evidence is `art:23a323f313d2193873c59ee8ab59a0f1197167a0b4c6d008346d771c3e72de57` and the relays `note:20261004T2102Z-report-relay-p2-redteam-timing` and `…-deployment-decisions`. The spec goes beside `experimental/pous/p2/` when the code moves.
- **The lock:** "104 pins, about 73 after the reduction" was round 2's looser count. Under the 2:03 PM guarantee ruling, the lock-reduction draft (`cursor/pous-lock-reduction-3cf5`) keeps 15.
  - *Kept (11):* `BandMultiMeetsFamily` and its D2, D1 and D0 forms; `ChainDenseMeets64`; and six P2 pins. Code reads all of them today.
  - *Held (4):* `DigestAU` and three `SecureErasureMeets*`, while #1096 and #1086 are open.
  - That is the lock before the move. At the Python move, answers 1 and 2 take dense and P2 out, along with their code, leaving the band's four plus whatever the erasure PRs settle.

## Addendum, 00:50Z: import names under top's packaging call (notes 458c528e)

- **The protocol:** `protocols/pous/verity_pous/` goes to `verity/protocols/accounting/space/pous/`, imported as `verity.protocols.accounting.space.pous`.
  - Dense's overwrite chain, extracted before the move (answer 1), becomes `…space.pous.chain`.
  - `verity_pous` as an import name goes away. The vLLM option (`protocol_options/pous.py`), `benchmarks/pous` and the tests change with it.
- **Experimental schemes:** dense, P2 (v2 and v3, with their fixtures and the frozen spec) and P3 go to `experimental/verity_experimental/pous/{dense,p2,p3}/`, imported as `verity_experimental.pous.{dense,p2,p3}`.
- **The benchmarks:**
  - Today `bench.py`, the tests and `p2_v1` import `band_gpu`, `p2_v1`, `p2_gpu`, `hbm_audit` and `erase_calib` as bare top-level names off a `sys.path` entry for `benchmarks/pous`. The rule rules that out, and `-P` would break it.
  - They become one distribution, `benchmarks/pous/verity_pous_bench/{band_gpu,p2_v1,p2_gpu,erase_calib}/`, with `bench.py` as `verity_pous_bench.bench`. `hbm_audit` goes to `archive/` with TwoTierBandwidth (no host RAM).
  - The P2 harnesses stay in the benchmarks rather than moving to `experimental/`: `p2_v1` imports `band_gpu`'s shared native build, and `experimental/` shouldn't import a benchmark.
- **The grader** goes to `tools/` (the layout's "PoUS's grader"). Its Lean stays a Lake package, so no Python import name is involved.
