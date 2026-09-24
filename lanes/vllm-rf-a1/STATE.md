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

## Running (pod vyv-rf-a1, scripts `/workspace/rfa1/gate_{a,b}.sh`, logs `/workspace/rfa1/logs/`)
- 17:42Z gate (b) base, xdist: `OMP_NUM_THREADS=3 gate_b.sh /workspace/base b_base_x12 -n 12 --dist loadfile` -> `b_base_x12.{log,xml,rss}`.
  18:01Z at 98%, tail = `test_derive_realhf.py` + `test_derive_hf5b_realhf.py` (one worker each). Has F/E -> diagnose from the xml.
- 17:42Z gate (a) base: `nice gate_a.sh /workspace/base-reg a_base` -> `a_base.{log,xml}`. 18:01Z past the first row build, passing.
- 17:46Z gate (b) base, serial (the brief's exact command): `gate_b.sh /workspace/base-serial b_base_serial` -> `b_base_serial.{log,xml}`. 18:01Z at 53%.
- Summarizer: local `/tmp/rfa1/summarize.py RUN.xml` (overall/per-file counts, failures, grouped skips).

## Lints (worktree, uncommitted, in progress)
- `integrations/vllm/tests/lint/`: `_ratchet.py` (keys, allowlist compare, messages), `_imports.py` (import graph, INTERIM_LAYER from §5.2),
  `test_p09_layering.py`, `test_p02_value_checks.py`, `test_p05_properties.py` written; P1, P3, P4, P6, P7, P8, P10, P11, P12 next.
  Allowlists go in `tests/lint/allowlists/<name>.json` (generate with `_ratchet.dump_allowlist`, not committed as a tool).

## Next
1. Write `baseline.md` as soon as the xdist gate (b) xml exists (deadline ~18:27Z); fill gate (a) and serial when they finish.
2. Finish the lint modules, generate allowlists, run the lints locally (no torch needed) and on the pod.
3. Gates (a)+(b) at the lint head; READY.md with allowlist sizes.

## Open questions
- none yet

## Found, not fixed
- none yet
