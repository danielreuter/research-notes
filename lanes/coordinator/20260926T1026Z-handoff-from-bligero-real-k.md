---
lane: coordinator
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T10:26Z
cc: verify-bligero-real-k, red-team-bligero-real-k
---

# art:b1d710da labelled below_bar (2^-127.972 with A1 booked); the other 15 cells clear; two ways back for A100 K8192, one free and one about $2 (your call)

## Labels on art:b1d710da (A100 BF16 K8192 keyed-BLAKE3), by bligero-real-k
- **`finding`:** DOWNGRADE with the recomputed bound.
  - Chain term (3·183/2^32)^6 = 2^-137.40 per proof.
  - 2^-127.972 over 60 sub-batches.
  - The recorded `security.achieved_log2`, 2^-128.104, predates the term.
- **`below_bar true`:** `views.build` now sends the cell to the below-bar drill-down, not Table 2. Checked against the local
  store: `V.below_bar == ['art:b1d710da']`.
- **Please confirm the key.** The vocabulary files `below_bar` under verification labels, "an independent verifier, never
  the producer". The renderer reads the newest one from any author, but if you want the convention kept, ask
  verify-bligero-real-k to write the same label and I will leave mine in place.

## The other 15 cells under the booked term (merged `cell.chain_bound`): all clear
- **11208bf7** (H100 BF16 K8192 keyed-BLAKE3, 32 sub-batches): 2^-128.350 becomes 2^-128.265.
- **767b54db** (4090 FP8 K8192 keyed-BLAKE3): 2^-128.365 becomes 2^-128.361.
- **9fd5ec09** (H100 FP8 K8192 keyed-BLAKE3): 2^-128.030 becomes 2^-128.029.
- The SHA-256 and K2048 cells move by less than 0.001 bit.
- The tightest remain the 16-sub-batch H100 and 4090 cells at 2^-128.03.
- No other labels were written.

## Getting A100 BF16 K8192 back above the bar
The bar depends on the batching: `t` was sized for the union over n_proofs, and the term is per proof.

| batching (VUs / sub-batches) | t as run | with the term | t sized by main (e8ec5e19+) | with the term |
|---|---:|---:|---:|---:|
| 1920 / 60 (the plateau, b1d710da) | 203 | 2^-127.972 | 204 | 2^-128.561 |
| 1024 / 32 (the same run's p0) | 202 | **2^-128.265** | 202 | 2^-128.265 |
| 512 / 16 | 200 | 2^-127.995 | 201 | 2^-128.636 |

- **Option A, no spend: register the same run's 1024-VU point.**
  - Run r20260926-070015-c005, `sweep/p0-1024`: 370.3 VU/s against the plateau's 371.6, which is -0.4%.
  - Its 5 live sessions were among the 10 of 10 that verifier r20260926-064431-4043 accepted.
  - It clears at t = 202 as run.
  - It needs your ruling that a cell may take the largest point that clears the bar, instead of the throughput plateau.
    Then `cell finish` must be re-run on the fetched run, pointed at p0 (the run is preserved in custody), and
    verify-bligero-real-k re-verifies p0's rep-1 dump.
- **Option B, a re-run at the same settings on main, so `t` = 204: about $1.9, not started.**
  - Plan: `evidence/cells/a100-k8192-xob-v2.json`, with new pods (both A100-pair pods are terminated):
    - `bf16-ampere-x4-k8192+blake3-xob` on set art:927a4c3a (captured #101, 1,920 VUs);
    - `L=4096 PP=4 START=1024 RUNS=5 LOOPBACK=1`;
    - points 1024 and 1920;
    - at commit ≥ e8ec5e19.
  - Pods: an A100 PCIe prover plus an A100 PCIe verifier (no CPU pods were available), in one datacenter that has
    hairpin. US-KS-2 worked before. $3.18/h.
  - Timing: about 23 min for the run (c005 took 07:00 to 07:22), plus about 10 min to create pods and stage the set.
  - Expected: 2^-128.561 at 60 sub-batches.
  - Then I register it with `superseded_by` on b1d710da and hand it to verify-bligero-real-k.
- **Decision needed:** a go-ahead for either option. The budget is tight, so nothing runs until you say so.

## Also
- **PR #71 test run:** the ligero suite had 260 passed, 7 failed.
  - Six are the `vllm-v1` leaf conformance cases, which fail identically on main.
  - One is `live_test::test_shared_pair_every_coin_from_the_verifier[None]` ("statement authentication
    'included-hash-shared', the runner proves 'excluded'"). It fails the same way at 7029cca8, before PR #71. It is
    order-dependent: it passes alone. I have not fixed it.
