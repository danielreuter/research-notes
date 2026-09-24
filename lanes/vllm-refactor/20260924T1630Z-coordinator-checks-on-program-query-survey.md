---
id: vllm-refactor/coordinator-checks-2
lane: vllm-refactor
kind: note
created: 2026-09-24T16:30Z
---
# Coordinator spot-checks of survey-program-query-corr.md (at f0810a11)

## Confirmed
- **The integration forks core's Definition library.** `program/registry/prims.py:183` registers `Bf16ToF32` v1 and `:199` registers `F2fpBf16` v1. Core `verity/ml/prims.py:30,44` registers the same ids as different objects. `verity/ir/defs.py:35-38` raises `ValueError("registry already has a different definition")` when both register, so the integration can't import core's `verity.ml`.
- **One id computes two functions.** Core has `AmpereBF16TcDot16` v2 with the measured total semantics (`ml/prims.py:52`). The integration's `AmpereBF16TcDot16` v1 (`registry/prims.py:381`) was switched to the same total semantics in R17 without a version bump; its docstring at `:371-374` says the difference is on non-finite outcomes only. So the v1 id means different functions in pre-R17 and post-R17 evidence.

## Housekeeping
- The surveyor ran Python in the owner's checkout. That left 5 ignored `__pycache__` directories, which were removed with `git clean -fdX integrations/vllm/verity_vllm`. The checkout is still clean at `f0810a11`.
