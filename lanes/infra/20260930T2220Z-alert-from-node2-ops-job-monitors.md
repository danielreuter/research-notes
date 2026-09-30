---
id: 20260930T2220Z-alert-from-node2-ops-job-monitors
campaign: verity
lane: infra
kind: alert
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); node 2's idle-in-lease and unleased-GPU monitors, report only (the glide path's rule)
---

# Node 2's job monitors: one line for each catch, relayed to the owning coordinator

- 3:05 PM PDT: `gpu-idle-in-lease` on GPUs 0 and 5. Two of bc-6289d8b0's `kt-e70b` runs (PoUW) sat at 0.9% and 5.2% util, were stopped
  at `max_min`, and passed on retry, with about 0.2 GPU-h idle. Relayed to bc-2aa33ad8
  (`note:20260930T2220Z-alert-from-node2-ops-idle-in-lease-kt-e70b`).
- 3:20 PM PDT: `gpu-idle-in-lease` on GPU 5: bc-2aa33ad8's `hsplit-w3` at 0.8% util (low-util chunk, ended `more`). Relayed in the same `lanes/pous/` note.
- 3:40 PM PDT: `gpu-idle-in-lease` on GPUs 0, 2 and 4: bc-0de2d624's `harness-perdie` screen at 3–6% util. The jobs are done and the kind's efficiency is 94%. FYI, relayed in the same note.
