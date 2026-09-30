---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T08:30Z

**Run branch `cursor/coverage-v0-2622` @ `2847317c` is on origin.** It is `cursor/coverage-premerge-8ee1` `598c2a53` merged in, with your side taken for `targets.py`, plus the twins, #503's commits and the Gumbel variant.
- **First sm_120 pass:** SmolLM2-135M, 460/460 units bit-exact on a uniform draw. The slowdown is 1.54x prefill and 1.65x decode. It ran on the earlier tree `5bf96cd3` (#477 #481 #469) and is labelled with that prefix; it re-runs on `2847317c` because #486 changes FA2.
- **Unsupported:** Pythia-160M, whose Build refuses `aten.layer_norm.default` (no registered kind). The two Qwen2.5 twins, pending #483.
- **The queue:** the old tree's jobs are cancelled. Ten cells are being resubmitted smallest first on `config-run-row`. FP8 and MoE go in once the small cells are admitted.
