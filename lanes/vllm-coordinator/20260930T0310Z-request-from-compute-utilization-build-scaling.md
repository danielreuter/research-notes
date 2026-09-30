---
cursor:
  subagentId: "bc-fac4ba44-0b25-5091-9e44-a405e06abb80"
id: 20260930T0310Z-request-from-compute-utilization-build-scaling
lane: vllm-coordinator
kind: request
status: open
from: compute-utilization worker (bc-fac4ba44), for root and Daniel
---

# Request: how the Build's RAM, CPU and time scale to frontier models

Root asked me to choose hardware for a dedicated "represent big models" server: load a model, serve many configs, collect the Build, Programs and commitments, then run a tiny CPU replay. The host's RAM is the open question. `docs/circuit-extraction-server.md` carries the estimate below and will be corrected from your answer.

**What our records show:**
- **Measured:** completed Builds peak at 25–91 GiB RSS on 1–4 cores:
  - SmolLM2-135M, Llama-3.2-1B, Gemma-2-2B, Mistral-7B, OLMoE and Qwen3-4B;
  - contexts up to 1k/128, batches up to 64.
- **Your figure:** about 486 GiB for B1 at 4k/512. I read those rows (#11, #39) as Llama-3.2-1B and Qwen2.5-1.5B; please correct me if not.
- **So** Build RAM seems to track context, steps, layers and heads, not parameters.

**Questions** (a number or a rough exponent is enough):
1. What dominates the Build's RSS: the Program's Calls, the `Q_word` manifest's entries, or per-element values? How does it scale with the following?
   - context length: linear or quadratic, through attention;
   - decode steps;
   - layers;
   - heads;
   - hidden width;
   - MoE expert count and top-k;
   - TP degree (one Program per rank?).
2. Your rough Build RAM and wall time on 1 core for **DeepSeek-V3 (671B)**: 61 layers, hidden 7168, 128 MLA heads, 256 routed experts plus 1 shared, top-8. Please give both of these:
   - B1 at 1k/128;
   - B1 at 4k/512.
3. The same for **Kimi K2 (~1T)**: 61 layers, hidden 7168, 64 MLA heads, 384 routed experts plus 1 shared, top-8.
4. Does splitting the Build per request (or per decode step) bound its RAM, and at what cost in time? And does the Build parallelize across cores if Programs are derived per request?
5. What else the integration needs before a frontier model is representable:
   - TP > 2 or expert parallelism;
   - MLA attention;
   - block-FP8 and NVFP4 MoE GEMMs;
   - anything else.

My working estimate, to be replaced by yours: Build RAM of about 0.2–0.5 TiB at 1k context, and 3.7–7.4 TiB at 4k unless the Build is split per request. The 4k figure scales your 486 GiB by the ratio of layers × heads: 15× for DeepSeek-V3 and 7.6× for Kimi K2.
