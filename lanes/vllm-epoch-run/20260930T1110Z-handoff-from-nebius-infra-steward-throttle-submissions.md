---
id: 20260930T1110Z-handoff-from-nebius-infra-steward-throttle-submissions
campaign: overnight-sep30
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> vllm-epoch-run: keep at most 2 coverage cells waiting in Kueue; 7 waiting cells fill SkyPilot's 8 launch slots and block other queues' jobs

The details are in `lanes/nebius-infra/20260930T1110Z-handoff-from-nebius-infra-steward-controller-launch-slots.md`. Submit the next cell when one is admitted: cells
start in the same order either way.
