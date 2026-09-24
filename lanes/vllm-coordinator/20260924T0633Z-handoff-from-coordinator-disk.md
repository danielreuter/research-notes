---
lane: vllm-coordinator
kind: handoff
from: coordinator (verity morning-tables session)
created: 2026-09-24T06:33Z
---

# Shared laptop disk: your 5.2 GB fixture is the one blob `evict` cannot free

The laptop hit the guardian's 3.5 GB disk floor at 06:24Z and it SIGKILLed lane processes (both sessions are exposed). Cursor's
`state.vscdb` is 74 GB and grows ~1 GB/h with the agents running, so free space keeps shrinking until a Cursor restart + vacuum.

`research data evict` holds back `art:e7ad07834c92ec8ffc2992d9a8857680e8ba058a23a8c6595d7f3c1c903f774a` (fixture/v1, row #57
match values, 46 GB tree, 5.16 GB of it local): flagged remote but never verified. If its push is complete, a
`research data push <art> --verify head` (or `research data preserved <art>`) then `research data evict --target-free-gb 9`
frees 5 GB; if the push is still running, nothing to do until it lands. I did not touch it.

I freed 3.5 GB of finished-lane /tmp scratch on my side (now 7.0 GB free).
