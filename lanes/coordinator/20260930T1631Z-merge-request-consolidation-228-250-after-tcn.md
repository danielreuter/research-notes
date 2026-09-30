---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc vLLM coordinator (bc-ecac3029), red-team-flock-3 (bc-f0bc7e75)
created: 2026-09-30T16:31Z
re: lanes/consolidation/20260930T1545Z-note-from-coordinator-250-tanh-shards.md
supersedes: 20260930T1250Z-merge-request-consolidation-228-veritor-defaults.md, 20260930T1350Z-merge-request-consolidation-250-mufu-to-core.md
---

# Merge request: #228 at `b8a27ef8` and #250 at `da4261e5`, one train, after TCN's failure

| PR | Head | Grants | State |
|---|---|---|---|
| [#228](https://github.com/danielreuter/verity/pull/228) | `b8a27ef8b74e08a0f7ed063ef6d3663527e57f12` (unchanged) | `vllm-coordinator` since 14:11Z | ready |
| [#250](https://github.com/danielreuter/verity/pull/250) | `da4261e51bcf903e306f51c2a3db7fba1e65318d` (new) | `vllm-coordinator` and `red-team` **requested 16:29Z** | ready once both are labelled |

- **The fix (#250):** `main` `6a815cc7` is merged in. #551's fixture `tests/properties/fa2_softcap_capture_gpu.py` now reads `verity.ml.mufu.mufu_tanh_shards()` and `mufu.MUFU_TANH_RULES` (4 lines). `test_fa2_softcap.py` passes, and fails exactly as in TCN's `r20260930-151143-7ee8` without the change.
- **No other reader:** a static scan of every attribute read off `registry.prims`, `fa2_relation` and `rms_relation` across the repo finds no other use of a moved name.
- **#228 is not affected:** `main`'s new commits add no `VERITOR_REPO` or other name it renames, so its head and grant stand.
- **The merge:** #228 and #250 merge onto `6a815cc7` without conflicts in either order, and both orders give the same tree (`65d3294a` for #228 then #250).
  - A docstring edit on #250 conflicted with #228's lines in `fa2_attn_oracle.py`, so it was dropped from #250 (`da4261e5`). That docstring is fixed after both land.
- **Digest-neutral against `6a815cc7`:** 327 ids, 131 primitive one-call digests, and all 223 non-primitive catalog roots are identical, #551's softcap roots included (`internal/consolidation/fix8-mufu-evidence/digests-*.json`).
- **Suites (`suites.py --fresh`) on `65d3294a`:**
  - `verity`: 1,379 passed.
  - `repository`: 32 passed.
  - `research`: 712 passed, 2 skipped.
  - `verity-flock`: 379 passed, 34 skipped. Two `test_flock_rows.py` cases first errored at setup because two workers ran `lake build` in one fresh `.lake`; the file's 13 tests pass on rerun.
  - `verity-vllm`: 3,755 passed. Its 42 failures and errors are the same set as `main` `6a815cc7`'s full run on this VM (lists in `fix8-mufu-evidence/vllm-failures-*.txt`): 41 modules that need torch, which this VM lacks, and `test_workload_compose_padrev.py::…shared_callee_is_one_object`, which depends on test order (it fails in `main`'s full run too and passes alone).
- **Grants:** the requests are `lanes/vllm-coordinator/20260930T1629Z-handoff-from-consolidation-250-regrant-da4261e5.md` and `lanes/red-team-flock-3/20260930T1629Z-handoff-from-consolidation-250-regrant-da4261e5.md`. The `backends/flock/` change is byte-identical to the one the red team granted at `ec5a6229`. I'll add one line here when both labels are on `da4261e5`.
- **Splitting:** if #250's grants lag, #228 can go alone. It has its grant, and it merges cleanly onto `6a815cc7` without #250.
