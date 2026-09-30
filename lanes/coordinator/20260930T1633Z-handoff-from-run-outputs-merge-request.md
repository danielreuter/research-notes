---
cursor:
  subagentId: "bc-a98dbece-9d80-5206-b600-9688b5e14c35"
id: 20260930T1633Z-handoff-from-run-outputs-merge-request
lane: run-outputs
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/run-declared-outputs-4c35
---

# Merge request: custody uploads declared outputs (Daniel's ruling, Sep 30)

- **PR:** [#575](https://github.com/danielreuter/verity/pull/575), branch `cursor/run-declared-outputs-4c35`, commit
  `af19129a`, one commit on the local `main` from the environment snapshot.
- **What changes:** custody's run record uploads the run's own files, the files matching `--declared-output` globs, and
  undeclared files up to 256 MiB. It lists every other file in `meta.trimmed` with path, size and sha256, and no bytes.
  `.custody` still pins those files by hash.
- **Warning:** when custody trims, it warns that undeclared uploads will be dropped once lanes declare their outputs.
  Tightening to that later is `UNDECLARED_CAP_BYTES = 0`.
- **Also in this PR:**
  - The workload gets `RESEARCH_RUN_DIR`.
  - New skill `.agents/skills/writing-runs/SKILL.md`, routed from `AGENTS.md`.
- **Tested:** the `tools/research` suite passes (714 passed, 2 skipped), and so does `tests/test_repository.py`.
- **For you to do:** `check` isn't recorded, and nothing touches `backends/flock`. Please run
  `research merge cursor/run-declared-outputs-4c35`, or put it on a train.
- **Possible conflict:** `20260930T1635Z-handoff-from-run-on-fixes-merge-request` also touches `research run`. This PR edits
  only `store/custody.py`, the `--declared-output` argument and the `Popen` in `telemetry/run.py`, the store README's custody
  paragraph, and `test_run_custody.py`. If that PR changes the same lines, rebase whichever lands second.
- **Deviation from the approved design:** there is no `--custody-keep-all` flag. `--declared-output '*'` keeps everything,
  so no new flag has to be threaded through the remote launcher.
