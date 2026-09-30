---
id: 20260930T2228Z-handoff-from-infra-go-early-switch-cluster-build
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# GO: Daniel approved the 2-window gate (3:22 PM PDT). Switch node 2 at the ~4:15 PM PDT slot, under these conditions

This lifts the HOLD in `note:20260930T2213Z-handoff-from-infra-switch-timing-window-plan-cluster-build`. Every one of these must hold:
1. **#586 merged:** train TQS, `r20260930-221143-c9f1`, expected about 3:52 PM PDT.
2. **Windows 2 (about 3:45 PM) and 3 (about 4:15 PM) clean** in the live shadow, with 0 safety divergences.
3. **One deploy, outside a window:** agent-mode `gpu-lease` together with the `fill_runner` `agent.lock` change, with **15 minutes'
   notice** to bc-2aa33ad8 through @compute-accounting.
4. **The canary** is the 5:00 PM PDT window (attempt 67). It must land inside the 0.13–0.15% prefill spread; if it doesn't, run
   `cluster agent stop` at once.
5. **The rollback drill** runs within the first hour, by node2-ops.

If a condition slips, switch after the next two clean windows, before the 9 PM PDT cutoff. **Post "switched at h:mm PM PDT"** (or the
slip, with its cause) in `lanes/infra/` immediately.
