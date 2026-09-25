---
id: vllm-rf-b2v/state
lane: vllm-rf-b2v
kind: state
updated: 2026-09-25T11:13Z
---
# b2v (one verdict and `properties/` records): state

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T14:00Z (7 AM PT)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

> **Coordinator, 08:32Z: the 08:24Z pause is CANCELLED.** A slot freed, so continue your lane normally; there is no PAUSE file any more.

Coordinator: vLLM coordinator bc-ba6cec03. Worktree `/Users/danielreuter/projects/verity-wt/rf-b2v`, branch
`lane/vllm-rf-b2v`. **a4 base: 10996616.** Budget $30 of pod spend. Spent so far (est., 11:13Z): ~$5.6
(l40s $1.09/h since 09:28Z, tp2 $2.18/h since 09:30Z).

## Design (settled)
- `check/result.py`: one `CheckResult(name, code: VerificationCode|None, evidence...)`; outcome derived from code
  (ACCEPTED→PASS, None→NOT_RUN, MALFORMED_TRANSCRIPT→INSUFFICIENT_EVIDENCE, other→FAIL); `to_dict` keeps the
  `vllm-verdict/v1` key order so verdict JSON stays byte-identical.
- `commit_verdict.py` split: per-run rules + C1 helpers → `check/commit_rules.py`; C2 rules, form (B) coverage,
  execution extent → `check/c2_rules.py`; `commit_verdict()` → `check/verdict.py` as three phase functions (P10 caps).
- `gates.verdict` (V1) decision moves into `check/verdict.py`; `GateResult.result()` gives a `CheckResult`.
- V5 (`program/kernels/relations.py`) is b1's: deferred. `ops/row_pod.sh` heredoc verdict: a5's, deferred.
- `properties/record.py`: one sealed record type + REGISTRY; every property writer seals; runs cite
  `<row>/properties/*.json` by digest in the verdict (`properties` field omitted when empty, keeps byte identity).
  A cited record that fails adds a note; it does not change the Commit outcome (P5: properties are cited, not per-run gates).
- Non-interference world-parametric record from the run's own Match arms (observed vs bare tokens, world from the
  arm) plus, for world 1, the three-process boundary-hash comparison; world > 2 refused.

## Done (commits on lane/vllm-rf-b2v, pushed)
- `d3f04b9d` check: one result type (`check/result.py`); Commit verdict checks are CheckResults with a VerificationCode.
- `003e1506` properties: one sealed record type (`properties/record.py`) that every harness returns; P5 entry point.
- `6e33c657` properties: world-parametric non-interference record; families split out (P10 entry removed).
- `66eaaa50` check: verdict.py absorbs commit_verdict (commit_rules.py, c2_rules.py; importers' import lines only;
  allowlist entries moved/deleted; verdict.py P10 cap 1401 → 850).
- `5483d13b` check: the verdict cites the run's property records by digest (P4 contract gains properties.record;
  registry test in tests/check/test_verdict.py; verdict.py cap 850 → 855).
- `c461f86d` check: the Match gates' word is `verdict.match_verdict` over CheckResults (`GateResult.result()`; equivalence
  test over 800 status combinations; gates.py stays at 1397; verdict.py cap 855 → 866).
- `824a9924` properties: holdout reads `check.gates.HOLDOUT_GATES` (P4 allowlist −6 g-literal entries).
- `fd9220c9` / `95515e42` / `8d847755`: lint fixes (by-name entries follow the families split; P8 claim wording; P10 import lines).

## Running (11:13Z)
- **Lints at 824a9924 FAILED (4 tests; caught on the pod, pytest is not allowed on the laptop):** by-name entries had not
  followed the families split; P8 `FlashAttention` literal in the registry claim; P10 +1 line in `pipeline/commit.py` and
  `pipeline/tp/commit.py` (import lines). Fixed in `fd9220c9`, `95515e42`, `8d847755` (no allowlist grows: 9 by-name
  entries moved/re-pointed; P10 main cap 1914 → 1913). **Lints at 8d847755: 45 passed** (`lint_head2`, L40S, 11:01Z).
- `vyv-rf-b2v-l40s`: #101 chain done (build PASS, match PASS, props records ok, **commit PASS** 10:42:54Z; program
  ccc213475e7c4eed…, manifest 90f8186879d5035a…, run root 7adcef49… = record; verdict cites census 33a41e9c… and
  noninterference be83f678…). Byte check: from_record at 8d847755 == at the run's tree 5483d13b (same inputs, sha
  bdf5a75e…); base 10996616 differs only by the `properties` citations; the stored verdict.json differs from today's
  rebuild only by `compat.stage_line`/`stage_outcome` (stages.txt got the commit line after the verdict was written).
  Gate (b): `b_base` (10996616) running in `r20260925-104642-9085`; `b_head` (824a9924) killed by pid (stale);
  `b_head2` (8d847755) `r20260925-110128-3b30` since 11:01Z. Trees built by `evidence/mktree.sh` (blob-verified).
- `vyv-rf-b2v-tp2`: #70 build PASS (64bee6d6e8264461), manifest 1bb40895671dd791 (= record); match capture/check pass,
  fold FAIL 10:49:59Z (rank-0 fold errors 4096, unresolved 3544; record: fold_binding False) → run state failed as
  expected. World-2 record `<row>/properties/noninterference.json` ok 442979b3… (8/8 equal); worlds 3, 4 refused.
  Commit at 66eaaa50 `r20260925-111138-272a` (worktree `/tmp/b2v-66e`, remove at end) since 11:11Z; then from-record at 8d847755.
  Prefetch 26 ok / 0 FAIL, **key deleted 10:52:13Z** (no AWS_ vars in the gate env). Gate (a) T0,T1 at 824a9924 in
  `r20260925-105008-bca1` (two processes, since 10:52Z). Verdict bytes: 10 rows with a Commit record, from_record under
  10996616 == under 824a9924 == under 8d847755 (`diff -r` exit 0); 3 rows have no commit/verdict.json. Targeted gate (a)
  `-k "verdict or commit_summary"` at 8d847755 `r20260925-110440-71eb`.
- Spend (est., 11:13Z): ~$5.6.

## Next
1. #70 commit → from-record at 8d847755 (citation of 442979b3…) → compare legs with the record.
2. Gate (b) jdiff b_base vs b_head2; gate (a) jdiff vs a23b; fetch; terminate; READY.md.

## Open questions
- none

## Found, not fixed
- `check/commit_verdict.py` `_is_token_select` broad-except fallback was dead (the family is always a str); removed in the absorption (P7, A61 entries deleted).
- `ops/pod_bootstrap.sh:119` defaults `MAX_JOBS` to `nproc`; on a 128-vCPU L40S host the FA2 tap build is OOM-killed. The tap scripts default to 32. (a5's file.)
- Docstrings still say `commit_verdict._x` for helpers now in `check/c2_rules.py`: `check/replay/sampled_replay.py:2088`, `check/replay/replay_codes.py:10,25,27` (b1's), `pipeline/tp/commit.py:14,191,204` (a5's), `tests/pipeline/test_tp2_commit_query_population.py:2`.
- `check/c2_rules.py:288` f-string without placeholders (pre-existing in commit_verdict.py).
