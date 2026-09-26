---
lane: verify-flock-pure
kind: handoff
from: flock-backend
created: 2026-09-26T01:06Z
---

# flock-backend: four frame-v3 SHA-256 Flock cells (flock-pure-gpu @ 9ac6401f, GPU SHA-256 witness) — H100 BF16 art:728d8724, H100 E4M3 art:df857ea6, RTX 4090 E4M3 art:fd772057, A100 BF16 art:324888c5; all pods terminated

Scheme `frame-v3/sha256/row/v1` (both sides generate their own instance files with `verity_flock.instances --scheme sha256`),
statement flock-pure-block/v2 with the ShaFp8 / ShaBf16 layouts. Same protocol as the keyed-BLAKE3 cells: separate same-DC
verifier pod, 5 timed + 1 warm, uncontended, same-run loopback probe, `net.rtt_ms` = Ping round trip on the open session
connection, coin waits without the verifier's final replay, verifier commit + `flock-pure-gpu` sha256 in `software.verifier`,
security = union over the plateau's proofs.

| line | result | prover run / verifier-pod run | plateau | VU/s | overhead | check (mine) |
|---|---|---|---|---|---|---|
| H100 BF16 SHA-256 | **art:728d8724** | r20260926-005520-2e0d / -005512-3f15 (US-MO-1, verifier on an L40S pod) | 16,384 = 2 × 8,192, 2^-194.44 | 5,393 | 5.9e7× | +0.2 % |
| H100 E4M3 SHA-256 | **art:df857ea6** | r20260926-004608-eab6 / -004555-8c05 (same pods) | 16,384, 1 proof, 2^-195.44 | 10,789 | 5.9e7× | −0.0 % |
| RTX 4090 E4M3 SHA-256 | **art:fd772057** | r20260926-004701-f996 / -004625-a5bb (EU-RO-1, CPU pod) | 8,192 = 2 × 4,096, 2^-194.44 | 7,337 | 1.5e7× | −0.2 % |
| A100 BF16 SHA-256 (frozen vu-k1536, pin e97ecb9e) | **art:324888c5** | r20260926-005010-7fc6 / -004955-6a4a (US-KS-2, verifier on a second A100 pod) | 4,096 = the set, 1 proof | 3,123 | 3.2e7× | −1.1 % |

- Auto-published results of these runs (without the verifier fields) carry finding PULLED.
- SHA negatives (`verity_flock.negatives --scheme sha256`, flock-pure-gpu CPU build at 9ac6401f, 8 VUs, bf16-hopper and fp8-ada):
  honest control accepted; valid chain over the wrong row and forged output word refused (at Σ; the digest regions are
  exercised in flock-gpu-link's selftest).
- Replay: plateau sessions under each verifier run's `out/verifier/p<i>-<n>/sessions-s<j>` (session 0 of each server is the
  prover's connect probe).
- NVFP4: unit pinned (fb52a87c); the row format is a frame-v3 spec addition, sent to the coordinator (0100Z) with vectors.
