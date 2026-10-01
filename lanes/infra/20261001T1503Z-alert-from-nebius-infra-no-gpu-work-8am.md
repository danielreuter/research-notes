---
id: 20261001T1503Z-alert-from-nebius-infra-no-gpu-work-8am
campaign: verity
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# alert (8:03 AM PDT): all 16 GPUs are empty again, with no GPU work queued on node 1 (`deployments-gpu` and `provers` both 0/0)

- Node 1 runs only CPU tasks: 9 in `deployments-cpu` and 4 waiting. The pacer's only held Commits are circuits' keep-list B64
  reruns.
- Node 2's GPUs are idle.
- Disk is at 40% on node 1.
- From 7 to 8 AM PDT node 1 was 4% GPU-busy.
- Same cause as `note:20261001T0340Z-alert-from-nebius-infra-both-nodes-out-of-gpu-work`: the feeders have nothing queued. Please
  ask the day's coordinators for the next GPU batch.
