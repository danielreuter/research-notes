---
lane: wave-a100-3
kind: handoff
from: coordinator
created: 2026-09-24T06:15Z
---

# Three facts that change your close-out (read before registering more)

1. **`reg.sh` drops `run_id`, so the contract rejects every result it registered** ("contract: run_id must be a non-empty
   string", e.g. art:03fd448a, art:152a9c68, art:1fab5137 in the tables-fix render
   `lanes/tables-fix/20260924T0602Z-tables-render.md`). The workaround is obsolete: `reverify.py` handles a bench-result
   whose run_id is the runner's `b-ligero-...` since f68ab6da. For the remaining runs, delete the
   `m["bench_run_id"] = m.pop("run_id", None)` line (keep run_id as the runner wrote it). Do not re-register the old ones.
2. **None of wave-a100-2's A100 results can enter Table 2**, whatever their labels: `bf16-ampere-v3 / -v3x4` read a
   non-frozen synthetic set (`bench-instances-bf16-ampere/v1`, a runner bug fused-phases fixed at 9989797f), the v1 cells
   predate the phase-sum fix (buckets were per-key medians across reps), and `--tile 64x64` (shared64) is a drill-down by
   user decision. Register for the drill-downs and custody only; no extra dumps beyond what reg.sh already does for the
   two hash cells.
3. A new lane `fill-dc` re-runs the A100 row on the fused-phases tip with a fresh pod. Do not hand your pods over: terminate
   both as soon as custody is confirmed (the prover host was too noisy for timing anyway).

In your FINAL, mark each cell "drill-down only" with its reason letter (I instances, P phase-sum, S shared hashing).
