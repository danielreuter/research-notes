---
lane: verifier-cost
kind: report (working; updated at every checkpoint)
created: 2026-09-24T19:05Z
status: open
base: main 22741456
branch: lane/verifier-cost in ~/projects/verity-main-wt/verifier-cost
pods: vy-live2b-verifier-ro (pitmqu0zrycw5i, cpu3m 8 vCPU, EU-RO-1, $0.44/h; keep-pod until custody) + GPU provers one at a time
budget: $10; FINAL 01:10Z
---

CHECKPOINT 22741456 (19:08Z) [open] context read; custody put of 5.25 GB sessions running on verifier pod (run r20260924-190646-2eca); next: extract session measurements, plan GPU prover runs

# verifier-cost: real verifier cost for every Table 2 cell (D3)

Spec: campaigns/afternoon/BRIEF.md `### verifier-cost`. Inbox at start (19:04Z): nothing.

## 1. Custody of the 2026-09-23 live sessions (vy-live2b-verifier-ro:/workspace/live/sessions)

- 19:05Z: 50 session dirs (5 `c…` challenge-stream, 45 `s…` Ligero), 3782 files, 5,252,776,381 bytes (885 sub_NN.proof /
  .stmt / .coins, 45 .bin, 1080 json). Server still up (pid 14506, `live serve --jobs 8 --threads 1 --target-bits 128`).
- Whole tree (proofs included) put from the pod as one run-files/v1 with a 3 h minted credential passed via `--env`:
  run r20260924-190646-2eca, script `evidence/pod-scripts/01-preserve-sessions.sh` (also writes files.txt, sha256.txt).
