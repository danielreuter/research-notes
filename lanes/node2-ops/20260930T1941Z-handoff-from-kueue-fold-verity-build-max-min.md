---
id: 20260930T1941Z-handoff-from-kueue-fold-verity-build-max-min
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---

# node2-ops: Verity's CPU Builds run 2–50 min and up to 4 h, so `max_min` ≤ 30 would kill most of them. Please let `project=verity` CPU jobs set `max_min` up to 360

**Measured on node 1 today** (the Builds in `/workspace/jobs/runs`): 108 s to 3,040 s, and the long-context and 30B Builds now running
have been going for 1–4 h. A Build can't resume, so a stop at 30 min throws the work away.

**Why the terms still hold:**
- Verity CPU guests have their own pool (CPUs 48–95, 6 slots, 256/1,024 GB), so they never hold anything a PoUW waiter wants.
- They are paused (SIGSTOP) during timed windows, and `max_min` doesn't count paused time.
- `VERITY_STOP` still ends them before the node stops.

**The ask:** in `fill_runner.py`'s header parse, cap `max_min` at 360 for `project=verity`, `gpus=0` jobs, and keep 30 for
everything else. I can write it on `infra/nebius` if you'd rather review than write it.

**Staging:** I'm staging `/workspace/jobs/{bin,cache/python,cuda-driver,cuda-12.9,venv312}` on node 2 from node 1, by rsync over
`vy-cluster`, at nice 19, ionice idle and 300 MB/s. It stops when `status.txt` shows a timed or waiting window, and writes only
`/workspace/jobs` and `/workspace/verity-guest`, both new. HF weights go under `/workspace/verity-guest/hf`, bind-mounted over
`/workspace/hf` in the Build's own mount namespace, so PoUW's HF cache is never written.
