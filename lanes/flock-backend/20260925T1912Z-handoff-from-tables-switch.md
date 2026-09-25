---
lane: flock-backend
kind: handoff
from: tables-switch
created: 2026-09-25T19:12Z
---

# The record your first pure-Flock result needs to fill the Flock column with no renderer change (and one blocker: rule K, the line's GPU)

The Flock column is on main (PR #32, `a1ccdecd`). The test
`test_a_pure_flock_record_fills_the_flock_column_without_renderer_changes` on lane/tables-switch (`backends/numerical/tests/bench/test_views.py`)
pins the record below: a `bench-result/v1` with these fields lands in the Flock column on the `frame-v3 · keyed-BLAKE3 rows`
line of its subcircuit, marked `(prov.)` until red-team-flock grants the statement. Reply here (or to the coordinator) if a
field doesn't fit what you emit.

**Family and configuration (the key):**
- `workload_fingerprint.software.backend.name` starts with `flock` (the word, case-insensitive: `flock union, flock-128-r2 (backends/flock)`).
  A name starting `verity-gkr` is A-GKR, which is where route (a) goes.
- It must not also match a `drilldown.VARIANTS` recogniser (a B-Ligero or A-GKR name). The configuration is then
  `Flock (flock-128-r2, live coins)` (`views.FLOCK_CONFIG`, scheme `frame-v3/blake3-row`, full relation).

**Profile, class, security:**
- `profile` = the line's target name (`verity.verification.target.TARGETS`, for example `fp8-ada-mma-draft/2026-09-22`).
- `proof_class` = `NON_ZK_PROOF` (Flock's declared class on main), with `zk_mode = "none"` (the contract validator requires it).
- `security.achieved_log2` = the accountant's whole-proof bound (≤ −128 passes the default filter; flock-128-r2's
  −195.5 does), and `security.target`.

**Hardware:** `hardware.gpu.name` must be the line's device under `tables.normalise_sku`, for example the RTX 4090 on the FP8 Ada line.
Rule K rejects a run on any other device. **A CPU-pod run fails K on every line.** If the Flock prover is CPU-only, the run
still has to happen on the line's GPU pod, with its `hardware.gpu` recorded. If that's wrong for Flock, tell the coordinator:
it's a rule question for Daniel, not something to work around in the record.

**Workload:** `B` = the instances in the timed run; `instances` = the line's frozen set or its stream ref (seed, recipe,
manifest), or an `instance-equiv/v1` accepted by a non-producer (rule I).

**Measurements:**
- `t.total` (proving), `commit.seconds` (the warm median of committing the batch's values afresh), and the six buckets
  summing within the phase-sum rule (`contract.validate`).
- Interaction record (live: coins every squeeze): `rounds.sequential_depth` (round trips on the critical path, ~1,070),
  `net.bytes_out`, `net.bytes_in`, `net.rtt_ms`, `net.wait_seconds` (or `t.total_live`), and a top-level
  `interaction: {rtt_method: "..."}` naming how the RTT was measured. The measured prover compute plus the wait must land within
  ±10% of `t.total + rounds × 1 ms + bytes ÷ 10 Gb/s` (the reference: same datacenter). Otherwise it's reason M.
- `protocol: {warm: true, runs: ≥5, statistic: "median", contended: false}` and `sweep: {id, point, plateau: true}` (the
  plateau rule: sweep B upward and mark the plateau point).

**Custody and verification:** `refs.run_files` (or `refs.proof`) naming a preserved dump (`--custody-r2`, or `research data put --preserve`),
plus a label `independently_verified=true` by someone other than the producing lane or campaign (for example the live
verifier's session or a red-team lane).
