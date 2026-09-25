---
lane: flock-gpu-link
kind: handoff
from: coordinator
created: 2026-09-25T18:16Z
---

# Add a head-to-head to docs/flock-gpu-route.md: route (a) on GPU vs a pure Flock backend (relation + hashes, the census unit circuit), both at 2^-128

The root asks (11:15 AM PT) for a section in `docs/flock-gpu-route.md` that compares, on the same GPU class and instance
count:
- **Route (a) on GPU:** A-GKR prime side + Flock hashes + the cross-field link (L1–L4). Project it from your L2/L4
  design and the CPU route (a) numbers: prime ~2.6 s, Flock ~21 s with live remote coins at 4,096 VUs.
- **A pure Flock backend** proving the relation plus the hashes in one binary-field circuit: the census unit circuit
  (`docs/binary-backend-census.md`; flock-bench measured the unit + BLAKE3 leaves at 0.42–0.58 s on a 5090 at 4,096 BF16).
  There's no link at all.

Both at **2^-128 whole-proof**. C8 is decided: A-GKR's hash budget counts toward the bound. Use Flock's 128-bit profile,
not Fast100 (flock-128: ~1.0× on H100, 2× on CPU).

For each: prover time, verifier time, proof and communication size, rounds, x native, and what's still missing to measure
it. Close with a recommendation on which route deserves the CUDA work. That call decides whether your L2/L4 build continues.
