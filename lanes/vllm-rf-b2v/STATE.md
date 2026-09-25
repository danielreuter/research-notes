---
id: vllm-rf-b2v/state
lane: vllm-rf-b2v
kind: state
updated: 2026-09-25T10:42Z
---
# b2v (one verdict and `properties/` records): state

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T14:00Z (7 AM PT)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

> **Coordinator, 08:32Z: the 08:24Z pause is CANCELLED.** A slot freed, so continue your lane normally; there is no PAUSE file any more.

Coordinator: vLLM coordinator bc-ba6cec03. Worktree `/Users/danielreuter/projects/verity-wt/rf-b2v`, branch
`lane/vllm-rf-b2v`. **a4 base: 10996616.** Budget $30 of pod spend. Spent so far (est., 10:37Z): ~$3.7
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

## Running
- `vyv-rf-b2v-l40s` (clgfo42ik8b60d, 1x L40S, cgroup 62 GB): first bootstrap `r20260925-093143-cafd` FAILED rc=3 (FA2 tap
  build OOM-killed: `ninja -j 128`, exit 137; pod_bootstrap.sh defaults MAX_JOBS=nproc=128). Rerun MAX_JOBS=32
  `r20260925-095828-2f7d` BOOTSTRAP-OK 10:04Z. #101 chain `r20260925-101202-5fdc` at 5483d13b (`evidence/chain101.sh`):
  build PASS 10:14Z (manifest 90f8186879d5035a), match PASS 10:35Z; props rc=0 10:37Z: `<row>/properties/`
  noninterference.json ok digest be83f678… (world 1, tokens equal, boundary hashes 1088/1088), census.json ok digest
  33a41e9c…; commit stage running since 10:37Z.
- `vyv-rf-b2v-tp2` (qxi7kk83o1oxz4, 2x L40S, cgroup 377 GB): BOOTSTRAP-OK 09:56Z. #70 build,match `r20260925-095754-ee6c`
  at 66eaaa50 (PAIRS=1): build PASS 10:20Z digest 64bee6d6e8264461, manifest 1bb40895671dd791 (both = record); match
  capture+check pass 10:37Z; fold running. Then noninterference.record(world 2) → `<row>/properties/`, commit at 66eaaa50, then
  `check.verdict from-record` at the head (tp_stage.sh writes no vllm-verdict/v1).
- No CPU pod available (10:25Z: cpu3m x64/x32, cpu5m x64/x32, cpu3g x16 all "no instances available"). Plan: lints, unit
  tests and gate (b) head+base on the L40S pod after #101 (GPUs hidden, `evidence/l40s_gates.sh`); gate (a) T0,T1 and the
  verdict byte A/B on the TP2 pod (GPUs hidden, nice), as f56 did. Trees `/workspace/{head,base}` syncing to both pods.

## Next
1. GPU chains (above); fetch; terminate.
2. Gates (lints, b, a) as above; direct byte comparison of verdict JSON (`evidence/verdict_bytes.py`, base vs head); READY.md.

## Open questions
- none

## Found, not fixed
- `check/commit_verdict.py` `_is_token_select` broad-except fallback was dead (the family is always a str); removed in the absorption (P7, A61 entries deleted).
- `ops/pod_bootstrap.sh:119` defaults `MAX_JOBS` to `nproc`; on a 128-vCPU L40S host the FA2 tap build is OOM-killed. The tap scripts default to 32. (a5's file.)
- Docstrings still say `commit_verdict._x` for helpers now in `check/c2_rules.py`: `check/replay/sampled_replay.py:2088`, `check/replay/replay_codes.py:10,25,27` (b1's), `pipeline/tp/commit.py:14,191,204` (a5's), `tests/pipeline/test_tp2_commit_query_population.py:2`.
- `check/c2_rules.py:288` f-string without placeholders (pre-existing in commit_verdict.py).
