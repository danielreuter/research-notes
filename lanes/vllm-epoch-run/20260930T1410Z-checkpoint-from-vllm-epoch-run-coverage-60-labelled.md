---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T14:10Z

**60 cells labelled, 15 pass.** New: SmolLM2-135M top-p (`r20260930-133623-ce84`) and TinyLlama top-p (`r20260930-133707-8fdf`) pass 460/460 with MAX_GATES raised to 44M and 30M; the Llama top-p and Gumbel re-runs (113M) and the two 4k-context cells are running. The run branch `2f5d600b` adds infra/nebius `763ea668` (the two-task template now publishes Attempts), #551 (the sm_120 softcap) and `b0b612e0`, which makes a config run's decision document `config_record.json` so the Commit Attempt carries its verdict (the steward's 13:56Z gap). Qwen3-30B-A3B (re-run for its Attempt) and Gemma-2-2B (on #551) are submitted on the two-task template.
