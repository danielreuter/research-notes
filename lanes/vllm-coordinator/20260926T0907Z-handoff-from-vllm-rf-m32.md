---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-m32 (bc-7039be6c-2a9f-5501-af51-ee96bf96b428)
created: 2026-09-26T09:07Z
---
# MERGE-READY PR #62: `lane/vllm-rf-commit-mem` 34dd3554 (base origin/main 2ba5e62c): #23 Commit memory findings

PR: https://github.com/danielreuter/verity/pull/62 (draft). Please forward it to the research coordinator.

**1. Admission.** F-dA-15 counted only the pinned pool. For #23 it admitted 182,765 MiB (from the run's
`commit/admission_native_collect_v2b.json`), and the Commit OOM'd at 239,372 MiB. The sampler shows a 167.7 GiB pool plus a 51 GiB parent
heap, then 32 forked workers, and the run died 90 s after the fork.
- `96f6ec9d`: predicted = pool + `admission_bound.committer_resident` (the row planner's commit stage minus its pool term).
- Against the recorded peaks (`tests/pipeline/fixtures/admission/commit_peaks.json`):
  - #23: at least 226,996 MiB measured, 305,510 predicted, refused.
  - #67: 176,321 MiB measured, 191,020 predicted, admitted.
- `commit.py` is unchanged in size (P10 `main` 1770, module 2939).
- The R17-29 planner in `commit.py` also said "would REFUSE" (318,329) for #23, but it is record-only. Making it govern is a policy call
  I left alone.

**2. Orphaned workers.**
- `b7ff4737`: `check/replay/fork.fork_pool` / `die_with_parent` (`PR_SET_PDEATHSIG` SIGKILL plus a ppid check). It is used in the
  replay, the VU draw (`vu_store`), `stoch_recompute` and the Match legs.
- `34dd3554`: a test fix.

**Gates** (git clone, `verity_sampled_proofs` importable, CPU-only; evidence `lanes/vllm-rf-m32/evidence/mem-gate-results.txt`):
- r20260926-082110-dc3a (head b7ff4737, base 2ba5e62c):
  - Lints: head rc 0.
  - Targeted tests (admission, fork pool, and every test file importing a changed module): head 246 passed / 8 failed, base
    240 passed / 7 failed. The 7 are `test_artifact_applicability_independent`, pre-existing and identical at base.
  - The 8th was my plain-Pool control test hanging on the orphans' open stdout pipe, which is the bug itself. Fixed in 34dd3554.
- r20260926-090444-21e3 (34dd3554): `test_fork_pool` + `test_admission_commit` 18 passed.
- Both runs are PRESERVED. Pod vyv-rf-m32-mem (an L4 host with the GPU hidden; every CPU shape and A4000/A5000/A4500 were out of stock)
  was terminated at 09:06Z.

**Calibration follow-up (#4 dense Match): not done, not cheap.**
- #4 is `smollm2-135m`. It has no MODELS entry, so the planner uses phi3's coefficients and predicts the Match at 125,105 MiB.
- Its only record of the Match peak is the epoch STATE's "80 GB". `r20260925-175229-a415` was never published, and no preserved run
  carries moe67's cgroup: it is v1, and the skip11 waiter's sampler saw only its own processes.
- An architecture-true entry (Llama-3.2-1B's coefficients scaled to 30 layers, hidden 576, per-layer widths) predicts 64,673 MiB,
  which is **below** 80 GB. So a tightening without #4's per-term breakdown would be unsound.
- Needed: #4's `sweep/smollm2-135m__.../timeline_report.json`, `admission.json` and the attempt's `resources.jsonl`, copied from moe67
  if it still holds a415, or recorded on #4's next run.
- #23's refusal is untouched either way: llama32-1b has its own entry.

Spend: this task about $0.40. Lane total about $9.5.
