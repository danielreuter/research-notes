---
id: vllm-rf-b2v/ready
lane: vllm-rf-b2v
kind: ready
status: draft
created: 2026-09-25T11:30Z
updated: 2026-09-25T11:30Z
---
# vllm-rf-b2v READY: one verdict and `properties/` records (SYNTHESIS §6 B2, verdict part)

- **Branch:** `lane/vllm-rf-b2v` (pushed). **Head:** `8d847755`. **Base:** `10996616` (a4's head, not merged).
- 10 commits, 48 files (all under `integrations/vllm`), +1,889 / -1,400 against `10996616`. Nothing under `packages/verity`.
- Gates: lints 45/45 at `8d847755`; gate (b) head vs base on one pod: GATE_B_SUMMARY; gate (a) T0,T1: GATE_A_SUMMARY; GPU
  rows #101 (world 1, L40S) and #70 (world 2, 2x L40S) reproduce the record's digests and cite their `properties/` records.

## Gate evidence

Environment on both pods (`ops/pod_bootstrap.sh`, venv `/workspace/venv312`): Python 3.12.14, torch 2.13.0+cu129, vLLM
0.28.1rc1.dev472+gd9105ea80, pytest-xdist 3.8.0. No CPU pod was available (10:25Z: cpu3m x64/x32, cpu5m x64/x32, cpu3g x16 all
"no instances available"), so the CPU gates ran on the two GPU pods with `CUDA_VISIBLE_DEVICES=""`, niced, and (gate (a))
`oom_score_adj` 1000 so the GPU rows kept priority.

| pod | RunPod | used for |
|---|---|---|
| `vyv-rf-b2v-l40s` (`clgfo42ik8b60d`) | 1x L40S, 128 vCPU, cgroup 62 GB | row #101 (world 1), census, lints, gate (b) head and base |
| `vyv-rf-b2v-tp2` (`qxi7kk83o1oxz4`) | 2x L40S, 128 vCPU, cgroup 377 GB | row #70 (world 2), gate (a) T0,T1, verdict byte A/B |

**Trees.** Uploading a 250 MB tree from the laptop ran at ~300 KB/s, so the gate trees were built on the pods by
`evidence/mktree.sh`: the tracked files of a tree already on the pod (a `research run` source tree or a synced tree), plus
`git diff --binary A B` applied with `git apply`, then **every file's git blob id checked against `git ls-tree -r B`** (0
mismatched, 0 extra; the listings and patches are in `evidence/trees/`). Each tree's commit is in its `.b2v-tree` or
`.research-source.json` and printed in every gate `.status`.

### (1) Lints

`python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q`

- **At `8d847755`: 45 passed** (`lint_head2.log`/`.xml`, L40S, 11:01Z).
- At `824a9924` they failed (4 tests, `lint_head.log`), which is how the last three commits came about: the by-name entries had not
  followed the families split (`6e33c657`), the registry claim carried a `FlashAttention` literal (P8), and the two importers
  of `commit_verdict` in `pipeline/` each grew by one line (P10). pytest isn't allowed on the laptop, so this was the first run.
- **No allowlist grows** (entries base -> head): P4 64 -> 58, P7 355 -> 354, P10 76 -> 74 (sum of caps 67,464 -> 65,894), P11
  715 -> 713, by-name 219 -> 218; every other allowlist unchanged. P4's -6 are g-literal entries; see Deferred for the rest.

### (2) Gate (b), full suite

`OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile` (`evidence/gate_b.sh`, a1's with the log
directory moved and GPUs hidden), both trees on the L40S pod, overlapping in time.

GATE_B_DETAIL

### (3) Gate (a), regression T0 + T1

`VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression`
(`evidence/gate_a.sh`), TP2 pod.

GATE_A_DETAIL

- **Fixtures and the credential.** One key, minted on the laptop at 10:43Z (`--ttl 3h --permission object-read-only --via
  local`) and piped into `/root/r2ro.env` on the TP2 pod, never echoed (only its variable names were listed). `prefetch.sh`
  fetched all 26 artifacts (0 failures) and deleted the file at 10:52:13Z; `tp2_gates.sh` refused to start while it existed and
  logged 0 `AWS_*` variables in the gate environment. No key reached the L40S pod.

### (4) The verdict JSON of every regression row

- **Gate (a) T0's `verdict` and `commit_summary` checks cover it**: `verdict` rebuilds each row's `vllm-verdict/v1` in memory
  with `verdict.from_record` (the rows carry no `verdict.json` of record) and grades it against the v1 facts; `commit_summary`
  lifts `commit/verdict.json`. At `8d847755` (`a_head2_vc`, `-k "verdict or commit_summary"`): **20 passed, 6 skipped** (14 s),
  the same 20 that pass in a23b's base run.
- **Direct byte comparison** (`evidence/verdict_bytes.py`, TP2 pod): for each of the **10 rows with a Commit record**,
  `from_record(row).dumps()` under `10996616`, under `824a9924` and under `8d847755`. **All 10 byte-identical** across the three
  trees (`diff -r` exit 0; `verdict_bytes.{base,head,head2}.txt` list the sha256 per row). The other 3 rows (the OLMoE and
  Qwen3-30B-A3B TP2 rows and the SmolLM2 B=16 row) have no `commit/verdict.json`. No regression row has `properties/`, so the new key is absent.

### (5) GPU acceptance

**Row #101** (`llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`, L40S, world 1), one tree
(`5483d13b`) for every stage, `evidence/chain101.sh`, run `r20260925-101202-5fdc`:

| | this run | record |
|---|---|---|
| build | PASS 10:14Z | |
| manifest_digest | `90f8186879d5035a…` | `90f8186879d5035a` |
| match | PASS 10:35Z | |
| commit | **PASS** 10:42:54Z (295 s), every check group PASS | PASS |
| program_digest | `ccc213475e7c4eed…` | `ccc213475e7c4eed` |
| run root | `7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5` | same |

- **Non-interference, world 1**: `<row>/properties/noninterference.json`, `ok`, digest
  `be83f67833921627f88647eaaddb87f3f3e52698fac1fe76292a4736c7861361`. The run's own Match arms (`match/capture/tokens.json`
  observed, `match/control/tokens.json` bare, both world 1): tokens equal (1 request); plus the three-process boundary-hash
  comparison (`properties.noninterference --compare`): PASS, 1,088 / 1,088 hashes equal over 32 steps and 16 layers.
- **Census** (needs the GPU; same pod): `<row>/properties/census.json` = the sealed `census --reconcile` record, `ok`, digest
  `33a41e9ce973d4046f4c0d877b4dcbd429d5844d730cb4eff8a750a28e2fec10`.
- **The run cites both by digest**: the commit stage's `from-record` wrote `$D/verdict.json` with
  `properties: [census 33a41e9c…, ok; noninterference be83f678…, ok]` and no notes.
- **Byte check at the final head**: `from_record` on this row's evidence gives byte-identical text under the run's tree
  `5483d13b` and under `8d847755` (sha256 `bdf5a75e…`). Under the base `10996616` the text differs only by the appended
  `properties` list. The stored `verdict.json` differs from today's rebuild only by `compat.stage_line` / `stage_outcome`:
  `row_pod.sh` appends the commit line to `stages.txt` after writing the verdict.

**Row #70** (`olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager`, 2x L40S, world 2), every stage at
`66eaaa50` (`tp_stage.sh`, `WORLD=2 NCCL_P2P_DISABLE=1 PAIRS=1`), runs `r20260925-095754-ee6c` (build, match) and ROW70_COMMIT_RUN:

| | this run | record |
|---|---|---|
| build | PASS 10:20Z | |
| program_digest | `64bee6d6e8264461` | `64bee6d6e8264461` |
| manifest_digest | `1bb40895671dd791` (357,796 identities, complete) | `1bb40895671dd791` |
| match | capture + check pass (8,448 collectives, 0 mismatches, tokens equal); fold FAIL (rank 0 errors 4,096, unresolved 3,544) | fold_binding False |
ROW70_ROWS

- **Non-interference, world 2**: `<row>/properties/noninterference.json`, `ok`, digest
  `442979b3aa090ccc79d57b35116934c2fe4d78e40ad387462913514438471a7b`: both arms taken at world 2 (`tp: 2`), 8 / 8 requests
  equal. Worlds 3 and 4 raise `ValueError` ("tensor-parallel world 3 refused: non-interference is recorded at worlds (1, 2)").
ROW70_CITE

## What changed

- **One result type** (`d3f04b9d`): `check/result.py`, `CheckResult(name, code: VerificationCode | None, ...)`. The outcome is
  derived from the code: ACCEPTED -> PASS, None -> NOT_RUN, MALFORMED_TRANSCRIPT (= `MISSING_INPUT`) -> INSUFFICIENT_EVIDENCE,
  any other code -> FAIL. `to_dict` keeps the `vllm-verdict/v1` key order. The Commit verdict's checks are CheckResults.
- **One sealed record type** (`003e1506`): `properties/record.py`, `PropertyRecord` + `seal` (`ok`, `digest` = sha256 of the
  canonical JSON without `digest`) + `REGISTRY` (one `Property` per 5.1 property: fa_tap_exactness, noninterference, census,
  golden, holdout, difftest, quarantine_lint, protected). Every property harness returns a sealed record. `records_of(row)`
  reads `<row>/properties/*.json`.
- **World-parametric non-interference** (`6e33c657`, `fd9220c9`): `noninterference.record(match_dir, world, *, run, hashes)`
  compares the run's observed Match arm with its bare arm (per request: id, prompt ids, generated ids), takes the world from
  the arms and refuses one that isn't in `WORLDS = (1, 2)`; at world 1 it folds in the boundary-hash report. The Gemma-2 and
  GPT-NeoX boundary helpers moved to `properties/noninterference_families.py` (noninterference.py 803 -> 765 lines, its P10
  entry deleted), with `FINAL_NORM_MODULES`, and their by-name entries followed them (`fd9220c9`).
- **verdict.py absorbs `commit_verdict`** (`66eaaa50`, `8d847755`): `check/commit_verdict.py` is gone. The per-run rules and C1
  helpers are in `check/commit_rules.py`, the C2 rules (form (B) coverage, execution extent) in `check/c2_rules.py`, and the
  decision `commit_verdict()` in `check/verdict.py` as three phases (`_c1_verdict`, `_c2_verdict`, `_after_release_verdict`).
  verdict.py: 1,401 -> 866 lines. Importers changed their import lines only (tests, `pipeline/commit.py`,
  `pipeline/tp/commit.py`); `pipeline/commit.py` now takes `required_classes_default` from its top-level import.
- **Runs cite property records by digest** (`5483d13b`): `from_record` appends `properties` (one citation per
  `<row>/properties/*.json`: name, schema, digest, ok, source, problems) and a note for a record that fails or is malformed. The
  key is omitted when a row has no records, so every existing verdict text is unchanged. A citation never changes the outcome:
  properties are cited records, not per-run gates (P5). P4's allowed set gains `properties.record`.
- **V1, the Match gates' word** (`c461f86d`): `gates.verdict()` returns `verdict.match_verdict([r.result() ...], GATES)`;
  `GateResult.result()` maps pass / fail / skipped / other to ACCEPTED / CHECK_MISMATCH / None / MISSING_INPUT. A test checks
  it against the old status rule over all 800 status combinations of the frozen gates.
- **Holdout** (`824a9924`): `properties/holdout.py` reads `check.gates.HOLDOUT_GATES` instead of `G`-literals (P4 -6).
- **Lint fixes** (`fd9220c9`, `95515e42`, `8d847755`): above.

## What didn't change

- No Program digest, manifest digest, commitment root, leaf id or regression verdict: #101 and #70 reproduce the record's
  digests and run root; the 10 regression verdict texts are byte-identical at base and head. The runs' code identity is the
  tree's git sha (`source_identity.json`); no hashed code-identity digest is in the verdict.
- The Commit outcome rule: `commit_verdict` returns what it returned (the gate (a) `verdict` / `commit_summary` checks and
  the byte A/B), including on #57, the negative.
- One behaviour change in V1, unreachable today: a frozen gate reporting a status other than pass / fail / skipped (e.g.
  `unknown`) made the Match verdict ACCEPTED before and INCOMPLETE now. No frozen gate returns such a status.

## Deferred

- **`ops/row_pod.sh:686-800`, the heredoc verdict** (a5's): folds into `check/verdict.py` after a5 moves it into the CLI.
- **`pipeline/tp/match.py` part 3** (a5's) still compares instrumented and control tokens itself; `noninterference.token_parity`
  is the same rule, and the call site switches when a5's pipeline changes land.
- **A `check_properties` runner** that writes the records at the stage (a5's pipeline): here `evidence/chain101.sh` and a
  one-liner wrote them into `<row>/properties/` before the Commit.
- **V5** (`program/kernels/relations.py`, b1's).
- **P4, the rest**: the 11 reason-prefix entries are in b1's `check/replay/` and `program/kernels/`, b4's `engine/` and
  `program/frontend/`; the remaining g-literal / g-identifier entries are the gate ids themselves in `check/gates.py`,
  `check/match/global_match.py`, `check/executed_prefix.py` (a G-key rename, C3) and in `pipeline/` (a5's); the 2 verdict-import
  entries of `c2_rules.py` (`check.replay.replay_codes`, `query.manifest.format`) wait for b1 and c4ir.

## Rebase notes

- Onto `origin/main` when a4 merges: `git rebase --onto origin/main 10996616 lane/vllm-rf-b2v`, then `--force-with-lease`.
- Conflict risk: `pipeline/commit.py` (476-477, 1315) and `pipeline/tp/commit.py` (199, 313-314) import lines, a5's files;
  `tests/lint/allowlists/*.json` and `tests/by_name_allowlist.json` (moved entries); `check/replay/*` docstrings still say
  `commit_verdict._x` (b1's).

## Found, not fixed

- `ops/pod_bootstrap.sh:119` defaults `MAX_JOBS` to `nproc`; on the 128-vCPU L40S host the FA2 tap build was OOM-killed
  (`ninja -j 128`, exit 137, the pod's one OOM kill). `MAX_JOBS=32` worked. (a5's file.)
- Gate (b) writes into the tree it tests: it rewrote 31 tracked files under `docs/data/ref-prims/` and left 3 new JSON files and
  3 `.so` builds (+ locks) under `program/kernels/cpp/build/`. A tree that ran gate (b) no longer matches its commit.
- Docstrings still say `commit_verdict._x` for helpers now in `check/c2_rules.py`: `check/replay/sampled_replay.py:2088`,
  `check/replay/replay_codes.py:10,25,27` (b1's), `pipeline/tp/commit.py:14,191,204` (a5's),
  `tests/pipeline/test_tp2_commit_query_population.py:2`.
- `check/c2_rules.py:288` f-string without placeholders (was in `commit_verdict.py`).
- `check/commit_verdict.py`'s `_is_token_select` broad-except fallback was dead (the family is always a str); removed (P7 and
  its A61 entry deleted).
- `research run --cwd source` runs from the source root when launched outside the source's `integrations/vllm`; the relative
  `verity_vllm/ops/tp_stage.sh` then isn't found (runs `r20260925-111138-272a`, `r20260925-111454-b341`, both failed at once).
  `--cwd source/integrations/vllm` works.
