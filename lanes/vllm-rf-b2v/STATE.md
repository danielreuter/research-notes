---
id: vllm-rf-b2v/state
lane: vllm-rf-b2v
kind: state
updated: 2026-09-25T12:15Z
---
# b2v (one verdict and `properties/` records): state

> **COORDINATOR, 12:26Z, URGENT (laptop disk at 1.5 GiB):** STOP `research fetch --all` and every other laptop-side fetch or copy of run outputs, now. Launch new runs with `research run --on ... --custody-r2`: the pod publishes the attempt and every run file to R2 itself, and the pod guard accepts that. Inspect results on the pod (ssh) or read them from R2; plain `research fetch {run}` is for status only. Keep XML and evidence in your notes under about 5 MB. Remove local copies you already fetched only once R2 has them.

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T15:30Z (8:30 AM PT; updated 11:31Z)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

> **Coordinator, 08:32Z: the 08:24Z pause is CANCELLED.** A slot freed, so continue your lane normally; there is no PAUSE file any more.

Coordinator: vLLM coordinator bc-ba6cec03. Worktree `/Users/danielreuter/projects/verity-wt/rf-b2v`, branch
`lane/vllm-rf-b2v`. **a4 base: 10996616.** Budget $30 of pod spend. Spent so far (est., 11:33Z): ~$6.6
(l40s $1.09/h 09:28Z-11:27Z, terminated; tp2 $2.18/h since 09:30Z).

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

## Running (12:15Z)
- **Lints at 8d847755: 45 passed** (`lint_head2`, L40S). The failures at 824a9924 were fixed in `fd9220c9`, `95515e42`,
  `8d847755` (no allowlist grows).
- **Gate (b) done** (L40S): head `8d847755` 31F/3662P/306S/6xF (4005) vs base `10996616` 32F/3646P/306S/6xF (3990);
  jdiff exit 0: no new failure/skip/skip reason, 15 new tests pass, none deleted/renamed; sigint test failed -> passed.
- **#101 done** (L40S, world 1): commit PASS; program/manifest/run root = record; verdict cites census 33a41e9c… and
  noninterference be83f678… (ok). **L40S pod terminated 11:27:26Z**, evidence in `evidence/l40s/`, `evidence/row101/`.
- `vyv-rf-b2v-tp2`: #70 build/manifest = record, fold FAIL as recorded, world-2 record 442979b3… ok. Commit at 66eaaa50
  `r20260925-111729-3301` (pair 0 instrumented + finalize; the record's took ~90 min). **Gate (a) done** (824a9924,
  `r20260925-105008-bca1`): 73 passed / 85 skipped of 158 = a23b test by test; jdiff exit 1 only on 2 skip texts renamed by
  `5cc0506e` (before the base: `row_pod_tp2.sh` -> `tp_stage.sh`). Outputs in `evidence/tp2/gates/`. From-record at 8d847755 on
  #70 before the commit: NOT_RUN, cites noninterference 442979b3… ok.
  Verdict bytes: 10 rows with a Commit record identical under 10996616 / 824a9924 / 8d847755. Targeted gate (a)
  `verdict or commit_summary` at 8d847755: 20 passed, 6 skipped. Key deleted 10:52:13Z.
- READY.md drafted (gate (a) and #70 commit placeholders).

## Next
1. #70 commit -> from-record at 8d847755 (citation of 442979b3…) -> compare legs with the record.
2. Gate (a) jdiff vs a23b; fetch TP2 evidence and runs; terminate TP2; remove /tmp worktrees; READY.md final.

## Open questions
- none

## Found, not fixed
- `check/commit_verdict.py` `_is_token_select` broad-except fallback was dead (the family is always a str); removed in the absorption (P7, A61 entries deleted).
- `ops/pod_bootstrap.sh:119` defaults `MAX_JOBS` to `nproc`; on a 128-vCPU L40S host the FA2 tap build is OOM-killed. The tap scripts default to 32. (a5's file.)
- Docstrings still say `commit_verdict._x` for helpers now in `check/c2_rules.py`: `check/replay/sampled_replay.py:2088`, `check/replay/replay_codes.py:10,25,27` (b1's), `pipeline/tp/commit.py:14,191,204` (a5's), `tests/pipeline/test_tp2_commit_query_population.py:2`.
- `check/c2_rules.py:288` f-string without placeholders (pre-existing in commit_verdict.py).
