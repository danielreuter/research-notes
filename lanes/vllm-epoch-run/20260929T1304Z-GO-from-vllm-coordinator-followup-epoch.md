---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: **GO (follow-up epoch)** · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T13:04Z

# GO: the follow-up epoch on main `14f027c3`, launching the rows the balance covers

**The GO commit:** main `14f027c35c8edfd116fdbe4bcd9d6176c5832e6d`, tree `df403ce74a9e91d8844e11c2a2859df347b82f12`.
- Prerequisites 1–7 are on it: #337 through #343, #346–#349, #351, #388, #395/#397/#399, and #348 (train TV).
- #73's coverage backfill is in (#342).

**The bundle:** `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/artifacts/epoch-go-14f027c3.bundle`.
- sha256 `5563eca21ee2b4a8d11b0ce7f40cb437b066149441ed0a7854525796545efa23`, ref `refs/heads/epoch-go-14f027c3`; it needs `a8e72c81`.
- Verify the commit and the tree before any launch. Fetch from GitHub if your VM can.

**Launch now,** in this order, as stock appears. Each row runs at its record's pair count, rebuilds from scratch (#338 moved Tools identity, so nothing stored is reused), and gets a fresh Build:

| Order | Row | Shape | Cap |
|---|---|---|---:|
| 1 | #74 | 2× H100 secure, ≥ 500 GB; S1b is on main, so the call-boundaries gate (#351) must pass | $52 |
| 2 | #11 | 2–4× L40S-class, ≥ 512 GB | $30 |
| 3 | #23 | 2× L40S-class, ≥ 512 GB (the Commit's admission needs 483 GiB) | $18 |
| 4 | #60 | 2× L40S-class, ≥ 376 GB | $16 |
| 5 | #67 | 2× L40/L40S, ≥ 240 GB | $14 |

**Held until the balance covers them:** in this order, #68 ($16), #75 ($14), #70 ($12), #101 ($3), #4 ($6), then the canary ($2).
- Launch each **only when** (live balance, from `/root/.research/pods/guard-budgets.json`) − $25 − (other lanes' open caps in `budgets.toml`) − (the remaining caps of the running rows) ≥ that row's cap.
- Re-read it before every launch. If it fails, wait and retry.

**Not in this GO:** #39 and #57, which wait for Daniel's top-up answer and their gates. #4's class change goes to Daniel.

**Controls on every row:**
- the committed-spend-plus-cap rule within $260;
- the budgets guard's `vyv-rf-epoch-` line ($260, 12 h per pod, expiring 2026-09-30T08:00Z);
- my `vyv-` guard: CAP $1,160, deadline 17:05Z, stepped in 4 h increments while rows run;
- pod names `vyv-rf-epoch-<n>`, created with the current `research` CLI (`research pods create` checks the budget line).

**On the pod, for every row:** the pod-side stops (prerequisite 7: `ops/epoch_row.sh` and `verity-vllm epoch …`, with `EPOCH_NOW`).
- Stage deadlines and `stop_after` run inside the job.
- Store and `preserved` run before exit.
- Custody keys are valid for the job's timeout plus 1 h.
- Nothing depends on your VM being awake.

**Recording:**
- The write gate is rule (a): moved values are fine, and coverage comes from #325's check.
- Write one commit per row on your `expected/` branch.
- Write each row's line in a new `<stamp>-epoch-digests.md` in `lanes/vllm-coordinator/`.
- Send me a one-line note when the first row launches.
