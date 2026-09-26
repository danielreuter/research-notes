---
lane: verify-bligero-real-k
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T13:16Z
cc: coordinator, red-team-bligero-real-k
---

# Two B-Ligero #101 cells on an L40S to verify: art:dd6b0cac (K2048) and art:c64377df (K8192), both at or below 2^-128 with A1 booked

These are the #101 headline candidates (root's goal 11:44Z): BF16 x4 keyed-BLAKE3 on #101's captured sets, proved on the served
GPU. They were planned through `bench.cell plan` on main 961d0667 (PR #74), and its machine-identity check passed.

| art | statement | prover run | input set | plateau | bound (booked) |
|---|---|---|---|---|---|
| art:dd6b0cac | `gemm-coordinate/k2048/sm80-mma-bf16+frame-v3/blake3-keyed` (`bf16-ampere-x4-k2048+blake3-xob`) | r20260926-122746-a284 | art:123dc234 (captured #101, 6,272) | 2,048 VUs = 16 sub-batches, t = 200, 1,985 VU/s | 2^-128.03 (`chain_field` 2^-147.8) |
| art:c64377df | `gemm-coordinate/k8192/sm80-mma-bf16+frame-v3/blake3-keyed` (`bf16-ampere-x4-k8192+blake3-xob`) | r20260926-130128-a83c | art:927a4c3a (captured #101, 1,920) | 1,024 VUs = 32 sub-batches, t = 202, 396 VU/s | 2^-128.265 (`chain_field` 2^-137.4) |

- **Verifier:** one live run, r20260926-122717-c116, served both cells in turn, 15/15 + 10/10 sessions accepted.
  - The K8192 plan's own verifier job was not launched; its plan names the same pod and run.
  - The run was stopped by process group after the second cell (rc 143).
- **Pods, US-MO-1, both L40S:**

| pod | role | machine | public IP | kernel boot id |
|---|---|---|---|---|
| vy-bligero-l40s-101 (8loxygl068ukkc) | prover | 9sng1e8op7yw | 64.247.206.218 | c878c736 |
| vy-bligero-l40s-101-ver (vdel26rpc47d2g) | verifier | mszbaoah5eb7 | 64.247.206.229 | 1ae4223a |

  - Public-port route, 0.13 ms RTT, 2.1 Gb/s. Stamped in `cell.placement`.
  - Both pods are draining now.
- **Dumps:** `meta.artifacts[0]` (`sweep/<plateau point>/proofs`), rep 1. Reverify with main e8ec5e19 or later (`chain_field`
  booked) and `--instances-root` from the re-staged captured set.
- **Interaction:** the only problem on either cell is measured time 45% / 41% under the serial model, recorded in a `note`.
