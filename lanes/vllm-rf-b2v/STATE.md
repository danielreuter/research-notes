---
id: vllm-rf-b2v/state
lane: vllm-rf-b2v
kind: state
updated: 2026-09-25T09:25Z
---
# b2v (one verdict and `properties/` records): state

> **Coordinator, 08:32Z: the 08:24Z pause is CANCELLED.** A slot freed, so continue your lane normally; there is no PAUSE file any more.

Coordinator: vLLM coordinator bc-ba6cec03. Worktree `/Users/danielreuter/projects/verity-wt/rf-b2v`, branch
`lane/vllm-rf-b2v`. **a4 base: 10996616.** Budget $30 of pod spend. Spent: $0.

## Design (settled)
- `check/result.py`: one `CheckResult(name, code: VerificationCode|None, evidence...)`; outcome derived from code
  (ACCEPTED→PASS, None→NOT_RUN, MALFORMED_TRANSCRIPT→INSUFFICIENT_EVIDENCE, other→FAIL); `to_dict` keeps the
  `vllm-verdict/v1` key order so verdict JSON stays byte-identical.
- `commit_verdict.py` split: C1 helpers + rule functions → `check/commit_rules.py`, replay/population helpers →
  `check/replay_rules.py`, `commit_verdict()` → `check/verdict.py` as phase functions (P10 function cap).
- `gates.verdict` (V1) decision moves into `check/verdict.py`; `GateResult.result()` gives a `CheckResult`.
- V5 (`program/kernels/relations.py`) is b1's: deferred. `ops/row_pod.sh` heredoc verdict: a5's, deferred.
- `properties/record.py`: one sealed record type + REGISTRY; every property writer seals; runs cite
  `<row>/properties/*.json` by digest in the verdict (`properties` field omitted when empty, keeps byte identity).
  A cited record that fails adds a note; it does not change the Commit outcome.
- Non-interference world-parametric record from the run's own Match arms (observed vs bare tokens, world from the
  arm) plus, for world 1, the three-process boundary-hash comparison; world > 2 refused.

## Done (commits on lane/vllm-rf-b2v, pushed)
- `d3f04b9d` check: one result type (`check/result.py`); Commit verdict checks are CheckResults with a VerificationCode.
- `003e1506` properties: one sealed record type (`properties/record.py`) that every harness returns; P5 entry point.
- `6e33c657` properties: world-parametric non-interference record; families split out (P10 entry removed).

## Running
- 09:25Z: creating GPU pods `vyv-rf-b2v-l40s` (#101, non-interference world 1, census) and `vyv-rf-b2v-tp2`
  (2x L40S, #70, non-interference world 2).

## Next
1. GPU chains (above); fetch; terminate.
2. Absorb `commit_verdict` (split script) and verdict citations of `properties/` records; commit each.
3. V1 (`gates.verdict`) decision into `check/verdict.py`.
4. Gates (lints, b, a) on CPU pods; direct byte comparison of verdict JSON; READY.md.

## Open questions
- none

## Found, not fixed
- `check/commit_verdict.py` `_is_token_select` broad-except fallback is dead (`query/manifest/format.py` is stdlib-only); removed in the absorption.
