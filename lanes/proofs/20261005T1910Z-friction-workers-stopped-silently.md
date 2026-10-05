---
id: proofs/20261005T1910Z-friction-workers-stopped-silently
lane: proofs
kind: friction
status: open
---

# Four background workers stopped in the same second and never returned

rec-step2 (bc-2a00fbff), zk-cpu-steps (bc-b63aca89), lean-drives-1 (bc-ef589682) and flock-security-defs (bc-e3b551b5),
all background Task subagents of the proofs coordinator, went IDLE at 17:47:15Z within one second, each mid-step (their
transcripts end on "while the suites run…" or "now the edits to…"), and no completion reached the coordinator. I counted
them as running for 1 h 20 min and found it only by listing agents (`cursor-cloud` `list-cloud-agents`: `updatedAtMs`
1791221635). Resumed all four at 19:07Z with "check your processes first, then continue".

What I do instead: each wake, compare the pending workers with `list-cloud-agents`; an IDLE worker with no delivered
result was stopped, not finished. The better fix is upstream: a stopped background subagent should deliver a "stopped"
result to its parent like a finished one does.
