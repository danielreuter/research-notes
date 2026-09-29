---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T17:18Z · re: `20260929T1705Z-checkpoint-…`

**#101's recovery is agreed.** Rebuild the record off-pod from the preserved Build and records, then run `rebaseline run`, the gate and the write. Apply the same to any other row cut this way; its evidence must be preserved in full, as #101's was.

**Please also open a small PR on main** fixing #346's flaw: bound `epoch_row.sh`'s record stage by the run end, not the job end. Add an `EPOCH_NOW` test where the store ends near the job end. The running rows keep their code (`14f027c3`); the PR is for the next epoch.

**#70's community-driver refusals and the switch to secure only:** fine.
