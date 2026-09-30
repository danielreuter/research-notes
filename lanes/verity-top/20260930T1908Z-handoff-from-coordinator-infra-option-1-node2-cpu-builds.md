---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: verity-top
kind: handoff
from: coordinator (relaying root)
to: the infra coordinator (via verity-top)
created: 2026-09-30T19:08Z
---

# Option 1 from the utilization watch: run Verity's CPU Builds on node 2's idle CPUs

Root hands this to you, from the postmortem's noon line (`docs/gpu-utilization-postmortem.md`, Progress at 12:00 PM PT).

- **Why:** node 2's CPUs were 11% busy from 10 to 11 AM, while node 1's coverage is bound by CPU Builds (node 1 CPUs at 31%, down from 44%, after the dispatcher went live).
- **The ask:** run Verity's vLLM-deployment CPU Builds (the CPU queue of the GPU/CPU split) on node 2's idle CPUs, preemptibly, never during node 2's timed windows.
- **The policy already given to POUS:** `lanes/pous/20260930T1722Z-reply-from-verity-root-to-pous-one-cluster`, points 1–3. Each owner's work goes first on its own node; the other project borrows only idle capacity, preemptibly. Whether Verity may borrow node 2 at all is marked there as Daniel's to confirm.
- **First step:** a written plan to Daniel, since it's a cross-project node change. It should cover which Builds, the CPU range on node 2, how Build outputs reach node 1's GPU queue, and preemption. The `backfill` Kueue quota change you already carry needs one too.
