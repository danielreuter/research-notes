---
lane: vllm-coordinator
kind: handoff
from: vllm-more-exports (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4)
created: 2026-09-26T13:54Z
---

# vllm-more-exports REOPENED: #67 export re-run on vyv-more-exports-moe2 (1x L40S community, 251 GB, $0.79/h), Commit only, ends about 16:30Z

- **Scope** (root's reopen): re-run #67 with PR #80 (the export's draw budget starts after the population build) and PR #63 (MoE expert cuts), on the tree `cursor/vllm-67-rerun-0df4` @ `8f2f1624` (#63 + #80). Budget about $12; stop at the budget or the 16:45Z guard.
- **Pod:** `vyv-more-exports-moe2`, pod `b83fk4drgx340u`, registered with guard 90. Bootstrap run `r20260926-134954-df82`.
- **Plan:** Commit only (`--stages commit`), over #67's Build restored from its preserved run (`r20260926-082002-43e0` `programs/`, workload digest `7b79c784…`). Build and Match already passed at 09:46Z and 10:57Z. With no Match dir the live oracle compare isn't armed (a logged warning), which the export doesn't need.
  - That saves about 2.5 h, and the rest fits before 16:45Z: bootstrap, manifest rebuild (15 min), Commit and replay (about 100 min), export (about 30 min).
- **Cost:** about $2.5 at $0.79/h.
