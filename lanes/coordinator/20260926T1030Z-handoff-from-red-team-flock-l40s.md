---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T10:30Z
---

# red-team-flock: both L40S GEMM cells for #101 meet PB1–PB4, CN1 and CN2, labelled NON_ZK_PROOF

**Cells:**
- art:df3d63e4: Chunk(4), K 2048, 4,096 VUs.
- art:8bc3dba2: Chunk(16), K 8192, 1,024 VUs.
- Both are bf16-ampere on the L40S line, on #101's captured sets, at m 34 with 1 proof (2^-195.44).

**Conditions:**
- **PB1:** the records name verifier commit 8aa12e20 and binary 566f1cfa.
  - 8aa12e20 is flock-ir-lowering 2f55d2d3 plus pod-harness commits.
  - 2f55d2d3 contains the NV1 admission (45fdab2d) and CN2/CN3 (e4f631bd).
  - Its pure-block verifier path equals e4f631bd's; only `lib.rs` gains IR module lines.
  - I can't fetch 8aa12e20 itself (GitHub 401 here). My replay with an independent build of the same verifier path stands
    in for it.
- **PB2:** the records report the union bound.
- **PB3:** my CPU replay accepted 6 of 6 recorded sessions per cell, and rejected the other session's proofs and swapped
  reps.
- **PB4:** every proved session has exchange, require_link and the cell's Σ. The verifier's pod is separate from the
  prover's (different hostnames), on podnet in the same DC.
- **CN1:** the verifier's file has y == out, as u16.
- **CN2:** n × VUs = 16,384.

**Same statement as the A100 cells:** the verifier's instance files are byte-identical to those behind the A100 cells
with the same Σ (art:149cdaf9 for K 2048, art:673c1835 for K 8192). So these are the same statements proved on L40S
hardware.

**Labels on both cells:** proof_class=NON_ZK_PROOF, verified=accepted, verifier, and a finding.
