---
cursor:
  subagentId: "bc-a80fa085-ee8b-5c0d-99d2-c81a08a6a795"
---

lane: vllm-verify-optins · kind: handoff · from: vllm-verify-optins (bc-a80fa085) · created: 2026-09-27T06:40Z

# ESTIMATE before the first pod: one CPU pod, about 4.2 h, about $8.8 (cap $10 of the $20)

## Tree
None of #98, #102, #105, #106 or #109 is on main, so I verify a local merge. Branch `cursor/verify-optins-merge-a795` @ `b7a4092a` (pushed; not for merging):
- main `ae5db5d3`;
- #98 `4f87f275` (for `query.cross_call` and the member check);
- #105 `b0a12771` (which carries #102 `64a4c3d3`);
- #106 `df13126f`;
- #109 `39e3b24c`.

There were two conflicts, both additive, and I kept both sides:
- `pipeline/manifest.py`: #98's `--cross-call-check` and #102's MS class;
- `frontend/target_profile.py`: #105's `fa3_construction` and #109's `weight_only_calls`.

## Why a CPU pod answers all three tasks
- A Build is GPU-free: it exports on `meta` against a declared `TargetProfile` (`apply_target_profile`).
- On the pod I run the Build's own commands: `verity-vllm build` for the step and the eight request shapes, then `global-program`, then `manifest build-global`.
- `--target` is the record's device target (#57 `[8,9]`/142 SMs, #73 `[9,0]`/132, #74 its declared block), plus the knob. The workload files stay unedited, so "unset" is comparable byte for byte.
- Record digests are compared from `tests/regression/expected/<row>.json`: the step Program, the 8 shapes, the workload Program and the manifest.

## Plan, pod type, hours and dollars
**Pod:** `vyv-rf-verify-optins-cpu`, RunPod **cpu5m, 32 vCPU / 256 GB, $2.08/h**, registered with `--project verity --guard 90`.
- The recorded derives peak at about 8.4 GB RSS. Two Builds run concurrently at 6 to 8 derives each.
- Pod wall is about 4.2 h, so about **$8.8**, and I stop at a **$10** cap. The guard deadline is 15:00Z, and I expect to finish by about 11:30Z.

| task | pod work | pod h (share) | $ |
|---|---|---|---|
| bootstrap | venv, vLLM `d9105ea80`, three checkpoints (about 20 GB), a smoke Build | 0.5 | 1.0 |
| #57 | Builds with the knob unset and with `once`, run concurrently; `cross_call` on all 9 Programs of each; the `+ 1` Call counts | 0.9 | 1.9 |
| #73 | Builds unset and with `check-inf-per-iteration`; `Q_word_v1` unit_rule with the member check on every distinct specialization of the new Build (`Attention_v4` included), and `cross_call` | 1.4 | 2.9 |
| #74 | an unset Build; `SHARED_SCALE` substituted on the stored Programs (`art:9d14bd11`, all 9), with the member check and `cross_call` | 1.4 | 3.0 |

**The #74 value check (part of the #74 row above).** No stored #74 run holds values: the records keep verdicts and roots, and there has been no VU export for #74 since 09-22. So on the pod I evaluate a prefix of the recorded request Programs with the replay's row kernels (`kernels/rows.py`), using the checkpoint's weights and the workload's prompt ids. That gives the Program's own `x_s`, which the record's GREEN local replay showed equal to the served values. Over a sample of steps (every request's prefill at the first layers, plus request `LP73_T1`'s decode step if it fits), I compare:
- the host products, numpy f32 `x_s[kb] * w_s[nb, kb]`;
- the old construction's `F32Mul_v1` operands at every (n, kb), evaluated by the IR's `evaluate_batch`;
- the old and new Definitions' outputs on sampled coordinates.

**The one risk.** vLLM on a host with no NVIDIA driver may resolve a non-CUDA platform, and then pick a non-FlashAttention backend. The smoke Build shows this within about 20 minutes (about $0.7). If it happens, I terminate the pod and ask you for the cheapest single-GPU pod with `CUDA_VISIBLE_DEVICES=""` (the tested GPU-free path), at about $1/h for the same plan.

**Not in this estimate.** "Optionally, the Match under the new construction" (#73) needs an H100 capture, because the records carry no capture. After the CPU results I'll send you a separate H100 estimate if the fold emits `Attention_v4` (about 2 h, about $7).

Reply GO in `lanes/vllm-verify-optins/` (or my inbox). I prepare the scripts on the VM meanwhile, and create no pod before your answer.
