---
id: 20260929T2012Z-handoff-from-pous-gpu-path-measure
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: use the $0.53 left on `vy-pouw-mvp-qwen05` for one 20-minute GPU-path measurement (no new money)

- **Background:** #389's end-to-end run passed at $2.32 of $2.85. Its PoUW linears ran as a CPU numpy op. Daniel asked
  for the GPU path next.
- **The code:** bc-dd22acf8 wrote the committer's per-unit steps as C++ that builds for both CPU and GPU, in draft #435,
  stacked on #389. The CPU build is leaf-for-leaf identical to the numpy path. The CUDA build compiles for sm_89 but
  hasn't run yet.
- **Ask:** let the remaining line (about $0.53, until 22:00Z) cover one measurement on one SECURE RTX 4090 at
  $0.74/h or less.
  - Lease of at most 0.5 h; honest runs only (Daniel: no staged tamper arms).
  - Expected about 20 min and $0.25.
  - It runs the GPU bit-exactness gates, then times BF16, the GEMM floor, and SHA-256, SHA-512 and TurboSHAKE128
    throughput on the 4090. Those 4090 hash rates are still estimates in POUS's hashing accounting.
- **If you'd rather keep lines single-purpose:** a new line `vy-pouw-gpu-path` at $0.40 and 0.5 pod-hours, expiring 6 h
  after approval.
- **The fused kernel plus a vLLM run comes later:** about $2.05 and 2.75 pod-hours. That will be a separate request
  once the measurement is in.
