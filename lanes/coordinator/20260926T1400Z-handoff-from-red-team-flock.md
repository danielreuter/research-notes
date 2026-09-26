---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T14:00Z
---

# red-team-flock: route (a) on the L40S for #101 is labelled NON_ZK_PROOF: art:e1a2dfc3 (K 2048) and art:7a0d186b (K 8192)

**Per-cell checks (CPU, my own a7500a4b builds):**
- **Statement rebuild:** both statements are byte-identical to my independent rebuild. They are the same statements as
  the A100 cells at 2,048 and 512 VUs, and the prime commitments equal the verifiers'.
- **Gate:** `cell_gate` passed on all 10 sessions: the prime proof (pinned circuit, pinned commitment, live coins) and the
  Flock replay. The only failing check is `non_producer`, because the live verifier is the producer's; this re-run is the
  non-producer check.
- **Negatives, all rejected:**
  - a relabel to the other K;
  - another session's proof;
  - the A100 cell's proof of the same statement;
  - the other K's proof;
  - the Flock replay at the wrong K.

**Placement:**

| Cell | Prover machine | Verifier machine | Public IPs | Link |
|---|---|---|---|---|
| e1a2dfc3 (US-NC-1) | av7yp9ygnbzg | hl5m5gd6160a | 103.196.86.5 vs .193 | RunPod pod network, 0.13 ms |
| 7a0d186b (US-TX-4) | h1ovgmmrd3dh | bmf6gxxmufbv | 195.26.232.178 vs .152 | 10.0.129.112, 0.21 ms |

- **e1a2dfc3:** the boot ids differ too. The prover is an L40S and the verifier an H200 box.
- **7a0d186b, checked closely:** both pods are L40S, but they are not co-resident.
  - The kernel boot ids differ (7a6297a1... vs 343d5975...), and containers on one host share a boot id.
  - The link is RunPod's routed pod network, not a host-private 172.x bridge at 0.03 ms.
  - The session records' verifier host, e76353b806fc, is the placement's verifier.

**Labels on both cells:** proof_class=NON_ZK_PROOF, verified=accepted, verifier, same_device=false, and a finding.

**Open item:** the agkr-l40s-101 bundle (508e6e74, with 47dcd5a4 and 1a1bb6a2) hasn't arrived. It would only confirm the
live verifier's source, since my replay already verifies the proofs independently, so it doesn't gate the labels. I'll
diff it if it lands.
