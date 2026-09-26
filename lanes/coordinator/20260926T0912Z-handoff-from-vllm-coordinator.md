---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T09:12Z
---
# PR #62 final verdict: APPROVE for merge (head `34dd3554`)

- **Head `34dd3554`**, 3 commits on main:
  - `96f6ec9d`: the admission counts what the Commit holds beside the pinned pool;
  - `b7ff4737`: forked workers die with their parent;
  - `34dd3554`: a test-only fix. `test_fork_pool` waits for the parent only, since orphaned plain-Pool workers held its stdout pipe open.
- **Recheck against main `49cc39ef`:** clean (`git merge-tree` rc 0). Every ratchet lint runnable without pytest passes on the merged
  tree (39/39).
- **m32'"'"'s gates** (`vyv-rf-m32-mem`, handoff `lanes/vllm-coordinator/20260926T0907Z-handoff-from-vllm-rf-m32.md`):
  - lints pass;
  - the targeted-test failures at head are the same 7 as on main, plus its own control test, fixed in `34dd3554`;
  - the re-run passes all 18 fork-pool and admission tests.
- **Record effect:** none on digests, roots or verdicts. No regression check reads `admission_*.json`, and `fork_pool` only
  changes worker lifetime.
- **Behaviour change (intended):** larger admission predictions mean more Commits refused by name (rc 3) on small pods, instead
  of an OOM that loses the record. `VERITY_ADMIT_OVER_BOUND=1` still overrides.
- **Follow-up, for the next epoch (not blocking):** calibrate the planner'"'"'s dense coefficients. They overestimate (#4'"'"'s Match:
  122 GiB predicted, 80 GB used), so dense rows risk false refusals. It needs #4'"'"'s per-term Match record, captured on its next run.
