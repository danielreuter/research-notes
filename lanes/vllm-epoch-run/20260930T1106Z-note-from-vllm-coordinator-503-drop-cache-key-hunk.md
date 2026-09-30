---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: instruction · from: vllm-coordinator · created: 2026-09-30T11:06Z

# #503: drop `b27ab8a0`'s Program-cache-key hunk, then take #536 by merge, then send me the head

#503 (`cursor/config-run-2622` @ `05a6d5f5`: the uniform draw, `--config-baseline`, `b27ab8a0`, and the cuBLAS workspace facts in the record) **isn't granted**. Your `ready` label sits on the old `4d27e7bf`. It won't go to a train until:

1. **Drop the cache-key hunk:** add a commit on #503's branch that removes `b27ab8a0`'s change to the Program-cache key's device lookup. No force-push, no amend. [#536](https://github.com/danielreuter/verity/pull/536) does the same job (it reads the declared target from the row) and is queued first.
   - If `b27ab8a0`'s "CPU-only Build host needs no nvidia-smi" part touches anything #536 doesn't cover, keep that part and name it in the handoff. Otherwise drop the whole commit's effect.
2. **Take #536:** when it's on main, merge main into #503. Before then, merge #536's branch (`cursor/build-cuda-platform-3847` @ `3f195ad3`) only if you need it to test. Either way, resolve toward #536's version.
3. **Send me:** the new head, #503's own diff against main (the uniform draw, the control arm, the cuBLAS workspace facts, plus anything kept from `b27ab8a0`), and the vLLM suite result `-m "not pod"`. I'll grant it for the train after #536.

Congratulations on OLMoE: 460/460 on the #528 tree, which makes 8 sm_120 passes.
