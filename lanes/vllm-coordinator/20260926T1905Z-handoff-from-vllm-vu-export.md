---
cursor:
  subagentId: "bc-eab8c043-7f1c-5a4d-802c-0b9aa73f289b"
---

# Handoff from vllm-vu-export: Q_word_v1 steps 1–3 done. PR #82 to merge; two new commitments and one rule call for Daniel (20260926T1905Z)

lane: vllm-vu-export · kind: handoff · from: vllm-vu-export (agent bc-eab8c043) · created: 20260926T1905Z

**Merge request: PR #82** (`cursor/q-word-query-289b`, head `f037f68e`, base `main` `0ceb481d`). Please pass it to the research coordinator. Nothing of record changes: the query of record stays `Q_module_body_v1`, and the check is off by default.

- **The rule** is Daniel's 16:53Z partition: X = 16, or one ≤ 32-bit boundary gate, with ≤ 2-gate recomputes. It lives in `verity_vllm/query/word.py`.
  - `check_query` is wired into `manifest build | build-global --word-check 16/32` (env `VERITY_WORD_CHECK`).
- **program.json** gains per-group `q_word_v1`, per-edge words, bits, `words_per_read` and `ports`, and `varying_calls`.
- **#101 on L40S** (`r20260926-173050-5a18`, `vyv-vu-export-g3`):
  - Build, Match and Commit PASS;
  - Program `ccc21347` and manifest `90f81868` unchanged;
  - **run root `7adcef49…5dec5` == record**;
  - the word check has no violations (294.1 M units, 43.0 M committed interior words).
- **Tests** (`r20260926-180827-f206`): the vllm lints plus the query, program-graph, CLI and exporter tests, rc 0. `test_repository` needs a git clone.
- **Pod:** terminated 18:22Z; about 52 minutes and about $1. Custody verified on all four runs.
- **Findings for Daniel** (`docs/fine-query-plan.md`, §3, §4, §4b):
  1. **Norm scale.** One committed 32-bit word per norm Call per row: 9,471 on #101. It needs taps in the CUDA fused norm and the Triton norm; Gemma's comes from its ATen chain.
  2. **MoE router.** The masked argmax rounds commit 1,074 (OLMoE) or 2,171 (Qwen3-30B) words per token. The options are a tap, or restating the router body.
  3. **Attention.** The FA2 / FA3 stream carries every committed word except the last block's guarded max, one per head and row. The recommended fix is a one-line rule change, no tap change.
- **Counts:** the 13 rows total 163.1 G units and 40.2 G committed interior words (table in §5). **No width violations on any row.**
- The query switch and the re-baseline epoch stay unstarted.
