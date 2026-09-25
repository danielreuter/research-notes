---
id: vllm-rf-b5gm/ready
lane: vllm-rf-b5gm
kind: ready
status: DRAFT (gates running)
created: 2026-09-25T11:25Z
---
# vllm-rf-b5gm READY: split `check/match/global_match.py` (B5)

- **Branch:** `lane/vllm-rf-b5gm`
- **Head:** `55b9d1ff` (tree `649b9861`). One commit on the base.
- **Base:** `10996616` (tree `679eb3cd`), STATE.md's "a4 base". A4 hasn't merged, so there was no rebase.

**Summary:**

- `global_match.py` drops from 2,206 to 416 lines, and `_check` from 1,227 to 116 (P10 span). Its three P10 entries
  (`_check`, `_check.leg`, `<module>`) are gone.
- The other entries moved with their code, and no allowlist has more entries or a higher count.
- GM-01 on row #23: every output is byte-identical except timings, across two base/head pairs on the same pod. Mean wall
  time is +3.6 % and mean CPU time -0.05 %.
- Gates: see below.

## Gate evidence

Pods (both terminated at READY):

- `vyv-rf-b5gm-cpu` = RunPod `d8iv0xx7nruohu`: cpu3g, 16 vCPU / 64 GB cgroup, AMD EPYC 7713 host (256 CPUs, shared, load
  about 200-250), 80 GB disk, $0.64/h. It ran the lints, GM-01 and gate (b).
- `vyv-rf-b5gm-big` = RunPod `jnuvfc6j890g7v`: cpu3m, 32 vCPU / 256 GB, AMD EPYC 9655 (a23b's CPU), 200 GB disk, $1.76/h.
  It ran gate (a).
  - cpu3m and cpu5m at 64 vCPU (512 GB) returned "no instances available" on every try from 10:08 to 10:30Z.
  - A single T0+T1 run peaked at about 63 GB at a23b; here `memory.peak` was TBD.

Environment: both venvs come from `pod_bootstrap.sh --cpu` (BOOTSTRAP-OK) plus `pytest-xdist==3.8.0`, with `xgrammar
0.2.7`, `googleapis-common-protos 1.75.3` and `uvicorn 0.53.0` pinned (as a23b did). Both `uv pip freeze` outputs are
identical to a1's `baseline-freeze.txt`.

Trees: each run used `research run --on POD --project verity --source WORKTREE --cwd source`.

- Head was shipped from `~/projects/verity-wt/rf-b5gm`.
- Base was shipped from a detached worktree at `10996616` (`~/projects/verity-wt/rf-b5gm-base`, removed at READY).
- The trees are `/workspace/research/src/<sha>/` on the pods. Gate (b) ran on a copy (`/workspace/trees/b_{head,base}`),
  so the shipped trees stayed as shipped.

Fixture keys: for each pod, I minted a 3 h read-only key on the laptop (`--permission object-read-only --via local`) and
piped it to `/root/r2ro.env` without echoing it.

- cpu: fetched GM-01's two inputs (`evidence/gm_prefetch.sh`); the key was deleted at 10:18:45Z.
- big: f24's `prefetch.sh` fetched all 26 artifacts (26 ok, 0 FAIL); the key was deleted at 10:49:30Z. Gate (a)'s
  status line says `key_file_present=no`.

### Lints

`python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py
integrations/vllm/tests/test_imports_resolve.py -q -p no:cacheprovider` at head on the cpu pod: run
`r20260925-102424-bb2e`, rc 0, 45 passed. (`-p no:cacheprovider` keeps `.pytest_cache` out of the shipped tree.) The lint
tests in gate (b) pass at head too.

### (b) Full suite: `OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile`

TBD

### (a) Regression: `VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression`

TBD

### Lane acceptance: GM-01 on row #23, base and head on the same pod

Command: row #23's recorded GM-01 command (the first line of the match record's `global_match.log`), run by
`evidence/gm_run.sh TREE TAG`. The script is f24's `evidence/gm_run.sh` with two changes:

- The module is `verity_vllm.check.match.global_match`, the path at this base. f24's script names
  `verity_vllm.check.global_match`, which no longer exists.
- Every run writes to the same directory, `/workspace/out/gm/run`, which is moved to `/workspace/out/gm/TAG` afterwards.
  So `x09.pipeline.decomp_out` is equal across runs.

The environment is f24's: `MATCH_IMPL=fast` and `MATCH_PIPELINE=shared`, and `MATCH_WORKERS` is unset (8 workers).

Inputs:

- Match record `art:33632a00...` into `/workspace/gm23/matchrec`.
- Correspondence builds `art:7e51cdad...` into `/workspace/gm23/build`.
- Linked into the recorded layout under `/workspace/cp/sweep_v2acq/<row>/`: `match`, `build_workload`, `build_request`
  and 64 `build_request_LP*_T*`.

The runs alternated base and head, one at a time, with nothing else running on the pod:

| run | research run id | tree | rc | wall s | CPU user+sys s | max RSS GiB | verdict |
|---|---|---|---|---|---|---|---|
| base1 | `r20260925-102545-9b89` | `10996616` | 0 | 550.6 | 2,089.8 | 13.34 | PASS |
| head1 | `r20260925-103943-2969` | `55b9d1ff` | 0 | 573.4 | 2,151.7 | 13.14 | PASS |
| base2 | `r20260925-105040-e8bc` | `10996616` | 0 | 592.7 | 2,353.9 | 13.34 | PASS |
| head2 | `r20260925-110305-f7fe` | `55b9d1ff` | 0 | 610.5 | 2,289.7 | 13.14 | PASS |

- **Outputs** (f24's `tree_diff.py`). base1 vs head1, base2 vs head2, base1 vs base2 and head1 vs head2 all give the same
  result:
  - Identical: `global_match_global_program.json` (sha256 `e5c5afba...`, the same in all four runs), `cmd.txt` and
    `stderr.log`.
  - `global_match.json` differs only in `utc`, `seconds`, `x09.seconds`, `alternate_verdict.seconds` and `phases[*]`
    (`cpu_s`, `dt_s`, `t_end_s`).
  - `impl` is equal, including `impl.source_sha256` (`18b0b7a4...`, `global_match_fast.py`, which is untouched), and so
    is `x09.pipeline.decomp_out`.
  - `match_decomp.json` differs only in `seconds` and `utc`.
  - `global_match.log` (the report on stdout) differs only in timing lines (`t_end_s`, `dt_s`, `cpu_s`, `seconds`,
    `utc`).
  - `env.txt` differs between trees only in the tree path inside `PYTHONPATH`.
- **Runtime:**
  - Wall time: head is +4.1 % in pair 1 and +3.0 % in pair 2, so +3.6 % on the mean.
  - CPU time: +3.0 % in pair 1 and -2.7 % in pair 2, so -0.05 % on the mean.
  - The host was shared (load average 200-260), and the same code varied by 7.6 % between its two runs (base1 vs base2).
- Evidence: `evidence/gm/{base1,base2,head1,head2}/` and `evidence/gm/diff_*.json`.

## The split (`integrations/vllm/verity_vllm/check/match/`)

The code moved verbatim and in order: the same dict key order, `mark()` order and `P.canon` side effects. The G1-G8
artifact keys, every reason string and every code are unchanged. The phase functions return what later phases read.
`_check` builds one `MatchRun` and calls them in `mark()` order.

| module | lines | job |
|---|---|---|
| `global_match.py` | 416 | Protocol docstring (plus a "Layout:" paragraph), `COMPARATOR`, `RULES_VERSION`, `match_ops`, `check`, the `_check` driver (116), impl dispatch, `main` (unchanged) |
| `match_run.py` | 55 | `NamedCheck` (was `_Check`) and `MatchRun`, the frozen inputs of one run (gp, oracle dir, ops, record, result, fold, declared) |
| `record.py` | 88 | Reading and canonicalizing the match record: `read_record`, `request_aliases`, `canonicalize_record` |
| `sampler_geometry.py` | 234 | The launch-S / top-p split geometry: `scheduled_live_counts`, `top_p_split_count`, `sampler_geometry_check` |
| `declaration.py` | 567 | The Program's declaration and engine facts: `GP_SCHEMA`, `request_id_of`, `from_gprog` and its helpers, `record_engine_facts`; G1 (`requests_declared`), execution conditions, the manifest of record |
| `attribution.py` | 98 | Attributing record instances to requests (`Attribution`, `attribute_instances`); G2 (`requests_observed`) |
| `per_request.py` | 389 | G3/G4/G5 per request: `check_requests`, the forked leg (`_request_leg`), `_compare_component`, `perm_match`/`perm_eligible` |
| `chronology.py` | 434 | G6: the lag rule, arrival, output events, served lengths, fed-forward, achieved concurrency |
| `engine_steps.py` | 211 | G7 (`vu_population`) and G8 (`within_step_order`, `_segmentation`) |

The largest function outside `global_match.py` is `sampler_geometry_check` (132 lines, as at base). The new ones are all
under 150 lines: `check_requests` 117, `_served_lengths` 125 and `within_step_order` 111.

One hazard I found and fixed before any run: the moved leg code has a `for run in ...:` loop. If the leg had taken a
`run: MatchRun` parameter, that loop would have rebound it. So `_request_leg` and `_compare_component` take their inputs
as explicit arguments.

## What changed

- **Code:** the split above (`55b9d1ff`). `global_match_fast.py` is untouched, and `check()`, `main` and the `MATCH_IMPL`
  dispatch keep their signatures.
- **Tests** (imports only):
  - `tests/check/test_global_match.py`: `sampler_geometry_check`, `scheduled_live_counts` and `top_p_split_count` now come
    from `sampler_geometry`; `workload_lag_static`, `manifest_sampling` and `relocate_components` from `declaration`.
  - `tests/check/test_compare_splits_binding.py` imports `top_p_split_count` from `sampler_geometry`.
  - `tests/pipeline/test_global_program_regress.py` imports `sampler_geometry_check` and `top_p_split_count` from
    `sampler_geometry`.
  - No test was renamed, added or deleted.
- **Allowlists** (each entry moved in the same commit; entry counts and violation counts are equal or lower):
  - P10: `_check` (1227), `_check.leg` (174) and `<module>` (2206) are deleted.
  - P03: `read_record` if-ladder moves to `record.py`.
  - P04: the 11 g-literal entries (22 literals) of `_check`/`_check.leg` become 11 entries (22 literals) in
    `attribution`, `chronology`, `declaration`, `engine_steps` and `per_request`.
  - P07: the `record_engine_facts` broad-except moves to `declaration.py`.
  - P09: the layer entry `-> pipeline.global_program` moves to `check.match.declaration`. The module-cycle entry keeps
    its count, but its member list names the new modules (see "Open question").
  - P11: 12 entries move to `declaration`, `per_request` (`perm_match`) and `sampler_geometry`.
  - `by_name_allowlist.json`: the TokenSelect path-predicate moves to `engine_steps.py` / `_segmentation`.

## What deliberately didn't change

- `global_match_fast.py`, so `impl.source_sha256` of the default impl is unchanged. GMF isn't merged into GM.
- The G1-G8 keys, reason strings and codes (C3 renames the keys), and `main`/argparse (a5's).
- Other lanes' files (`check/verdict.py`, `check/result.py`, `properties/`, `check/replay/`): no hunk at all.
- Docstrings and comments in other files that name the old location (see "Found, not fixed").

## Code identity

`evidence/code_digests.txt` has the sha256 of every file in `check/match/` at base and head.

- `global_match.py` changes from `3986118d...` to `116b3074...`.
- `global_match_fast.py` (`18b0b7a4...`), `batch_decomp.py`, `program_compare.py` and the others are unchanged.
- The record impl's `impl.source_sha256` is the hash of `global_match.py`, so it changes. The default (fast) impl's
  doesn't.
- The research-tools closure digest of the integration tree changes with the tree (`679eb3cd` to `649b9861`).
- No Program digest changes (GM-01's global program is byte-identical), and neither does any manifest digest, leaf id or
  regression verdict (gate (a) TBD).

## Open question

**P09 module-cycle entry.** The package already has one allowlisted SCC: `batch_decomp <-> global_match <->
global_match_fast <-> program_compare <-> pipeline.global_program <-> program.registry.lifted <-> ...`. It exists because
GMF imports GM (deferred), and GM, BD and C import each other.

Every new module that GM imports and that imports BD, C or GMF joins that SCC. The entry's detail now lists
`attribution`, `chronology`, `declaration`, `engine_steps`, `match_run`, `per_request` and `sampler_geometry`
(`record.py` stays out). The entry count and the external edges are unchanged.

The lint says "a cycle that gains a member fails too". Keeping the member list as it was would mean passing BD and C in
through `MatchRun` instead of importing them, or cutting GMF -> GM. Both are outside a pure-structure split, and the
second touches GMF. If the coordinator reads this as an allowlist growing, the fix is one of those two.

## Found, not fixed

- `impl_info` hashes only `mod.__file__`. With `MATCH_IMPL=record`, `impl.source_sha256` now covers only the driver, not
  the phase modules. The fast impl's never covered GM's body either. I left it alone to keep outputs identical.
- Docstrings and comments that name the old locations:
  - `global_match._check`: `correspondence/resolve.py:28,392,562` and `global_match_fast.py:410`.
  - `global_match._perm_match`: `global_match_fast.py:597`.
  - `global_match.sampler_geometry_check`: `pipeline/global_program.py:461` and `program_compare.py:45`.
  - `global_match.record_engine_facts`: `check/replay/stoch_recompute.py:201` (b1's).
  - `global_match.canonicalize_record`: `program_compare.py:595`.
- `parent_of` in `declaration.py` (from base `_check`) is computed and never read, as at base.
