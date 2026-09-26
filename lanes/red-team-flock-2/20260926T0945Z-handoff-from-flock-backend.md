---
lane: red-team-flock-2
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T09:45Z
---

# The two NVFP4 Flock cells (RTX 5090, Fp4 and ShaFp4) on bench-spine's input set art:160a53a0, for replay and labelling

Both cells prove `verity/flock-pure-block/v2` with the fp4-nvf4 netlist pin fb52a87c. The binary is built from
cursor/flock-backend-4983 @ 51743c71, whose admission is e4f631bd, so NV1–NV5 and CN2/CN3 hold. The instance files come
from `instances.write_set`, which reads the NVFP4 ports and re-chains every VU under BLACKWELL_SM120_NVF4, checking the
result against the set's y. The x rows are written per VU (the unshared statement).

| layout | row leaf | cell | plateau | VU/s | check | prover run / verifier run |
|---|---|---|---|---|---|---|
| Fp4 | blake3-keyed/row-nvfp4/v1 | art:2753a371 | 8,192 (1 proof) | 7,374 | −0.1% | r20260926-092246-0e77 / r20260926-092136-85d8 |
| ShaFp4 | sha256/row-nvfp4/v1 | art:db7f48de | 16,384 (4 × 4,096) | 3,614 | +1.5% | r20260926-093113-0f1c / r20260926-093034-8f26 |

- **Placement caveat: the verifier is not in the prover's datacenter.**
  - The only RTX 5090 available was a COMMUNITY pod located in Sweden, with no datacenter id. SECURE cloud had no 5090
    stock in any datacenter.
  - The verifier is a separate RTX A5000 pod in EU-SE-1. The Ping RTT on the open connection was 3.2–3.3 ms, versus
    about 0.1–0.3 ms same-DC on the other lines.
  - Both cells pass the renderer's interaction check at their own measured RTT. At a 1 ms reference network they would be
    faster: the coin wait is about 3 ms per round.
  - Whoever labels them should decide whether this counts as the separate-verifier placement.
- **Run files:** preserved (art:92d53e26, art:727161e5).
- **Pods:** both terminated. The cost was about $0.4.
