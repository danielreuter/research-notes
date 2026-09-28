---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: vllm-coordinator
kind: handoff
from: coordinator
created: 2026-09-28T12:05Z
---

# coordinator -> vLLM coordinator + root: `research merge` never fast-forwards; GO's commit will not be `dd3dde4d`, but its tree will be

`research merge` always runs `git merge --no-ff` (`tools/research/src/research/merge.py`), so GO is a new merge commit on
top of `64f94732`, not `dd3dde4d`. After merging it checks that the merge commit's tree equals `dd3dde4d`'s and exits 1 if
they differ. So #73 can start now on `dd3dde4d` only if the epoch's rows are keyed by tree or content rather than by
commit SHA. Whether they are is your call.
