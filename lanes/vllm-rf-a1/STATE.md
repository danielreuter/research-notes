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

## Running
- pod bootstrap (next)

## Next
1. Read `tools/research/README.md`, `integrations/vllm/ops/` bootstrap scripts; provision `vyv-rf-a1`.
2. Run gates (a) and (b) at 72884c8a; write `baseline.md`.
3. Lints.

## Open questions
- none yet

## Found, not fixed
- none yet
