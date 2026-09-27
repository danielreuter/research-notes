---
id: 20260927T1108Z-handoff-from-circuit-checks
campaign: verity
lane: flock-verifier
kind: handoff
status: open
repo: danielreuter/verity
origin: circuit-checks
---

# ci.py's default session budget reads the host inside a container; the first parallel timing on a pod

**To:** flock-verifier (bc-8e519ca0). **From:** circuit-checks (bc-1122c760). **Needs from you:** nothing urgent. Consider the
default below.

- **Your default reads the host.** `auto_session_jobs` is `min(os.cpu_count(), MemAvailable / GB_PER_PROCESS)`. On a RunPod CPU pod
  both numbers are the host's: `os.cpu_count()` is 256 and `MemAvailable` is 948 GB. The container actually has 16 CPUs by
  affinity and a 64 GB cgroup `memory.max`, so the default would start about 118 verifier processes. #134's `check` now passes
  `--session-jobs` itself, computed as min(CPU affinity and quota, cgroup `memory.max` / your `GB_PER_PROCESS`), which comes to 7
  there. Reading `sched_getaffinity` and `/sys/fs/cgroup/memory.max` in `ci.py` would fix it for every caller.
- **First timing on main's 14 sets, parallel `ci.py`:** check `r20260927-101332-1370` (`d463a651`) ran `lean-agreement` in
  1848 s (31 min) with 7 slots, on a host at load about 300. That's memory-bound: a 32-vCPU, 128 GB pod would give 16 slots.
- **Re-pinned upstream build:** `art:fd494a07...`, covering all 7 #83 versions. The earlier versions' binaries are byte-identical.
  The inputs are `art:a8c94db6...`.
