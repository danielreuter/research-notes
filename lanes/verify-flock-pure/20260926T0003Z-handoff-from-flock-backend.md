---
lane: verify-flock-pure
kind: handoff
from: flock-backend
created: 2026-09-26T00:03Z
---

# flock-backend: H100 FP8, RTX 4090 FP8 and A100 BF16 Flock cells re-measured with the open-connection RTT probe (next publish); all pods terminated

Same protocol as art:1589ffe1 (H100 BF16, 23:52Z): flock-pure-block/v2, separate same-DC verifier pod serving its own instance
files, 5 timed + 1 warm, uncontended, same-run loopback probe, `net.rtt_ms` = 64-byte Ping round trip on the open session
connection (30 probes before Hello in every timed session), coin waits without the verifier's end-of-session replay, the
verifier's commit and `flock-pure-gpu` sha256 in `software.verifier`, security = union over the plateau's proofs.

| line | result | prover run / verifier-pod run | plateau | VU/s | overhead | check at the measured RTT (my recomputation) |
|---|---|---|---|---|---|---|
| H100 E4M3 (fp8-hopper) | **art:c3e83404** (supersedes 37215309) | r20260925-234521-e968 / -234513-abf3 (US-MO-1; verifier on an L40S pod, no CPU pods) | 16,384, 1 proof, 2^-195.44 | 13,598 | 4.7e7× | −1.9 % (RTT 0.36 ms) |
| RTX 4090 E4M3 (fp8-ada) | **art:7afeecbe** (supersedes ed0047be) | r20260925-234847-b20d / -234753-f84e (EU-RO-1, CPU pod) | 4,096, 1 proof, 2^-195.44 | 9,836 | 1.09e7× | +3.8 % (RTT 0.18 ms) |
| A100 BF16 (FIRST, bf16-ampere, frozen vu-k1536 059103cf…) | **art:167e64a8** (supersedes fb526e50) | r20260925-235101-1e2d / -235045-9b93 (US-KS-2; verifier on a second A100 pod, no CPU pods) | 4,096 = the whole set, 1 proof, 2^-195.44 | 3,757 | 2.7e7× | +0.2 % (RTT 0.14 ms) |

- bf16-ampere: `lowering_sha256` e97ecb9e… (PINS in verity_flock/lowering.py since 3b0ebfb0; the verifier ran with `--pin`), AM1.
- Verifier commit 0864d146 / e52eca82 (the same verifier code; e52eca82 only adds the instance-writer scheme switch). The only
  verifier change since a6a6e548 is the additive `Ping` answer (see 23:52Z).
- Replay: plateau sessions under each verifier run's `out/verifier/p<i>-<n>/sessions-s0` (session 0 is the prover's connect probe).
- SHA-256 row leaves: `verity_flock.instances --scheme sha256` (sha256/row/v1, verifier-side generation) and
  `verity_flock.negatives` (honest control, valid chain over the wrong row, forged output word; all three pass on the
  keyed-BLAKE3 path at 8 VUs — they are refused at Σ, the digest regions themselves are exercised by flock-gpu-link's selftest)
  are on cursor/flock-backend-4983 @ e52eca82. No SHA cells yet: flock-gpu-link's SHA timings are host-witness bound
  (not cell-quality until its device SHA-256 witness), and this round's budget went to the RTT re-runs. Say if you want them run as is.
