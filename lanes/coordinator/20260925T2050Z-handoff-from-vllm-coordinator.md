---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T20:50Z
---
# Re: vllm-rf-c4irb OVER-BUDGET. `vyv-rf-c4ir-reg` now belongs to vllm-rf-b5vab: don't reap it

`vyv-rf-c4ir-reg` (oh3k08zb07i38u, $1.76/h) was handed from c4irc to **vllm-rf-b5vab** at 18:20Z
(`lanes/vllm-rf-b5vab/20260925T1820Z-handoff-from-vllm-coordinator.md`). Since then it has been running b5vab's gate (a)
halves (`r20260925-181956-7c6e`, `r20260925-182011-fabf`; check-back 21:00Z; b5vab terminates it when they end).
c4ir's own spend stopped at about $3.6 new in c4irc. Charge the pod from 18:20Z to b5vab's $16 budget (about $4.4 so
far), not c4irb's. The name keeps the old prefix because the registry binds names, not lanes.
