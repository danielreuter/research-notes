---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-epoch
created: 2026-09-26T00:55Z
---
# epoch STATUS (for the 6:30 PM PT day-plan report)

**Branch** `lane/vllm-rf-epoch` @ `ad8050e9` (pushed), on b4c `5494e29f`:
| commit | item | kind |
|---|---|---|
| `30427930` | 1 c2b `dedf5313`: Programs cite core `AmpereBF16TcDot16_v2` | epoch |
| `a784d421` | 2 a/b: profile id without the pod id; profile-fallback raises (**protected** `vllm_adapter.py`: owner review) | epoch |
| `89cd9d1a` | 6: the admission lag import (digest-neutral) | non-epoch |
| `73a9a90a` | 7: `research_tools.CLOSURE` + `verity/evaluation/**` (key-only; code_identity 54ed9053… -> e58416b9…) | epoch |
| `ad8050e9` | m32 `271a0952` (pre-gate): `chunk_header` M mod 2^32 | non-epoch |
Deferred as larger than S: 2c (label from capability), 3 (G1–G8 key names), 4 (host `chunk-leaf-v1` label). Item 5 (golden)
was re-recorded on moe67 (`smollm2-135m-m1` -> `d72cd7ad…`, as c2b predicted). It lands as its own owner-review commit with the write.

**Rows** (Build+Match at `a784d421`, #67 at `89cd9d1a`; every Commit at `ad8050e9`):
- Re-recorded, Commit done: **#101** PASS (18:15Z). **#57** Commit FAIL (`local_replay`; a FAIL-class row, and its Match has no fold).
- Commit running: **#4** (moe67), **#67** (tp70), **#70** (tp70b). **#60** re-run at 00:48Z with `VERITY_ADMIT_OVER_BOUND=1`
  (named on the record): the fixed F-dA-15 admission refused it by 2.1 GB at moe68's 119 GiB. **#23** Commit is next on moe67.
  - **Finding:** #23 is GREEN, but its Match FAILs (NO FOLD) at the epoch tree.
- **Not re-baselined, pre-epoch evidence** (they stay on the old `expected/`):
  - #11 and #39: memory (planner: #39 Build 486 GiB).
  - #73: Commit OOM at 251 GB.
  - #74: time.
  - #75: rank Build of LP1024_T127 hit the 7200 s timeout.
  - #68: its Build was still running after 4.3 h at 00:52Z, so it couldn't end before 03:00Z. The big pod is terminated.
- Findings for READY: the M >= 2^32 header (fixed by m32); `row_pod.sh` has no TP hook (my first #70/#75 runs were invalid, since redone
  through `tp_stage.sh`); the #23 Match fold failure; the planner's dense coefficients overestimate (#4 Match: 122 GiB predicted,
  80 GB used).

**Plan:** on each remaining pod, `rebase.sh` (runs `r20260926-004934-*`) waits for its Commits, copies the rows' outputs
(files < 200 MB) into its run for R2, then runs `rebaseline.py run --record` (T0,T1, -k those rows) and `table`. I expect
`rebaseline.py write --dry-run` by about **02:15Z** and the real `write` plus the golden commit on the lane branch by about
**02:45Z**, at the epoch tree. The merge-main rerun (with the sampled_proofs PYTHONPATH fix) won't fit before 03:00Z, so it
follows in the review. Pods are terminated as each rebase run is PRESERVED.

**Pods:** moe67, moe68 ($1.09/h each), tp70, tp70b ($2.18/h each), so $6.54/h. Terminated: g1, g2, tp75, h100, big.
**Spend:** about $85, heading for about $100 by 03:00Z (budget $130).
