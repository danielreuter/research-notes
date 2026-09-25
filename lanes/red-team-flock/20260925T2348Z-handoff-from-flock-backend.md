---
lane: red-team-flock
kind: handoff
from: flock-backend
created: 2026-09-25T23:48Z
---

# flock-backend: four Flock cells (re-)registered with corrected coin waits — H100 bf16 art:bb289d47, 4090 fp8 art:ed0047be, H100 fp8 art:37215309 (new), A100 bf16 art:fb526e50 (new)

| line | result (new) | runs (prover / verifier pod) | plateau | VU/s | overhead | check at TCP-connect RTT |
|---|---|---|---|---|---|---|
| H100 BF16 (bf16-hopper) | art:bb289d47 (supersedes 6d1295ed) | r20260925-220115-3522 / r20260925-220103-b7c0 | 8,192, 1 proof | 6,265 | 5.1e7× | −13 % |
| RTX 4090 E4M3 (fp8-ada) | art:ed0047be (supersedes d1961ba4) | r20260925-215031-5d4e / r20260925-214955-238b | 4,096, 1 proof | 10,159 | 1.05e7× | −11 % |
| H100 E4M3 (fp8-hopper) NEW | art:37215309 | r20260925-231324-0465 / r20260925-231308-e3f4 (US-MO-1) | 16,384, 1 proof | 13,497 | 4.7e7× | −12 % |
| A100 BF16 (FIRST, bf16-ampere, frozen vu-k1536) NEW | art:fb526e50 | r20260925-232627-dc51 / r20260925-232617-62cb (US-KS-2, verifier on a second A100 pod: no CPU pods there) | 4,096 = the whole frozen set, 1 proof | 3,470 | 2.9e7× | +4 % |

All: flock-pure-block/v2, 5 timed + 1 warm, uncontended, security 2^-195.44 (one proof each; union field recorded), verifier commit + flock-pure-gpu sha256 in software.verifier, same-run loopback probe, net.rtt_ms = TCP connect median measured in the run. The A100 uses the frozen bench-instances/v1 vu-k1536 set (rebuilt on both pods from the committed seeds, sha256-checked against the manifest), so its batch cannot exceed 4,096; bf16-ampere lowering pin e97ecb9e (flock-backend 3b0ebfb0, matches flock-gpu-link). Superseded ids carry finding PULLED: 6d1295ed, d1961ba4, 32f35945, 053fb31c.

**Correction in all four:** the session `wait_s` included the verifier's end-of-session replay (read after Finish); net.wait_seconds, live.prover_compute_seconds, live.coin_wait_per_round_ms and live.loopback_round_seconds are now computed from wait_s − verify_s (interaction.wait_correction). Honest coin waits are 0.05–0.18 s per session (0.18–0.57 ms/round), loopback 0.05–0.23 ms/round. Against those, the fresh-TCP-connect RTT (0.33–0.91 ms) overstates the per-round network cost, so the ±10 % check fails at −11 to −13 % for three cells. An established-connection RTT probe (echo on the verifier pod) is the fix for the next runs; say if you want the cells re-run with it.
