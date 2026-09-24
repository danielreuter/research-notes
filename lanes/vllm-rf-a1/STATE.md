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
- 17:42Z gate (a) base: `nice gate_a.sh /workspace/base-reg a_base` -> `a_base.{log,xml}`.
- planned: serial gate (b) in `/workspace/base-serial` (tag `b_base_serial`) once the xdist run is in its real-HF tail.

## Next
1. Read `tools/research/README.md`, `integrations/vllm/ops/` bootstrap scripts; provision `vyv-rf-a1`.
2. Run gates (a) and (b) at 72884c8a; write `baseline.md`.
3. Lints.

## Open questions
- none yet

## Found, not fixed
- none yet
