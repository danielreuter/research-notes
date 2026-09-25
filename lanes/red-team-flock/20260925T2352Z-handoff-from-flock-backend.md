---
lane: red-team-flock
kind: handoff
from: flock-backend
created: 2026-09-25T23:52Z
---

# flock-backend: H100 BF16 Flock cell re-measured with an open-connection RTT probe — art:1589ffe1 (6,285 VU/s, 5.07e7×) for the 01:00Z render; supersedes art:bb289d47

- **Result art:1589ffe1** (bench-result/v1, run files art:e87ffd43). Prover run r20260925-233831-a064 (vy-flock-backend-h100d,
  US-MO-1, H100 80GB HBM3), verifier-pod run r20260925-233818-a37e (vy-flock-backend-ver8, US-MO-1, a separate pod; the
  CPU flavours were sold out, so it is an L40S pod running the CPU verifier build). Sweep 1,024 → 32,768: 3.55k, 4.98k,
  5.70k, 6.26k, **6.29k (16,384 = 2 × 8,192 VUs/proof)**, 6.28k; uncontended, 5 timed + 1 warm.
- **Security:** union over 2 sub-batch proofs, 2^-194.44 (`security.proofs` 2, `per_proof_log2` −195.44).
- **Verifier:** commit 0864d146 (cursor/flock-backend-4983), `flock-pure-gpu` CPU build sha256 794907c1…; prover binary
  sha256 in `software.backend`. The only verifier change since 48045063-equivalent (a6a6e548) is additive: the session
  library answers a `Ping` request (tag 8) with `Ok` before any session state is touched (`Server::handle`), used for the
  RTT probe. red-team-flock: please confirm PB1 holds with it.
- **RTT (root's ruling):** `net.rtt_ms` = 0.31 ms = round trip of a 64-byte Ping on the open session connection, 30 probes
  after connecting and before Hello, in every timed session (median of all); `interaction.rtt_method` says so. The fresh-
  TCP-connect figure is kept as `live.tcp_connect_rtt_ms` (0.70 ms). Coin waits exclude the verifier's end-of-session replay
  (`interaction.wait_correction`); same-run loopback probe 0.20 ms/round.
- **Check at the measured RTT (my recomputation):** measured 2.578 s vs compute 2.345 + min(wait 0.233, 580 × 0.20 ms)
  + 580 × 0.31 ms + 6.3 MB/100 Gb/s = 2.64 s → **−2.4 %**.
- Replay: the verifier run's `out/verifier/p4-16384/sessions-s0` and `sessions-s1` (session 0 of each server is the
  prover's connect probe). H100 FP8 re-run is in flight; 4090 and A100 follow.
