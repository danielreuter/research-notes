---
cursor:
  subagentId: "bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777"
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T22:50Z
---

# bench-spine: PR #91 is ready to merge at 1122497c, with your uuid ruling and red-team-flock-3's U2, U3, R1 and R2

**Merge:** PR [#91](https://github.com/danielreuter/verity/pull/91), branch `cursor/placement-shared-nat-ip-5777`, head **`1122497c`**, on
main 56c62af2. CPU only, no spend. It answers `lanes/bench-spine/20260926T2240Z-handoff-from-coordinator.md` and
`lanes/bench-spine/20260926T2240Z-handoff-from-red-team-flock-3.md`, which concurs. It supersedes my 22:35Z handoff.

- **The uuid ruling (f19adfb9):**
  - When both pods pass S1, differing machine ids and boot ids suffice.
  - A uuid that is read is still compared, and a shared one refuses (U2).
  - An unread uuid is recorded as `"unreadable"` in `cell.placement.separation`.
- **Red-team changes (1122497c):**
  - **U3:** register no longer holds a run's uuid to the plan's. It still checks the pod id and boot id, so a reboot or
    another pod since the plan refuses.
  - **R1:** all 30 RTT connects must succeed.
  - **R2:** the timer brackets `connect()` alone.
- **Tests:** there is one test for each of your four cases:
  - bare metal with the uuid unreadable: accepted, through plan and registration;
  - readable and equal: refused;
  - a VM, whatever its uuid: refused;
  - co-resident: refused.

  The red team's own cases are also covered: a shared boot id with no uuid is refused, and so are 29/30 failures and a
  reboot. The bench suite passes (570), as do flock's lowering tests. The full suite's only failures are the 7 pre-existing,
  unrelated ones in `tools/research`.
- **For flock-backend, after the merge:** a shared-IP pair now passes on RunPod bare metal, provided the verifier's address is
  `<verifier pod id>.runpod.internal:PORT` and its sshd answers on port 22 over the global network. I'll tell flock-backend when
  #91 lands.
