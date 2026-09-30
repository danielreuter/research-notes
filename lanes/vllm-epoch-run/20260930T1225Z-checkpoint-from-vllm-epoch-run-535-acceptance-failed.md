---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T12:25Z

**#535's acceptance run failed, so the Qwen2.5 batch-1 cells are not requeued.** Job 162 (`r20260930-120040-7f5f`, Qwen2.5-0.5B B1) failed its Commit identity coverage: 768 of 11979 required identities have no binding, the first being step 0 `model.layers.0.self_attn.qkv_proj/out`, which is the post-bias qkv activation. 58 cells are labelled (13 pass). The two-task cells are in: Qwen3-30B-A3B, and the top-p/Gumbel re-runs with raised MAX_GATES (Llama top-p and Gumbel, SmolLM2, TinyLlama). The 4k/1k context cells go in after the quiet hour.
