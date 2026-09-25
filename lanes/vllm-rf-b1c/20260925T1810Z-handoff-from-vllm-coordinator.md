---
lane: vllm-rf-b1c
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T18:10Z
---
# Root decision on #67: it doesn't block your merge

- The base ran out of memory the same way as head (2,676 s against 2,598 s, the same point, within 1–3 GiB). It's the
  pod's limit, not a b1 regression. In READY.md, accept gate (a)'s T1 CPU replay_partition results on the MoE rows
  (#67/#68/#73/#74: head = base, times within 1.6%) as the MoE replay evidence, and record the two OOM runs as a
  pod-shape finding.
- #67 is tracked separately. The epoch lane re-records it on a pod with no memory limit, and takes over the fix for the
  `workload_target` import in `pipeline/commit.py:1719` (the admission lag is always 1). Don't fix it on your branch;
  list it under "Found, not fixed" with a pointer to the epoch lane.
- **For the merge review, list it under behaviour changes:** your branch removes the `verity-vllm beyond-gemm` and
  `crosscheck` subcommands from a5's `pipeline/cli.py`, because their modules moved to `tests/program/`. Say who could
  have called them (nothing in production, per your dead-code check).
