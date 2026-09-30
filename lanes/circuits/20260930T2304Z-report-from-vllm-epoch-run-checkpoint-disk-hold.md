---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-09-30T23:04Z · checkpoint; on your 22:39Z filler handoff and the resource steward's 22:43Z RAM policy

**Checkpoint:** 439 labelled: 108 pass, 22 fail, 309 unsupported (node-2 Commits apart: 0). **Bundle GB waiting: 67** (node 1 `/workspace` 73%). **Node-1 dispatch is on hold** (root 22:52Z): the feeder labels and cleans
up but submits nothing, and a loop keeps my waiting node-1 Commits suspended (19 at 22:54Z). Running Commits and node-2 work continue.

- **Filler is out**, and has been since 22:25Z: the feeder's queue holds only the approved subsets and the MoE subset. The 78 unapproved cells, plus the 25 I withdrew at their
  Build, sit in `grid_not_approved`, which is never dispatched. My 22:06Z checkpoint predates that.
- **RAM (resource steward):** from the next dispatch, a Build requests 48 GB (was up to 235). Commits stay at 64 GB below batch 8 and 170 GB at batch 8+. I set no limits.
- **Two labels corrected** (not verification results): g058 (Mistral B8 1k top-p) was SIGKILLed (rc 137) at 22:54Z while writing its 105 GB bundle, and n001 (TinyLlama B64 1k
  greedy) got SIGTERM at 22:57Z, both during the disk emergency. The feeder had labelled them from the Build task's interim record as "commit not run". It now spots an external kill
  and says so. Neither is an approved item, so neither reruns.
- **New passes:** n127 (Qwen2.5 on #557), plus k03, n093 and n086 earlier.
