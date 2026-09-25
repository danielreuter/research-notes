---
lane: verify-night-2
kind: handoff
from: coordinator
created: 2026-09-25T10:24Z
---

# Red-team verdict is in: fp8-ada+blake3 (main 3301c435) and fp8-ada-x4+sha256 (da74b03e) PASS. A cell counts once its dump passes main's reverify

See `lanes/coordinator/20260925T1130Z-handoff-from-red-team-standard-hash.md`. The BLAKE3 gadget scan found 0 free rows
for 8:0.5 (fp8-ada+blake3), 8:1 and 16:1, and the x4 shape is finishing. This is the grant my 1017Z note waited for, for
fp8-ada+blake3 and blake3-80gb's cells (same statement).
- For each 4090 fp8-ada+blake3 cell (e9932b72 first, then e7d59ab6, 5d20ad00, d6328cf5): once main's `reverify` passes
  (roots recomputed, stems = proofs = entries, batch n = count), record `verified=accepted` with ref 3301c435. On a cell
  that carried an UNDER RE-VERIFICATION finding, also record the finding CLEARED.
- A cell verified only by a pre-3301c435 reverify doesn't count. Re-run it.
- fp8-ada-x4 cells wait for the x4 gadget scan result. +sha256 cells count at da74b03e once b-ligero-sha256's tip is on
  main; until then, verify and record, but hold CLEARED.
- SP1 art:49695f7c: the red team reviewed your `19-sp1c-verify.sh` and says it closes R3 if it prints PASS on all 5 reps.
  It's a drill-down result (2^-92.9), not a Table 2 cell.
- **The first +blake3 cell that is accepted at 3301c435: send me a one-line handoff immediately.**
