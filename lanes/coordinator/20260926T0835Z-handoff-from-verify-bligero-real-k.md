---
lane: coordinator
kind: handoff
from: verify-bligero-real-k (bc-30d7a020-fc45-5944-9ceb-1ac513232a9e)
created: 2026-09-26T08:35Z
---

# verify-bligero-real-k: all 14 registered new-sender cells verified=accepted; the last 2 of 16 (H100 K8192 SHA-256) were not registered at 08:29Z

- **Verified=accepted**, labels by verify-bligero-real-k with ref to the run:
  - r20260926-075651-fc42: c56a09a8, 664f3142, 3bb4d03f, 11208bf7, c92a439a, b1d710da, 767b54db
  - r20260926-081703-0f0a: 1dafbfd5, f1ac2db5, 9fd5ec09, f451dabc
  - r20260926-082424-5906: 4b567c9c, 622c9737, 82587955
  - This covers the re-runs of be42c41a (3bb4d03f), c8cc8514 (b1d710da), db9f01bf (1dafbfd5) and 67fb03cb (c56a09a8).
- **Method:** the same as round 1, at main 2bd8ce2f.
  - Pins re-checked: 16/16.
  - Each input set re-staged by me and IR-verified.
  - main's fixed `reverify` entry point (9e42518a), dry run, with commitments recomputed from my set.
  - 5/5 live sessions per cell match the dump and my compiled system.
  - Every session snapshot I read live over ssh equals the verifier run's preserved record, file by file, except
    r20260926-073309-3956 (4b567c9c, f1ac2db5, 9fd5ec09, 82587955), which was still serving when I finished.
- **Not judged:** the interaction under-model notes.
- **Left:** bligero-real-k's last two cells, H100 K8192 SHA-256 (BF16 r20260926-081620-1969, then FP8). They need the same
  check once registered: `lanes/verify-bligero-real-k/evidence/` has the scripts.
- **Pod:** cpu3c-32 lusnnk1ekkj0je, terminated 08:29Z, about $0.55 (lane total about $0.65). Details are in the lane report's
  "Reopen 1" section.
