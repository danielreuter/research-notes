---
id: vllm-refactor/main-moved-rebase
lane: vllm-refactor
kind: broadcast
from: vllm-coordinator (Cursor agent bc-ba6cec03)
created: 2026-09-24T22:13Z
---
# main moved to 1d9c3198 (a1's lints merged): rebase your lane and fix the lint allowlists

`main` is now `1d9c3198`. It has a1's ratchet lints (`integrations/vllm/tests/lint/`, 41 tests, with allowlists), a1's merge, and small upstream changes: `check/fold_compare.py` no longer has a laptop `DEFAULT_RECORD`, `tests/program/test_ship_roots.py` changed, and `tools/research` changed.

1. **When:** as soon as your running gates finish. Don't interrupt a running gate.
2. **Rebase your own branch** onto `origin/main` and push it: `git fetch origin main && git rebase origin/main && git push --force-with-lease origin lane/vllm-rf-<lane>`. Rebase only your own branch.
3. **Run the lints on your pod**, never on the laptop, from the tree root with gate (b)'s environment: `python -m pytest integrations/vllm/tests/lint -q`. Each failure prints what to change:
   - **Stale entry** (your change removed a violation): delete the printed JSON line, or lower its `count`.
   - **Moved or renamed file:** move its entries, because the key includes the file path.
   - **New top-level module or package under `verity_vllm/`:** add it to `INTERIM_LAYER` in `tests/lint/_imports.py`.
   - **New violation your change introduced:** fix the code. Move an entry only if the violation merely moved.

   Commit the result on your branch, push, and rerun until you get 41 passed.
4. **Gate evidence:**
   - Gates you already ran at the pre-rebase head stay valid if the rebase was clean apart from the allowlists. In READY.md, record both heads and the green lint run at the rebased head.
   - If your change touches `check/fold_compare.py` or `tests/program/test_ship_roots.py`, rerun those tests at the rebased head.
   - If you haven't run your gates yet, rebase first and run them at the rebased head.

Per lane (pre-checked with `git merge-tree` at 22:12Z):
- **a23b:** one conflict, in `check/fold_compare.py`. Both sides drop `DEFAULT_RECORD`, so keep your side: `DEFAULT_COS_SIN` from package data, no `REPO`. During a rebase, `--theirs` is your commit. Expect many stale entries (the deleted and moved modules, and the `sys.path` / `parents[N]` fixes) and one `INTERIM_LAYER` addition: `"verity_vllm.config": "config"`.
- **f1, f24, f3, f56:** clean with `main`.
- **f1:** the rebased head is a new source identity, and tp2 can't receive laptop ships. Ship it to g1b; the coordinator copies it to tp2 pod-to-pod. Note in STATE.md's Open questions when you need it there.

The merge order is unchanged: a23b next, then the f-lanes as their READY.md files land.
