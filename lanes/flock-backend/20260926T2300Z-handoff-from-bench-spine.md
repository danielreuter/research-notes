---
lane: flock-backend
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T23:00Z
---

# bench-spine: the shared-NAT-IP rule is on main (PR #91, merge e93da678); a RunPod pair sharing a public IP can now register

This supersedes my 22:15Z and 22:35Z notes; the `product_uuid` blocker is gone.

**What a shared-IP prover/verifier pair needs:**
- both pods bare metal: no `hypervisor` CPU flag, and a bare-metal DMI `sys_vendor`. Your netlist pods (Supermicro, Lenovo)
  pass. An unreadable `product_uuid` is fine;
- different RunPod machine ids and different `boot_id`s;
- the verifier address `--verifier-addr <verifier pod id>.runpod.internal:PORT`, resolving into 10/8;
- the verifier's sshd answering on `<verifier pod id>.runpod.internal:22`. The prover's job wrapper makes 30 TCP connects to it
  before the job; all 30 must succeed, with a median of at least 0.1 ms.

**What happens at each step:**
- `bench.cell plan` probes both pods over ssh when their public IPs match.
- `register` re-checks everything on each run's `placement.json`. A missing value refuses, and so does a reboot (a changed
  `boot_id`) or a different pod between plan and run.
- The record carries `cell.placement.shared_public_ip: true` and the evidence under `separation`.

Pairs with distinct public IPs are judged as before.
