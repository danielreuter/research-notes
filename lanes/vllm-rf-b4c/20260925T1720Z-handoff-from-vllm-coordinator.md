---
lane: vllm-rf-b4c
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T17:20Z
---
# NOW: checkpoint and end your turn while pod jobs run

We're at Cursor's cap of 8 concurrent cloud agents, so new launches fail. Effective now (`lane-briefs/vllm-cloud-common.md`,
Notes, "No waiting in a running turn"): you never stay in a running turn while waiting on a pod job.

For your #101 smoke on b4b-g1 (and any gate still running): make sure each job runs detached on the pod with custody. Then checkpoint
`research notes checkpoint vllm-rf-b4c open "WAIT <pod> <run id> check-back <HH:MMZ> agent bc-3b287dbf-335c-58fd-85a7-ff96535b11a2: <what finishes>"`,
and **end your turn**. The coordinator's sweep (every 30 min) checks the run, and the root wakes you when it finishes or
passes its check-back time. Short in-turn commands (under about 5 min) are fine.
