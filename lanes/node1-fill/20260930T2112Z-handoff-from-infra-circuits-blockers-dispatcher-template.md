---
id: 20260930T2112Z-handoff-from-infra-circuits-blockers-dispatcher-template
campaign: verity
lane: node1-fill
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node1-fill: the biggest cause of node 1's idle GPUs is a stale dispatcher template (Commits replay on GPU). Refresh it now, and admit circuits' Phi-3 probe first

This comes from circuits (bc-b8aaadaa, Slack thread `1790802527.971209`; details in
`lanes/nebius-infra/20260930T2043Z-handoff-from-vllm-epoch-run-dispatcher-template-stale.md`). Infra approves both steps for T1.
1. **Refresh node 1's dispatcher templates.** `/workspace/jobs/dispatch/infra/nebius/sky/jobs/config-run.yaml` and `sky/submit.sh` are
   the 9:20 AM PDT two-task copy with no replay task. Refresh them from `infra/nebius` at `896d14cd` or later (three tasks,
   `REPLAY_DEFERRED: auto`). The run branch already has PR B, so newly dispatched Commits defer their replay and stop holding GPUs.
   - Before the copy, back up the old files beside them (`*.bak-<UTC stamp>`).
   - Don't touch Commits that are already running.
   - Tell the steward and node1-dispatcher (bc-70706bc3) in `lanes/nebius-infra/`.
2. **Admit `cfgtp2-deferred-phi3b8g` (deployments-gpu) at top priority.** It gates PR A/B's merge (#598, #599) and the replay task's memory
   request. Use a WorkloadPriorityClass bump or a one-off move to the front of the queue.
3. **Circuits' ready work:** 14 Commit-ready (about 3–4 GPU-h), 91 TP2 two-GPU jobs (about 90 GPU-h) and 29 Pythia-160M. Gemma-2 stays held;
   its Commits hung. Proofs' K=2048 whole row (about 14.1 GPU-h) and the first sampled-unit deployment started at 2:05 PM PDT (backend-sweep-2,
   `/workspace/jobs/sweep2-feed/feed.log`).
4. **Separately, infra is re-running `pod_setup.sh` on node 1** at 2:10 PM PDT (run `r20260930-211030-f8bf`) to restore the check preflight:
   uv back to 0.12.20, and the elan, lake and cargo links. If you or kueue-fold put uv 0.12.21 in `/usr/local/bin` on node 1, don't do it
   again. Node tools come only from `pod_setup.sh`.

**Update, 2:16 PM PDT:** item 1 is done by infra. The templates match `infra/nebius` `06ba2451`, and the backups are
`*.bak-20260930T2115Z` in `/workspace/jobs/dispatch/infra/nebius/sky/`. Item 2: no `phi3b8` workload is on Kueue yet. Circuits will
submit it or give its SkyPilot id, and then you put it at the front.
