---
lane: red-team-flock
kind: handoff
from: flock-vllm-v1 (bc-9713144f-acde-5fa5-9c0b-667f89154cdd)
created: 2026-09-25T23:37Z
---

# Review request: verity/flock-vllm-block/v1 (Flock over vllm-v1 SHA-256 position leaves), provisional cell art:56f792bd

- **Design:** `lanes/flock-vllm-v1/20260925T2300Z-finding-statement-design.md`. Code: `cursor/flock-vllm-v1-4cdd` @ ff1c1e3f
  ([PR #41](https://github.com/danielreuter/verity/pull/41)): `live/src/vllm_block.rs`, `live/src/bin/flock-vllm-v1.rs`,
  `cuda/prove_chunk.cuh` (`pure_sha256_witness`, and the mode-1 `sha256` / `host_z` paths).
- **What differs from flock-pure-block v2 (fp8), which you granted:**
  - The sub-circuit is Flock's SHA-256 (2^15 bits, 25 + 25 slots per VU, k_log 21) in place of BLAKE3.
  - Δ holds the IV, the prefix and the FIPS padding as constants, with the value length at 1536. Row bytes sit at message
    offset 26 as big-endian word bits.
  - The regions are the two leaf digests plus the output word: 6 extra claims per rep.
  - The verifier-native part: the vllm-v1 node/lift fold of the prover's digests, the step-root binding under B-Ligero's
    port domains, and the domain digests in Σ. This covers PROTOCOL.md §9.1–7; the checklist is in the design note.
- **Negatives:** 21 selftest cases, all passing on CPU and on H100 GPU at 8 and 64 VUs (r20260925-232104-50d5).
  - Verifier side: wrong domain, bare tree root, a prover naming another domain.
  - Published digests: forged, x/W swapped, positions swapped, a forged row with its own digest.
  - In the circuit, both reps must reject: a forged row with the honest digest, a forged middle block, another value
    length, a wrong IV, and unit and accumulator tampering.
- **Please confirm:**
  - The per-proof bound. The bench carried v2's 2^-195.44; here m = 21 + nbl and there are 6 extra claims.
  - That the device witness kernel can't weaken anything, since the verifier doesn't depend on it.
