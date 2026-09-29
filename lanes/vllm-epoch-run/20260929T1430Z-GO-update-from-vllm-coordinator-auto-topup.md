---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: **GO update** · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T14:30Z · amends `20260929T1304Z-GO-from-vllm-coordinator-followup-epoch.md`

# GO update: the balance no longer gates launches. Launch the held rows

Daniel: "It'll top itself up." RunPod reloads automatically.

- **Launch now,** in GO order as stock appears: #68 ($16), #75 ($14), #70 ($12), #101 ($3), #4 ($6), then the canary ($2). Drop the balance-coverage test.
- **#39 ($30) and #57 ($15)** are approved once their own gates pass: #244 on main for #39, and #57's host evaluation under about 90 min per Commit. Check each gate before launching.
- **Still enforced:**
  - the $260 `vyv-rf-epoch-` line: the rows total about $251, with #74 at $75;
  - the committed-spend-plus-cap rule within $260;
  - my `vyv-` guard (CAP $1,160) and the budgets guard.
- **The $25 floor is now a tripwire:** if the live balance (`/root/.research/pods/guard-budgets.json`) falls below $25, auto-reload has failed. **Pause new launches** and write one line to `lanes/vllm-coordinator/`. Running rows continue under the guards.
