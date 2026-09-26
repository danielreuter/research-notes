---
lane: coordinator
kind: handoff
from: verify-bligero-real-k (bc-30d7a020-fc45-5944-9ceb-1ac513232a9e)
created: 2026-09-26T13:45Z
cc: bligero-real-k
---

# verify-bligero-real-k: #101 L40S cells art:dd6b0cac (2^-128.03) and art:c64377df (2^-128.265) verified=accepted; prover and verifier confirmed on different machines

- **Both verified=accepted**, ref r20260926-133012-30ab (PRESERVED), at main e77d40c9.
  - Pins 16/16 again.
  - Captured sets re-staged by me and IR-verified.
  - reverify PASS: custody, PINNED, commitments recomputed from my set. Batches: 16/16 and 32/32.
  - 5/5 sessions per cell from verifier run r20260926-122717-c116's store record match the dump and my compiled system.
- **Bounds**, my exact recomputation with chain_field booked; both equal the verifier's figure:
  - art:dd6b0cac: 2^-132.03 per proof, 2^-128.03 over 16 sub-batches. Chain term 2^-147.8, negligible.
  - art:c64377df: 2^-133.2655 per proof, 2^-128.2655 over 32 sub-batches. Chain term 2^-137.396; 2^-128.350 without it.
- **Different machines**, from the harness's own records (job.json, launch.json) and the verifier's session records:

| | prover | verifier |
|---|---|---|
| kernel boot id | c878c736 | 1ae4223a |
| hostname | 13837d713f4a | 4d9fbee72571 |
| GPU UUID | GPU-129a3a88 | GPU-0c4713c5 |
| public IP (launcher ssh host) | 64.247.206.218 | 64.247.206.229 |

  - The verifier saw every session's TCP peer as 64.247.206.218.
  - RunPod machine ids 9sng1e8op7yw and mszbaoah5eb7 exist only in the producer's plan record: the pods are terminated and
    can't be re-queried. The boot ids already establish separate hosts.
- **Not judged:** the interaction notes.
- **Pod:** no CPU pod was available in about 20 tries, so an RTX 3090 was used for CPU only. Terminated 13:38Z, about $0.09
  (lane total about $0.95). Details: the lane report's "Reopen 4" and `lanes/verify-bligero-real-k/evidence/separation-l40s-101.json`.
