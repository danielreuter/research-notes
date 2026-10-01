---
id: 20261001T0036Z-handoff-from-proofs-bf16-hill-cpu-collisions
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-bf16-hill
---

# Three lanes' 74-gemm-hill.sh jobs pin the same cores on node 1; a lock fix is on my branch, and the other two lanes need it too

**Blocker for clean baselines.** The dispatcher runs every job under `taskset -c 96-159`, so only explicit `CPUSET`s keep jobs apart. Tonight they overlap:
- **proofs-verify-overlap** passes no CPUSET, so the script's default of 48 pins **96-143**. That was true of its base run (4:56 to 5:06 PM PDT) and is true of the `ahead10` run now.
- **proofs-flock-fp** pins nvf4 to 128-143 and mxf4 to 112-127, which are my K=8192 and K=4096 slices.

So my seed-coin K=2048 and K=4096 points, the new K=4096 point and the running K=8192 point all shared cores with another prover and verifier. The verifier is CPU-bound and dominates the session, so it's the most distorted part. The new K=2048 point (96-111, 5:20 to 5:25 PM) overlapped no other hill job.

**Fix, on `cursor/proofs-bf16-hill-95d4`:**
- **fe8fca029:** `74-gemm-hill.sh` takes a lock on every 16-core slice it pins (`cpu-slices.sh`, under `/workspace/jobs/slices`). A job that finds its slices held waits for them.
  - With CPUSET, it takes the slices CPUSET touches.
  - Without CPUSET, it takes any ceil(CPUS / 16) free slices. CPUS still defaults to 48, so the verify-overlap lane's runs keep their 48 cores.
- **1c1436102:** a per-slice sampler flags a point `cpu-slice-shared` when anything else used its cores, and records the GPU memory peak.
- **Ask:** proofs-verify-overlap and proofs-flock-fp take `backends/flock/pod/{74-gemm-hill.sh,cpu-slices.sh,gemm_hill.py}` from fe8fca029. The locks only separate jobs that all take them.

**Also found:**
- **Statement size isn't a free lever.** An m = 35 statement peaks at about 70 GiB on the 96 GB card (K=2048 and K=4096), so m = 36 needs a memory cut first.
- **Kueue keeps preempting my K=16384 job** (three pods so far). It restarts from scratch each time.

**My plan:**
- Re-run K=4096 and K=8192 step 0 on fe8fca029, from a second tree, so a preempted K=16384 pod can't pick up new code.
- Append every point, with its flags, to the roll-ups.
