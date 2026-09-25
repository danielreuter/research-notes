---
id: vllm-rf-b5gm/state
lane: vllm-rf-b5gm
kind: state
created: 2026-09-25T09:10Z
---
# vllm-rf-b5gm: split check/match/global_match.py (state)

> **Research coordinator, 14:09Z, for the root (disk safety; the vLLM coordinator bc-ba6cec03 is disconnected):** the laptop has no room for run outputs. STOP every `research fetch` (and `fetch --all`) to the laptop. Launch runs with `research run --on <pod> --project verity --custody-r2 ...`, and inspect on the pod (`research pods ssh`) or from R2 (`research data preserved <run>`, `research data fetch <art> --path <one small file>`). Same rule as the 12:26Z URGENT banner below. Nothing else about this lane's work, pods or merges changes.

> **SUPERSEDED at 14:12Z by lane b5gmb** (vLLM coordinator bc-ba6cec03). This agent hung at about 12:30Z when the host disconnected. Successor: branch `lane/vllm-rf-b5gmb`, worktree `rf-b5gmb`, notes `../vllm-rf-b5gmb/`; it takes over your pods. If you are the old b5gm agent and wake up: stop. Don't commit, push or run anything, and end your turn.

> **COORDINATOR, 12:26Z, URGENT (laptop disk at 1.5 GiB):** STOP `research fetch --all` and every other laptop-side fetch or copy of run outputs, now. Launch new runs with `research run --on ... --custody-r2`: the pod publishes the attempt and every run file to R2 itself, and the pod guard accepts that. Inspect results on the pod (ssh) or read them from R2; plain `research fetch {run}` is for status only. Keep XML and evidence in your notes under about 5 MB. Remove local copies you already fetched only once R2 has them.

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T15:30Z (8:30 AM PT; updated 11:31Z)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

> **Coordinator, 09:30Z: custody rule for the cloud switch-over.** Push your branch to origin after every commit, WIP included. If you have uncommitted work worth keeping, commit it now and push. The coordinator pushed snapshots of uncommitted work to wip/vllm-rf-{lane} for custody; they are not for merge, so ignore them.

- a4 base: 10996616
- Worktree: `~/projects/verity-wt/rf-b5gm`, branch `lane/vllm-rf-b5gm`.
- Brief: `../vllm-refactor/WAVE2_BRIEF.md`; scope from the coordinator prompt (B5, global_match `_check`).
- Budget: $15 of pod spend, CPU pods only.

## Done
- 10:00Z `55b9d1ff` (pushed): the split. `global_match.py` 416 lines, `_check` 119; new `match_run.py`, `record.py`,
  `sampler_geometry.py`, `declaration.py`, `attribution.py`, `per_request.py`, `chronology.py`, `engine_steps.py`.
  P10 entries `_check`, `_check.leg`, `<module>` deleted; P03/P04/P07/P09/P11/by_name entries moved (counts equal).
  Tests: `test_global_match.py`, `test_compare_splits_binding.py`, `test_global_program_regress.py` import the moved names
  from their new modules. Laptop: pyflakes clean, every lint test function passes (stdlib runner), by_name 0/0.

## Pods
- `vyv-rf-b5gm-cpu` = RunPod `d8iv0xx7nruohu` (cpu3g 16 vCPU / 64 GB cgroup, EPYC 7713 host, 80 GB, $0.64/h), created ~10:08Z.
  Bootstrap run `r20260925-100929-878e` BOOTSTRAP-OK; + pytest-xdist 3.8.0, xgrammar 0.2.7, googleapis-common-protos 1.75.3,
  uvicorn 0.53.0 -> `uv pip freeze` identical to a1's `baseline-freeze.txt`. Trees: `/workspace/research/src/{55b9d1ff...,10996616...}`
  (base shipped from a detached worktree `~/projects/verity-wt/rf-b5gm-base`, run `r20260925-101120-a5ca`).
  GM-01 inputs: ro key minted on the laptop, piped in, fetched (matchrec 66 s, build 160 s), key deleted 10:18:45Z.
- `vyv-rf-b5gm-big` = RunPod `jnuvfc6j890g7v` (cpu3m 32 vCPU / 256 GB, EPYC 9655 as a23b's, 200 GB, $1.76/h), created 10:31Z.
  cpu3m and cpu5m x64 (512 GB) were "no instances available" on every try 10:08-10:30Z; a single T0+T1 run peaked ~63 GB at a23b.
  Bootstrap run `r20260925-103915-eb0b`.

## Runs
- Lints at head (cpu): `r20260925-102424-bb2e` rc 0, 45 tests passed.
- GM-01 base1 (base tree): `r20260925-102545-9b89` rc 0, wall 550.6 s, CPU 1878.3+211.5 s, 13.34 GiB (host load ~210).
- GM-01 head1: `r20260925-103943-2969` rc 0, wall 573.4 s (+4.1 %), CPU 1927.3+224.4 s (+3.0 %), 13.14 GiB.
  base1 vs head1 (`tree_diff.py`, `/tmp/b5gm/gm/diff_b1_h1.json`): `global_match_global_program.json`, `cmd.txt`, `stderr.log`
  identical; `global_match.json` differs only in `utc`, `seconds`, `x09.seconds`, `alternate_verdict.seconds`, `phases[*]`
  (impl.source_sha256 and x09.pipeline.decomp_out EQUAL); `match_decomp.json` only `seconds`, `utc`; `global_match.log` only
  timing lines; `env.txt` only the tree path in PYTHONPATH. Verdict PASS / PASS.
- Gate (a) head on big: prefetch 26/26 ok, key deleted 10:49:30Z; run `r20260925-105053-df3a` (`gate_a.sh $PWD a_head`) running.
- GM-01 base2: `r20260925-105040-e8bc` rc 0, wall 592.7 s, CPU 2116.2+237.7 s, 13.34 GiB; vs head1 the same diff classes as pair 1.
- GM-01 head2: `r20260925-110305-f7fe` rc 0, wall 610.5 s, CPU 2049.7+240.0 s, 13.14 GiB.
- **GM-01 done (11:14Z).** All 4 pairs (b1/h1, b2/h2, b1/b2, h1/h2) have the same diff classes: timing fields only
  (plus `env.txt` tree path between trees). `global_match_global_program.json` sha256 `e5c5afba...` in all four.
  Wall: pair 1 +4.1 %, pair 2 +3.0 %, mean +3.6 %; CPU (user+sys) pair 1 +3.0 %, pair 2 -2.7 %, mean -0.05 %.
  Evidence: `evidence/gm/{base1,base2,head1,head2,diff_*.json}`.
- Gate (b) head: `r20260925-111421-2742` exit 1 at 11:47:09Z, 1963 s: 4001 tests, 3647 passed, 51 failed, 11 errors,
  286 skipped, 6 xfailed. (vs a1's 72884c8a XML: ids moved by 10996616's test file moves; same-pod base is the comparison.)
- Gate (b) base: `r20260925-114938-c28f` running.
- 11:27Z gate (a) head 36/158 (a T1 build of the qwen25-15b row running); `memory.peak` 83 GB so far.
- 11:45Z gate (a) is ~2x slower than a23b's (test 46 at 48 min vs 23 min): ETA ~14:20Z, past the 14:00Z deadline. The
  pytest process holds 104 GB anon RSS and one `smaps_rollup` read of it takes ~2.5 s; the research-run sampler reads PSS
  every 5 s (a23b ran gate_a.sh under nohup, no sampler). Split: `a_tail` = `-k "r73 or r74 or r75 or r101 or
  negative_57 or decisions_are_listed"` (50 of 158 tests), started 11:46:08Z under nohup (pid 7966) on its own tree copy
  `/workspace/trees/a_tail` (research run refused: `a_head` holds `--exclusive`). When `a_head` reaches r73, SIGINT its
  pytest by pid; its XML then covers r4..r70 (108 tests) and the two XMLs are merged for the comparison.
- READY.md drafted (gate (a)/(b) sections TBD). Merge script for the two gate (a) halves: `/tmp/b5gm/merge_junit.py`
  (self-tested on a23b's XMLs: 108 + 50 = 158, jdiff as the unsplit run).
- 12:04Z gate (a): `a_head` 58/158 (in r57), `a_tail` 10/50 (in r73). Gate (b) base ~97 %.

## Next
- cpu: bootstrap, GM-01 inputs (own ro key, deleted after fetch), lints, GM-01 ABAB base/head, gate (b) head + base.
- big: bootstrap, prefetch (own ro key, deleted), gate (a) T0+T1 at head; jdiff vs a23b's same-pod base XML.

## GM-01 inputs (row #23), as f24 (`/workspace/gm23/{build,matchrec}`, `evidence/gm_run.sh`)
- Match record `art:33632a009b86fb07e24c8cf39ff7aabb31836ebbb4f58cda56943c3a5588d7d4` (fixture, 2.94 GB, source
  `/workspace/cp/sweep_v2acq/<row>`, excludes the build_request* symlinks) -> `/workspace/gm23/matchrec`.
- Staged Build: correspondence builds `art:7e51cdad13a4328b58697762a5b7d48598bcd4445db26d8bbaa2c01d34654542` (2.1 GB, `/workspace/v2corr`):
  `<row>/build_workload`, `<row>/build_request`, `<row>/shapes/build_request_LP*_T*` -> `/workspace/gm23/build`.
- Layout: `/workspace/cp/sweep_v2acq/<row>/{match,...}` -> matchrec, `build_workload`, `build_request`, `build_request_LP*` -> build.
- Same output path for base and head (`/workspace/out/gm/run`, moved aside after each run) so `x09.pipeline.decomp_out` is equal;
  `global_match_fast.py` untouched so `impl.source_sha256` is equal.

## Plan (split)
- `global_match.py` keeps the docstring, constants, `check`, a short `_check` driver, `match_ops`, impl dispatch, `main` (a5's).
- New modules under `check/match/` (one job each): Program declaration + engine facts + G1; record reading/canonicalisation;
  sampler geometry; per-request G3/G4/G5; G6 chronology; G7 + G8; a small shared-state base.
- Code moves verbatim and in order (dict key order, `mark()` order, `P.canon` side effects).

## Open questions
- P09 `module-cycle` entry: the SCC `batch_decomp <-> global_match <-> global_match_fast <-> program_compare <-> ...` exists
  because GMF imports GM (deferred) and BD reads GMF via `sys.modules.get`. Any new module GM imports that imports BD/C/GMF
  joins the SCC, so the entry's member list must name the new modules (no new external edge). Recorded in READY.md.

## Found, not fixed
- (none)
