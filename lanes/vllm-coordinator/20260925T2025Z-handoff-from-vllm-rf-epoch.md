---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-epoch
created: 2026-09-25T20:25Z
---
# epoch: DECISION NEEDED. 7 PM PT isn't reachable; three rows need a >= 256 GB pod that RunPod doesn't have

**Where it stands at 20:25Z**
- Done: #101 PASS (18:15Z, moe67; Program `573313ed…`, manifest `ee65240e…` = c2b's epoch value).
- Build is the long pole, not Commit. On L40S the request-Program derives are CPU-bound: #4 (SmolLM2 B16) took 2 h, #70's
  Build took 88 min, and #73's Build (H100) has run 2 h 20 min.
- **My error, fixed:** `row_pod.sh` has no TP hook (the header note I relied on was wrong), so #70 and #75 first ran the
  TP1 path. #70's Build/Match at 17:55–19:38Z are invalid. #75 was stopped at 20:17Z and relaunched through `tp_stage.sh` on tp75
  (`r20260925-201729-6f0c`). #70 goes to a new 2x L40S pod `vyv-rf-epoch-tp70b` (`wto6vcl88f3aau`, $2.18/h,
  bootstrap `r20260925-201842-c282`, then rows), because tp70 holds #67.
- **Memory:** #39's Build was OOM-killed (rc 137) at moe68's 125 GB cgroup. #57's advisory predicts a Match refusal at 119 GiB.
  #11 (the same B1 i4096 o512 shape as #39) is queued on moe67, which is also 125 GB. #68 still has no pod: the loop has found
  no L40S with >= 256 GB since 18:13Z (1x --min-ram 256, or 2x --min-ram 150). It retries until 21:00Z.

**ETAs if nothing else fails:** #4 ~20:50Z, #70 ~23:30Z, #67 (tp70 GPU 0) ~00:30Z, #57 and #60 (moe68) ~23:00Z, #73 ~21:30Z and #74
~01:00Z (h100), #75 ~02:00Z or later. #11, #39 and #68 are blocked on a >= 256 GB pod. The rebaseline would run 03:00Z at the
earliest, past the 00:30Z vyv- deadline.

**Spend:** about $30 so far. Current burn is ~$12.5/h (moe67, moe68 $1.09 each; tp70, tp75, tp70b $2.18 each; h100 $3.49).
Running to ~02:00Z adds ~$70, so ~$100 of the $110.

**Decision asked (pick one):**
1. Extend the vyv- deadline to ~03:00Z, and accept a partial epoch at review time: rows that can't get memory (#11, #39, #68)
   stay on their old expected, listed as not re-baselined.
2. As 1, and also allow a larger shape for #11/#39/#68 if one appears: an A-class host isn't an option (the rows are L40S-keyed),
   so it's more L40S retries.
3. Stop after the current Builds: land the epoch commits for review now, and re-record in a later window with capacity.
Until I hear back, everything keeps running and the big-pod loop keeps trying.
