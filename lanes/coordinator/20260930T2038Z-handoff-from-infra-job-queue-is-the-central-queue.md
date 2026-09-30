---
id: 20260930T2038Z-handoff-from-infra-job-queue-is-the-central-queue
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# Research coordinator: "Job queue stage 1" is the central queue (#586). Merge checks become one job kind on it, not a second queue

Daniel's ruling 6: you keep the merge trains until "Job queue stage 1" runs a whole train. Infra reads that as the one central
queue across both nodes (#586), not as a separate `research jobs` service. The merge check becomes a job kind on that queue,
using its CPU slots on node 1, with the same `research merge` evidence.
- **Your review is needed** on cluster-build's small `tools/research` change, `research run --queue`, which cluster-build will
  send you in this lane.
- **If you see a reason to keep `research jobs` separate,** say so in `lanes/infra/` with your reasons. Otherwise infra plans
  the train as wave 5 of `note:20260930T2035Z-draft-one-queue-cutover-and-onboarding`.
