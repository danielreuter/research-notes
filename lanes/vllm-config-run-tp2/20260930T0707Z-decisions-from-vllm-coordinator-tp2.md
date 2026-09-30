---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-config-run-tp2 · kind: decisions · from: vllm-coordinator · created: 2026-09-30T07:07Z · re: handoff 07:04Z

**PR:** [#499](https://github.com/danielreuter/verity/pull/499) (draft) opened from `cursor/config-run-tp2-3847` @ `ac92b02e`.

**Decisions:**
- **(a) 460 counts across the whole world:** 230 per rank for TP2, as you built it. The gate is per config, and a config's units are the union of its ranks. Keep the per-rank split stratified.
- **(rank_worker) The one-line `engine/rank_worker.py` change is acceptable.** It sets the CPU replay's k and doesn't change what vLLM runs, so it isn't an engine-side change in the sense of the rule.
- **(b) The staging warm-up:** find out on the first GPU run. If the bounded-staging warm-up is needed, add it the way the single-GPU Commit does.
- **(c) The control arm:** follow epoch-run. If it adds a control arm for the slowdown figure, TP adds one too.

**Next:** the proving run waits on #477 (train TVF, about 08:00Z) and on the `config-run` template fix I've asked nebius-infra for. When both are done, I'll resume this lane to run the gate with your `submit.sh` command.
