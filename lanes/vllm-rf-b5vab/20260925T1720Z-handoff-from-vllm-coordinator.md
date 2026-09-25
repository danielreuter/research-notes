---
lane: vllm-rf-b5vab
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T17:20Z
---
# NOW: checkpoint and end your turn while pod jobs run

We're at Cursor's cap of 8 concurrent cloud agents, so new launches fail. Effective now (`lane-briefs/vllm-cloud-common.md`,
Notes, "No waiting in a running turn"): you never stay in a running turn while waiting on a pod job.

For your pod search and gate (a): make sure each job runs detached on the pod with custody. Then checkpoint
`research notes checkpoint vllm-rf-b5vab open "WAIT <pod> <run id> check-back <HH:MMZ> agent bc-a4fbe8b2-3532-5d9a-9cfa-bf614fca043f: <what finishes>"`,
and **end your turn**. The coordinator's sweep (every 30 min) checks the run, and the root wakes you when it finishes or
passes its check-back time. Short in-turn commands (under about 5 min) are fine.
