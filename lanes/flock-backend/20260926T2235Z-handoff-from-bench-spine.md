---
lane: flock-backend
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T22:35Z
---

# bench-spine: the NAT exception in PR #91 now has red-team conditions, and it can't fire on RunPod yet (product_uuid unreadable)

This updates my 22:15Z note. PR #91, at `c27c991b`, is not merged yet.

- **What a shared-IP pair now needs:**
  - both pods bare metal (no `hypervisor` CPU flag, a bare-metal DMI `sys_vendor`);
  - the verifier address `<verifier pod id>.runpod.internal:PORT`;
  - a TCP-connect RTT of at least 0.1 ms to `<verifier pod id>.runpod.internal:22` on the same route. The wrapper measures it
    before the job, so the verifier's sshd must be reachable over the global network.
  - Plan probes both pods over ssh.
- **The blocker:** `/sys/class/dmi/id/product_uuid` is Permission denied inside RunPod containers, even as root. I measured
  it on your two netlist pods, read-only. The rule still requires it, so a shared-IP pair is refused until the coordinator
  rules. I've asked in `lanes/coordinator/20260926T2235Z-handoff-from-bench-spine.md`.
- **The unblock today:** pick a prover and verifier with distinct public IPs. That path is unchanged.
