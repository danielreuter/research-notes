---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
---

# census-json: every served workload's subcircuits bound. Merge request (PR #67, stacked on #64)

**To:** research coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628).

## Merge request
- **PR:** [PR #67](https://github.com/danielreuter/verity/pull/67), `cursor/census-all-workloads-574a`. It targets #64's branch `cursor/headline-bindings-l40s-574a` and includes main `daf24d74`.
- **Merge order:** merge [PR #64](https://github.com/danielreuter/verity/pull/64) first, then #67, which GitHub retargets to main.
- **Tests:** `backends/numerical` passes (929). CPU only.
- **Parity:** tables, raw JSON and parity are byte-identical. Only the census block, the headline section and the entities headline change.

## What it does
- **Bindings:** 42 more bound census subcircuits, so every (template, parameters) of every census workload is bound.
  - **Ids and displays:** the bench spine's where it binds the template, otherwise its id form.
  - **Attention T ranges:** each spans every stratum the subcircuit serves. #101's head also serves #11, so its range is now 1–4607.
  - **Headline:** it now names every gap by subcircuit (`no result` / `commitment opening`).
- **No spine generator yet** (pinned in `test_headline.NO_SPINE_GENERATOR`):
  - FA3 attention;
  - greedy token select;
  - embedding;
  - the MoE router, expert coordinates (plain and weighted) and sum;
  - the FP8 block-scaled GEMM;
  - bias-add;
  - the bf16 scalar multiply.

  A test checks that the spine generates for the other new ids.

## Per workload

| Workload | Bound | Spine generates | No spine generator yet |
| --- | --- | --- | --- |
| #101 Llama-3.2-1B top-p · L40S | 9 of 9 | FA2 d64 · GEMM k2048, k8192 (sm80) · top-p V128256 · RMSNorm fused, Triton N2048 · RoPE d64 · SiLU i8192 | embedding |
| #11 Llama-3.2-1B greedy · L40S | 9 of 9 | FA2 d64 · GEMM k2048, k8192 (sm80) · RMSNorm fused, Triton N2048 · RoPE d64 · SiLU i8192 | embedding · greedy V128256 |
| #39 Qwen2.5-1.5B · L40S | 10 of 10 | FA2 d128-bn64 · GEMM k1536, k8960 (sm80) · RMSNorm fused, Triton N1536 eps1e-06 · RoPE d128 · SiLU i8960 | bias-add N2048 · embedding · greedy V151936 |
| #57 Gemma-2-2B · L40S | 7 of 7 | GEMM k2048, k2304, k9216 (sm80) · RoPE d256 | scalar mul N2304 · embedding · greedy V256000 |
| #60 Mistral-7B · L40S | 9 of 9 | FA2 d128-bn64 · GEMM k4096, k14336 (sm80) · RMSNorm fused, Triton N4096 · RoPE d128 · SiLU i14336 | embedding · greedy V32768 |
| #67 OLMoE-1B-7B · L40S | 12 of 12 | FA2 d128-bn64 · GEMM k2048 (sm80) · RMSNorm fused, Triton N2048 · RoPE d128 · SiLU i1024 | MoE router, expert k2048, expert-weighted k1024, sum · embedding · greedy V50304 |
| #68 OLMoE-1B-7B · L40S | 12 of 12 | same as #67 | same as #67 |
| #73 Qwen3-4B · H100 | 11 of 11 | GEMM k2560, k4096, k9728 (sm90 wgmma) · RMSNorm fused N2560, Triton N2560 and N128 (eps1e-06) · RoPE d128 · SiLU i9728 | FA3 d128-bn128 · embedding · greedy V151936 |
| #74 Qwen3-4B-FP8 · H100 | 12 of 12 | GEMM k2560 (sm90 wgmma bf16) · RMSNorm fused N2560, Triton N2560 and N128 · RoPE d128 · SiLU i9728 | FA3 d128-bn128 · FP8 block GEMM k2560, k4096, k9728 (G128) · embedding · greedy V151936 |

**Missing:** none. #57's softcap attention and GeLU·mul are not evaluable in the source run and sit outside its mix (its `not_evaluable_vus`), so they have no template to bind.
