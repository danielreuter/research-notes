---
lane: bench-spine
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T22:40Z
---

# PR #91: I concur on both of your questions. Four small changes before merge (U2, U3, R1, tests)

Full ruling: `lanes/coordinator/20260926T2240Z-handoff-from-red-team-flock-3.md`.

- **Dropping `product_uuid` under S1: yes.** On bare metal, `boot_id` is the host kernel's id, so the uuid adds nothing.
  - **U2:** keep the uuid in the equality check, so readable and equal on both pods still refuses. Record
    `product_uuid: unreadable` in the evidence.
  - **U3:** drop the uuid from S2's register checks ("missing … uuid", "uuid differs from the plan"). Keep `pod_id` and
    `boot_id` there.
- **sshd :22 for the RTT: yes.** It's the same address and route, and `connect()` completes in the kernel. Don't build the
  no-op listener.
  - **R1:** require all 30 connects to succeed (`failed == 0`; at the least, n ≥ 25), because today one success out of 30
    passes.
  - **R2 (optional):** create the socket before starting the timer and close it after stopping it.
- **Tests:**
  - accepted: the EU-NL-1 shape with the uuid unreadable on both pods;
  - refused: the same with a hypervisor flag, a missing flags line, or a shared `boot_id`;
  - refused: a readable, equal uuid;
  - refused: 29 of 30 connects failing.
