---
lane: coordinator
kind: handoff
from: jolt-scout
created: 2026-09-25T08:10Z
---

# jolt-scout: go/no-go = NO-GO for Table 2; an optional drill-down lane only once PR #1618 lands

Report: `lanes/jolt-scout/20260925T0647Z-report-jolt-scout.md`. Evidence:
art:a53998e6d3c89ac1e579bc974c417f0928f33aad8adea1fa0fa66148c80dbb52. Durable facts: `kb/jolt-prover.md`.

**Why no-go.** Curve Jolt (Dory/BN254) fails the Table 2 security filter on two counts:
- BN254 gives about 100-bit computational security (GT DLP by SexTNFS, ~2^99.7).
- Sumcheck challenges are 125-bit masked, for a statistical error of about 2^-110.

Fixing either needs upstream protocol changes: a pairing curve of 128 bits or more for Dory, and full-width challenges.
The Blake2b transcript is fine (no algebraic hash).

**The three targets:**
- **Curve Jolt with ICICLE** is dead. It only ever accelerated HyperKZG G1 MSMs, was removed in 2025-07/08, and the last
  rev that has it does not compile.
- **Lattice Jolt (Akita)** has no CUDA and no ZK, so I skipped it per the user's rule.
- **LayerZero's "Jolt Pro"** is closed source.

The only live GPU path is the unmerged draft PR #1618 (curve Jolt, native CUDA). It built and ran on the 4090 at
5.7-8x the 16-vCPU CPU speed at 2^24, with 2^25 as the most that fits in 24 GB.

**Measured (4090 pod):**
- The VU guest runs the verbatim bare.rs kernel at 34.1k cycles/VU. With keyed-BLAKE3 frame-v3 row leaves (the survey's
  recommendation, adopted), the committed statement is 126.1k cycles/VU; with SHA-256 it is 239.6k.
- CPU prove for B=64 committed with keyed-BLAKE3 is 30.5 s, and the proof verifies.
- BlindFold ZK adds only 3-5%.
- On PR #1618's cuda backend, B=48 committed with SHA-256 proves in 9.5 s. The PR does not yet support the BLAKE3 inline.
- Projected 4,096-VU batch on one 4090: bare ~3.3 min and committed ~5-14 min, each split across 12-86 proofs.
  SP1 bare on an A100 takes 18.5 s.

**If you want a drill-down lane later**, trigger it when PR #1618 merges or a 128-bit Jolt configuration appears.
- Name: `jolt-drilldown`.
- Scope:
  - Put the guest in `backends/jolt/` with the frozen rows and the real frame-v3 keyed-BLAKE3 leaf.
  - Carry the BLAKE3 inline into PR #1618's decoder.
  - Split batches across proofs, run the §Sweep, and record Table 3 buckets.
- Cost: 4090 ~4 h (~$3) plus an optional H100 hour (~$3), about 6-8 agent-hours. It changes no other lane's plan.

This lane's pod was terminated at 08:07Z; it cost about $1.00.
