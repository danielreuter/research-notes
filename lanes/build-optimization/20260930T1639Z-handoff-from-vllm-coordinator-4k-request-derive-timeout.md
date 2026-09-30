---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: build-optimization (bc-47d0a3ed) · kind: handoff (PRIORITY: blocks 16+ coverage deployments) · from: vllm-coordinator · created: 2026-09-30T16:39Z

# Batch-1, 4k-context request derives hit the 7,200 s Build timeout on sm_120

**The finding** (epoch-run): k23 (Llama-3.2-1B) and k24 (SmolLM2-135M), rtxpro6000, B1, i4096/o512.
- The **step** Program derives in seconds. The **request** Program (a 4,096-token prompt plus 511 output tokens) doesn't finish within 7,200 s, running on about 2 cores at 100–127 GiB.
- **16 more grid deployments** are parked behind this.
- Epoch-run is running one k24 rerun with a 12 h timeout to measure it. Read its timeline and RSS when it lands.

**The ask:** make the request derive reuse the step Program's structure, so it doesn't scale badly with sequence length.
- A request is the step Program repeated per engine step, with attention's key/value reads growing by one row per token. Today the derive re-traces or re-builds per step.
- Find where the time and memory go: tracing, Program construction, canonical encoding, `Q_word` cuts, or manifest building. Then reuse the step's derived Definitions per step shape (the Program cache, or templating per engine step), so only the genuinely per-token parts, the attention rows' T, are new work.
- Whatever you change, **the request Program's digest must stay byte-identical** to today's for rows that do finish (e.g. a 1k-context row). Prove it on one before and after.

Also check whether #479's parallel derives or #558's encode-once already help here. A single request derive is one process, so probably not.

Send PR heads to me as `-handoff-` files in `lanes/vllm-coordinator/`. I'll grant and route them to the next train.
