---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator
created: 2026-09-29T08:32Z
---

# #289's merge request confirmed at 96815f64 (main 610ee10f merged in); #327 at 94b079b1 follows it

**Superseded (2026-09-29 08:54Z)** by `20260929T0854Z-merge-request-flock-314-289-327-on-180f8771.md`: new heads on `main` `180f8771`.

- **#289:** head `96815f647d732224a36f1945ec53c2cd435a855a`. `main` `610ee10f` (D4, trains T1–T6) is merged in, and #314's build fix and check step are still inside.
  - The conflicts were mechanical:
    - `main`'s multi-table session: #289's `host_units` and rep-1 reuse are carried per table, keyed by (session tag, table);
    - `check.py`'s groups: `flock-circuit-build` still runs after `circuit-check`.
  - Local results: the GPU builds compile, `check_build.sh` passes, 72 lib tests pass, `verity-check` passes (35), and `verity-flock` passes 363 tests. Its 3 failures here were memory kills under xdist on a 15 GB VM, and they pass serially.
  - It needs the train's recorded check, with the agreement inputs.
  - The merge request is `20260928T1824Z-merge-request-refinement-train-flock-gemm-witness-289.md`, updated.
- **#327:** head `94b079b1215815fc6cddc07d845827626632349e`, a clean merge of #289's new head. The GPU builds compile, and its tests and `check_build.sh` pass.
  - It merges after #289.
  - The merge request is `20260929T0150Z-merge-request-flock-host-bucket-327-after-289.md`, updated.
- **#336's GPU run is held** until Daniel's budget, and I've marked its request.
