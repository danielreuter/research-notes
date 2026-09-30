---
id: 20260930T2022Z-checkpoint-replay-on-cpu-phi3-queued
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: report
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2 (bc-35ab914e)
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

Checkpoint: PR A is `15c0f8b98` and PR B is `96dfc94b4`. SmolLM2 acceptance is done (see
`note:20260930T2006Z-handoff-from-vllm-config-run-tp2-replay-on-cpu-pr-heads`). The Phi-3 B8 deferred probe
(`cfgtp2-deferred-phi3b8g`, `deployments-gpu`) is waiting to be admitted: `/tmp/resubmit.sh` retries while Kueue has more than 6 jobs waiting.
The host watcher is `/workspace/research/runs/cfgtp2-cpu/watch.sh <probe>`.
