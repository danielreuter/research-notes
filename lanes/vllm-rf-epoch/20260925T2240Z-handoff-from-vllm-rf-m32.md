---
lane: vllm-rf-epoch
kind: handoff
from: vllm-rf-m32 (bc-7039be6c-2a9f-5501-af51-ee96bf96b428)
created: 2026-09-25T22:40Z
---
# M mod 2^32 fix: 271a0952 (lane/vllm-rf-m32), gates green

`271a0952` (non-epoch, cherry-pickable, one file + tests): `scheme.chunk_header` passes `M & 0xFFFFFFFF`, as the CUDA kernels
write it, so #4's Commit (M = 5036944512) no longer raises `InvalidArtifact` in `native_host.verify`. Bytes for M < 2^32 are
unchanged. Gate (b) on the same pod shows no new failures or skips (`lanes/vllm-rf-m32/READY.md`). Please report #4's Commit result
with it to the coordinator.
