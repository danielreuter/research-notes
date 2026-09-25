---
lane: vllm-rf-a5c
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T17:20Z
---
# NOW: checkpoint and end your turn while pod jobs run

We're at Cursor's cap of 8 concurrent cloud agents, so new launches fail. Effective now (`lane-briefs/vllm-cloud-common.md`,
Notes, "No waiting in a running turn"): you never stay in a running turn while waiting on a pod job.

For your re-gate of 40b9e571 on t1: make sure each job runs detached on the pod with custody. Then checkpoint
`research notes checkpoint vllm-rf-a5c open "WAIT <pod> <run id> check-back <HH:MMZ> agent bc-ac8c8a30-44dd-575f-b5aa-45d0e17beb15: <what finishes>"`,
and **end your turn**. The coordinator's sweep (every 30 min) checks the run, and the root wakes you when it finishes or
passes its check-back time. Short in-turn commands (under about 5 min) are fine.
