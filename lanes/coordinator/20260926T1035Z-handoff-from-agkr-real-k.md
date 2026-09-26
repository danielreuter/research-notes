---
lane: coordinator
kind: handoff
from: agkr-real-k (bc-90879fa8-ea65-5d51-8e4d-ddeb832bf806)
created: 2026-09-26T10:35Z
---

# Cells registered; both pods drained and terminated at about 10:32Z (re-pause 10:20Z honoured: nothing was left in flight)

**Route (a) re-sweeps.** Each reaches its GPU-memory cap now that the two bugs are fixed. A100-SXM4-80GB in US-MD-1, verifier on a
second A100 (no CPU stock there), NON_ZK_PROOF claimed at 2^-130.19:

| cell | art | plateau | VU/s | proving overhead | runs (verifier / prover) |
|---|---|---|---:|---:|---|
| K = 2048, #101 art:123dc234 | **art:a0ca8ef6** | 4,096 VUs (6,272: CUDA OOM) | 283 | 2.7e8× | r20260926-095014-2234 / r20260926-095028-c0bd |
| K = 8192, #101 art:927a4c3a | **art:a979dfcb** | 1,024 VUs (1,920: CUDA OOM) | 63.5 | 3.0e8× | r20260926-101258-e284 / r20260926-101301-8697 |

- Both passed `bench.cell check` with no problems. Every live session was accepted (Flock, Python and pinned Rust verifier).
- They supersede art:95fdd0ae (2,048 VUs, stopped by the scatter_terms bug) and art:20197f8b (512 VUs, stopped by the harness bug).
- I sent the new ids to red-team-flock and verify-flock-pure (10:26Z handoffs). The code differs from the verified a7500a4b only in
  cell.sh, so verify-flock-pure's `verify-cells.sh` applies as it is.
- Please make sure the two old cells get `superseded_by` once the new ones are verified. I'm writing FINAL now; red-team-flock has
  written that label before. I'm not writing it myself yet, so the render isn't left without a verified A-GKR real-K cell in between.

**A-fs (drill-down).** A-GKR alone, Fiat-Shamir coins, x and W private: the weaker statement, never a spec cell. Run
r20260926-102535-c15b, whole set per proof, 5 reps, pinned Rust verifier 5/5:
- art:7ae6c190: K = 2048, 6,272 VUs, 1.16 s, 5,408 VU/s, 1.4e7×.
- art:0e1095f3: K = 8192, 1,920 VUs, 1.42 s, 1,353 VU/s, 1.4e7×.
- Proofs are in the run record art:e92cad62.
- The prime prover is about 20× faster alone, so route (a)'s cost at real K is the Flock CPU side and the live rounds.

Spend: this round about $2.3 (two A100s for about 43 min), lane total about $5.0. PR #69 is updated with the new cells. The FP8
spine sets stay out of reach without a Flock statement change (the blocker note is in my report).
