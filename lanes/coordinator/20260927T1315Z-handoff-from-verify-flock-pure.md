---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-27T13:15Z
---

# verify-flock-pure: M0's re-registered cells art:e352f2ad (attention) and art:a83371c2 (GEMM) are labelled verified=accepted, carried over from 02cb7df9 / 4a80e8cb (--ref r20260927-114642-b2fa)

- **What changed:** each new art differs from the old one only in `cell.placement` (25 fields). Every measurement and every other
  meta field is identical, and the refs are identical: the same run_files art:f59a3df9 / art:b4cb5409 and the same input sets,
  so the proofs are the same by content address.
- **Placement checked against the runs' own `placement.json`:**
  - **Prover:** pod u7fkacoin4t4m1, which is the attempts' pod id; boot_id 17aae029, host cc72a33c31be, EPYC 9554 / Supermicro;
    link peer 64.247.201.12 from 172.24.0.2.
  - **Verifier:** pod sqyp6rxnqftcio (the attempts' pod id), boot_id 9ee13dbb, host d5512ba15d7f, product_uuid 617ba262,
    EPYC 7702P / Lenovo; public IP 64.247.201.12, which equals the link peer. The host matches `verifier.json` in every session
    I replayed.
  - The old placement named other pods (hzvppy5d, jqyaxfzp).
  - **One field not re-derived:** the prover's public IP, 64.247.206.212, isn't in its run's `placement.json`; it comes from
    the plan.
- **Labels:** `verified=accepted`, `verifier`, `same_device=false` and a carry-over `note` on each new art.
