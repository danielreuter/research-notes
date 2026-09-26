---
lane: vllm-vu-export
kind: handoff
from: vllm-more-exports (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4)
created: 2026-09-26T14:24Z
---

# vllm-more-exports: no #67 art ids today. The re-run is blocked on L40S capacity; it's ready on a #63+#80 tree for a later window

- Thanks for the #80 fix and the #63 review (your 1344Z handoff). The combined tree is `cursor/vllm-67-rerun-0df4` @ `8f2f1624`.
- The re-run didn't happen. Secure L40S had no stock, and the two community L40S pods couldn't init CUDA. It can't land before the 16:45Z guard now.
- **Recipe for whoever runs it** (Commit only, about 2.7 h on a secure L40S with 233 GB or more):
  - Restore #67's Build from art:8180df8f (`programs/` and `evidence/build_summary.json`), plus `build_workload/workload_program.json` with `workload_digest` `7b79c784…`.
  - Run `STAGES=commit PROGRAM_DIGEST=7b79c784… verity-vllm row run …`.
  - It's in `lanes/vllm-more-exports/` (report, "Reopened 13:45Z"). `evidence/pod-scripts/vme_row.sh` supports `STAGES`, `RUN_TESTS` and `SKIP_GRAPH`.
