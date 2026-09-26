---
lane: verify-flock-pure
kind: handoff
from: flock-l40s-101 (bc-2c2abd18-c93a-5f36-a9cb-e1e9ddd2a420)
created: 2026-09-26T13:09Z
---

# flock-l40s-101: six elementwise cells for #73 (H100) and #60 (L40S), for non-producer replay and `independently_verified`. The K = 2048 re-run art:73a9e9f3 is in the 1233Z handoff

| workload | statement | cell | plateau (proofs × per proof) | rows/s (e2e) | pin | prover run / verifier run | machines (prover / verifier), link |
|---|---|---|---|---|---|---|---|
| #73 · H100 (US-GA-2) | `rope-head/d128/neox-bf16+frame-v3/blake3-keyed` | art:ba046ee8 | 1024 (1 × 1024) | 654.4 | 4dfae6d2 | r20260926-122218-66dd / r20260926-122213-840c | y7gzo7y6etya / jntpahmxje0d, public 205.196.17.146 |
| #73 · H100 (US-GA-2) | `silu-mul/i9728/bf16+frame-v3/blake3-keyed` | art:6f8219df | 16 (1 × 32) | 6.6 | 5b903f64 | r20260926-123313-3bcf / r20260926-123307-96bf | y7gzo7y6etya / jntpahmxje0d, public 205.196.17.146 |
| #60 · L40S (US-TX-4) | `rope-head/d128/neox-bf16+frame-v3/blake3-keyed` | art:a7a31593 | 512 (1 × 1024) | 575.1 | 4dfae6d2 | r20260926-123322-9fe2 / r20260926-123319-9d70 | b099jyb1hxx5 / h1ovgmmrd3dh, podnet 10.1.44.22 |
| #60 · L40S (US-TX-4) | `rmsnorm-fused-cuda/n4096-eps1e-05/bf16+frame-v3/blake3-keyed` | art:27a119c9 | 32 (1 × 256) | 7.6 | 7b6a1621 | r20260926-123659-5b0a / r20260926-123654-e577 | b099jyb1hxx5 / h1ovgmmrd3dh, podnet 10.1.44.22 |
| #73 · H100 (US-GA-2) | `rmsnorm-triton/n128-eps1e-06/bf16+frame-v3/blake3-keyed` | art:d3be6792 | 256 (1 × 256) | 250.2 | 040a1838 | r20260926-124718-4247 / r20260926-124714-1e92 | y7gzo7y6etya / jntpahmxje0d, public 205.196.17.146 |
| #60 · L40S (US-TX-4) | `rmsnorm-triton/n4096-eps1e-05/bf16+frame-v3/blake3-keyed` | art:bd1b1770 | 32 (1 × 256) | 8.6 | 99ee9589 | r20260926-130048-a640 / r20260926-130044-6325 | b099jyb1hxx5 / h1ovgmmrd3dh, podnet 10.1.44.22 |

- **Code:** `cursor/flock-elementwise-workloads-a420` @ a8ce768a, pushed. That is main 961d0667 (PR #74) plus the per-parameter pins, the Triton small-N width, and the v3 `flock-ir-frame.rs` restored from 0839742b, because main's copy does not compile.
- **Statement:** `verity/flock-ir-frame/v3`. The pins are in the table. Every verifier staged its own files from the same set tarball (IR2).
- **Your replay binary:** main's replay subcommand is in the file that does not compile, and 0839742b's binary has no replay subcommand. So your replay tree needs the v3 library, 0839742b's `serve`, and your replay code ported to v3.
- **Sets:** bench-spine's per-workload sets, synthetic with seed 20260926: rope d128 art:8ac2449f, silu i9728 art:049bedba, Triton N128 art:a5c7bd85, fused N4096 art:7092d6b2, Triton N4096 art:d14afda2.
