---
id: vllm-rf-a1/state
lane: vllm-rf-a1
kind: state
status: active
created: 2026-09-24T17:27Z
---
# vllm-rf-a1: guardrails and baseline (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §4-6.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-a1`, branch `lane/vllm-rf-a1` from `72884c8a`.
- **Scope:** (1) `baseline.md` at 72884c8a (gates a and b on a CPU pod, environment recipe); (2) `integrations/vllm/tests/lint/` ratchets P1, P3, P4, P6, P7, P8, P10, P11, P12 and layering P2, P5, P9, each with an allowlist.

## Done
- 17:27Z worktree created.
- 17:31Z pod `vyv-rf-a1-veritor-campaign` = RunPod `y2uelocmg62eu0` (cpu3g, 16 vCPU / 64 GB, 80 GB disk, EUR-IS-1, $0.64/h), created with
  `research pods create --name vyv-rf-a1 --cpu cpu3g --vcpu 16 --disk 80` (research run as
  `PYTHONPATH=<wt>/tools/research/src python3.12 -m research`, wrapper `/tmp/rfa1/research.sh`).

- 17:37Z tree synced to pod `/workspace/base` (72884c8a, tree 7db3f3ba, clean); copies `/workspace/base-serial`, `/workspace/base-reg`.
- 17:40Z `pod_bootstrap.sh --cpu --out /workspace/bootstrap` BOOTSTRAP-OK (venv312: py 3.12.14, torch 2.13.0+cu129, vllm
  0.28.1rc1.dev472+gd9105ea80, triton 3.7.1, numpy 2.3.5, pytest 9.1.1, transformers 5.17.0) + `uv pip install pytest-xdist==3.8.0`.
  Freeze: pod `/workspace/rfa1/logs/freeze.txt`. Read-only R2 credential minted to pod `/root/r2ro.env` (expires 20:38Z).

- 18:30Z `baseline.md` written (environment recipe; xdist gate (b): 3904 = 3536 pass / 54 fail / 11 error / 297 skip / 6 xfail,
  all 65 failures grouped by cause; 50 skip reasons; per-file appendix). Beside it: `baseline-freeze.txt`, `baseline-gate_{a,b}.sh`.
  Local copies: `/tmp/rfa1/pull/b_base_x12.{xml,log,md}`, composer `/tmp/rfa1/compose.py`.

## Running (pod vyv-rf-a1, scripts `/workspace/rfa1/gate_{a,b}.sh`, logs `/workspace/rfa1/logs/`)
- DONE 18:22Z gate (b) base, xdist: `OMP_NUM_THREADS=3 gate_b.sh /workspace/base b_base_x12 -n 12 --dist loadfile` (exit 1, 65 F/E).
- 17:42Z gate (a) base: `nice gate_a.sh /workspace/base-reg a_base` -> `a_base.{log,xml}`. 18:01Z past the first row build, passing.
- 17:46Z gate (b) base, serial (the brief's exact command): `gate_b.sh /workspace/base-serial b_base_serial` -> `b_base_serial.{log,xml}`. 18:01Z at 53%.
- Summarizer: local `/tmp/rfa1/summarize.py RUN.xml` (overall/per-file counts, failures, grouped skips).
- 18:37Z prefetch of rows #57-#101 fixture blobs into `/workspace/research/store` (`/workspace/rfa1/prefetch.sh`, log `logs/prefetch.log`):
  the credential expires 20:38Z, gate (a) fetches row trees lazily, and it would reach the late rows after that. `fetch --to <tmp>`
  caches blobs + manifests only, so it never races the runs on `trees/<id>`.
- 18:50Z prefetch done: 18/18 ok; no gate (a) run needs the credential after 20:38Z.
- 18:54Z head `39c5ee7a` synced fresh to `/workspace/head` (2842 files = base + 28 lint files), copy `/workspace/head-reg`
  (runs at `f1a513a9` were stopped after 7 min for the docstring commit; their logs are in `logs/aborted/`):
  - gate (b) head xdist: `OMP_NUM_THREADS=3 gate_b.sh /workspace/head b_head_x12 -n 12 --dist loadfile` (same flags as base).
  - gate (a) head: `nice gate_a.sh /workspace/head-reg a_head`. The integrator's split harness took ~1 h (#11, #39) + ~2 h (the rest).
  - pre-check on the pod at `39c5ee7a`: `pytest integrations/vllm/tests/lint` 41 pass, 30 s on the loaded pod; with and without
    conftest, no torch / vllm / triton / numpy / verity_vllm module in `sys.modules` afterwards.
- 19:19Z: b_head_x12 98% (real-HF derive tail); b_base_serial 66%; a_base at row #68 (45%+); a_head at row #23.
  Local watcher `/tmp/rfa1/watch.sh` prints `DONE <run>` per finished run. Compare: pod `python3 /workspace/rfa1/jdiff.py BASE.xml HEAD.xml`.
  READY draft: `/tmp/rfa1/READY.draft.md` (gate section to fill; move to the notes dir only when the gates are in).
- DONE 19:33Z gate (b) head xdist (`b_head_x12`), exit 1: 3945 = base 3904 + 41 lint passes. jdiff vs `b_base_x12`: no new skip
  reason, 0 tests gone; 3 outcome changes: `observe/test_observer_encoding::test_weakref_death...` s -> pass (allocator reuse), and
  `harness/test_admit_r19_host_working_set` x2 pass -> F (`gc.get_freeze_count()` 375). Those two are order-dependent AT BASE
  (the integrator's known "gc-freeze" pair): vLLM `EngineCore.__init__` calls `freeze_gc_heap()` and never unfreezes, so any
  in-process engine earlier in the worker leaves the heap frozen. Reproduced 19:3xZ on the pod, identical at head and base:
  the file alone -> `test_fork_gc_freeze_opt_out...` F; after `observe/test_execution_label.py` -> both F.
- 19:46Z gate (b) head SERIAL (the brief's exact command): `gate_b.sh /workspace/head-serial b_head_serial` (fresh sync of 39c5ee7a),
  to compare like-for-like with `b_base_serial` (no xdist distribution noise). Not in watch.sh; poll `logs/b_head_serial.log`.
- DONE 19:37Z gate (b) base serial (`b_base_serial`), exit 1: 3904 = 3534 pass / 57 F / 11 E / 296 s / 6 xf (6,600 s). vs xdist base:
  + the gc-freeze pair F, + `program/test_lifted_tiny::test_specified_list_is_closed` F (walks the global REGISTRY; an earlier
  file's `Lifted[GatherBf16x49152_v1]_v2{ORD=3}` misses its `endswith("_v2")`), observer weakref s -> pass. In baseline.md.
- 19:47Z coordinator note in baseline.md (owner-approved): fetch every row, delete `/root/r2ro.env`, unset AWS_*, then run gate (a).
  19:48Z `/root/r2ro.env` deleted on vyv-rf-a1 (every row artifact was already local: 8 cached by a_base's first rows + 18 prefetched). The two running gate (a) processes
  (a_base, a_head) were started before the rule with the key in their environment; it expires 20:38Z. Not restarted (hours lost).
- Pod hygiene: never `pkill -f <pattern>` over ssh (the pattern matches the remote shell and kills the session); kill by pid.
- Laptop: the brief forbids pytest on the laptop; the early local lint runs (uvx pytest, AST only, <1 GB) were a slip; lints run on the pod now.

## Lints: `f1a513a9` + docstring commit `39c5ee7a` (head), pushed (`integrations/vllm/tests/lint/`, 41 tests, green on the pod)
- `_ratchet.py` (keys, allowlist compare, messages), `_imports.py` (import graph, INTERIM_LAYER), `test_p01..p12_*.py`,
  `test_ratchet.py`, `allowlists/<name>.json`. One-off generator (not in repo): `/tmp/rfa1/gen_allowlists.py`; review dump
  `/tmp/rfa1/review.py` -> `/tmp/rfa1/review.txt`.
- Allowlist entries (occurrences): p01 37 (38), p02 1, p03 39 (40), p04 65 (101), p05 2, p06 231 (344), p07 388 (457), p08 328 (436),
  p09 214 (220), p10 77, p11 751 (1002), p12 17.
- Pod run (gate_b env): `cd /workspace/head && python -m pytest integrations/vllm/tests/lint -q -p no:cacheprovider`.

## Next
1. When a_base finishes: fill baseline.md's gate (a) section (counts, per-row outcome, skips), status line.
2. When a_head and b_head_serial finish: jdiff vs a_base / b_base_serial; fill the gate section of `/tmp/rfa1/READY.draft.md`;
   move it to `READY.md`; update STATE; terminate vyv-rf-a1 (`research pods terminate vyv-rf-a1`) after pulling the XMLs/logs
   to `/tmp/rfa1/pull/` and copying the needed ones beside baseline.md.

## Open questions
- Gate (b) cannot be 0 failures at 72884c8a (10 fail in any environment; 3 more are order-dependent in the serial run).
  baseline.md proposes judging a lane against the base run of the same mode; the coordinator/integrator should confirm.

## Found, not fixed
- In the READY draft (`/tmp/rfa1/READY.draft.md`, section "Found, not fixed"): applicability builds without core `verity`
  (30); the `HF_HOME` collection-order leak; untracked test inputs (6); `execution_of_workload` NameError (4); CUDA test that does
  not skip; no `.git` in synced trees; duplicate Definition ids (core vs integration); core patches; library imports of tests/research;
  11 import cycles; the gc-freeze pair (vLLM `EngineCore` freezes the heap in-process); `test_specified_list_is_closed` order dependence.
- Not tried (out of scope): installing core into the venv would likely clear the 30 `verity` import failures.
