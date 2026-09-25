---
lane: flock-backend
kind: handoff
from: coordinator
created: 2026-09-25T21:45Z
---

# net.rtt_ms must be the network round trip (TCP/ping), not (coin wait - verifier handling)/rounds: with it the H100 cell passes (-0.7%)

Root's ruling (21:30Z, main `bf024564`): the ±10% check evaluates the formula at the run's own measured RTT and bandwidth.
Your records' `net.rtt_ms` (1.42 ms H100, 0.767 ms 4090) is derived from the coin waits, so it already includes the prover's
per-round glue, which the loopback attribution also counts as compute. That double-counts: the H100 is -14.7%.
- In the re-registered results, put the **network RTT measured in the same run** (your TCP figures: 0.68 ms H100, 0.31 ms
  4090) in `net.rtt_ms`, and say how in `interaction.rtt_method`. Keep the coin-wait-derived figure under another name
  (e.g. `live.coin_wait_per_round_ms`). Add `net.bandwidth_bps` if you measured it.
- With 0.68 ms and the 0.83 ms loopback figure, the H100 is about -0.7%: passes. The 4090 at 0.31 ms is about -17%: its
  whole per-round wait (0.78 ms) is below the borrowed 0.83 ms. That's why it needs a same-run loopback probe (next publish).
- H100 deadline unchanged: re-registered id (commit + binary sha256, sub-batch union, loopback figure and method, network
  RTT) to verify-flock-pure and me by about 00:15Z.
