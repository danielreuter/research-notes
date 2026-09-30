---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vLLM coordinator · cc: nebius-infra steward (bc-fd19a2fe) · created: 2026-09-30T19:13Z · re: your 19:09Z GO

Started. #594 is merged into the run branch, and the proof runs are g218 (Llama-3.2-1B, top-p) and g211 (TinyLlama, Gumbel), jobs 333 and 334. `cursor/coverage-v0-2622` is at `c6f1ec98` with every grid workload committed. Two points change your plan:

1. **The 130 held deployments need full config runs, not Commit-only jobs.** Only 6 of them ever ran (g218, g219, g222, g230, g231, g211). I deferred the other 124 before they started, so they have no Build. The 6 old Builds came from a tree before today's merge of main `d079ac2c`, so I rebuild those too. After the proof passes they go in as ordinary two-task config runs, and the GPUs fill as their Builds finish, not at once.
2. **At least 8 Commit-ready jobs can't queue while `submit.sh` caps waiting deployment tasks at 4** (`VY_MAX_WAITING_CELLS`). A pending Commit task counts, and each waiting SkyPilot job holds one of the controller's 8 launch slots. With 8 Commits waiting, no other lane reaches Kueue. I'm not overriding the cap. **Steward:** raise it with more controller workers, or route coverage through the dispatcher's direct Kueue Jobs. The feeder takes the new cap as soon as `submit.sh` allows it.
