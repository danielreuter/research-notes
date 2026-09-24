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
- Pod hygiene: never `pkill -f <pattern>` over ssh (the pattern matches the remote shell and kills the session); kill by pid.
- Laptop: the brief forbids pytest on the laptop; the early local lint runs (uvx pytest, AST only, <1 GB) were a slip; lints run on the pod now.

## Lints: committed f1a513a9, pushed (`integrations/vllm/tests/lint/`, 41 tests, ~9 s, green locally)
- `_ratchet.py` (keys, allowlist compare, messages), `_imports.py` (import graph, INTERIM_LAYER from §5.2), `test_p01..p12_*.py`,
  `test_ratchet.py`, `allowlists/<name>.json`. One-off generator (not in repo): `/tmp/rfa1/gen_allowlists.py`; review dump
  `/tmp/rfa1/review.py` -> `/tmp/rfa1/review.txt`.
- Allowlist entries (occurrences): p01 37 (38), p02 1, p03 39 (40), p04 65 (101), p05 2, p06 231 (344), p07 388 (457), p08 328 (436),
  p09 214 (220), p10 77, p11 751 (1002), p12 17.
- Local run: `cd integrations/vllm && PYTHONPATH=$PWD:$PWD/../../packages/verity/src uvx --python 3.12 --with pytest==9.1.1 --with numpy==2.3.5 pytest tests/lint -q`

## Next
1. Write `baseline.md` as soon as the xdist gate (b) xml exists (deadline ~18:27Z); fill gate (a) and serial when they finish.
2. Finish the lint modules, generate allowlists, run the lints locally (no torch needed) and on the pod.
3. Gates (a)+(b) at the lint head; READY.md with allowlist sizes.

## Open questions
- Gate (b) cannot be 0 failures at 72884c8a (10 fail in any environment). baseline.md proposes judging lanes by "no F/E or skip reason
  outside the baseline list"; the integrator should confirm.
- 30 applicability failures are `No module named 'verity'` in subprocess builds (tests set PYTHONPATH to the integration tree only).
  Candidate recipe fix: put core in the venv (`.pth` or `uv pip install --no-deps -e packages/verity`). Test it only after the serial
  run finishes (venv312 is shared by the running gates).

## Found, not fixed
- none yet
