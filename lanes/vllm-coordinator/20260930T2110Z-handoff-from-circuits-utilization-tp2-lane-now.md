---
id: 20260930T2110Z-handoff-from-circuits-utilization-tp2-lane-now
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: PR A/B are priority 1 now; grant #598/#599 the moment the Phi-3 B8 probe passes, and start the TP2 lane's 2-rank Build fix now

Daniel's targets (2:06 PM PDT): node 1 ≥60% GPU-busy by 3:30 PM PDT, both nodes ≥80% by 6:00 PM PDT. Node 1 was 4% busy 1–2 PM.
The replay on the GPU is the biggest cause, so PR A/B (#599/#598) are priority-1 work.

- **The Phi-3 B8 probe** (`cfgtp2-deferred-phi3b8g`) was waiting for admission behind >6 waiting jobs. I've asked @infra to admit
  it at top priority (Slack thread 1790802527.971209). Please have the TP2 lane drop `/tmp/resubmit.sh`'s ">6 waiting" gate for it.
- **Grant #598/#599 in the same turn the probe passes**, file the merge request, and send the replay task's measured peak memory to
  the steward (the template asks 64 GB). Epoch-run's note: #503's uniform replay draw had to be ported into PR A's `c2_replay.py`
  and `replay_bundle.ARGS`; whichever of #503 and PR A lands second needs those two lines.
- **Don't wait for the acceptance to start the TP2 lane on the GPU-less 2-rank Build** (my 1:30 PM handoff): the 91 TP2 jobs hold
  both GPUs through their Build now, so it's also priority 1. It can code while the probe queues.
- The dispatcher's stale two-task template (epoch-run's 1:43 PM finding) is with @infra; epoch-run keeps PR B on its run branch.

Your Slack relay is live, so post results on Slack or here, whichever is faster.
