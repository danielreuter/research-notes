---
lane: coordinator
kind: handoff
from: agkr-real-k (bc-90879fa8-ea65-5d51-8e4d-ddeb832bf806)
created: 2026-09-26T09:35Z
---

# MERGE-READY: PR #69 (cursor/agkr-real-k-f806 @ a7500a4b, origin/main merged): A-GKR route (a) at K = 2048 / 8192 + the A-route-a bench.cell driver

- **PR:** https://github.com/danielreuter/verity/pull/69, tip a7500a4b. origin/main (47 commits) is merged in; the only conflict was
  the backends/numerical CHANGELOG, where both entries are kept.
- **Cells registered:**
  - art:95fdd0ae: K = 2048 at 2,048 VUs, 231 VU/s, 3.3e8× proving.
  - art:20197f8b: K = 8192 at 512 VUs, 52.3 VU/s, 3.6e8× proving.
  - Both are NON_ZK_PROOF claimed at 2^-130.19, on A100 in US-MD-1 with the verifier on a second A100 (the DC had no CPU stock).
  - Both carry a `note` label saying why their sweeps stopped. K = 2048 stopped on the kernel bug; K = 8192 on the harness bug.
    Both bugs are fixed in the PR.
  - They need a non-producer verification (G3). The store-only recipe is `lanes/agkr-real-k/evidence/pod-scripts/30-gate-cells.sh`
    with the art ids in the red-team request (09:30Z handoff). My producer pre-check is r20260926-092055-36d6: 10/10 sessions pass
    everything except non_producer.
- **Behaviour changes:**
  - `verity-gkr-verify` accepts two new relations and 8 commitment pins.
  - `tools/cell_gate.py` replays Flock at sigma's K. It was always K = 1536, which refused every real-K record.
  - `gpu/kernels.py scatter_terms` uses 64-bit offsets. This is prover-only; offsets below 2^31 are unchanged.
  - `tools/cell.py statement` takes `--input-set` / `--verifier-side`, and gains `finish` and `register`.
  - `bench_result.py --input-set` runs A-fs at an input set's K.
  - The A-GKR lowering admits K = 2048 and 8192.
  - New bench.cell driver `A-route-a`.
  - Nothing changes at K = 1536: the `bf16-ampere+blake3` pin still regenerates byte for byte.
- **Tests:** verifier cargo 39 + 4; `backends/gkr/tests` 60 on the pod with torch; bench 537 locally; flock-link selftest 49/49 at both
  K, on the pod and on the merged crate locally.
- **Known failures:** none of mine. In a broad local run, `test_every_registered_kernel_is_self_checked_here` fails only when
  backends/numerical's tests run before packages/verity's. It passes in the repo's configured order and alone.
- **Negatives:**
  - A stale prime state is rejected by the record replay.
  - A Fiat-Shamir prime prover is refused at Hello.
  - The wrong-K relation claim is refused.
  - The prover-side overflow produced an invalid proof, and both verifiers rejected it.
- **Paused by your 09:10Z guard, ready to launch:** `bash $RESEARCH_NOTES/lanes/agkr-real-k/evidence/pod-scripts/launch-cells.sh`
  (default `k2048 k8192 afs`). It creates the pods, runs the K = 2048 and K = 8192 re-sweeps with the fixes, runs A-fs on both sets,
  registers the cells, and drains. Estimate about 1.5 h on two A100s, about $5, or less with a CPU verifier if the DC has one.
- **FP8 spine sets:** not covered by A-GKR. Route (a)'s Flock side hashes 16-bit words only. 8-bit words would be a Flock statement
  change: flock-link's row length and Σ's `bits` line, plus a decision on the committed FP8 y word. A-fs alone doesn't bind operands,
  so it can't run on a committed statement.
- **Pods:** both terminated after draining (all runs preserved), about $2.7.
