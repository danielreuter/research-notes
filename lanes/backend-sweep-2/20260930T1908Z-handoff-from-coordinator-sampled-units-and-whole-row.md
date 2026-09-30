---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: backend-sweep-2
kind: handoff
from: coordinator (relaying root)
to: backend-sweep-2 (bc-62b7c7a1)
created: 2026-09-30T19:08Z
---

# Two approvals from root (utilization watch, postmortem noon line)

**(b) Approved: whole-row proving for the K = 2,048 GEMM coordinate.** This answers your question to the RC.
- **Budget:** about 14 GPU-hours.
- **Stop:** as soon as the measured whole-row cost agrees with your per-shape extrapolation within 5%. Report both figures and the stop point in your hourly line.
- **Queue:** the same ready-file path (`/workspace/jobs/ready/backend-sweep-2/`), as `provers` jobs. M0's pinned benches keep priority.

**(a) New: prove the 460 sampled units of every passing vLLM deployment.**
- **Scope:** 58 deployments pass so far (the labels at 11:41: 58 pass, 22 fail, 74 unsupported). Root estimates a few GPU-hours in all.
- **Queue:** one ready file per deployment, or per chunk of units, on the prover build you already use. Check the first deployment's selftest and byte identity before queueing the rest, as with the shapes.
- **As more pass:** add deployments as they're labelled pass.
- **Record:** each job writes a labelled Attempt naming the deployment and its unit range.

**Order:** (a) first, since it's cheap and every deployment benefits; then (b), interleaved with the remaining Llama shapes.
