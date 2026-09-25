---
id: vllm-rf-b2v/state
lane: vllm-rf-b2v
kind: state
updated: 2026-09-25T08:58Z
---
# b2v (one verdict and `properties/` records): state

> **Coordinator, 08:32Z: the 08:24Z pause is CANCELLED.** A slot freed, so continue your lane normally; there is no PAUSE file any more.

Coordinator: vLLM coordinator bc-ba6cec03. Worktree `/Users/danielreuter/projects/verity-wt/rf-b2v`, branch
`lane/vllm-rf-b2v`. **a4 base: 10996616.** Budget $30 of pod spend. Spent: $0.

## Design (settled)
- `check/result.py`: one `CheckResult(name, code: VerificationCode|None, evidence...)`; outcome derived from code
  (ACCEPTED→PASS, None→NOT_RUN, MALFORMED_TRANSCRIPT→INSUFFICIENT_EVIDENCE, other→FAIL); `to_dict` keeps the
  `vllm-verdict/v1` key order so verdict JSON stays byte-identical.
- `commit_verdict.py` split: C1 helpers → `check/commit_rules.py`, replay/population helpers →
  `check/replay_rules.py`, `commit_verdict()` → `check/verdict.py` as phase functions (P10 function cap).
- `gates.verdict` (V1) decision moves into `check/verdict.py`; `GateResult.result()` gives a `CheckResult`.
- V5 (`program/kernels/relations.py`) is b1's: deferred. `ops/row_pod.sh` heredoc verdict: a5's, deferred.
- `properties/record.py`: one sealed record type + REGISTRY; every property writer seals; runs cite
  `<row>/properties/*.json` by digest in the verdict (field omitted when empty, keeps byte identity).
- Non-interference world-parametric: world 1 (existing three processes), world 2 (rank hooks + collective
  recorder vs bare), world > 2 refused.

## Done
- worktree created at 10996616.
- survey of V1..V5, properties/, P4/P5/P10/P11 lints, f24 replay_codes, f56 fa_tap_exactness.

## Running
- nothing. No pods.

## Next
1. Commit `check/result.py` + P4 `VERDICT_ALLOWED`.
2. Absorb `commit_verdict` (split script), commit.
3. `properties/record.py`, non-interference world 2, census record, verdict citations; then GPU pods
   (L40S #101, 2x L40S #70).
4. Gates (lints, b, a) on CPU pods; byte comparison of verdict JSON; READY.md.

## Open questions
- none

## Found, not fixed
- `check/commit_verdict.py` `_is_token_select` broad-except fallback is dead (`query/manifest/format.py` is stdlib-only); removed in the absorption.
