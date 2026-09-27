---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-27T01:20Z
---

# A CPU verifier can't work for a shared-NAT pair: RunPod CPU pods get no global-network interface. Continuing with the cheapest GPU verifier

- **What I tried:** following your 00:32Z note, two EU-NL-1 attempts used an L40S prover plus a CPU verifier (cpu3c, 2
  vCPU, created with `globalNetworking: true`).
  - Both had no route within 15 minutes.
  - On the second, the verifier had no `podnet1` interface (only 172.24.x on eth0), and `<id>.runpod.internal` didn't
    resolve. The L40S had `podnet1` 10.0.32.103.
  - So RunPod applies global networking only to GPU pods, and PR #91's rule (verifier at `<id>.runpod.internal`) can't
    be met by a CPU pod.
- **What I'm doing now:** the verifier is the cheapest GPU pod in the prover's datacenter (RTX 2000 Ada / A4000 / L4 /
  A5000 / A40 / 4090 / PRO 4500, and a PRO 6000 only as a last resort; no H100). Each pair is terminated after its
  attempt: no route within 15 minutes, or the queue done.
- **Time box:** until about 02:17Z (2 hours from 00:17Z).
- **Spend so far:** about $5 of $25. No pods were idle between attempts. Both pods of the 01:13Z pair are terminated.
