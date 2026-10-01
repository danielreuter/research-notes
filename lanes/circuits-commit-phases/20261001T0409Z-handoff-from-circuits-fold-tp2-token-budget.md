---
id: 20261001T0409Z-handoff-from-circuits-fold-tp2-token-budget
campaign: verity
lane: circuits-commit-phases
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: fold the TP2 token-budget fix (`b642a4a4b`) into your branch, so it lands with fixes 1 and 2 and needs no PR of its own

- **The fix:** `cursor/tp2-commit-token-budget-ec1f` @ `b642a4a4b`, by vllm-tp2-gpuless-build. A TP2 Commit crashed because the engine's
  `max_num_batched_tokens` (2048) was below `max_model_len`.
- **Evidence:** the TP2 canary p047 passed on it (`r20261001-015257-ea78`, 460/460), and the epoch run already carries it on its run
  branch. Its test is `test_tp_token_budget.py`.
- **Why fold it:** circuits is over its open-PR cap, and this fix is small and touches the same config-run Commit path as your work.
- **What to do:** `git cherry-pick -x b642a4a4b` onto `cursor/commit-gpu-phases-8c79`. Run its test with your suites, and name it in your
  PR body as a separate commit.
