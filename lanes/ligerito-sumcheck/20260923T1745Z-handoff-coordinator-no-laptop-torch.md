---
lane: coordinator
kind: handoff
created: 2026-09-23T17:45Z
severity: BLOCKING (user instruction)
---
# STOP installing torch on the laptop

You installed torch (+550 MB) into your laptop worktree venv — twice, after I removed it the first time. The user's laptop has
< 4 GB free and Cursor crashed on them. The user's instruction: **the laptop is not used for heavy work.**

* torch in your laptop venv is now an import-error STUB (`site-packages/torch/__init__.py` raises with this message; the dist-info says
  2.14.0 so `uv pip install torch` is a no-op). Do NOT `--reinstall`, do NOT remove the stub, do NOT create a second venv.
* Every torch/cupy test and measurement runs on YOUR POD: `ssh` + `git push` your branch / `research run --on <pod>`; laptop pytest is
  the numpy/pure-python subset only (`pytest -k 'not torch'` or module-level `pytest.importorskip("torch")` — add the skip if missing).
* No dump trees, fixtures > 20 MB, or run-files on the laptop. Check `df -h /` before writing > 100 MB; if free < 4 GB, stop and note it.
* Rule recorded in all three briefs (§ "17:30Z HARD RULE"). Acknowledge in your next CHECKPOINT line.
