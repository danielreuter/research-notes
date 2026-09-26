---
lane: vllm-coordinator
kind: handoff
from: vllm-vu-export
created: 2026-09-26T04:00Z
---

# Handoff from vllm-vu-export: OOM-ordering follow-up, #4 done, pod terminated (04:00Z)


**OOM ordering** (your 02:30Z follow-up): fixed on PR [#53](https://github.com/danielreuter/verity/pull/53) at `e83fc179`.
- The export now runs serially whenever less than 20% of the process's memory limit is free. It reads the cgroup v2 or v1 limit and usage, falling back to MemAvailable over MemTotal.
- A forked pool can therefore no longer take a memory-tight Commit down before `summary.json` and `verdict.json` are written.
- I kept the call where it is. Moving it after the verdict would mean holding the Programs, the binding map and the reader alive through openings-after-release and the rest of the Commit, which is exactly the heap your concern is about.
- With this in, `VU_EXPORT=0` shouldn't be needed on #60, #67 and #68. I leave lifting it to you.
- Not yet tested on a pod: this commit and the chunked-edges commit `f4422026` came after the pod was terminated, and the VM rule keeps pytest off my VM. Everything up to `93e7f3c3` passed in `r20260926-030342-4dc0`.

**#4:** PASS, run `r20260926-000408-c3b4`. Program `801635556bb6f3c9…`, manifest `3bbd860f…`, run root `0a077fd4…`. The export `art:886e659d…` has 7 sets and 11,008 inputs. It was drawn before the stratum-order fix, so it has no K = 576 GEMM coordinates.

**Pod:** `vyv-vu-export-g1` was terminated at 03:09Z after every run was PRESERVED. Lane spend was about $4.3.
