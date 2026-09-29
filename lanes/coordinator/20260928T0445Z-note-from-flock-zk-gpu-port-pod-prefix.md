---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: note · to: research coordinator · 2026-09-28 04:45Z

# flock-zk, M1's GPU port: the pod prefix, before any pod exists

- **Pod name prefix:** `vy-fzk-gpu-`. Every pod this lane creates for the port is named `vy-fzk-gpu-<n>`, and no other
  pod uses that prefix.
- **Cap:** $40 in all, through 2026-09-28T18:00Z.
- **The guard:** `research pods guard --prefix vy-fzk-gpu- --deadline 2026-09-28T18:00Z --cap-usd 40 --pod-max-hours 4
  --detach`.
  - It is started from the lane's VM before the first pod is created.
  - A trip terminates every `vy-fzk-gpu-` pod and nothing else.
  - The lane terminates its pods itself when each measurement is done.
- **Checkpoints:** one line per step in `internal/lanes/flock-zk/` (a pod's start, build, selftest and bench, and its
  termination), with each run through `research run`.
- **CPU first.** The work so far is all on CPU:
  - M2 (with M1) is merged onto #193 (on #192). The CPU selftest in zk mode passes 31 of 31 on RoPE at m = 25, and the
    circuit pin matches #192's.
  - The CUDA changes are compile-checked on the VM with nvcc 13.3 (sm_89) before any pod.
  - The first pod is one L40S, for build, `selftest --zk --gpu`, the GPU-vs-CPU byte-equality check and the overhead
    bench against M0.
