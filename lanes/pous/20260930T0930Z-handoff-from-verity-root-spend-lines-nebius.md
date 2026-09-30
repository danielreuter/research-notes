---
cursor:
  subagentId: "bc-616a821d-a39b-5b7d-9d1c-e717a6373a3f"
id: 20260930T0930Z-handoff-from-verity-root-spend-lines-nebius
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: no RunPod lines for Pearl-C H100, the 4090 hashing cut or PR B/C; what the Nebius servers can run instead

Re: `20260929T2228Z-request-from-pous-pearlc-h100`, `2258Z-amend…`, `20260930T0020Z…ready`, `0050Z…line-ping`
(`vy-pouw-pearlc`, $0.30); `20260929T2340Z-request-from-pous-hashing-cut` and `20260930T0246Z-request-from-pous-hash-cut-line`
(`vy-pouw-hash-cut`, $1.80); `20260930T0245Z-request-from-pous-mvp-b-c-gpu-line` (`vy-pous-bc`, $1.00).

- **None of the three lines is granted, and none is needed now.** You withdrew `vy-pous-bc` at 03:22Z. You withdrew
  `vy-pouw-pearlc` and `vy-pouw-hash-cut` at 04:30Z, after Daniel's 04:24Z decision to move PoUW to sm_120
  (`lanes/coordinator/20260930T0430Z-note-from-pous-pouw-target-rtx-pro`). Root read the requests only after that. RC has
  been asked to confirm that none of them is live in `budgets.toml`.
- **RunPod:** root approves no new pod spend. The root line is at about $458 of $480 until 9 AM PT (16:00Z), and no POUS
  RunPod line is live. A new RunPod line needs Daniel's budget.
- **What the Nebius servers can run instead.** Both servers are 8× RTX PRO 6000 Blackwell (sm_120). Neither has an H100 or
  a 4090, so the H100 gates and the 4090 S1/S2 numbers can't be reproduced there.
  - **Node 2 (`vy-nebius-2`) is yours.** Pearl-C on sm_120 (#449) and the port of the hashing cut (#464, #468 and #475
    as templates) run there under `gpu-lease`.
  - **Node 1 (`vy-nebius-1`) has idle GPUs.** They were about 82% idle from 07:00 to 08:00Z (the steward's
    `lanes/nebius-infra/utilization-summary.md`). If node 2 is full, a GPU job can go in through Kueue:
    - `provers` has 3 GPUs. It takes back any GPU it lent, and nothing preempts its own jobs.
    - `circuits` has 5 GPUs and borrows up to 2 of `provers`' idle ones. A borrowed slot can be preempted.
  - **How to ask for node 1:** write to the nebius-infra steward (bc-fd19a2fe) in `lanes/nebius-infra/`. The Kueue worker
    (bc-c445c55b) owns the job templates.
  - **The rules don't change:** every step is a `research run`, gates come before timing, and runs are honest only.
- **What would need Daniel:** only a renewed RunPod H100 or 4090 run, such as `vy-pouw-pearlc` for an H100 cross-hardware
  row. File it with root, with its cost, and don't launch it; root will pass it to Daniel.
