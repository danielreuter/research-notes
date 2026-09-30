---
id: 20260930T1915Z-rulings-from-daniel-one-pool
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1), recording Daniel's rulings of 19:12Z (relayed by verity-top)
---

# Daniel's infra rulings (19:12Z): both nodes are one pool with one central scheduler; the cutover is approved now

Daniel wants the Project centralized fast, so it stops being scattered. Both nodes are one big pool of workers. No ceremony:
good engineering.

1. **Node-2 cutover: approved** (`note:20260930T1858Z-handoff-from-pous-one-cluster-to-infra-cutover-plan`). Go as fast as is
   reasonable. Infra may shorten the shadow gate (3 h and 6 windows) once the evidence is good enough, switch when it makes
   sense, and report after.
2. **Borrowing: yes, both ways, GPUs and CPUs alike.** Node 2's timed windows stay protected: no guest work runs in a window.
3. **Timing: now.**
4. **Access: the simplest thing that works; hardening comes later.**
   - Agents keep the research SSH key they already use on both nodes.
   - The scheduler's link between the nodes uses one new key pair, `vy-cluster`, in both nodes' `research` `authorized_keys`,
     over TCP 22.
   - No CA, and no Nebius, IAM or security-group change.
   - Secrets are never printed.
5. **One central queue and scheduler across both nodes.** Node 1's Kueue is folded into it, planned with the steward. It doesn't
   remain a separate scheduler.
6. **Merge trains:** the research coordinator keeps running them until Job queue stage 1 runs a whole train. Then infra takes the
   machinery.
7. **Spare CPU on node 2:** no separate key. It is part of the one pool, and the held Verity-pool enforcement on node 2 may be
   deployed as the interim guest path.
8. **Utilization target: confirmed.** At least 95% GPU busy, with at least 90% of it useful work, reported hourly for each node.

These are rulings. Lanes act on them without asking again. Changes to the live nodes need no separate written plan to Daniel for
the one-pool work: the cutover plan is approved and infra owns the details. Anything outside it (spend, IAM, the VM lifecycle,
destructive steps) still goes to Daniel.

## Later rulings

- **19:33Z, approvals via Slack:** every approval moves to Approve/Deny buttons in private `#approvals` (`C0C5UCA0S0Z`). Only
  Daniel's user id (`U0BEN96ES8Y`) can decide. `/approvals` stays as the history and the fallback. The console coordinator
  (bc-ddee017b) builds the website route, and infra builds `research slack approval`.
- **19:44Z, Slack relay: yes.** The docs-site broker holds the bot token and relays an allowlisted set of Slack calls for Verity
  agents that authenticate with Cursor OIDC. Running coordinators get Slack without a relaunch.
