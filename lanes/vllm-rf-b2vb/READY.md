---
id: vllm-rf-b2vb/ready
lane: vllm-rf-b2vb
kind: ready
status: final
created: 2026-09-25T11:30Z
updated: 2026-09-25T14:40Z
---
# vllm-rf-b2vb READY: one verdict and `properties/` records (SYNTHESIS §6 B2, verdict part)

b2vb succeeds b2v (agent bc-7d05cc29, hung at the 12:30Z host disconnect) from its pushed head `8d847755`. b2vb added no code:
it finished #70 (world 2) and its Commit comparison, the verdict A/B on #70, custody of the TP2 pod's runs, and this file. Evidence
added by b2vb is in `vllm-rf-b2vb/evidence/`; b2v's is in `vllm-rf-b2v/evidence/`.

- **Branch:** `lane/vllm-rf-b2vb` (pushed). **Head: `ed8f6625`**, rebased (14:36Z, no conflicts) with `git rebase --onto
  origin/main 10996616` onto **main `33e4d8d1`** (a4 merged). Before the rebase the head was **`8d847755`** on `10996616`; the gate
  evidence below was taken there. It carries over: `git diff 8d847755 ed8f6625 -- integrations/vllm packages/verity` is empty, and
  main's `integrations/vllm` and `packages/verity` equal `10996616`'s (coordinator 14:20Z).
- 10 commits, 48 files (all under `integrations/vllm`), +1,889 / -1,400 against main (and against `10996616`). Nothing under `packages/verity`.
- Gates: lints 45/45 at `8d847755`; gate (b) head vs base on one pod: no new failure / skip / skip reason, 15 new tests pass;
  gate (a) T0,T1: 73 passed / 85 skipped of 158, test by test as a23b's (no outcome change; two skip texts renamed before the base).
- Acceptance: the verdict JSON is byte-identical at base and head for the 10 regression rows with a Commit record, and for #101 and
  #70 apart from the appended `properties` citation. Row #101 (world 1, L40S) equals the record: program, manifest, run root, PASS.
  Row #70 (world 2, 2x L40S) equals the record: program, manifest, tp run root `0b91229f…`, FAIL, and 32/32 Commit fields against f1's
  base Commit of record. Each row cites its non-interference record by digest (`be83f678…` world 1, `442979b3…` world 2).
- All pods terminated (TP2 at 14:31Z after its runs went to R2). Spend about $13.1 of $30.

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

- **At `8d847755` (head): 31 failed, 3,662 passed, 306 skipped, 6 xfailed** (4,005 tests, 1,342 s; `b_head2`, 11:01-11:24Z,
  run `r20260925-110128-3b30`).
- **At `10996616` (base): 32 failed, 3,646 passed, 306 skipped, 6 xfailed** (3,990 tests, 1,475 s; `b_base`, 10:48-11:12Z, run
  `r20260925-104642-9085`).
- **Test by test** (`jdiff.py b_base.xml b_head2.xml`, `b_jdiff2.txt`, exit 0): **no new failure, no new skip, no new skip
  reason; no test deleted or renamed**; 15 new tests, all pass (`test_gates_fixtures::test_verdict_is_the_match_verdict_over_check_results`,
  `test_verdict::test_from_record_cites_property_records_by_digest`, `test_verdict::test_the_code_is_the_outcome`, 8 in
  `properties/test_noninterference.py`, 4 in `properties/test_record.py`). One outcome change, failed -> passed:
  `ops/test_row_pod_cancel_forwarding::test_sigint_is_forwarded_the_same_way` (a signal-timing test with a 15 s timeout, in a file
  this branch doesn't touch; f24's READY records the same flip).
- The 31 failures common to both include the two that failed in the head-only unit run at `824a9924` (`unit_head.log`):
  `check/test_gates_fixtures.py::test_card_json_roundtrip_and_schema` (no `out/gen/cards/SCHEMA.md` in a clean tree) and
  `commit/test_native_jit_keying.py::test_pod_release_fails_closed_...` (no `sweep/pod_release.sh`).
- A first head run at `824a9924` (`b_head`) was stopped by pid at 10:59Z once its lints had failed; its partial log is kept.
  Peak memory of the two concurrent runs: 45 GB of the pod's 62 GB (`b_base.rss`); no OOM kill during the gates.

### (3) Gate (a), regression T0 + T1

`VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression`
(`evidence/gate_a.sh`), TP2 pod.

- **At `824a9924`: 73 passed, 85 skipped, 0 failed** (158 tests), run `r20260925-105008-bca1` (`evidence/tp2_gates.sh`), in two
  processes started together at 10:52Z with `CUDA_VISIBLE_DEVICES=""`: `-k replay_partition` 9 passed, 4 skipped (1:14:12,
  `a_head_rp`), `-k "not replay_partition"` 64 passed, 81 skipped (0:58:56, `a_head_rest`); merged into `a_head.xml`.
- **Test by test against a23b's** `gate_a-t0t1-base-72884c8a-samepod.xml.gz` (`jdiff.py`, `a_jdiff.txt`): 158 = 158, 73 passed and
  85 skipped on both sides, **no test deleted, renamed or added, no outcome changed, no new failure, no new skip**. jdiff exits 1
  on two skip reasons only: `manifest_digest` on #70 and #75 now says "merged by `tp_stage.sh`" where a23b's says "merged by
  `row_pod_tp2.sh`". That text is `tests/regression/checks/manifest_digest.py:46`, renamed by `5cc0506e`, which lies between a23b's
  `72884c8a` and this lane's base `10996616`; this branch doesn't touch `tests/regression/`.
- **The final head `8d847755`** differs from `824a9924` by import lines (the same `REQUIRED_CLASSES_DEFAULT` /
  `required_classes_default` objects bound at the top of `verdict.py`, `pipeline/commit.py`, `pipeline/tp/commit.py`), the moved
  `FINAL_NORM_MODULES` tuple, one claim string in `properties/record.py`, and allowlist JSON. The gate's `verdict` and
  `commit_summary` checks were rerun there (`a_head2_vc`, run `r20260925-110440-71eb`): 26 tests, 20 passed and 6 skipped, each
  with the outcome and skip reason it has in a23b's run and in `a_head` (`a_head2_vc_vs_ref.txt`).
- All outputs are in `evidence/tp2/gates/` (`.log`, `.xml`, `.status`, `.env`; the `.env` files hold variable names and paths, no
  credential).

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
  trees (`diff -r` exit 0; `evidence/tp2/gates/verdict_bytes.{base,head,head2}.txt` list the sha256 per row, the texts are in
  `verdict_bytes/`). The other 3 rows (the OLMoE and
  Qwen3-30B-A3B TP2 rows and the SmolLM2 B=16 row) have no `commit/verdict.json`. No regression row has `properties/`, so the new key is absent.
- **The two GPU rows of this lane, which do carry `properties/`**: #101 (below) under `5483d13b` and `8d847755` byte-identical, and
  under the base only without the appended `properties`; #70 after its Commit under `10996616` and `66eaaa50` byte-identical, and
  under `8d847755` the same text with the 10-line `properties` block inserted (b2vb, `vllm-rf-b2vb/evidence/fr70.txt`).

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
`66eaaa50` (`tp_stage.sh`, `WORLD=2 NCCL_P2P_DISABLE=1 PAIRS=1`), runs `r20260925-095754-ee6c` (build, match) and
`r20260925-111729-3301` (commit). Reference: the fixture (class FAIL) and f1's base Commit of record at `72884c8a`
(`r20260924-221949-8668`, PAIRS=3, `vllm-rf-f1/commit70-base-head.tgz`), the one lane b4 compared against.

| | this run | record |
|---|---|---|
| build | PASS 10:20Z | |
| program_digest | `64bee6d6e8264461` | `64bee6d6e8264461` |
| manifest_digest | `1bb40895671dd791` (357,796 identities, complete) | `1bb40895671dd791` |
| match | capture + check pass (8,448 collectives, 0 mismatches, tokens equal); fold FAIL (rank 0 errors 4,096, unresolved 3,544) | the same (f1 base, b4) |
| commit | **FAIL** rc=1 12:20:11Z (3,751 s), pass False | FAIL, pass False (class FAIL) |
| tp run root | `0b91229f06480ce4047fa344ce1602c4fa38d493b8b7e568713db74ac1b31957` | same, in each of the 3 pairs |
| per-rank roots | `3e646ae3…` / `bf129350…` | same |

- **The Commit, field by field** (b4's `cmp70.py` on this run's `commit/summary.json` vs f1's base Commit of record,
  `evidence/cmp70-66eaaa50-vs-f1base.txt`): **32/32 equal**: tp run root and per-rank roots; leaves, tensors, bytes and classes per
  rank; openings 64/64 per rank; tokens equal; commit_pass and pass False; value check PASS; match oracle per rank; sampled replay
  False (partial: 484 q/k-norm strata not evaluated); boundary linkage True; cross-rank collectives False (154 picks per pair, all
  equal; the AllGather2 sites without a stratum); fold-match binding False with the same reason; query population False (25,408 per
  rank) with the same counts; weights pin (same roots of record); required manifest digest and classes; committer and openings.
  The 09-22 record on the pod (57a66b1 / 6d9cad0c) has the same roots; its `value_check` FAIL and manifest `ede1ad81` are pre-v2 and
  differ from f1's base in the same way (`evidence/cmp70.txt`).
- **Non-interference, world 2**: `<row>/properties/noninterference.json`, `ok`, digest
  `442979b3aa090ccc79d57b35116934c2fe4d78e40ad387462913514438471a7b`: both arms taken at world 2 (`tp: 2`), 8 / 8 requests
  equal. At the head (`evidence/ni70.txt`): the stored digest recomputes; `noninterference.record(match, 2)` rebuilt from the row's
  own Match arms gives the same digest; worlds 3 and 4 raise `ValueError` ("tensor-parallel world 3 refused: non-interference is
  recorded at worlds (1, 2)"); `records_of(row)` = [noninterference `442979b3…`, ok].
- **The run cites it, and the verdict text is otherwise unchanged** (`evidence/fr70.txt`, TP2 pod, after the Commit):
  `from_record(row).dumps()` under the base `10996616` and under the run's tree `66eaaa50` is byte-identical (sha256 `a7c32c87…`,
  33,283 bytes); under the head `8d847755` it is that text with one inserted `properties` block (10 lines: noninterference,
  `verity-vllm/noninterference/v2`, digest `442979b3…`, ok, no problems) and nothing else (`diff` shows only the insertion). The
  outcome is INSUFFICIENT_EVIDENCE under all three trees: the TP Commit writes no `commit/verdict.json` (see Found, not fixed); the
  row's decision is `tp_stage.sh`'s commit FAIL above.

### Pods, spend and custody

- `vyv-rf-b2v-l40s` terminated 11:27Z (its runs fetched by b2v before the 12:26Z rule, evidence in `vllm-rf-b2v/evidence/l40s/`).
  `vyv-rf-b2v-tp2` terminated 14:31Z by `research pods drain` ("all 8 attempt(s) preserved"). Spend: L40S ~1.98 h x $1.09 +
  TP2 ~5.0 h x $2.18 = **about $13.1 of $30**.
- The TP2 pod's 7 runs predate `--custody-r2`, and their attempts had been published to the pod's store without a run record. b2vb
  pushed the 7 attempts to R2 with `research data custody RUN --publish` (a delete-free key minted on the laptop, 1 h, piped into
  the pod and deleted after 43 s; `evidence/custody_tp2.sh`). That tool refuses to give custody to logs of attempts published
  without a record ("only `research fetch --all`"), so their run files went to R2 through a `--custody-r2` run instead:
  `r20260925-142514-883f` (`evidence/preserve.sh`) copied the 7 run dirs (99 files, 124 MB), #70's row evidence (28 files, 22 MB:
  top level, `commit/` without the two 219 MB binding maps, `properties/`, `match/` files under 1 MB to depth 2), the gate outputs
  (52 files) and the pod scratch, with a `PRESERVED.sha256` list. Custody: run record
  `art:b250b63253504c1cbcfba56a1aa115a9896f26026ae47cd5c05762de31642a3b`, 207 files, PRESERVED with sha256 readback. Not kept:
  #70's 37 GB capture, its 171 MB manifest, its binding maps and rank Programs (reproducible, digests above), the fixtures.

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

- Done 14:36Z: `git rebase --onto origin/main 10996616 lane/vllm-rf-b2vb` (main `33e4d8d1`), clean; pushed with
  `--force-with-lease` (`8d847755` -> `ed8f6625`). Commit map `8d847755..` -> `ed8f6625..`: d3f04b9d 1e5ad65a, 003e1506 d32be0a6,
  6e33c657 8ffd2647, 66eaaa50 f151ed07, 5483d13b 8f165d86, c461f86d fed414b2, 824a9924 64502384, fd9220c9 3ff17abf,
  95515e42 a01dd204, 8d847755 ed8f6625.
- Conflict risk with other wave-2 lanes: `pipeline/commit.py` (476-477, 1315) and `pipeline/tp/commit.py` (199, 313-314) import lines, a5's files;
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
- The TP Commit (`pipeline/tp/commit.py`, a5's) writes `commit/summary.json` (`delta-tp/v1`) but no `commit/verdict.json`, so
  `verdict.from_record` on a TP row gives INSUFFICIENT_EVIDENCE with program, manifest and run roots empty, at base and head alike.
  Folding the TP decision into `vllm-verdict/v1` belongs with the `row_pod.sh` heredoc (a5's CLI).
- research tooling: `research data custody --triage` suggests `research data label RUN custody waived --by WHO`, but the store's
  vocabulary has no `custody` key, so the label is refused (nothing written; not forced with `--off-vocab`).
