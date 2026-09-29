---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc vLLM coordinator (bc-ecac3029), constants (bc-613ddf45)
created: 2026-09-28T04:58Z
priority: before the epoch's S4 forks (Daniel: the primitives move lands before the epoch if possible)
---

# Merge request: PR #223, the FP32/BF16 primitives into core `verity.ml.fp32` (fix 8, first PR, digest-neutral)

- **PR:** [#223](https://github.com/danielreuter/verity/pull/223), branch `cursor/silicon-prims-to-core-ac68`, head **`de3d49b071e0db43cb09f156e010ddf6ee4fe304`** (new at 06:47Z; it was `4663051f`), on `main` `6746f408`. Ready, CPU only, $0.
  - **Why the head moved:** `4663051f` failed the integration's P1 lint (`tests/lint/test_p01_core_abstractions.py`), because `prims.py` imported the private `verity.ml.fp32._decode` and `_round_f32`.
  - **The fix:** `fp32` now exports them as `f32_decode` and `f32_round`, and `prims.py` imports those. The lint and the registry tests pass (49 passed, 1 skipped), and `test_fp32.py`'s digest pins are unchanged.
  - `check` doesn't collect vLLM tests, so it wouldn't have caught this. Please use the new head.
- **Contents:**
  - 15 primitives (`F32Add`, `F32Mul`, `F32Fma`, `F32Div`, the `*Ftz` family, `F32Max`, `GuardNegInfZero`, `Bf16Add`, `Bf16AddF2fp`, `Bf16MulF32`, `Bf16MulBf16`, all `_v1`) move verbatim into core. The integration's registry re-exports them, so each registers once.
  - A test states which function each `AmpereBF16TcDot16` version is.
- **Digest-neutral, with evidence:** on `main` and on the branch, these are identical:
  - 254 registered ids;
  - 85 primitive descriptor digests;
  - 790 catalog Definition digests;
  - 30 whole-model program digests;
  - per moved primitive, its output fingerprint.

  circuit-check's JSON reports for the 15 ids are identical before and after, with 0 failures. The evidence scripts and outputs are in `internal/lanes/coordinator/evidence/prims-to-core-ac68/`.
- **Tests:** targeted runs, with the same outcome on `main` and the branch. Core `ml`/`evaluation`/boundaries: 223 passed. `circuit_check`: 828 passed, 2 xfailed. 33 vLLM test files: 493 passed. The vLLM set also has two failures and a collection error, the same ones on `main` (a NaN-sign test, and two torch-only tests).
- **Order:**
  - Trial merges are clean with #221 (G0), #219 and #220.
  - It and the epoch's S4 both edit `integrations/vllm/verity_vllm/program/registry/prims.py`, in different places. Merge this before S4's branch forks, or S4 rebases.
  - It removes nothing from #210's allowlist, since its backend repoints are deferred.
- **For the vLLM coordinator:** the integration's `registry_version()` keeps the same primitive rows, but its `sources` hash changes, as with any edit to `registry/prims.py`. Nothing pins it, but check whether any manifest you write in the epoch records it.
- **What doesn't move:** the MUFU and `div.full` primitives. Their evaluators call the integration's JIT C++ over its compressed tables, so porting them needs exhaustive equality evidence and a home for the tables beside `verity.ml.library`'s SHA-512 entries. That's a second PR, also digest-neutral, after the epoch's switch PRs. The note to the constants lane about the tables is `20260928T0455Z-note-to-vllm-coordinator-and-constants-from-consolidation-prims-to-core.md`.
