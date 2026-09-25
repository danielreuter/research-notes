---
lane: hash-commit
kind: handoff
from: coordinator
created: 2026-09-25T06:50Z
---

# commit-gpu: benchmark commitment throughput (serving time) for BOTH schemes with the commit_cost benchmark

Both commitment schemes are now first-class for proof backends (user decision 11:41 PM PT): **frame-v3** and **vllm-v1** (vLLM's existing framing, now core-defined: PR #15 merged on main 00ffe398: `verity.commitments.frame_v3` + `vllm_v1`, leaf schemas `sha256/row/v1` and `blake3-keyed/row/v2`, vllm-v1 lowering in its PROTOCOL.md §8-9 with per-level opening traces, and the four-variant `benchmarks/commitments` commit_cost benchmark). Backends must be able to prove over vLLM's commitments: Table 2 gets lines for both schemes and Table 3 splits serving (commitment) and proving time for both. Order: finish frame-v3 where under way, then the vllm-v1 variant. Merge origin/main (>= 00ffe398) into your branch and use the core schemas and vectors (drop any local stand-in). The survey gate still applies to in-circuit hash gadget design. Also: PR #18 (main 6fdd261b) makes algebraic-hash results admissible and flagged.

For commit-gpu specifically: measure commitment throughput (serving time) for frame-v3 AND vllm-v1, each with SHA-256 and BLAKE3 where the scheme allows (frame-v3: SHA-256 words, SHA-256 rows, keyed-BLAKE3 rows; vllm-v1: its SHA-256 position/fa2h leaves; BLAKE3 only if its spec allows), through `benchmarks/commitments` commit_cost (four variants), byte-identical to the core vectors, 4090 then H100. Report GB/s and ms per 4096 instances per variant as bench-result/v1 with the commitment bucket.
