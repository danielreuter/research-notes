---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T11:25Z

**53 cells labelled: 9 pass, 14 fail, 30 unsupported.** New passes since 09:40Z: OLMoE at 460/460 on the #528 tree (`r20260930-104018-c6e8`) and Llama-3.2-1B B8 at 1k context (`r20260930-102756-ce52`: the Build peaked at 17 GiB over 28 min, the Commit at 60 GiB). Running are the other three B8 cells, Qwen3-4B, Qwen2.5-1.5B (bias), Qwen3-30B-A3B (Build timeout 7200 s) and the two new 4k-context cells. The run branch is `cursor/coverage-v0-2622`, now including #536 and infra/nebius `9540e031`; its prefix is `pre-merge #486 #481 #469 #487 #502 #483 #501 #528 #536 @ e0dff9af`.
