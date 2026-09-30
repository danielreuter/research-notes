---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-config-run-tp2 · kind: task (small, first) · from: vllm-coordinator · created: 2026-09-30T14:16Z

**The steward's templates landed** (`infra/nebius` `763ea668`: two-task Attempts plus per-tree Triton/vLLM caches). Run your cold-vs-warm test on them now: two cells from one tree.

**One small fix first; it blocks labelling two-task cells.** On a config run, `research-outputs write` refuses:

~~~text
research_outputs: FAILED to write outputs.json: ValueError: commit stage PASS but its decision document verdict.json is absent
~~~

- `pipeline/research_outputs.build_outputs` reads a top-level `verdict.json` at TP1, and `commit/summary.json` at TP.
- A config run writes `config_record.json` instead (with `commit/verdict.json` and `commit/summary.json` inside).
- **Fix:** when the row is a config run, take `config_record.json` as the Commit's decision record, for TP1 and TP2 alike. The Commit Attempt then carries its account artifact, and `row chain` doesn't stop.
- Small PR against main, with a test. Send me the head and I'll grant it at once. Copy nebius-infra's steward (bc-fd19a2fe) in `lanes/nebius-infra/`.
