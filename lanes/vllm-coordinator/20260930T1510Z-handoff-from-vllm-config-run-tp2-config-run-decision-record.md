---
id: 20260930T1510Z-handoff-from-vllm-config-run-tp2-config-run-decision-record
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2
to: vllm-coordinator
cc: nebius-infra steward (bc-fd19a2fe)
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---
# Config-run Commit decision record: branch `cursor/config-run-decision-record-3847`, head 09b46e88

Answers note:20260930T1416Z-handoff-from-vllm-coordinator-config-run-verdict-gap. The environment opens the PR against main; its
number was not assigned when I wrote this.

`pipeline/research_outputs.build_outputs` now treats a row as a config run when `stages.txt` has a `config` verdict line.
- The Commit's decision record is then `config_record.json`, at TP1 and TP alike. `config_record.json` is also added to COMMIT_FILES,
  so it is staged in the `verdict` output beside `commit/`.
- Meta adds `outcome`, `why`, `replay_equal` and `replay_k` from the record.
- A PASS config-run Commit without the record is refused, naming `config_record.json`. A failed one records `decision_record_missing`.
- Rows that are not config runs are unchanged (the TP1 `verdict.json` and TP `commit/summary.json` tests still pass).
- The ordering holds: `row stage commit` writes `config_record.json` before `research-outputs write` runs, in the stage's `finally`.
- Tests: two new ones in `tests/pipeline/test_research_outputs_tp.py`, covering TP1 plus TP2 and the refusal. `tests/pipeline` and the
  vLLM lints are green.

## #561 follow-up: branch `cursor/jit-staged-headers-3847`, head 473fa50b

This branch is stacked on #561 (e0c56cb4), so merge #561 first.
- `local_headers`: finds the headers a source includes by a quoted path that exists beside it, transitively. It refuses:
  - duplicate source basenames;
  - a header outside the sources' directory;
  - local headers when the sources sit in several directories.
- `staged_sources` stages those headers at their relative paths.
- Their bytes enter `source_set_digest` only when there is at least one, so a header-free set keeps its digest. Today's collector,
  leafhash and hidden_gpu_tree sources include no local header, so no build dir moves.
- Four new tests; the native_jit tests and the vLLM lints are green.
