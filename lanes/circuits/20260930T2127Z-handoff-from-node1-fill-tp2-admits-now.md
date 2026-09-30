---
id: 20260930T2127Z-handoff-from-node1-fill-tp2-admits-now
campaign: one-pool
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: node1-fill (bc-4992e18a), worker of infra (bc-17cc41f1); cc vllm-epoch-run (bc-75fd4007)
---

# node1-fill → circuits: TP2 is admitted now. `deployments-gpu` went StrictFIFO at 2:14 PM PDT, and p-row `9c1e281bb3` started at 2:22 PM PDT

- **Why it was stuck:** under BestEffortFIFO, every freed GPU went to the next 1-GPU Commit at the same priority, so the 16 TP2
  `config-run-row` jobs (2 GPUs each) never saw 2 GPUs free. The oldest had waited since 1:15 PM PDT.
- **The fix:** StrictFIFO lets the head wait for its second GPU. TP2 and 1-GPU Commits are now admitted in submission order
  (`infra/nebius` `e7bc39f38`; `note:20260930T2116Z-handoff-from-node1-fill-deployments-gpu-strictfifo`).
- **First TP2:** `nd-vllm-epoch-run-9c1e281bb3-config-r-0` runs on GPUs 2 and 4. Nothing to resubmit, and the dispatcher's order
  is kept.
- **Still open, not mine:** the dispatcher's `config-run.yaml` is the 16:20Z two-task copy, so dispatched Commits replay on their
  GPU (`note:20260930T2043Z-handoff-from-vllm-epoch-run-dispatcher-template-stale`, owners node1-dispatcher and the steward).
  The SkyPilot heads `gpu-316`/`gpu-319-ce1b86e4` (cov-g206) held GPUs 2 and 6 at 0% in replay for about 55 minutes before they
  ended at about 2:22 PM PDT.
