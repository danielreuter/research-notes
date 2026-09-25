---
lane: tables-switch
kind: handoff
from: flock-backend
created: 2026-09-25T20:40Z
---

# Flock cell records: t.total INCLUDES the live coin waits (buckets do too); use t.total − net.wait_seconds as prover compute in the ±10 % check

- Flock draws every challenge live, so its phases (and `t.total`, the six-bucket sum) include the prover's coin waits; the
  record says so in `interaction.t_total_includes_wait: true` and carries `live.prover_compute_seconds = t.total −
  net.wait_seconds`, `t.total_live` (= t.total), `net.wait_seconds`, `live.network_wait_seconds` (wait minus the verifier's
  handling), `live.verifier_round_seconds`, `rounds.sequential_depth`, `net.bytes_out/in`, `net.rtt_ms`, and
  `interaction.hello_rtt_ms`.
- H100 8,192-VU example (r20260925-202748-e488): t.total 2.47 s, wait 0.44 s, 290 round trips, 3.1 MB up: compute 2.02 +
  wait 0.44 = 2.47 vs reference 2.02 + 0.29 + 0.0003 = 2.31 (+7 %). With t.total itself as "compute" the reference
  would be 2.76 and the check would fail at −11 %, so please read t.total − net.wait_seconds when the flag is set.
- `N_subbatches` / `batching{total, per_proof 8192, in_flight 1}` are set above 8,192 VUs (m35 is Flock's largest config).
