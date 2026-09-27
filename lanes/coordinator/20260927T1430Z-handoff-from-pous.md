---
lane: coordinator
kind: handoff
from: pous
created: 2026-09-27T14:30Z
---

# pous -> coordinator: a new POUS lane `pous-gpu` will use one H100 pod for about 3 h, with its own $100 budget; please advise

Daniel has authorized $100 for POUS GPU measurements over the next 3 hours, until about 17:30Z. That budget is separate from the research cap.

- **Lane:** `pous-gpu`. It's a Cursor cloud worker following `kb/cloud-lane-setup.md`, and it checkpoints in `lanes/pous-gpu/`.
- **Pod:** a single H100 SXM, named `vy-pous-gpu` (registered, `--project verity`, with a guard), used through `research run --on … --campaign pous`. It will be terminated before FINAL.
- **Code:** measurement kernels live in the POUS store, not in Verity.

Questions (reply in `lanes/pous-gpu/` so the lane sees them directly):
1. Should POUS spend be tracked separately from the $300 research cap, and does the steward need anything to do that?
2. Which RunPod H100 template or bootstrap should it use? Is `backends/direct/ligero/pod_bootstrap.sh` right for a CUDA kernel-timing lane, or is there a better one?
3. What's the recommended way to `research run` a source tree that isn't a Verity commit, for example `--source <dir>` with a throwaway git repo?
4. Are there pitfalls with fused-kernel timing on your pods: clocks, MIG, or other tenants?
