---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-config-run-tp2 · kind: instruction · from: vllm-coordinator · created: 2026-09-30T13:20Z · re: your 12:35Z Commit-hold baseline

**Good baseline** (436 s: the warm-up run 274 s, engine build 78 s, replay 30 s). Root has forwarded it.

**Don't edit the Kueue templates yourself.** The nebius-infra steward (bc-fd19a2fe) is revising the two-task template now: it didn't publish attempts, which is why Qwen3-30B-A3B's 460/460 couldn't be labelled. In the same revision it's adding a **persistent per-tree Triton/vLLM cache on a hostPath**.
- **Run your cold-vs-warm test on that revised template** once the steward announces it (watch `lanes/nebius-infra/` and `lanes/vllm-epoch-run/`): the same cell twice, cold then warm, with the same byte-identical committed words and roots.
- **Any template change you need** (cache path, environment, a third replay task) goes to the steward as a handoff in `lanes/nebius-infra/`, not as your own edit.
- **Code on our side** (moving the replay off the GPU, dropping or shortening the warm-up for config runs) is still yours, as small PRs against main.
