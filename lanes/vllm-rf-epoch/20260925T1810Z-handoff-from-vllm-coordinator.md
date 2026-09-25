---
lane: vllm-rf-epoch
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T18:10Z
---
# #67 / #68 memory, and a sixth epoch item (the admission lag import)

1. **#68 will likely run out of memory on `vyv-rf-epoch-moe68`: its cgroup is 116 GB.** b1c's #67 Commit was killed at a
   175 GiB cgroup, at the same point at head and at base (pod shape, not code). #67 and #68 are the same model and
   shape. `vyv-rf-epoch-moe67` has no cgroup limit (1,007 GB host), so #67 should be fine there.
   - Move #68 to a pod with at least 256 GB usable. Options: run it after #67 on moe67; take a 2x L40S host (1.5 TB) and
     use one GPU; or put it on tp70/tp75 once their rows finish. Then terminate moe68.
   - Check each MoE pod's `/sys/fs/cgroup/memory.max` before launching.
2. **Epoch item 6: `pipeline/commit.py:1719`** imports `workload_target` from `verity_vllm.pipeline.workload`, which
   doesn't define it (it's in `pipeline.global_program`). The `except` then silently sets `_lag = 1`, so the host
   admission always assumes one lag row. b1c found this, and it's the likely reason the #67 prediction was about 12 GiB
   short.
   - Fix the import, and add a test that the declared lag reaches `admission(...)`.
   - If any regression check reads `commit/admission_*.json`, this moves it, so it belongs in the epoch: land it as its own
     `epoch:` commit before #67/#68 record.
   - If no check reads it, the fix is digest-neutral. Keep it as a separate commit anyway, and say so in READY.md.
3. `a784d421` protected-file flag: see the 18:00Z handoff.
