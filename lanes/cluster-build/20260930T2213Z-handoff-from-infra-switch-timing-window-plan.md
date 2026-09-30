---
id: 20260930T2213Z-handoff-from-infra-switch-timing-window-plan-cluster-build
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: switch node 2 after tonight's window 3 (about 4:15 PM PDT), once #586's train lands. The 5:00 PM repeat of attempt 67 is the first canary


> **HOLD (3:13 PM PDT):** the 2-window gate changes the approved cutover plan, so it waits for Daniel's OK, which verity-top is
> asking for. **Do not deploy the 4:15 PM PDT switch unless infra relays his yes in this lane.** If there is no yes by 4:10 PM PDT, keep
> the 6-window gate and the switch slot of about 5:45 PM PDT (after window 5), with the 6:30 PM window as the canary. Get everything
> else ready either way.

**PoUW's timed-window plan tonight** (compute-accounting, 3:12 PM PDT). Only the first window is firm; the rest are proposed.
1. Window 6 (#593, CUDA-graph decode), which ran 2:34–2:39 PM (`r20260930-213419-ec49`).
2. About 3:45 PM: #588's plain-GEMM divisors, whole-node.
3. About 4:15 PM: GPU 1's -h2 rows.
4. About 5:00 PM: GPU 2 repeats attempt 67, the canary's spread.
5. About 5:45 PM: window 7, the MVP's -h2 on #596, or a repeat of window 6.
6. About 6:30 PM: attempt 67 again.

**The gate for the live shadow is 2 clean windows, not 6.** Infra shortened it at 1:38 PM PDT
(`note:20260930T2038Z-handoff-from-infra-submit-path-first`), because the replay covers 27 windows with 0 safety divergences
(`art:04f3724c…`). So the switch can come right after window 3 (about 4:15–4:30 PM PDT), once these hold:
- **#586's merge (train TCL):** expected by about 3:45 PM PDT;
- **the live shadow:** windows 2 and 3 are clean, with no safety divergence;
- **deploy together:** agent-mode `gpu-lease` with the `fill_runner` change, outside a window, with 15 minutes' notice to bc-2aa33ad8
  through compute-accounting;
- **the canary** is the 5:00 PM window (attempt 67), which must land inside the 0.13–0.15% spread; otherwise run `cluster agent stop`;
- **the rollback drill** runs in the first hour, run by node2-ops.

If windows 2 or 3 slip, switch after the next two clean windows. The 9 PM PDT cutoff still binds; past it, the switch holds to 8 AM.
Post "switched" with the time in `lanes/infra/`.
