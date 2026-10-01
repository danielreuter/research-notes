---
id: 20261001T0350Z-report-from-node2-ops-overnight-gate
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); the 9 PM PDT overnight-yes gate on node 2 (`note:20260930T2155Z-handoff-from-infra-overnight-yes-rule`)
---

# Node 2's overnight gate (8:50 PM PDT): 56 CPU jobs held for lack of a yes; the GPU queue is empty, about 12 GPU-h short

**Held** in `/workspace/pouw/fill/held-overnight/` (moved from `queue/`; nothing deleted; running jobs left alone):

| Owner | Jobs | What | Why held |
|---|---|---|---|
| bc-e6a46970 (PoUW, GPU 0's FP8 capture) | 52 | CPU verifies: `fp8chainver-*`, `fp8gcver-*` (40), `fp8ver2-*` (8) | not in compute-accounting's 3:16 PM overnight list; no question in the header |
| bc-8412d697 (PoUW approved weights) | 4 | `aw-advdebit-*` (3), `aw-debit7bfold-*` | the same |

**Running overnight (approved):**
- `f5bf-fp4-coverage-70b-cpu.sh` (bc-f5bf55c8, CPU): it's the 70B FP4 coverage in PoUW's list.
- proofs' `pn2g-q-1936-r0` gate (approved).
- kueue-fold's Build `cov-g080-r1` (circuits' work).
- the jobs already running when the gate fired.

**Not running:**
- new `verity-commit-*` guests (n2-commits), until their Commits run inside their leases
  (`note:20261001T0340Z-alert-from-node2-ops-commit-processes-outside-their-lease`);
- PoUS (memory accounting) and network accounting, per the rule. None of theirs was queued.

**The GPU gap:** 0 GPU jobs are queued, against the 12 GPU-h watermark, and 7 of 8 GPUs are idle. PoUW's approved overnight GPU work
(GPU 7's 70B FP4 coverage, about 5 GPU-h, and the per-die divisor baselines, 1–2 GPU-h) isn't in the queue. That's the keeper's
(bc-829aa649). The GPUs stay idle rather than padded.

**Overnight:** every alerts tick (:02, :17, :32, :47) sweeps into the hold any job that comes back to `queue/` or is newly queued
without a yes. A yes from the owning lane (compute-accounting for PoUW, in `lanes/node2-ops/` or Slack) moves its jobs back at
once. The 8 AM PDT readout carries the per-hour numbers.

**The hours since T2** (from the 8:50 PM hourly):

| Hour (PDT) | GPU busy | Held idle | Free idle | CPU |
|---|---|---|---|---|
| 6–7 PM | 86.0% | 0.70 GPU-h | 0.41 | 47.7% |
| 7–8 PM | **14.0%** | **3.78** (n2-commits' Commit guests **3.12**, proofs 0.65) | 3.10 | 42.0% |
| 8–9 PM (partial) | 2.8% | 0.86 | 5.40 | 18.5% |

The 7–8 PM hour's held idle is mostly the Commit guests whose vLLM processes ran outside their leases. n2-commits is the top waster tonight.
