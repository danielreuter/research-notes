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

## Done
- 17:33Z worktree created.

## Running
- nothing yet

## Next
1. Read the code for each defect; read `tools/research/README.md` and `integrations/vllm/ops/` bootstrap scripts.
2. Provision a CPU pod `vyv-rf-f24`; measure the baseline if a1's `baseline.md` isn't there.
3. Fix D5..D13, one commit each; gates (a), (b); GM-01 byte-identity + runtime for D10.

## Open questions
- none yet

## Found, not fixed
- none yet
