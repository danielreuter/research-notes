---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T23:30Z
---

# For review: ShaFp8 (sha256/row/v1 leaves) on fp8-hopper, H100. CPU and GPU selftests pass.

- **What changed:** nothing in the statement since the ShaFp8 note (23:15Z). This is the same layout with the fp8-hopper
  netlist (pin 904ca664, which you granted at 23:20Z). The binary is at ad0aa41d. The only change after 5b41d4af is that
  the host witness is cached across reps; the verifier path is unchanged.
- **Evidence:** run r20260925-232133-996e, art:29438e24, H100. CPU and GPU selftests pass every case at 8 and 64 VUs,
  including the SHA cases (a substituted midstate and an altered padding word). Sessions at 4,096 and 8,192 VUs are
  accepted.
- **To review:** the SHA prefix, midstate and padding constants (Δ constant rows), and the big-endian message-word
  mapping in `pure_block.rs` (`sha_prefix`, `be_words16`, `delta_sha`). These are shared with the fp8-ada, bf16-hopper
  and bf16-ampere SHA lines.
