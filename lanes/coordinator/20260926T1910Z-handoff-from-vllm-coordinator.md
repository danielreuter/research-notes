---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T19:10Z
---
# PR #82 verdict: APPROVE (head `f037f68e`, vllm-vu-export: `Q_word_v1{X,W}` + its width check, opt-in; fine-query plan steps 1–3)

- **Recheck against main `2431e3c1`:** clean. Every ratchet lint runnable without pytest passes on main + #82 (39/39). The lane's tests
  (`r20260926-180827-f206`: the vllm lints, query, program-graph, CLI and exporter) are rc 0. `test_repository` needs a git clone.
- **Scope:** 6 commits, 5 files. `query/word.py` is new (481 lines, under the P10 cap), with `tests/query/test_word.py`. There are
  changes to `pipeline/manifest.py` (+41) and `pipeline/program_graph.py` (+188).
- **The query of record is unchanged:** `Q_module_body_v1` stays the population. In `manifest.py`, the new `word=` parameter defaults
  to `None` in `build` / `build_global` / `build_tp`, and `--word-check` / `VERITY_WORD_CHECK` defaults to off.
  `word_check` only reads the manifest's required values ("the manifest is not touched") and raises a named `QueryRuleViolation`
  only when it's asked to.
- **Record evidence (#101 on L40S, `r20260926-173050-5a18`):** Build, Match and Commit PASS. Program `ccc21347`, manifest `90f81868`
  (7,043 identities, complete) and **run root `7adcef49…` equal the record**. Across the 13 rows, the word check reports no width
  violations.
- **`program_graph.py`** (the visualizer/export graph, off the record path) gains per-group `q_word_v1`, per-edge words/bits,
  `words_per_read` and `ports`.
- **For Daniel, not blocking this merge** (`docs/fine-query-plan.md` §3, §4, §4b): under the partition rule, three places need either
  new committed words or a rule call:
  - the norm scale needs one tapped 32-bit word per norm Call per row (CUDA fused and Triton norms);
  - the MoE router's masked-argmax rounds need a tap, or its body restated;
  - attention's last-block guarded max needs a one-line rule change, no tap.
  These belong to the query-switch decision, which isn't approved.
- Pod `vyv-vu-export-g3` is terminated (about $1). The vLLM guard is tripped at its 18:45Z deadline with no pods, and stays so
  until the next approved run.
