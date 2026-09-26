---
lane: verify-flock-pure
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T16:32Z
---

# Capacity gap: the five L40S re-runs and the two ChunkTail cells did not run before the 16:45Z pod deadline

- **Not run:**
  - the five re-runs of art:4e3f5048, aea553ae, 86780ca6, 4a319a65 and 89dab836, with the verifier on a provably
    different machine;
  - #57 K2304 and #39 K8960 (ChunkTail, from main with PR #75).
- **Why:** from 11:50Z to 16:30Z my poller never got an L40S prover plus a different-model verifier in one datacenter
  with a working route. It tried every 7 minutes, in 12 DCs.
  - EUR-IS-2 offered pairs on different machine ids twice. Its site NAT doesn't hairpin, and global networking gave no
    route there.
  - OC-AU-1 had no verifier.
  - The other DCs had no L40S.
  - No pods are running. Spend for the attempts was about $0.5.
- **The old five cells stay at NON_ZK_PROOF_DIAGNOSTIC.** I added no `superseded_by` labels, because nothing supersedes
  them.
- **Ready for whoever picks it up:** `lanes/flock-backend/evidence/gemm-workloads/launch.sh`, run with `P_NAME` / `V_NAME`
  / `P_DC` / `ONLY="k1536 k2048 k4096 k9216 k14336 k2304 k8960"`, on a tree with main's PR #74 and #75. That is
  cursor/flock-backend-4983 @ 755a397e, sent as a bundle in the 15:15Z handoff.
  - bench.cell's placement check then refuses a same-machine pair before any spend.
- **Also still open:**
  - the NVFP4 re-run on the frozen set (the 11:45Z note: no working 5090);
  - the captured FP8 H100 set (vllm-more-exports hasn't registered one).
