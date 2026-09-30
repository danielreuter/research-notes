---
id: 20260930T2110Z-handoff-from-infra-t3-tonight
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: T3 is due by 11:59 PM PDT tonight: #586 merged, `research run --queue` live, node 2 switched, and a first lane job through the queue

These are Daniel's targets (`lanes/infra/20260930T1845Z-report-infra.md` § Targets). Put the submit path first. The merge of #586 (after
#592) is requested from the old research coordinator.

Work backward from 11:59 PM PDT, and leave slack for a recorded `check` of about an hour:
- `research run --queue` pushed and reviewed by about 7 PM PDT;
- agent mode deployed and the switch made by about 9 PM PDT;
- the first lane job by about 10 PM PDT.

If a step will miss its time, say so in `lanes/infra/` at once, with what would make it fit.
