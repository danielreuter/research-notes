---
id: 20260930T2138Z-handoff-from-infra-t3-first-job-lean-audit
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: T3's first lane job is proofs' `lean-audit` kind (CPU, about 5–10 min). Register it; proofs' worker submits it once you post "queue live"

- **The job:** the Lean audit of `packages/verity/lean`. It has no Lake dependencies, takes about 5–10 minutes, produces small
  output, and passes or fails deterministically.
- **The kind to register:** `lean-audit`, phase `cpu` / `cpu-m`, `max_wall` 20 min, outputs = the audit report, owner `proofs`.
- **Who submits:** proofs' worker (Slack thread `1790803610.751809`). Post "queue live" plus the exact command in `lanes/infra/`,
  and proofs will be ready by 9 PM PDT.
- **Fallback:** one K=2048 whole-row GPU chunk (1 GPU, about 40 min), once node 2's guest staging is in.
