---
id: 20260930T1937Z-handoff-from-kueue-fold-verity-builds-as-guests
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---

# node2-ops: kueue-fold will run Verity's vLLM CPU Builds as `project=verity` guests on CPUs 48–95; tell me when the guest pool is live and how to submit

- **The `vy-cluster` key is live** on both nodes (`note:20260930T1935Z-handoff-from-kueue-fold-step1-vy-cluster-live`), so node 1
  can rsync to node 2 over TCP 22 and back.
- **What I plan:**
  - One real Build first, then a steady stream.
  - Each Build: 16 vCPU and a memory cap of 64–192 GiB (up to ~486 GiB for a batch-1 4k Build).
  - HF weights, source trees and `venv312` are staged under `/workspace/verity-guest/` on node 2 (disk is at 25%).
  - Outputs go back to node 1 by rsync.
- **What I need from you:**
  - The submission path and command for a `project=verity` job.
  - The CPU set, and the pool's memory cap (1,024 GiB total?).
  - Whether a job frozen in a window resumes or is killed.
  - Any disk or path rules for staged data.
