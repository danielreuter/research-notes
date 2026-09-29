---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-29T20:50Z

**#39 is deferred: its Build hit the Build's own 4 h cap.** The run is `r20260929-160603-ab18`, on 4× L40S SECURE; the row is Qwen2.5-1.5B B1 i4096/o512.
- The step derive passed (Programs `6bda7a53…`), but the request derive for the 4,096 + 512-token sequence was stopped at 14,434 s: `build FAIL rc=0/124`, with no workload Program and no manifest.
- The limit is `row_stages.build`'s `min(CAP=14400, 900 × scale)`. For LP 4096 and T 511 the scale is 256, so the cap is the full 4 h. The row carried no `BUILD_TIMEOUT`. It was not the job deadline, which was 21:39Z.
- The Build `art:b9cb60d6…` and the records `art:1b3ab37b…` are preserved. The pod is terminated, and the row spent $18.75 of its $30 cap, which frees $11.25 of committed spend.
- A rerun would need `BUILD_TIMEOUT` above 4 h, and nothing here says by how much. A fresh 4× L40S run of 8 h or more is over $35, which does not fit the $260 line. The stored Build holds the finished step derive but not the request derive, so resuming would only save the step derive's share.

I recommend leaving #39 deferred with its old record; its digest line says why. If you want a rerun, give the `BUILD_TIMEOUT`, the shape and the cap.

**The rest of the epoch:**
- #68's in-place resume is armed for after its 20:53Z cut and store.
- #67 waits for 2× L40S SECURE stock, ahead of #23.
- #74, #11, #75 and #70 are live.
- Written so far: #101, #60 and #4.
