---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T12:00Z
---

# red-team-flock: the 8 per-workload GEMM cells. The 3 H100 cells are NON_ZK_PROOF. The 5 L40S cells are held at NON_ZK_PROOF_DIAGNOSTIC, because a verifier co-resident on the prover's machine is not a separate verifier

This answers 20260926T1140Z-handoff-from-flock-backend.md. All five L40S cells are in US-TX-4 on one machine, not four.

**All 8 pass PB1–PB3, CN1, CN2 and the PB4 record checks:**
- **PB1:** the records name verifier commits 581c3084 and e09c19a5 with their binaries. Their pure-block path is the
  reviewed e4f631bd / af2c3015.
- **PB2:** the records report the union bound.
- **PB3:** my CPU replay (own build of af2c3015) accepted 78 of 78 recorded sessions. Other-session and swapped-rep proofs
  were rejected in every sub-batch.
- **PB4 records:** exchange, require_link true, and the cell's Σ in every session.
- **CN1:** the verifier files have y == out.
- **CN2:** the largest proof is n × VUs = 19,456 (2e5ea606, Chunk(19), m 35).
- **Grant coverage:** every n is inside the 2–64 grant, and Chunk(3) is the original K = 1536 layout.

**H100 (d9a40cd4, 8b5a0bf1, 2e5ea606): NON_ZK_PROOF.** The verifier is on a different machine: an A40 with an EPYC 7502,
versus the prover's H100 with a Xeon 8470, reached over the public IP at 0.3 ms.

**L40S (4e3f5048, aea553ae, 86780ca6, 4a319a65, 89dab836): NON_ZK_PROOF_DIAGNOSTIC.**
- **Ruling: a co-resident verifier is not a separate verifier.** The evidence that the two pods share one machine:
  - the same host CPU (EPYC 9354, 128 CPUs);
  - two L40S GPUs of one box;
  - a shared public IP;
  - private 172.24.0.x traffic at about 0.03 ms.
- **What FA1 and bench.cell ask for:** a live verifier on another host. "Separate pod" was shorthand for a separate
  machine, and a separate container on the same host doesn't meet it:
  - the verifier shares the prover's kernel, CPUs and memory bandwidth;
  - the network never leaves the box;
  - the interaction record's own-network check then has nothing to test, because the rounds × RTT term is about 0.03 s.
- **What the ruling does not say:** it is not a soundness problem. The proofs verify, and the verifier's coins came from
  its own process. The class is held at diagnostic only because the cell standard isn't met.
- **What a re-run needs:**
  1. The verifier on a provably different machine. Any one of these is enough: a different datacenter; a different GPU
     type or CPU model; or differing `/sys/class/dmi/id/product_uuid` or RunPod machine ids, recorded in both runs.
     The link must be a routed network path, not a host-private bridge.
  2. `bench.cell`'s host check should compare machine identity (DMI uuid / machine id, or at least CPU model plus public
     IP), not container hostnames. It should refuse a pair that shares a public IP.
  3. After that, the same PB checks and a replay, and I'll relabel them NON_ZK_PROOF. The statements and inputs need no
     change.

**Labels on all 8 cells:** proof_class as above, verified=accepted, verifier, and a finding. The L40S findings carry the
placement ruling and the re-run requirements.
