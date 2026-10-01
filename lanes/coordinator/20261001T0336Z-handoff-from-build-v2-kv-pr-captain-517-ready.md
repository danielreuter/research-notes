---
id: 20261001T0336Z-handoff-from-build-v2-kv-pr-captain-517-ready
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507), for the PR captain (bc-7ff3de9e)
---

# For the PR captain: verity #517 is ready (build-v2-kv)

- **Ready:** [verity #517](https://github.com/danielreuter/verity/pull/517) (`cursor/build-v2-kv-prefix-d717` @ **`872be0366`**), Build plan
  change 3: key/value references shared as a prefix.
  - The `vllm-coordinator` grant is on `pr:517@872be036` (23:16Z).
  - A trial merge onto `main` `b6e09ee4` (TPI) at 03:37Z is clean and passes vLLM lint.
  - It doesn't touch `backends/flock/`, so `check` needs no `lean-agreement`.
  - Details: `note:20260930T1436Z-merge-request-build-v2-kv-517`.
- **Tests at the head, local, without slow tests:** 1,716 vLLM program, observe and correspondence tests, 43 lint tests and 306 core
  tests pass.
- **No recorded `check` of the head:** say if the train needs one, and I'll record it on a slot you name.
- **build-v2-kv's open PRs:** 1, this one. #587 landed in TTR.
