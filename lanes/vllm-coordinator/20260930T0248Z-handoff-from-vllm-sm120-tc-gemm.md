---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T02:48Z
---

# sm_120 target registration head ready for review: cursor/vllm-sm120-target-422d @ d993873f (PR #465), lanes B and C can stack on it

- **Branch/head:** `cursor/vllm-sm120-target-422d` @ `d993873f`, base `origin/main` @ `05305a3e`. PR https://github.com/danielreuter/verity/pull/465 (draft).
- **What:** `config.TARGETS["rtxpro6000"] = (12, 0)`; `gemm_targets.REGISTERED["blackwell_consumer"]` (cc 12.0, vLLM family None, so default tiling); `TargetProfile.tensor_core_family` maps cc 12.0 exactly to `blackwell_consumer`; `targets.TARGETS["blackwell_consumer"]` with `flash_attn_versions=()`, so attention on sm_120 is refused by name until lane B registers FA2.
- **Decision 1, the dot:** the brief said "core's mma.sync m16n8k16", but on sm_120 core pins that instruction to **HOPPER_BF16_M16N8K16**, not the Ampere/Ada pipeline (the 5090 run disagrees with Ampere on 48,569 of 204,800 elements). So sm_120 GEMMs bind `Gemm_v2{K,N,DOT=HopperBF16WgmmaDot16_v1}` (same parameters), the same Definition as H100's, not `Gemm_v1`. Lane B should expect DOT=Hopper in FA2 on sm_120 too.
- **Decision 2, the name:** the key is `blackwell_consumer`, not `sm120`. The P8 lint flags code strings naming `sm_12x` or a GPU like `5090` outside quarantine/ and engine/profiles/, and its allowlist only shrinks.
- **No record moves:** for cc 8.0/8.9/9.0, the registry's JSON dump is byte-identical between origin/main and the head (same sha256). The dump covers the GEMM records, `TargetProfile` digests and families, `targets.describe`, the `gemm_spec` ids and the attention entries. No new Definition, so circuit-check and the partition checker don't apply.
- **Tests:** on the VM, without pytest or torch, every torch-free test in `tests/program/test_gemm_targets.py` and `tests/test_target_family.py` passes (new sm_120 cases included), and the P7/P8/P9/P11/P12 lint scans show no new or stale entries. **Still to run:** the full vLLM suite and one torch test (`test_bet_a_pins_the_default_tile_and_188_sms_on_the_pro6000`). I plan to run them on my first sm120 pod, before step 2's capture. Or tell me to use a CPU pod or `check` instead.
- **Registered before the correspondence:** the GEMM record's evidence says so; step 2 appends the run.
- **Found, not fixed (for lane B):** `query/required.py::_profile` picks the FA3 hidden stream for `cc[0] >= 9` when no FA version is observed, which is wrong on sm_120 (FA2).
- **Waiting on you:** confirmation that the `vy-sm120-` budget line is live. I create no pod until then.
