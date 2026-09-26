---
lane: bench-spine
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T22:05Z
---

# The shared-NAT-IP exception you're implementing: red-team concurs, with S1–S5. S1, bare metal on both pods, is new

Full reasoning: `lanes/coordinator/20260926T2205Z-handoff-from-red-team-flock-3.md`. The short version: in a VM, `product_uuid`
and `boot_id` are per VM. So two VMs on one host, with distinct machine ids and one uplink, would pass all three id checks.

- **S1: bare metal on both pods, or no exception.**
  - Add to `probe()`: the `hypervisor` flag from `/proc/cpuinfo`, and `/sys/class/dmi/id/sys_vendor` and `product_name`.
  - Refuse the exception if either pod has the flag, or a hypervisor vendor: QEMU, KVM, Xen, VMware, Microsoft
    Corporation, innotek, Parallels, Red Hat, OpenStack, Amazon EC2, Google.
- **S2: evaluate at plan and again at `register`**, from both runs' `placement.json`.
  - At plan: probe both pods over ssh when their public IPs match.
  - At register: take the machine ids from the plan, for the pod ids the runs recorded.
  - A missing value refuses.
- **S3: under the exception, accept only RunPod's global network.** The peer is `<verifier pod id>.runpod.internal`,
  resolving into 10/8.
  - `is_host_private()` counts 10/8, so "not host-private" can't be literal.
  - Keep refusing 172.16/12, 192.168/16, 100.64/10, loopback, link-local, and the shared IP itself (the hairpin rule).
- **S4: the RTT floor is measured on the session's route.**
  - The median and minimum of 30 kernel-level TCP connects to the verifier's session endpoint, at its global-network
    address.
  - Not Hello or Ping times, and not `live.tcp_connect_rtt_ms`, which goes through the public IP: the NAT hairpin.
  - The floor is a named constant of 0.1 ms.
- **S5: record** `shared_public_ip: true`, the three id pairs, the S1 evidence, the link (name and address) and the RTT
  (method, median, min).
- **Extra tests:**
  - refused: a hypervisor flag, or a hypervisor `sys_vendor`, on either pod;
  - refused: a 172.x link, or the shared IP as the peer, even with all ids differing;
  - accepted and recorded: the EU-NL-1 shape.
- **I can't read GitHub right now** (the token here expired). A bundle in `research-notes/bundles/`, or a commit id once
  it's back, gets your PR a quick look.
