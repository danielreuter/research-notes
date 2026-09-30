---
id: 20260930T0652Z-merge-request-train-speedup-495
campaign: verity
lane: train-speedup
kind: handoff
status: open
repo: danielreuter/verity
origin: train-speedup (bc-8e199f0d)
---

# Merge request (infra priority: unblocks checks on vy-nebius-1): #495 at 43ec23e5

- **PR:** [#495](https://github.com/danielreuter/verity/pull/495), branch `cursor/row-tests-tmp-native-collect-9ff8`, head `43ec23e5`, on
  main `29f691be`.
- **Change:** one test helper, `integrations/vllm/tests/pipeline/test_row.py` `_opts`. It passes
  `--native-collect-default <tmp>/nc_build`, so `SingleRow.prepare` no longer creates `/workspace/cp` on the checking machine. That
  directory is what failed TLN's check on vy-nebius-1: a non-root check can't create it.
- **Tests:** `tests/test_target_family.py`, `tests/pipeline/test_row.py`, `test_config_run.py` and `test_release_json.py` pass as a
  non-root user, and nothing is written to `/workspace/cp`. Without the change, the failing test creates it.
- **Cost in a train:** it changes a file in the vLLM suite's directory. So in a train that doesn't already change `integrations/vllm`,
  the vLLM suite runs; per-test verdicts keep reuse to what that module reaches.
- **Where to put it:** any train that already touches `integrations/vllm` (TVF, or #486's train), so the suite runs only once.
- **No** Lean, circuit or `backends/flock/` change.
