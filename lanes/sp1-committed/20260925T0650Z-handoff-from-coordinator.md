---
lane: sp1-committed
kind: handoff
from: coordinator
created: 2026-09-25T06:50Z
---

# Core schemes landed (PR #15, main 00ffe398): add a vllm-v1 variant next to frame-v3

Both commitment schemes are now first-class for proof backends (user decision 11:41 PM PT): **frame-v3** and **vllm-v1** (vLLM's existing framing, now core-defined: PR #15 merged on main 00ffe398: `verity.commitments.frame_v3` + `vllm_v1`, leaf schemas `sha256/row/v1` and `blake3-keyed/row/v2`, vllm-v1 lowering in its PROTOCOL.md §8-9 with per-level opening traces, and the four-variant `benchmarks/commitments` commit_cost benchmark). Backends must be able to prove over vLLM's commitments: Table 2 gets lines for both schemes and Table 3 splits serving (commitment) and proving time for both. Order: finish frame-v3 where under way, then the vllm-v1 variant. Merge origin/main (>= 00ffe398) into your branch and use the core schemas and vectors (drop any local stand-in). The survey gate still applies to in-circuit hash gadget design. Also: PR #18 (main 6fdd261b) makes algebraic-hash results admissible and flagged.
