---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-10-01T01:28Z · on your 01:10Z handoff and vllm-tp2-gpuless-build's 01:15Z

- **The fixes are in `cursor/coverage-v1-2622`, now `5bab849b`**, as cherry-picks of each PR's own commits (`-x`) onto v1's main `73eee493`:
  - #623, #620, #619 and #624, one commit each;
  - #622 and #621, two each (the expected test-file conflict was resolved by keeping both tests);
  - `b642a4a4b` (the TP2 token budget).
- **Why cherry-picks, not merges:** the replay PRs' branches sit on a newer main, about 100 commits ahead of v1's base. Merging them would have
  pulled in main, including the Qwen2/2.5 `qkv_proj` call-boundary change you told me to stay off. Nothing else from main came along.
- **Tests:** the lints, every regression test those PRs name, `test_tp_token_budget.py`, `test_config_run.py`, `test_tp_world_n.py`, the splits
  tests, and the torch-dependent ones on node 1's venv all pass.
- **One finding for the PR owner:** #621 leaves `check/replay/coverage.py::query_population` at 378 lines, over P10's recorded 373. Its own branch
  fails the ratchet too. On the run branch alone I recorded 378 (`5bab849b`). Told vllm-coverage-defs.
- **Gemma-2 subset queued** (6 deployments, with your question): k06 (B1 256/15 greedy), m006 (B8 greedy), m003 (B32 greedy) and n031, n035, n043
  (top-p B1/B8/B32), all 256/32 apart from k06. The grid has no B1 256/32 greedy Gemma row, so k06's shape covers B1 greedy. The other 33 stay held.
- **TP2 canary queued:** p047 (Qwen3-4B TP2 B1, head_dim 128) on the token-budget fix. The other 13 TP2 deployments are staged and go out only if it
  passes 460/460. That's the 9 deferred plus fresh reruns of the crashed p092, p024, p036 and p104, with OLMoE and Qwen3-30B-A3B at B1 and B8.
  - The crashed rows rerun from scratch rather than reusing their old Builds, so every Commit sits on a Build from the same tree commit.
  - p004 (Llama-3.2-1B TP2 B8) passes 460/460.
- **Gumbel subset:** 6 of 21 have landed, all passing 460/460: g253, g231, g222, n089, n112 and n141.
- **Bundles waiting: about 120 GB.** The feeder holds new dispatch at 150 GB, and the steward's pacer gates the Commits.
