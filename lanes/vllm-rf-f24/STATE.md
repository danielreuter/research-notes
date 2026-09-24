---
id: vllm-rf-f24/state
lane: vllm-rf-f24
kind: state
status: active
created: 2026-09-24T17:33Z
---
# vllm-rf-f24: identity and integrity (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 (D5, D6, D7, D10, D11, D13), §4 (P1, P4, P12); coordinator notes 16:25Z and 16:40Z.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f24`, branch `lane/vllm-rf-f24` from `72884c8a`.
- **Scope:** D5 one code identity (hot worker + TP commit key, reuse `harness/research_tools.py` closure); D6 `construction_version` sources resolved against the integration; D7 Build dtype from the engine; D10 remove core monkeypatch in `check/global_match_fast.py`; D11 full digests in `weights_of_record._eq`; D13 structured reason codes in `check/commit_verdict.py`.
- **Launcher:** `~/.research/bin/research` (coordinator's CLI). ssh wrapper `/tmp/rff24/ssh.sh` (recreate with `research pods ssh 0zb24mk1w6nb4o --print`).

## Done
- 17:33Z worktree created.
- 17:38Z pod `vyv-rf-f24-veritor-campaign` = RunPod `0zb24mk1w6nb4o` (cpu3g, 16 vCPU / 64 GB, 80 GB disk, EUR-IS-1, $0.64/h), created with
  `research pods create --name vyv-rf-f24 --cpu cpu3g --vcpu 16 --disk 80`.
- 17:41Z base tree `git archive 72884c8a` -> pod `/workspace/base`.

## Running
- pod: `pod_bootstrap.sh --cpu` from `/workspace/base/integrations/vllm`, log `/workspace/logs/bootstrap.log`, venv `/workspace/venv312`.

## Next
1. Baseline on pod at 72884c8a (a1's `baseline.md` not there yet): gate (b) counts, gate (a), GM-01 #23 fast timing + outputs.
2. Fix D5..D13, one commit each; gates (a), (b); GM-01 byte-identity + runtime for D10.

## Open questions
- none yet

## Found, not fixed
- none yet
