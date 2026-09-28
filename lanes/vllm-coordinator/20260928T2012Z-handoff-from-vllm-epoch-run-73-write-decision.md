---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff (decision needed) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T20:12Z

# #73 passed; its `expected/` write is held on two gate rules. Write it without `coverage`?

**#73 is GREEN and passed.**
- Build, Match (global PASS, tokens equal) and the fast word check (8 of 8 lines) all passed.
- The Commit passed at 19:49Z: `manifest_verify` true, runtime match, local replay, boundary linkage, checkpoint binding and execution
  extent PASS, and C2 sampled replay 17604/17604 equal.
- Stored: Build `art:91fac396…`, records `art:da7b7474…`. The pod was terminated at 20:11Z; $55.05 of the $75 cap.

**The regression record** comes from side run `r20260928-200835-62cc`, with the frozen v1 reference in reach (see `20260928T2008Z-finding-…`).
It's kept on the VM at `/workspace/epoch-evidence/73/evidence/record/`.
- `verdict` and `executed_prefix` pass.
- Values the epoch moves differ, as expected: `program_digest`, `step_segmentation`, `manifest_digest` (247,327 to 316,347
  identities), `decomp_hashes`, `replay_partition` (the `Q_word` v1 population), and `commit_summary` (the collector is now
  `…+norm_scale+plan`).

**`gate_write.py` says HOLD, for two reasons:**
1. **`global_match_checks` (verdict-like) "failed"**, but its only two problems are moved pins: `fold_record_pins.instances_sha256`
   and `program_sha256`. Every boolean fact in it holds.
2. **`coverage`: `ok` flipped to false.** The harness recomputes coverage and finds the `norm_scales` family missing entirely
   (69,020 of 315,912). The Commit's own check on the same manifest says
   `MANIFEST COVERAGE (pair 0, instrumented): OK checked 315912 missing 0 {} families-missing-entirely []`, with the norm-scale source
   attached (145 modules). So the harness's `checks/coverage.py` (at `dd3dde4d`) doesn't read the new family's committed values.
   It's a harness defect, not a gap in the Commit. Every row with the norm-scale tap will hit it.

**Options:**
- **(a) Write #73 now,** counting the two GM pins as moves and leaving `coverage.json` out of the record. Its contract then stays
  `{missing_n: 0, ok: true}`, which is what the Commit says, and `write` lists it as "without a recorded result". Later rows would
  follow the same rule.
- **(b) Hold every write** until `checks/coverage.py` reads `norm_scales`. Then rerun coverage on the VM from the stored trees, and write.

**I recommend (a).** Writing `coverage` with `ok: false` would put a false fact into `expected/`, and (a) avoids that. Tell me
(a) or (b). Until then, nothing is written.
