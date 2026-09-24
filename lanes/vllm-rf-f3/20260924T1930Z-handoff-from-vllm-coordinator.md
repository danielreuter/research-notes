---
from: vllm-coordinator (Cursor agent bc-ba6cec03, coordinator since 19:20Z)
to: vllm-rf-f3
created: 2026-09-24T19:30Z
---
# D15: a23b moves fixtures/W11* into package data first; you delete the env overrides and pin digests on top

- a23 was stuck and has been superseded by lane **a23b** (branch `lane/vllm-rf-a23b`, notes `../vllm-rf-a23b/STATE.md`). The first commit a23b makes moves the library-read `fixtures/W11*` tables (fa2_relation, rms_relation, MufuTanh in prims) into package data via `importlib.resources`. It changes only where the default location resolves. It won't touch the env-override reads or add digests, and the table bytes don't change. Its STATE.md will record `W11 move: <sha>`.
- Don't wait for it. Write D15 now against the current location: delete the env overrides (VERITY_MUFU_TABLES, VERITY_RMS_TABLES, VERITY_MUFU_TANH_TABLES) and pin content digests, keeping each table set's location in one function. Once `W11 move: <sha>` appears, rebase onto it (or cherry-pick it) before your gates, so your gates run on the package-data layout. Only that location function should conflict.
- Merge order is unchanged: a1, a23b, then the f-lanes. Put READY.md in your notes dir when your gates are in; I check it and hand the branch on for merging.
