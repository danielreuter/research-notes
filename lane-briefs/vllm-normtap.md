---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-normtap (norm-scale taps, opt-in, off the record path)

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-normtap`: the norm-scale taps Daniel approved (Sep 26, 19:33Z). First read
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md` and do its section 1. Then read
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md` (it overrides the setup page for vLLM
> lanes, including the no-waiting rule, the gate (b) git-clone procedure and `sampled_proofs` on PYTHONPATH), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-normtap.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-normtap open "..."`) within 10 minutes.

## What Daniel approved
Read `$STORE/docs/fine-query-plan.md` §4 and `$STORE/docs/boolean-core-architecture.md` §4.2, §4.4, §4.8.
- **One committed 32-bit scale per norm Call per token row**, from:
  - the **fused CUDA** `fused_add_rms_norm_kernel<c10::BFloat16, 0, true>` (`csrc/layernorm_kernels.cu` at vLLM `d9105ea80`; the IR
    model is `RMSNormFusedCuda_v2`). The tap is one store: thread 0 writes `s_variance` to `scale_out[blockIdx.x]` after the
    `__syncthreads()` that publishes it;
  - the **Triton** batch-invariant `_rms_norm_kernel` (`RMSNormTriton_v1`): `tl.store(scale_ptr + row, inv)` in a patched copy.
- This also covers **Qwen3's `q_norm` / `k_norm`**, which run through the same kernels: one scale per (token, head, layer).
- **Gemma's policy change** (plan §4; Gemma's norm is an ATen chain, not these kernels). Implement what the plan specifies for Gemma.
- **Not approved, don't build on it:** the re-baseline epoch, and the recompute threshold for tiny shared values ("2 gates" against
  "64 ANDs"). It's undecided, so nothing may depend on either value.

## Requirements
- **Opt-in and off the record path.** With the tap off (the default), everything is byte-identical to today: no Program, manifest,
  commitment root, leaf id or verdict changes, and #101's run root equals the record. The switch lives in the typed config /
  CLI (a5's), as one flag, like `VU_EXPORT`.
- **Build the taps like the FA2 tap:** a separately built tapped op (`ops/pod_fa2_tap.sh`), swapped in at launch the way
  `acquire/sources/hidden_source.py` does, owned by `engine/hooks.py` (uninstallable; P9).
- **An exactness property per kernel,** as `properties/fa_tap_exactness.py` does:
  - the tapped kernel's outputs are bit-identical to the installed kernel's;
  - every row's scale word is written;
  - the scale word equals the IR model's scale (`RMSNormFusedCuda_v2` / `RMSNormTriton_v1`) bit for bit.
  - For Triton, also show that the compiled arithmetic is unchanged.
- **With the tap on:** a new committed family (for example `norm_scale`), declared, collected and committed like the FA2 stream.
  The manifest and `Q_word_v1{16,32}` (PR #82's `query/word.py`) then see the scale as a committed boundary. That gives the run a
  different run root, which is expected and is never the record.

## GPU: nothing until the coordinator confirms Daniel's approval of the estimate
Start with code and CPU-side tests on your VM. **Create no pod until a coordinator handoff in your notes dir says the GPU estimate
is approved.** The coordinator's estimate for this lane:
- one L40S (driver 580 / CUDA ≥ 12.9), about 5–6 h: build both taps (~0.5 h); run both exactness properties on synthetic shapes,
  including Llama-3.2-1B (N = 2048), Qwen3 q/k norm head dims and Gemma's; then #101 end to end with the tap on and off (~2 × 1 h).
  About $6–7;
- one small CPU pod for lints and gate (b), head against base, in a git clone: about $1–2.
- **Lane cap: $10.** Stop and ask before passing it.

## Finish
- A merge-ready handoff to `lanes/vllm-coordinator/`: the exactness results, #101 with the tap off (run root = record) and on (the new
  family's word count against the plan's 9,471 for #101), and gate (b).
- READY.md, pods terminated, FINAL.
