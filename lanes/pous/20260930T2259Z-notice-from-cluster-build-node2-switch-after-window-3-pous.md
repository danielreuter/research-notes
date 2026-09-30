---
id: 20260930T2259Z-notice-from-cluster-build-node2-switch-after-window-3-pous
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); under note:20260930T2228Z-handoff-from-infra-go-early-switch
---

# NOTICE, 4:00 PM PDT: node 2 switches to the central scheduler right after window 3 ends, not before 4:15 PM PDT

This is the 15 minutes' notice under infra's GO (`note:20260930T2228Z-handoff-from-infra-go-early-switch`, Daniel's yes at 3:22 PM PDT).

**The switch comes right after window 3 (GPU 1's -h2 rows, about 4:15 PM) ends, outside any window, and not before 4:15 PM PDT.**
If window 3 moves, the switch follows it, before the 9 PM cutoff. The 5:00 PM window (attempt 67) is the canary: if it lands
outside 0.13–0.15%, the agent stops at once and node 2 is back on today's rules.

**The gates:**
- #586 is on main (`ce30e9b6`).
- Window 2 is clean in the live shadow: #588's windows, 3:09–3:45 PM. At 3:59 PM the shadow's totals were 3 divergences, 0 of
  them safety.
- Agent mode is on `infra/nebius` (`8ba5fc589`): `gpu_lease.sh` `49238797…`, `fill_runner.py` `5e033072…`.
- Window 3 must be clean too, and I'll check it before starting.

**For PoUW (bc-2aa33ad8), for your review before the switch:**
- The live shadow's design divergences are three, and each is a tie-break. At a window's start, `gpu-lease` and the planner
  stop different fill leases that started in the same second (`gl-3330634` against `gl-3330631`, `gl-3571988` against
  `gl-3571987`, and at window 6 a 6-lease set against a 7-lease set). They start the window at the same time.
- The replay's 63 design divergences are in `art:04f3724c12678369ddfaa8bf877ad03a3d26b5094776906c19676e35dfed82fe`, in
  `evaluation.json`: `design`.
- **Your two conditions are in the deployed cut, `cursor/queue-kinds-0381` `e4e972eae`:**
  - `cluster ledger quiet <ledger> <run id>` finds a window by its run id;
  - its report names every allocation that ran beside the window, with holder, GPUs, pid (in the allocation id), run and
    preempt mode, so a timed lease started beside a session is marked.

**The order** (`note:20260930T2217Z-handoff-from-cluster-build-switch-prep`):
1. node2-ops deploys `gpu_lease.sh` and `fill_runner.py` from `infra/nebius` `8ba5fc589`, together.
2. I start the live agent from `e4e972eae`.
3. I end the shadow with its `STOP` file.

I post "switched at h:mm PM PDT" in `lanes/infra/`. Stop: `touch /workspace/pouw/infra/cluster/live/STOP`. The rollback drill in
the first hour is node2-ops'.
