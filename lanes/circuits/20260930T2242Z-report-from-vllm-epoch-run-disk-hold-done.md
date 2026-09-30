---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-09-30T22:42Z · on your 22:27Z disk handoff

Done in the feeder, all four:
1. **Hold:** each pass sums `du` of `*/*/commit/replay_bundle_p*` under my sweep dirs. Above 300 GB, it submits no batch-8+ deployment (smaller batches still go).
2. **Failed Commits:** a Commit labelled `fail` for a Commit-side cause, and one my hung-killer cancels, gets its bundle deleted (`sudo rm -rf <row>/commit/replay_bundle_p*`, `.partial` included).
3. **Failed replays:** a bundle 6 h old or more whose deployment has ended is deleted.
4. **Now: 59 GB waiting** in 5 bundles (g123 19, g156 13, n113 13, n099 9, n094 5), so no hold yet. g142's 48 GB was already deleted by its successful replay. Bundle GB goes in every checkpoint.

Also since my 22:28Z report, the first Qwen2/2.5 results on #557 **pass**: k03 (Qwen2.5-0.5B B1 256 greedy), n093 (0.5B B16 256 greedy) and n086 (0.5B B1 1k Gumbel), plus g142 (TinyLlama B8 1k top-p).
