---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T11:06Z
---

# Qwen2.5 bias gap (your 10:27Z task): the bias is a weight and the Build side was wrong; fix is #535 (head `5d0e3acf`), no #483/#501 signature change

- **Which side was wrong.** The bias is a **weight**: pinned, and in the manifest's `weights` family (267 of 267 fields).
  - The unbound identity is **not** the bias. It is the post-bias **activation**, `instance_outputs` `qkv_proj` member `bias`, spec `BiasAdd_v1`.
  - The source is manifest `f8f25cfc` of `r20260930-093907-23fb`.
  - On cc 12.0, `TritonGemmRule` fused the launch and its bias add only on Ampere-family targets. So the Build bound the linear as `Gemm_v2` + a separate `BiasAdd_v1` Call, named `…/bias`.
  - The pre-bias word became a `call_boundaries` identity, the 768 host-evaluated ones.
  - The module's value became member `bias`. The collector binds a Linear's output as `out`, so that member never binds.
  - #483/#501 registered the Definitions and `bias_epilogue`, but no rule bound them. So the old Program also carried the bf16-after-rounding add, which is not what cuBLASLt serves.
- **The fix (#535, stacked on #501; retarget to main after the train).**
  - On `bias_epilogue == "f32"`, the rule fuses as cc 8.x does: one Call per row named after the add, so the value is member `out`.
  - M ≥ 2 gives `GemmBiasF32Epilogue_v1`; M = 1 gives `GemvBiasF32_v1` with the table's (V, T).
  - **#483/#501's Definitions and signatures are unchanged, so they stay in the train as planned.**
- **Limit: B ≥ 2 at one own row is refused by name.** The launch context declares `max_seqlen_q`, not the launch's total rows, so gemv (M = 1) and GEMM (M ≥ 2) can't be told apart. **Qwen2.5-1.5B B8 will therefore refuse at Build** instead of failing the Commit. B8 needs the launch's M per step declared in the launch context (`pipeline/launch_context`). Say if you want it next.
- **Digests.** The real Qwen2.5-0.5B request Build (LP 16, T 3) was run on `757fdf8c` with and without the fix.
  - **cc 8.9 is identical, `92554796…`** (456 × `GemmBias_v1`): `r20260930-105405-df15` vs `r20260930-105348-9393`.
  - cc 12.0 moves from `11a11dae…` (`Gemm_v2` + `BiasAdd_v1`) to `dedaa6e1…` (384 × `GemmBiasF32Epilogue_v1` + 72 × `GemvBiasF32_v1`).
- **Tests.** The targeted CPU set passes (`r20260930-104914-374d`, short slot): 8 new cases in `test_gemm_bias.py`, plus the bias, gemv, GEMM-target, lint and by-name tests.
- **Acceptance run in flight:** Kueue job 162, the `config-run-row` for Qwen2.5-0.5B cc 12.0 B1 with `REPLAY_K=460`, on a local tree of `757fdf8c` + #535. ETA about 11:50Z.
  - **Submitted with `--allow-stale`:** GitHub auth has refused fetches since about 10:52Z. `sky/` equals `infra/nebius` `4e96ed05`, fetched at 10:31Z, which contains `73998c0e`.
- **NVFP4 totality (next on your list) is already done.**
  - #523 `91d3f7a2` has the measured scale-byte rules (job 119, `r20260930-093614-53fd`) and a total kernel.
  - It is merged into #524 `ca71edd0`.
  - circuit-check passes 7 of 7 targets with 0 failures (`r20260930-102524-e321`).
  - So after this I go to `per_token_group_fp8_quant` unless you say otherwise.
- The steward's 10:08Z short-slot note has been acted on: every direct run is in check-s1.
