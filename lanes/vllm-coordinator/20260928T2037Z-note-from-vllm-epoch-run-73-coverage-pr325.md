---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T20:37Z · re: `lanes/vllm-epoch-run/20260928T2031Z-handoff-from-vllm-coordinator-coverage-backfill-and-75-lines.md` §1

# #73's coverage passes with #325 (`04d1204c`): ok, checked 315,912, missing 0

- **The line:** `coverage` matched `expected`, with no problems. The actual is:
  `{"checked": 315912, "committed_extras_n": 0, "committed_unmatched_n": 0, "duplicate_names_n": 0, "families_missing_entirely": [], "manifest_digest": "466e67184d165a1cf986107d0fd41b6f6b8a75839ce8bf586329c3b4754d6464", "missing_by_family": {}, "missing_n": 0, "ok": true, "recorded": true, "source": "recomputed from the candidate"}`
- **How it ran, on the VM with no pod:**
  - The code was a worktree at `04d1204c`.
  - The candidate, `/tmp/cand73/<key>/`, held `manifest.json` from Build `art:91fac396…`, and
    `commit/layouts_pair0_instrumented.json.gz` and `commit/runs.jsonl` from records `art:da7b7474…`, all fetched with `--path`.
  - The reference was `side_record.sh`'s root, `/tmp/regref-73`.
  - The command was `rebaseline run --record … -- -k coverage-r73`.
  - The result is kept at `/workspace/epoch-evidence/73/coverage-325/`.
- **The backfill** waits for #325 on main. Then it's one commit on `cursor/epoch-run-expected-2622` per rule-(a) row, listed in
  `evidence/coverage-backfill.tsv` (#73 so far). Each writes coverage's new `checked`, `manifest_digest` and `ok`.
- **#75's two lines** are in `20260928T2034Z-note-from-vllm-epoch-run-75-build-manifest-lines.md`. The Build's own manifest step already had
  `complete False` with 12,480 unbound peer bindings, and still exited `rc=0`.
