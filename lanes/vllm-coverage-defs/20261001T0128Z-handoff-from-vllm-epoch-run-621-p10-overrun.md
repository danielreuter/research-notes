---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vllm-coverage-defs, cc @circuits · created: 2026-10-01T01:28Z

# #621 is over the P10 size ratchet: `query_population` is 378 lines against its recorded 373

- `cursor/replay-norm-scale-index-987d` @ `cb341f707` (#621) adds 5 lines to `verity_vllm/check/replay/coverage.py::query_population`, making it 378
  lines.
- `tests/lint/allowlists/p10_size.json` records 373 there, on #621's branch and on main alike, so `tests/lint/test_p10_size.py` fails on the PR.
  "Recorded sizes only come down", so the fix is a split, not a higher record.
- Your six PRs otherwise pass the lints and their regression tests on the epoch run's branch, `cursor/coverage-v1-2622`, where they are
  cherry-picked onto main `73eee493`. That branch alone records 378 (`5bab849b`), so the Gemma-2 subset could run. Nothing on main or on your
  branches was changed.
