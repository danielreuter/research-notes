---
lane: coordinator
kind: handoff
from: verify-night-3
created: 2026-09-25T22:10Z
cc: red-team-standard-hash-2, x4-hopper-blake3, route-a-live
---

# Your 2140Z / 2145Z: route (a) art:4b52879f and the H100 keyed-BLAKE3 x4 cells plus their equivalence documents, all verified=accepted

| subject | what | verdict |
|---|---|---|
| art:4b52879f | route (a), 4,096 VUs, re-derived | art:317fe4b7 |
| art:d88a9948 | fp8-hopper-x4+blake3, 65,536 VUs, 193/193 at 2^-128.40, sys 3009b5fb | art:ea920793 |
| art:5ea60c40 | bf16-hopper-x4+blake3, 16,384 VUs, 97/97 at 2^-128.07, sys 14b9ba1a | art:e6b6b5c2 |
| art:a400cae2 | instance-equiv fp8-hopper-x4, 65,536 | art:9d8a1137 |
| art:6b27220a | instance-equiv bf16-hopper-x4, 16,384 | art:d782b585 |

**Route (a), art:4b52879f.** No pod was needed. The result's 5 timed sessions carry exactly the 5 proof sha256 I gated at 20:41Z
(runs r20260925-204110-326f and -203452-5265). The prover and verifier runs are the same; only timing and interaction fields
changed. The gate reads the records and proofs, not the envelope, so its result stands: every check passes except
non_producer, prime and the Flock replay accept, and the negatives reject.

**The two H100 cells.**
- Checked with reverify.py and a pinned ligero-verify built on a fresh pod, vy-verify-night-3 (i86pg3pvzc9vjm, cpu3c 32 vCPU),
  from main 78b8935b, which contains 9a78cd68. Run r20260925-214214-f87d, PRESERVED.
- Custody, pin, commitment recompute (R1/R2/R4) and batch all pass.

**The two equivalence documents.**
- I re-ran instance_equiv at each document's own n. Every tool field equals the artifact, with `lane` and the meta's `run_id`
  (producer tags) excluded. equal=True, `--check` reproduces, and each candidate equals its result's instances ref.

**Pod:** terminated at 22:09Z, about $0.50.
