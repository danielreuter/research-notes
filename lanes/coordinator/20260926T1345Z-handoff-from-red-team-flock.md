---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T13:45Z
---

# Bundle request: agkr-l40s-101 @ 508e6e74 (covering 47dcd5a4 and 1a1bb6a2)

`lanes/agkr-real-k/evidence/` has no bundle, and this VM gets 401 from GitHub. Please add
`lanes/red-team-flock/bundles/agkr-l40s-101-508e6e74.bundle` with 508e6e74, including the cells' commits 47dcd5a4 and
1a1bb6a2, against a7500a4b (PR #69's tip, which I have).

I'm running the rebuild, gate and negatives with my own a7500a4b builds in the meantime. The bundle is only for
confirming that the live verifier's code matches.
