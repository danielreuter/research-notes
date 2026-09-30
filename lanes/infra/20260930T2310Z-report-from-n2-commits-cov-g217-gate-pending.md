---
id: 20260930T2310Z-report-from-n2-commits-cov-g217-gate-pending
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: n2-commits (bc-698052e1), for the infra coordinator (bc-17cc41f1) and @circuits
---

# node-2 Commit gate: cov-g217 is queued to be compared with node 1's r20260930-175445-077e; no result yet

- **Gate pending (4:10 PM PDT):** `cov-g217` (Llama-3.2-1B, b8, greedy) is queued alone on node 2 as `verity-commit-proof-cov-g217` (prio 10).
  - It reruns node 1's Commit `r20260930-175445-077e` from the same job tree (`/workspace/jobs/src/cfb12962c56f051d`) and the same
    Build (`r20260930-174751-b0e1`, `art:f286e8fb…`), with the replay on the GPU as node 1 ran it.
  - Its row is in its own `SWEEP_DIR` (`/workspace/jobs/n2proof/cov-g217`), and nothing goes to node 1's dispatcher.
  - It starts once PoUW has no GPU job ready.
- **Compare rule:** equal run roots, equal committed leaves and manifest digests, and 460/460 replays. Node 1's run root is
  `4ed9a78373faf78b` and its program digest is `67b14828…`. Both nodes run driver 580.173.02 (node 1's record says so).
- **Held:** the other 16 Commits are in `/workspace/verity-guest/held-n2-commits/` on node 2. node2-ops' rule keeps guests out
  of `/workspace/pouw`. The offload loop (tmux `n2-commit-offload`) is stopped.
- **On pass:** release the held Commits, #557's 8 Qwen2.5 reruns first once their Builds exist. **On fail:** queue nothing.
- Script: `infra/nebius` `2de2c37e8`.
