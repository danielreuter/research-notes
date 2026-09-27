---
cursor:
  subagentId: "bc-a80fa085-ee8b-5c0d-99d2-c81a08a6a795"
---

lane: vllm-verify-optins · kind: handoff · from: vllm-verify-optins (bc-a80fa085) · created: 2026-09-27T06:55Z

# STOPPED the CPU pod per your rule; FALLBACK ESTIMATE: one secure L40S with the GPU hidden, about 5 h, about $5.5 (cap $8)

Tree: verification merge `cursor/verify-optins-merge-a795` @ `b7a4092a`.

## What happened on the CPU pod (06:41Z to 06:51:40Z, about $0.19)
- **The pod.** cpu5m, 16 vCPU / 128 GB, $1.04/h, RunPod `l32zhicuc7ce1b`. None of the 32-vCPU shapes had stock. It is terminated and unregistered.
- **Setup run `r20260927-064517-eb5b`** (PRESERVED). The bootstrap succeeded.
- **The smoke Build failed below the attention question.** With no NVIDIA driver, vLLM resolves `UnspecifiedPlatform`, and `EngineArgs.create_engine_config` raises `RuntimeError: Device string must not be empty`. This failed on both #73's step Program and #57's.
- **vLLM's CUDA extensions don't load on that host** (`vllm._C`, `_vllm_fa2_C` / `_vllm_fa3_C`), and the export needs their ops (`_C.cutlass_scaled_mm`, `_C.rms_norm`, …). So no CPU-only host can build these Programs. The recorded Builds ran on GPU hosts.
- Evidence: `lanes/vllm-verify-optins/evidence/cpu-pod-smoke/`.

## Fallback (asks your GO)
**Pod:** `vyv-rf-verify-optins-l40s`, `--gpu "NVIDIA L40S" --cloud SECURE --min-vcpu 16 --min-ram 90`, registered with `--project verity --guard 90`.
- It costs about $1.09/h, normtap's measured secure L40S (driver 580). The community L40S pods had driver 550, so I avoid them.
- The GPU is only there for its driver libraries. Every stage runs with `CUDA_VISIBLE_DEVICES=""`, the tested GPU-free Build path, and bootstraps with `--cpu`, so no native taps are built.
- If there's no stock, I'll take the next secure 48 GB card with at least 16 vCPU and 90 GB RAM at up to $1.1/h (RTX 6000 Ada or A6000).

| step | pod h | $ |
|---|---|---|
| bootstrap and smoke Build: step Programs of #73 and #57 against the record's step digests, and FlashAttention impls. I stop within 20 min if the smoke fails | 0.4 | 0.4 |
| #73 Builds: unset and `check-inf-per-iteration`, concurrently; `cross_call` and the exact member check | 1.5 | 1.6 |
| #57 Builds: unset and `once`, concurrently; `cross_call` and the `+ 1` counts | 1.0 | 1.1 |
| #74 unset Build; `SHARED_SCALE` substitution, `cross_call` and member check on its 9 request Programs and the step Program | 1.6 | 1.7 |
| margin | 0.5 | 0.6 |
| **total** | **about 5** | **about $5.5, cap $8** |

Adding the $0.19 already spent, the lane total stays under your $10.

## Already done on the VM (light IR and numpy checks; no torch, no Build)
**#74 `SHARED_SCALE` on the stored Programs (`art:9d14bd11`).** Six of the nine request Programs are done: LP73_T1, LP11_T94, LP165_T8, LP449_T2, LP365_T127 and LP633_T112. The other three go on the pod, using the unset Build once its digests equal the record's.
- `cross_call`: 0 recomputes in all six, under both constructions.
- Member check, FP8 Calls:

| construction | violations | recomputed gates | committed words |
|---|---|---|---|
| recorded | 293,760 (every FP8 Call) | 57.45 G | — |
| `SHARED_SCALE` | 0 | 0 | +452,390,400 |

**#74 value check, which you asked about.** The evaluator is `evidence/vo_fp8_values.py`. It runs the recorded request Program Call by Call with the replay's row kernels, from the prompt ids and the checkpoint of record (sha256 `b6154d74…`, which matches the pin).
- **Layer 0 of `LP73_T1`, step 0: no mismatches.** The host products equal the old construction's `F32Mul_v1` at all 35,962,880 coordinates of 200 Calls. Every sampled coordinate's own `F32Mul` gates, its old output and its new output (fed the host products) equal the row kernel's.
- **Edge pairs, the cases where the two could differ.** numpy's array multiply (the host path) differs from `F32Mul_v1` on 40 of 784 edge pairs.
  - All 40 have two NaN operands, and the difference is payload only: numpy's array path returns the first operand's quieted NaN, the IR the second's.
  - That's because `F32Mul_v1` is defined as numpy's scalar multiply (`prims.f32_mul_bits`), so the IR's own NaN choice rests on numpy.
  - With one NaN or none, all pairs are bit-equal, subnormals and overflow included.
- **Why #74 never meets that case.** `x_s` can't be NaN, because `Fp8GroupScale` folds `fmaxf` from `eps`, which drops NaNs. So the committed products never meet a two-NaN pair.
- **Found, not fixed.** For root's rule, the committer should call `F32Mul_v1` itself rather than a free numpy expression. The array form `w_s * x_s` (operands swapped) matches `F32Mul_v1(x_s, w_s)` on all 784 edge pairs.
- **Next.** The whole of `LP73_T1` (both steps, token check) and `LP11_T94`'s first 12 steps run on the VM now. They'll report every NaN, subnormal and inf operand and product, and the product range.

Reply GO in `lanes/vllm-verify-optins/`. I create no pod before your answer.
