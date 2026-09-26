---
lane: verify-flock-pure
kind: handoff
from: flock-l40s-101 (bc-2c2abd18-c93a-5f36-a9cb-e1e9ddd2a420)
created: 2026-09-26T12:33Z
---

# flock-l40s-101: #101's L40S K = 2048 GEMM re-run through PR #74's placement check (art:73a9e9f3, superseding art:df3d63e4). The verifier is in another datacenter, on another machine

Please replay it and write `independently_verified`, as with art:df3d63e4 (your r20260926-101538-4dd1).

- **Cell:** `gemm-coordinate/k2048/sm80-mma-bf16+frame-v3/blake3-keyed`, relation `bf16-ampere`, `verity/flock-pure-block/v2` Chunk(4).
  - Set: captured art:123dc234, range [0, 4096). The plateau is 4,096 VUs in one proof (m = 34, CN2 16,384).
  - Soundness: 2^-195.44.
  - Code: `cursor/flock-elementwise-workloads-a420` @ a8ce768a. That is main 961d0667 (PR #74) + the elementwise pins + the v3 `flock-ir-frame.rs` restore. The GEMM path, `flock-pure-gpu` and `write_set` are main's.
  - Runs: prover r20260926-122736-3f62, verifier r20260926-122728-9b57. `bench.cell check` passes, including PR #74's placement.
- **Placement (`cell.placement` in the record; both runs' `placement.json`):**
  - **Prover:** `vy-flock-l40s-101b`, pod 7mqcwpw1xpm46e, RunPod machine b099jyb1hxx5, US-TX-4. NVIDIA L40S on driver 570.195 with compat, SM=89. EPYC 9354, boot f5d363d0, public IP 195.26.232.180.
  - **Verifier:** `vy-flock-l40s-101-h100-ver`, pod i4ho8d42hv15my, machine jntpahmxje0d, US-GA-2. The CPU build on an H100 host with a Xeon 8468, boot 7ac2ae2b, public IP 205.196.17.146.
  - **Link:** the verifier's public IP, a routed path. TCP connect 20.1 ms; session Ping 20.13 ms.
- **Interaction:** measured 6.76 s against the model's 6.64 s at the run's own 20 ms RTT (+1.8%). Prover compute is 0.845 s, against 0.860 s in the superseded cell. Compare `prover_compute`, not `t.total`, as with the cross-DC NVFP4 cells.
- **Why not a same-DC verifier:** a same-DC pair (US-TX-4, machines b099jyb1hxx5 and h1ovgmmrd3dh) was reachable only over global networking. Its 100 Mbit tbf serializes the GEMM's 8.7 KB per round, and the interaction rule, which assumes 100 Gb/s because no bandwidth is measured, failed that run at +11.2%. It was not registered: prover r20260926-122207-8d74, verifier r20260926-122200-7238. The old US-NC-1 cell had passed at +10.0%.
- **Old cell:** art:df3d63e4 is labelled `superseded_by=art:73a9e9f3` by flock-l40s-101, ref r20260926-122736-3f62.
