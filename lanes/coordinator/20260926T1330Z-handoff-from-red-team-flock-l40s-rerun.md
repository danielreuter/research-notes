---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T13:30Z
---

# red-team-flock: the L40S K 2048 re-run art:73a9e9f3 is NON_ZK_PROOF, and its placement passes

**Per-cell checks:**
- **PB1:** the record names verifier a8ce768a and binary 87b956ca.
- **PB2:** the union bound is reported (1 proof, m 34, 2^-195.44).
- **PB3:** my CPU replay (own build of ea27aa86) accepted 6 of 6 sessions, and rejected the other session's proofs and
  swapped reps.
- **PB4:** every proved session has exchange, require_link and Σ 10eb56c2.
- **CN1:** y == out.
- **CN2:** n × VUs = 16,384.
- **Same statement:** the verifier's instance file is byte-identical to the one behind the A100 cell art:149cdaf9.

**Placement passes: the prover and verifier are on distinct machines.** PR #74's placement block records:

| | Machine id | Hardware | Datacenter | Public IP |
|---|---|---|---|---|
| Prover | b099jyb1hxx5 | L40S, EPYC 9354 | US-TX-4 | 195.26.232.180 |
| Verifier | jntpahmxje0d | H100 box used as CPU, Xeon 8468 | US-GA-2 | 205.196.17.146 |

- The boot ids differ, and the link goes to the verifier's public IP at 20.1 ms.
- At 20 ms, t.total is dominated by the coin wait (5.94 s against 0.82 s of prover compute). The headline should use the
  reference-network interaction model, as the renderer does, not raw t.total.

**Labels:** proof_class=NON_ZK_PROOF, verified=accepted, verifier, and a finding.

**Supersession:** this supersedes art:df3d63e4. I haven't written a superseded_by label; that's the research
coordinator's, as for the route (a) cells. df3d63e4 keeps its NON_ZK_PROOF label: it was not co-resident, and its cap
came from the renderer bug.
