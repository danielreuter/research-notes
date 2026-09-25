---
lane: poseidon-v1
kind: handoff
from: coordinator
created: 2026-09-25T10:36Z
---

# main 5ac28010: the GPU committer is verified byte-identical on A100 (sm_80) and H100 (sm_90); the Poseidon2 int8 sm_90 fix is merged

hash-commit-2 (`lanes/hash-commit-2/20260925T0932Z-report-hash-commit-2.md`):
- The frame-v3 / vllm-v1 committer passes 98/98 byte-identity on both GPUs. bf16-hopper+blake3 at 4096 VUs gives commit
  evidence c90e6d0d, identical on 4090, A100 and H100. Committer 3.5 ms on H100, 5.7 ms on A100.
- 2a92fe61 (now on main) fixes `Poseidon2Torch`'s int8 MDS on sm_90: cuBLASLt INT8 needs row counts that are multiples
  of 32. Before it, the torch int8 route failed on H100.

**For you specifically:** check which Poseidon2 path your H100 runs used. If any H100 result went through the torch int8 MDS
before this fix, it either failed or fell back. Say which in your next checkpoint. A fallback that changes timings but not
bytes is fine, but the footnote should name the path.
