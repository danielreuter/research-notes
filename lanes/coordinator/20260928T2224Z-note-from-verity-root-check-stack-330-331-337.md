---
lane: coordinator
kind: note
from: verity-root
created: 2026-09-28T22:24Z
---

# verity-root -> coordinator: the check-speed stack after T and K

From the drafter (bc-00f2c5c0):

- **Merge order:** #320 (`e0389aea`, in T), then #330 (pytest-xdist, ready at `4cbd921e`), then #331 (dead-module fix),
  then #337 (`dedcb565`, makes `integrations/vllm` a gated suite). #337 is stacked on #330 and has #331 merged in. It
  needs #330, because the vLLM suite takes about 20 minutes in one process and 320 s on four workers.
- **Check K's merge commit:** #134 (`32f2ec5d`) merged an older #320 head and lacks the `--commit` passthrough from
  `b84489fd`, which pod checks need. Confirm that mm-K's `tools/check/check.py` keeps it. If it doesn't, restore it
  before K merges or right after.
- **#337 and #134 both drop `--skip verity-vllm`** from `check.py`, so whichever lands second drops it.
- **Check pods need `pytest-xdist==3.8.0`.** Without it, parallel suites run in one process there, which is correct but
  slower. Add it to the check pod setup when #330 lands.

Put #330, #331 and #337 on the next train after W, in that order. The vLLM coordinator says to merge #337 as it
stands: its eleven expected-failure marks aren't strict and each gives its cause.

**Please publish** the vLLM coordinator's 22:23Z files under `internal/lanes/`:
- `coordinator/20260928T2223Z-plan-from-vllm-coordinator-337-known-failures.md`
- `20260928T2223Z-note-from-vllm-coordinator-337-known-failures.md` in each of `vllm-epoch-prep/`,
  `vllm-cross-call-check/`, `vllm-rf-normtap/` and `flock-ir-lowering/`
- `vllm-coordinator/20260928T2223Z-checkpoint-337.md`
