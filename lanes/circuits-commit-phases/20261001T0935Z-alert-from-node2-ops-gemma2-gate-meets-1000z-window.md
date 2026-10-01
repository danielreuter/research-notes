---
id: 20261001T0935Z-alert-from-node2-ops-gemma2-gate-meets-1000z-window
campaign: verity
lane: circuits-commit-phases
kind: alert
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6). Report only.
---

# Your gemma2-2b `fix1` Commit on node 2's GPU 3 will be preempted at 10:00Z (3:00 AM PDT) by Pearl-C4's all-GPU timed window

- **The run:** `r20261001-090342-83af`, `gate_job_n2nb.sh commit fix1 gemma2-2b__…b8__i1024__o128…`, leased with
  `--max-min 150 --preemptible` from 09:04Z, so to 11:34Z.
- **Where it is:** at 09:28Z it was 24 min into the single-core "weights of record" step (`verity_vllm.pipeline.cli commit`
  at 99% CPU), with GPU 3 at 2%. `gpu-idle-in-lease` fired at 09:10Z.
- **What happens at 10:00Z:** pouw-fp4's Pearl-C4 window takes all 8 GPUs (`gpu-lease 8 --wait --timed`, booked in node 2's
  `/workspace/pouw/fill/windows`). Your lease is preemptible, so it gets SIGTERM about 56 min in.
- **Your call:** let it run to the preemption, or stop it now and relaunch after 10:30Z. The next windows are 11:30Z (30 min),
  12:05Z (15), 13:00Z and 14:00Z.
- **For later launches:** direct `gpu-lease` runs don't read `fill/windows`, but fill jobs do. Pick a `--max-min` that ends
  before the next booked window.
