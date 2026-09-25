---
lane: verify-flock-pure
kind: handoff
from: flock-vllm-v1 (bc-9713144f-acde-5fa5-9c0b-667f89154cdd)
created: 2026-09-25T23:37Z
---

# Non-producer verification wanted (provisional cell): H100 fp8-hopper Flock over vllm-v1, art:56f792bd, 7,650 VU/s (8.4e7×)

- **Cell:** art:56f792bd, a re-registration of run r20260925-232104-50d5. Its result is art:057f9dc9 and its run files
  are art:96aaf52a. It supersedes art:f95c3438 and the host-witness cell art:ae856c69 (r20260925-225837-3a94).
- **Statement:** `verity/flock-vllm-block/v1`, binary `flock-vllm-v1`, source `cursor/flock-vllm-v1-4cdd` @ ff1c1e3f
  ([PR #41](https://github.com/danielreuter/verity/pull/41)). Design: `lanes/flock-vllm-v1/20260925T2300Z-finding-statement-design.md`.
- **Line and result:**
  - fp8-hopper on H100 80GB (US-MO-1). The verifier was a separate same-DC CPU pod (cpu3c-32), which served its own
    instance files: run r20260925-232101-016f, commit ff1c1e3f, flock-vllm-v1 sha256 d4cdf2eb….
  - Plateau: 65,536 VUs, 4 sub-batches of 16,384, 2^-193.44 union. 7,650 VU/s end to end, 6/6 sessions accepted.
  - Network: TCP RTT 0.89 ms, measured in the run. The loopback probe in the same run gave 1.06 ms per round.
- **Replay:**
  - The sessions and proofs are in the verifier run, under `out/verifier/p3-65536/sessions-s{0..3}`. Session 0 of each
    server is the prover's connect probe.
  - To build: `backends/flock/pod/40-vllm-v1.sh` with `ROLE=verifier` builds the CPU verifier. You can also run
    `bash backends/flock/pod/20-gpu-link.sh MODE=build GPU=0` and then
    `cargo build --release -p flock-live --bin flock-vllm-v1`.
  - To regenerate the instance files:
    `python -m verity_flock.instances fp8-hopper <n> <out> --scheme vllm-v1`. For a sub-batch, use
    `instances.write(..., lo, hi, scheme="vllm-v1")`.
- **vllm-v1-specific checks for a non-producer:**
  - The a/b/y roots in the instance header are step roots under B-Ligero's port domains (`ligero.vllm_tree`).
  - The verifier folds the prover's digests (from Commit) into those roots.
  - Σ carries the three domain digests.
