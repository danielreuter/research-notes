---
id: 20260930T2249Z-handoff-from-old-circuits-and-proofs-merge-request-609
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Merge request: #609 (TP2 GPU-less Build), head 4009ec303

https://github.com/danielreuter/verity/pull/609. Granted: label `pr:609@4009ec3034d8… grant vllm-coordinator`, synced.
- It is 3 files, Build path only: `select_cuda_platform(world)` makes the platform's `device_count()` answer the declared world. It merges cleanly with `git merge-tree` on main as of 22:45Z.
- Evidence: CPU-only run r20260930-212809-14a0 and GPU-visible run r20260930-220713-8e26 have equal digests (the per-rank Programs, correspondence, workloads, and global manifest bb87df12…).
- The torch-backed tests need the node; they passed there, and the vLLM `-m "not pod"` suite has no new failures.
