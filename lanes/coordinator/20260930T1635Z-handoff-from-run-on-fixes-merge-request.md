---
cursor:
  subagentId: "bc-0c4fbab5-c272-5c4c-8b3e-6e1684ae213e"
id: coordinator/20260930T1635Z-handoff-from-run-on-fixes-merge-request
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: run-on-fixes worker (bc-0c4fbab5)
---

# Merge request: `cursor/run-on-fixes-213e` (https://github.com/danielreuter/verity/pull/574), commit `bc1e858ec`

Please train: `research merge --train ... cursor/run-on-fixes-213e --on POD --project verity`. It changes only `tools/research`, not
`backends/flock`, so `lean-agreement` doesn't apply. `check` has not been recorded. Locally, the full `tools/research` suite passed
(716 passed, 2 skipped).

This covers items 1–3 and the `notes.py` line from note:coordinator/20260930T1615Z-handoff-from-verity-root-friction-run-on-late-failures:
- `--timeout` with units is parsed once at launch and shipped as seconds, so the custody guard and lease extension see it; a bad value is refused before launch.
- `fetch` shows a runner that exited before writing `status.json` (state `launcher-exited`, plus `launcher.log`'s last line).
- A relative command with `--source` and no `--cwd` is refused; the launcher prints the resolved workload cwd.
- `push_branch`'s refusal names the `research notes bind ... --pod none` fix.

Not done: item 4 (multipart stall) and the custody size cap. Custody is being redesigned by another worker and was left alone.
May conflict with #496 and #448 in `cli.py` and `remote.py`.
