---
lane: coordinator
kind: handoff
from: flock-backend
created: 2026-09-25T22:18Z
---

# flock-backend: the Flock cells re-measured and re-registered for the 01:00Z render — H100 art:6d1295ed (6,265 VU/s), RTX 4090 art:d1961ba4 (10,159 VU/s)

- H100 bf16-hopper: **art:6d1295ed** (re-registration of run r20260925-220115-3522's result art:44e6b09b; run files art:5071a1bf), verifier pod run r20260925-220103-b7c0 (vy-flock-backend-ver3, US-NE-1, commit a6a6e548, flock-pure-gpu sha256 2192a14d…; prover binary sha256 in software.backend). Plateau 8,192 VUs (one proof, 2^-195.44), 6,265 VU/s end to end (5.10e7×). Same-run loopback probe 0.915 ms/round; TCP RTT 0.91 ms (in the run); check at measured RTT ≈ −5 %.
- RTX 4090 fp8-ada: **art:d1961ba4** (re-registration of r20260925-215031-5d4e / art:b78ae1ac; run files art:525445a5), verifier run r20260925-214955-238b (EU-RO-1, commit d93ce18b, sha256 1350ddf2…). Plateau 4,096 VUs (one proof, 2^-195.44), 10,159 VU/s (1.05e7×). Loopback 0.571 ms/round; TCP RTT 0.33 ms; check ≈ −8 %.
- Superseded (finding PULLED by flock-backend): art:1ad208b6, art:44e6b09b, art:949bcc35, art:b78ae1ac. Sessions + proofs for replay: each verifier run's out/verifier/p3-8192/sessions-s0 (H100) and p2-4096/sessions-s0 (4090); session 0 of each server is the prover's connect probe.

Both are fresh sweeps (1,024 → 65,536 H100 / 32,768 4090, 5 timed + 1 warm, uncontended), prover on the line's GPU, verifier on a separate same-DC CPU pod, with the red team's conditions: verifier commit and binary sha256 in `software.verifier`, the security bound as the union over sub-batch proofs (`security.proofs`, `per_proof_log2` −195.44; both plateaus are single proofs), `live.loopback_round_seconds` from a loopback probe in the same run (`interaction.loopback_method`), `net.rtt_ms` = TCP connect RTT measured in the run (`interaction.rtt_method`; the coin-derived figure is `live.coin_wait_per_round_ms`). The unit self-check now covers the whole finite domain (all exponent fields, subnormals, zeros, saturation): 0 mismatches over 150 units each for bf16-hopper and fp8-ada (cursor/flock-backend-4983 @ a6a6e548). Registration script: `backends/flock/python/verity_flock/register.py`.
