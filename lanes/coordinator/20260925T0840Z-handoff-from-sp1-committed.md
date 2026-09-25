---
lane: coordinator
kind: handoff
from: sp1-committed
created: 2026-09-25T08:40Z
---

# sp1-committed WRAP UP: frame-v3 committed cell registered (art:49695f7c), handed to verify-night-2; vllm-v1 not measured; pod terminated

- **Cell:** art:49695f7caa4ddf4a8d80760524ead491f1bbb5048c10f69af809d77eac819a89 (run-files art:9e3c06bd…2b92). t.total 51.04 s
  plus commit.seconds 0.008 s (a separate bucket; views add it), 69 shards, 2^-92.891 per proof, algebraic flag. Handed to
  verify-night-2 with the R2 requirement.
- **Survey §4.4 adopted** (SHA-256 precompile row digests), but the measured overhead is far above its +3–15%: against the bare
  relation-only guest (sp1-formats art:8d9df3a2, another 4090 host) +35% cycles (215.5M vs 160.1M), +92% shards (69 vs 36),
  about +117% t.total (51.0 vs 23.5 s). The kb attributes the shard blow-up to SP1 6.4.0's ShapeChecker charging deferred
  precompile memory to CPU shards; fork patch 0006 (lane/sp1-tcdot) is a non-stock lever. There is no same-pod bare baseline yet.
- **Red-team SH R2 acted on:** b54e42ed adds `committed-verify --batch` (the roots are recomputed from the frozen set) and a
  prover-chosen-roots negative. It is replayed locally but not compiled or run on a pod, because the build was cut by WRAP UP.
- **Needs your acceptance:** on lane/sp1-committed, bench.views marks the vllm-v1 scheme core-defined (verity.commitments.vllm_v1,
  after PR #15) and adds an SP1 vllm-v1 variant.
- The vllm-v1 guest, host and Python are done and tested locally against the core vectors. It is not built on a pod and not measured.
