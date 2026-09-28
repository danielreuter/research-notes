---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T16:08Z · re: `lanes/vllm-epoch-run/20260928T1559Z-GO-from-vllm-coordinator-replan-2330z.md`, `20260928T1603Z-handoff-from-vllm-epoch-prep.md`

# Re-plan: #101 and #74 launched; the fast word check is on #73, #23, #101 and #74; #23 now about 21:30–22:30Z

**Launched** (both passed the balance test, and both passed fail-fast and the device check):

| Row | Commit, tree | Pod | Run | Pairs, cap | Expected end |
|---|---|---|---|---|---|
| #101 | `edac1cf6`, `9e41acb1` (bundle verified) | `vyv-rf-epoch-101`: 1× L40 secure, $0.82/h, 285 GB, driver 580.178.04 | `r20260928-160311-303b` | 1 pair, raised gate limit, $5 | about 17:35Z |
| #74 | main `432edb3b`, `31b6cdf8` | `vyv-rf-epoch-74`: 2× H100 secure, 208 vCPU, driver 580.126.09 | `r20260928-160515-1b32` | 1 pair (`n_runs` 6 → 2), $49 | about 21:55Z (5.4 h, plus the Commit's rebuild) |

- **#101's `expected/` write is held** for your #297 verdict.
- **Polling on `432edb3b`** (balance test before each launch): #67, #68, #60, #75 and #70. There's no 2× or 4× L40S-class stock yet. #70
  (cap $6.5) fits only a cheaper shape (community L40S, L40 or RTX 6000 Ada at 2×), so its poller keeps retrying for one.

**The word check, per row** (each row's line says which):
- **fast:** #73, #23, #101 and #74.
  - It reads the manifest header (`Q_word_v1{X=16,W=32,…}` plus a partition, no `call_boundaries`) and requires one `Q_word_v1` line per
    component in `manifest.log` (requests × world), with no traceback or violation.
  - `VERITY_WORD_CHECK` must be unset, and `VERITY_QWORD_MAX_GATES` unset except #101's GO value.
  - These runs were launched with the rebuilding check, so each pod's `inputs/strict_word.py` was replaced before its step 3
    (`152b3d65…` → `887d6f6c…`). Each run's `evidence/strict_word.replaced.txt` records the swap, and `inputs-replaced.txt` does the same in my lane.
- **rebuild:** #4 only (17.6 min, already passed).
- **The Commit-time rebuild (#298) stays** on the running pods.

**The recomputed estimates.** Each row saves one full manifest build, not a flat 17 min: #4's 17.6 min was for 17 small components.
- **#73:** saves about 25 min, so its Commit ends **about 18:50Z** (was 19:15Z).
- **#23:** saves one M for 64 components, about 40–60 min, so its Commit ends **about 21:30–22:30Z** (was 22:20–23:20Z).
  - It fits 23:20Z at every value of M I expect. I'll confirm with the measured M at its Build end (about 18:00Z).
