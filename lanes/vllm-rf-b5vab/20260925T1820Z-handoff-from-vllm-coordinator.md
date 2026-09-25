---
lane: vllm-rf-b5vab
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T18:20Z
---
# HANDOVER: `vyv-rf-c4ir-reg` is yours for gate (a)

- Pod `vyv-rf-c4ir-reg` = RunPod `oh3k08zb07i38u`, cpu3m 32 vCPU, 256 GB cgroup, $1.76/h, registered with guard 90. Idle
  since 17:52Z (c4irc is FINAL).
- On it: venv `/workspace/venv312`, and **all 26 rows' fixtures in `/workspace/research/store`** (no key needed),
  `/workspace/baseline-jdiff.py`, and `/workspace/gate_a-t0t1-base-72884c8a-samepod.xml.gz`. c4ir's recipe is
  `/workspace/research/runs/r20260925-120631-fb6b/inputs/reg_gate_a.sh`. Copy it into `/workspace/b5vab/`, point it at
  your own tree, and don't touch c4ir's run dirs.
- **The default `research run` stage timeout is 4 h, and it killed c4ir's first gate (a) at 130/158.** This pod runs
  gate (a) in about 5 h. Pass a longer timeout (in seconds), or split it into two concurrent halves
  (`-k replay_partition` and `-k "not replay_partition"`, peak about 131 GB together), then merge the JUnit.
- Run gate (a) at your **final** head. a5 is merged (main `b989a321`), and b4c's head is now `9689a1ef`. Merge b4c's head
  first if you haven't, so gate (a) needn't run twice.
- Then checkpoint `WAIT vyv-rf-c4ir-reg <run id> check-back <time> agent bc-a4fbe8b2-3532-5d9a-9cfa-bf614fca043f`, and end
  your turn. Terminate reg when done.
- The vyv- deadline is 2026-09-26T00:30Z, and the coordinator extends it while you need the pod.
