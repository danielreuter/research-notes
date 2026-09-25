---
lane: coordinator
kind: handoff
from: flock-backend
created: 2026-09-25T23:38Z
---

# flock-backend: BUG in my Flock interaction fields — net.wait_seconds (and the loopback per-round figure) include the verifier's final replay; correcting and re-registering now (affects art:6d1295ed for 01:00Z)

- The session's `wait_s` is the transport's total wait, read after `Finish`, so it includes the verifier's end-of-session
  verification (`verdict.verify_s`, 0.15–1.0 s) and the two proof uploads, none of which is inside `e2e_s`/`t.total`.
  Every Flock record I registered therefore overstates `net.wait_seconds`, understates `live.prover_compute_seconds`,
  and overstates `live.loopback_round_seconds` and `live.coin_wait_per_round_ms` (the loopback probe has the same bias).
  `t.total`, `e2e`, VU/s and the overheads are unaffected. Found on the A100 run, where wait (1.19 s) exceeded t.total (1.17 s).
- Corrected coin wait = wait_s − verify_s: H100 bf16 art:6d1295ed 0.425 → ~0.09 s (0.31 ms/round), loopback 0.92 → ~0.23
  ms/round; 4090 art:d1961ba4 0.203 → ~0.05 s (0.19 ms/round), loopback 0.57 → ~0.05 ms/round.
- Consequence for the ±10 % check: with honest waits the prover spends only ~0.1 ms/round on the network beyond its loopback
  glue, while `net.rtt_ms` (a fresh TCP connect, 0.9 ms H100 / 0.33 ms 4090) is a connect time, not an established-
  connection round trip. At the connect RTT the H100 check comes out about −16 %. The right RTT for the formula is an
  established-connection ping-pong; I'm adding that probe (an echo on the verifier pod) for the next runs.
- Doing now: re-register art:6d1295ed and art:d1961ba4 (and the two new cells) with the corrected wait/loopback fields and
  a note; I'll send the new ids before 00:15Z. Please hold 6d1295ed/d1961ba4 out of the render if the renderer can't
  take the corrected ones in time.
