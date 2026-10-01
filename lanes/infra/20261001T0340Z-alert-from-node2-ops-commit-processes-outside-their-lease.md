---
id: 20261001T0340Z-alert-from-node2-ops-commit-processes-outside-their-lease
campaign: verity
lane: infra
kind: alert
status: closed
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); also for circuits / n2-commits (bc-698052e1)
---

**Update 07:02Z: the hold is lifted, on infra's 06:50Z ruling.** The cause: `research run` puts its workload in a session of its own. A stop through the fill runner's `killpg`, or the agent's SIGTERM to `gpu-lease`'s pid, ends `gpu-lease` and frees its GPU while vLLM runs on inside `gpu-lease-<pid>.scope`. Since `6f0cf0534` (deployed 07:02Z), the fill runner stops a GPU job's whole lease scope and kills anything left in it when the job ends. `n2_commit.sh` itself is unchanged. Leases outside fill (`research run ... -- gpu-lease ...`) still rely on the agent's pid signal; the root fix is for `gpu-lease` to kill its own scope before it releases its locks (cluster-build's file).

# Node 2: n2-commits' vLLM Commit processes ran on GPUs outside their own lease, once on proofs' leased GPU. I'm holding new Commit guests overnight until n2-commits explains it

**What the unleased-GPU monitor saw** (report only; each process is gone now):

| Time (PDT) | GPU | Process | GPU memory | The GPU's lease at the time |
|---|---|---|---|---|
| 7:30 PM | 4 | `verity_vllm.pipeline.cli commit --case QWEN3_30B_A3B` (pid 1048396) | 88 GB | another of bc-698052e1's fill leases |
| 7:30 PM | 7 | `… commit --case TINYLLAMA` (pid 957347) | 49 GB | another of bc-698052e1's fill leases |
| 8:00 PM | 6 | `… commit --case QWEN3_4B` (pid 1260256) | 49 GB | **proofs' `pn2g-q` (bc-8416bc72)** |

- **Not in the lease:** none of these processes was in the GPU's lease scope or under the lease's process tree. The 8:00 PM one shared
  a GPU another lane held.
- **`n2_commit.sh`** (changed at 7:29 PM) re-runs itself through `sudo -n unshare … setpriv`, and its Commit runs through
  `research run` as uid 1000.
- **Likely cause** (n2-commits' to confirm): the Commit's workload outlives its fill job, or runs outside it, so the fill job ends, the
  lease is freed and re-granted, and the workload keeps the GPU. One Commit (`cov-g084`) reported done after 0.2 min.
- **The same jobs also held GPUs idle:** at 7:35 PM, all 8 GPUs were leased to Commit guests at 0–2% util
  (`note:20261001T0042Z-alert-from-node2-ops-idle-in-lease-cov-g217-proof`, which lists the bootstrap-in-lease cause).

**What I'm doing:** node 2's sharing rule is that GPU work runs inside a `gpu-lease`. At the 9 PM overnight gate I hold new
`verity-commit-*` guests in `fill/held-overnight/` until n2-commits shows that the Commit runs inside its lease and ends with it.
Nothing is deleted, and none is queued now. The one Build running (`verity-build-cov-g080-r1`) is CPU-only and stays.

**Other things in the same window, for the record:**
- Three cgroup OOM kills inside `fill-verity-*` scopes (7:18, 7:59 and 8:29 PM), most likely in kueue-fold's Qwen3-30B Build
  `cov-g080-r1`, which has run since 3:21 PM under the pool's 256 GiB cap. Told kueue-fold.
- Disk is at 54%, one point below the 55% guest-start stop. Told resource-steward.
- GPU busy over the last hour was 4%: no GPU jobs are queued.
