---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T04:28Z
---

# #476 merge-ready at e213ccc3: the vLLM suite's failure set equals base's (stacked on #465); 5b scale order settled

- **Suite (sm_120 pod, same pod for both):** head `9755dc08` (#476, which contains #465) run `r20260930-035619-48cb`; base `origin/main` `05305a3e` run `r20260930-035629-f454`.
  - Both ran `pytest tests -n 16 -m "not regression and not slow and not pod"`.
  - `tests/query/test_tp_moe_members.py` rebuilds stored TP2 MoE global manifests for 35+ minutes per case and has neither a `slow` nor a `pod` mark. I killed its subprocesses identically on both sides, so it fails in both. Its missing mark is found, not fixed.
  - **Failure sets are equal except one head-only failure:** my `test_hopper_words_are_not_the_ampere_chain`. Its random-normal data can't separate the two chains after bf16 rounding. **Fixed in `e213ccc3`**: wide-exponent operands keep one coordinate apart. On the pod, `test_gemm_target_correspondence.py`, `test_gemm_targets.py` and `test_target_family.py` pass (39 tests, the torch Bet A pins test included).
  - Base has 59 pre-existing failure/error lines on this pod.
- **Merge request:** **#476** `cursor/vllm-sm120-gemm-corr-422d` @ `e213ccc3`, on top of #465 (`cursor/vllm-sm120-target-422d` @ `f740c1d5`, already filed). No Definition, query or partition changes, so circuit-check and the partition gate don't apply. No existing digest moves.
- **5b per-tensor scale order** (run `r20260930-041842-76a2`): the CUTLASS sm_120 epilogue is `bf16(sa * (sb * acc))` on all 15,728,640 coordinates, 24 draws of vector and scalar scales over one 256x2560x4096 GEMM. 125 coordinates discriminate; `(sa*sb)*acc` misses 79 and `sb*(sa*acc)` misses 89. So the per-tensor Definition is `ScaledMmFp8_v1`'s order with the sm_120 step.
- **Pinning captures** (run `r20260930-041757-0bde`, e4m3 and e5m2, 25M elements each, fresh seed, declared model `BLACKWELL_SM120_E4M3/E5M2_M16N8K32` now in core on `cursor/vllm-sm120-fp8-probe-422d` @ `8eed14b0`) are running.
  - **Anchor question:** `trust.py` computes PINNED on the *anchor SKU* of the arch, which is the RTX 5090 for sm_120; the RTX PRO 6000 isn't in its SKU table. The PRO 6000 evidence will satisfy P2–P4 in substance. Formal PINNED needs either one 5090 sweep or a `Target` whose `anchor_device` is the PRO 6000. Your call; I'd take the Target route for the vLLM FP8 relation.
- **Next (per your decisions):** the `GemmBiasF32Epilogue_v1{K,N,DOT}` Definition PR, bound for `blackwell_consumer` only, and the time-boxed `gemvx` probe (at most 1 GPU-h). The simple FP32 orders I tried already miss 2–7 of 24.5k words; a designed cancellation probe is next.
