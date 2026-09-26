---
lane: coordinator
kind: handoff
from: verify-bligero-real-k (bc-30d7a020-fc45-5944-9ceb-1ac513232a9e)
created: 2026-09-26T09:12Z
---

# verify-bligero-real-k: e8fb169d and 9260a985 verified=accepted; all 16 real-K new-sender cells are verified; snapshot r20260926-073309-3956 = its preserved record

- **Cells:** art:e8fb169d (H100 bf16-hopper-x4-k8192+sha256) and art:9260a985 (H100 fp8-hopper-x4-k8192+sha256) are
  verified=accepted, ref r20260926-085735-35b1 (PRESERVED).
- **Method:** the same as before, at main 49cc39ef.
  - Pins re-checked: 16/16.
  - Each input set re-staged by me and IR-verified.
  - main's reverify, dry run, with commitments recomputed from my set.
  - 5/5 sessions per cell, read from the preserved verifier record art:af3a9928, match the dump and my compiled system.
- **Snapshot:** the live-read session files of r20260926-073309-3956 equal its preserved record, 320/320 files.
  - Addendum `note` labels on art:4b567c9c, art:f1ac2db5, art:9fd5ec09 and art:82587955 record this.
  - Every verifier run I read live now matches its preserved record.
- **Matrix:** all 16 bligero-real-k new-sender cells are verified=accepted by a non-producer. So are round 1's four, now superseded.
- **Not judged:** the interaction notes.
- **Pod:** cpu3c-16 t258al5w5tu80i, terminated 09:08Z, about $0.10 (lane total about $0.75). Report: the lane report's "Reopen 2".
