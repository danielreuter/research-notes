---
lane: coordinator
kind: handoff
from: flock-backend
created: 2026-09-25T21:24Z
---

# flock-backend: pure-Flock cells measured — H100 bf16-hopper 6,235 VU/s (5.1e7×), RTX 4090 fp8-ada 10,080 VU/s (1.06e7×); pods terminated; one interaction-check question

- **H100 BF16 (bf16-hopper, flock-pure-block/v2, flock-pure-gpu e5d54118):** r20260925-210043-fcce, result art:1ad208b6
  (run files art:deebc030); verifier pod r20260925-210019-0afe (separate same-DC pod, 0.68 ms TCP). Sweep 1,024 → 65,536:
  3.76k, 4.90k, 5.68k, 6.19k, 6.19k, **6.24k (32,768 = 4 × 8,192/proof)**, 6.23k VU/s; uncontended; 5 timed + 1 warm.
  Session at plateau: e2e 5.26 s (5.24–5.29), commit 0.049 s, 1,160 round trips, 12.5 MB up / 0.15 MB down, wait 1.71 s,
  verify 1.19 s, proofs 4.9 MB. overhead.vs_native_peak = 5.12e7× (B-Ligero keyed-BLAKE3: 2.76e8×).
- **RTX 4090 E4M3 (fp8-ada):** r20260925-211314-4880, art:949bcc35 (run files art:d3048b92); verifier r20260925-210919-f0c6
  (EU-RO-1, 0.31 ms TCP). 1,024 → 32,768 at 4,096/proof (8,192/proof OOMs, CUDA error 100 at m34, r20260925-210253-e8d3):
  6.53k, 8.61k, **10.08k (4,096)**, 9.98k, 9.93k, 9.89k VU/s. e2e 0.406 s, 262 round trips, wait 0.205 s. 1.06e7×.
  Statement is flock-gpu-link's new fp8 layout → red team pending, so (prov.).
- Earlier/slower runs kept as history: r20260925-203522-4cf9 (old binary, 3.29k), -204856-00b7 (6.14k at 8,192, loaded
  verifier host), -201921-2024 (guard counted our own prover as contention). All preserved.
- **Question (tables-switch's ±10 % interaction check):** Flock's per-round wait is set by prover-side live-hook glue, not the
  wire: loopback is ~0.83 ms/round, same-DC 1.42 ms (H100, US-MO-1) and 0.78 ms (4090, EU-RO-1). Against the 1 ms / 100 Gb/s
  reference the H100 cell lands at +11.9 % and the 4090 at −12.4 %, i.e. both outside ±10 % in opposite directions. Is that
  reason M for a measured same-DC session, or does the check only guard projected/loopback numbers? (Records carry
  `interaction.t_total_includes_wait`, `live.prover_compute_seconds`, `net.wait_seconds`, `net.rtt_ms`, `hello_rtt_ms`.)
- Sent to verify-flock-pure (2123Z) for replay + labels. Red-team request for v2 is in my 2040Z handoff; add the fp8-ada layout.
- Pods: vy-flock-backend-h100/-ver/-ver2 (US-MO-1), -4090/-ver4090 (EU-RO-1) all terminated by 21:21Z. Lane spend ≈ $5.5.
