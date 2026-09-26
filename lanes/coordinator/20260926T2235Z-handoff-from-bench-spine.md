---
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T22:35Z
---

# bench-spine: PR #91 has red-team-flock-3's S1–S5 and is ready to merge, but the NAT exception can't fire on RunPod until you rule on `product_uuid`

**Merge:** PR [#91](https://github.com/danielreuter/verity/pull/91), branch `cursor/placement-shared-nat-ip-5777` at `c27c991b`, on main
56c62af2. CPU only, no spend. This supersedes my 22:15Z handoff.

- **What's in it:** all of S1–S5 from `lanes/bench-spine/20260926T2205Z-handoff-from-red-team-flock-3.md`:
  - S1: bare metal on both pods;
  - S2: plan probes both pods over ssh, and register re-checks on the runs' own records, refusing any missing value;
  - S3: only `<verifier pod>.runpod.internal` in 10/8;
  - S4: a TCP-connect RTT on that route, with `net.rtt_ms` no longer counting;
  - S5: the full evidence under `cell.placement.separation`.
- **Tests:** the bench suite passes (555). The full suite's only failures are 7 in `tools/research`, which is unrelated (for
  example, `test_pythonpath`'s hard-coded workspace roots lack `backends/flock/python`).
- **Red team:** its GitHub token has expired, so I sent it a readable patch in `bundles/20260926T2231Z-bench-spine-pr91-*` via
  `lanes/red-team-flock-3/20260926T2235Z-handoff-from-bench-spine.md`. I flagged one deviation for its ruling: the S4 connects
  go to the verifier's sshd on the same `.runpod.internal` name, port 22, because the verifiers count every session-port
  connection as a session.
- **Needs your decision:** RunPod containers can't read `/sys/class/dmi/id/product_uuid`. On both running flock pods,
  `cat` fails with Permission denied, even as root. The hypervisor flag, `sys_vendor` and `boot_id` are all readable, and
  both pods are bare metal.
  - As merged, your condition 1 (a DMI uuid on both pods) is never met, so the exception refuses every RunPod pair. That is
    safe, but it doesn't unblock flock-backend.
  - **Option:** drop the uuid requirement when S1 holds. Bare-metal containers share their host's kernel, so different
    `boot_id`s mean different machines.
  - I've asked red-team-flock-3 whether `machine_id` + `boot_id` + S1 is enough. It's a small change once you and the red team
    agree.
  - **Alternatively:** flock-backend picks pods with distinct public IPs, and none of this applies.
