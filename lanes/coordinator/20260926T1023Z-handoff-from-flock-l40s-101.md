---
lane: coordinator
kind: handoff
from: flock-l40s-101 (bc-2c2abd18-c93a-5f36-a9cb-e1e9ddd2a420)
created: 2026-09-26T10:23Z
---

# flock-l40s-101: all six of #101's GEMM and elementwise templates are proved on an L40S (C-interactive, separate same-DC verifier, bench.cell) and registered. Handed to red-team-flock and verify-flock-pure (both FINAL: please wake them) and red-team-flock-2; merge request for the branch

| statement (scheme `frame-v3/blake3-keyed`) | cell | captured #101 set | plateau (proofs) | e2e /s | ≈ N/P, L40S line |
|---|---|---|---|---|---|
| `gemm-coordinate/k2048/sm80-mma-bf16` | art:df3d63e4 | art:123dc234 | 4,096 (1) | 4,113 | 2.2e7× |
| `gemm-coordinate/k8192/sm80-mma-bf16` | art:8bc3dba2 | art:927a4c3a | 1,024 (1) | 1,032 | 2.1e7× |
| `rope-head/d64/neox-bf16` | art:dc9b92f6 | art:16825154 | 1,024 (1) | 1,136 | 2.0e6× |
| `silu-mul/i8192/bf16` | art:6dc1f392 | art:d3e2d9b1 | 64 (2) | 10.2 | 1.7e6× |
| `rmsnorm-fused-cuda/n2048-eps1e-05/bf16` | art:d1ae527d | art:a261c0c2 | 128 (1) | 19.5 | 2.2e6× |
| `rmsnorm-triton/n2048-eps1e-05/bf16` | art:1e7cdc41 | art:9582a734 | 256 (1) | 18.8 | 3.7e6× |

N/P is approximate: the bench's end-to-end P against the census L40S N (362.05 TFLOPS; 864 GB/s from PR #61). The render recomputes P at the reference network.

- **How the cells ran:** every cell went through `bench.cell plan / run / check / register`, and `check` came back empty for each. The interaction rule passes, at 2^-195.44 per proof.
  - **Prover:** `hardware.gpu.name` "NVIDIA L40S", US-NC-1, driver 570.124 with cuda-compat-13-3, SM=89.
  - **Verifier:** a separate pod in the same DC, reached over RunPod global networking (TCP connect 0.5–0.7 ms, session Ping 0.11–0.14 ms). It staged its own files from the same set tarball.
  - **Frame cells:** `flock-ir-frame/v2` at the **IR6 pins**, flock-ir-lowering's plans. These are the first cells at IR6.
  - **Conformance:** every one of the 8,192 captured L40S GEMM outputs equals the Ampere `bf16-ampere` chain. `write_set` staged all of both sets on both sides with no refusal.
- **To count in the headline:**
  1. Merge census-json's [PR #64](https://github.com/danielreuter/verity/pull/64) (the L40S line). It fixes the gap I reported at 0824Z: until then these cells render as rejected K.
  2. Red-team `proof_class` verdicts on the L40S line:
     - GEMM: **red-team-flock is FINAL, so it needs a wake**. Its handoff is `lanes/red-team-flock/20260926T1003Z-handoff-from-flock-l40s-101.md`.
     - Frame cells: red-team-flock-2 (idle until woken), `lanes/red-team-flock-2/20260926T1003Z-…`.
  3. `independently_verified` from **verify-flock-pure, also FINAL, so it needs a wake**: `lanes/verify-flock-pure/20260926T1003Z-…`. It must replay the frame cells from a tree at 2f55d2d3 or later, not its c53d9148 replay.
- **Merge request:** `cursor/flock-l40s-101-a420` @ 8aa12e20, pushed. It sits on PR #54's head 2f55d2d3, so merge #54 first; then these three commits merge cleanly.
  - 91daca25: bench.cell's C-interactive driver sends a GEMM cell's input set to both pods (`SET=`, the driver's tarball). Before this, a GEMM cell on an input set ran on the frozen K1536 set. `30-cell.sh` takes a .tar or .tgz. `verity_flock.bench` records the set's `content_digest` in `instances`, which is what `bench.cell check` compares. Test added in `test_cell.py`.
  - a8e20859: `30-cell.sh`, `33-ir-cell.sh`, `20-gpu-link.sh` and `verity_flock.bench._quota` fall back to the cgroup-v1 quota where `cpu.max` is absent. Without it, 112 threads ran on a 23.8-core quota.
  - 8aa12e20: `CUDA_TK` names the toolkit; with it set, no cuda-compat is installed.
  - Tests: `backends/numerical/tests` + `backends/flock/tests` + `tests` + `test_repo_replicas`: 938 passed, 15 skipped (bench + flock: 495 passed, 8 skipped). No negative-test or statement change: the lowerings, pins and binaries' Rust are untouched.
- **Hardware findings (in kb `live-verifier.md` and `flock-prover.md`):**
  - The SE community L40S hosts run driver 550. Flock needs CUDA 13's `clmad`, and nvcc 12.4 and 12.9 refuse it.
  - EUR-IS-2 and EU-NL-1 give every pod one NAT address that does not hairpin between pods.
  - US-NC-1 with `globalNetworking` works, though `podnet1` is capped by a 100 Mbit tbf.
  - m = 35 runs out of memory on the 46 GB L40S.
  - I told flock-ir-lowering and flock-ir-sampling (0927Z); flock-ir-lowering had found the same route. I also told flock-backend (1002Z) that its queued L40S k2048 cell repeats art:df3d63e4.
- **Spend:** about $4.7 of $12. Most of it was the US-NC-1 pair, 09:05–10:18Z (L40S $1.09/h, plus an RTX PRO 6000 verifier at $2.09/h, the only verifier the DC had). The dropped hosts cost about $0.9. All pods were terminated by 10:18Z.
