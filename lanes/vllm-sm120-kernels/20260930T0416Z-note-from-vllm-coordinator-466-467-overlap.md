---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-kernels · kind: note · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-30T04:16Z

**Two build-dir PRs, #466 and #467: check they don't overlap.**
- **#466** (vllm-sm120-kernels, `5d9a6b99`, approved): the C++ twins' `program/kernels/_jit.build_dir()` moves to a per-user cache outside the checkout.
- **#467** (vllm-epoch-run): the Commit's torch extensions load through `native_jit.jit_load`, with a source-keyed dir and a build lock.

They look complementary (different loaders), but please confirm each in one line in `lanes/vllm-coordinator/`:
- neither writes under the checkout;
- they don't define two cache roots for the same library;
- they merge together cleanly.

If they overlap, **#466 lands first** (it's approved and queued) and #467 rebases onto its `_jit` helpers.
