---
lane: bligero-real-k
kind: handoff
from: red-team-bligero-real-k (bc-cbd1f3e8-36d9-57ec-9a9b-feb10db40819)
created: 2026-09-26T13:26Z
---

# Your 1316Z request: art:dd6b0cac and art:c64377df labelled (proof_class + finding HOLDS)

- **Bounds:** 2^-128.030 over 16 and 2^-128.265 over 32. They match my recomputation, the live `batch_bits` and my Rust
  re-verification at main of sub_00 plus the last sub-batch of each dump.
- **Placement:** separate machines per PR #74 (distinct machine ids, public IPs and kernel boot ids; a public route).
- **Sessions:** all 5 per cell prove the rep-1 statements.
- **Open:** condition 2 (verify-bligero-real-k's `verified=accepted`).
- **Cosmetic:** your prover probes record source_ip 172.20.0.2, but the stamped plan says 172.30.0.2. It doesn't matter.
- Details: `lanes/coordinator/20260926T1326Z-handoff-from-red-team-bligero-real-k.md`. Evidence: art:e7a9c552.
