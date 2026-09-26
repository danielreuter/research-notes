---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-m32 (bc-7039be6c-2a9f-5501-af51-ee96bf96b428)
created: 2026-09-26T01:10Z
---
# DEADLINE vllm-rf-m32: confirming gate (a) on main 5f8d8789 runs past 03:00Z (ETA ~03:40Z)

- Run r20260925-224745-e739 on vyv-rf-m32-reg (fjr66whubb8kn8, cpu3m 32 vCPU / 256 GB, $1.76/h). Gate (a) T0+T1 has run since
  22:47:52Z. At 01:05Z it was at 82 of 158 tests, about 48% of a23b's per-test time profile (6391 s total). It is healthy: pytest RSS
  30 GB, cgroup 44 GB of 256 GB. It runs about 2.7x slower than a23b's pod because the host is shared (EPYC 7713, load average about
  570).
- Projection: about 2.5 h more, done around 03:35–03:45Z. That's past my brief's 03:00Z pod deadline. Please extend the vyv-rf-m32-reg
  guard to 04:30Z, or tell me to stop it.
- Spend: task 2 is at about $4.6 now and about $8.9 at the ETA (cap about $9). The lane total is about $9.3.
- Why I'm not restarting: a fresh pod means a new bootstrap, a prefetch and a key mint, plus about 1.8 h of gate even on a quiet host.
  That's no earlier and costs more.
- The WAIT checkpoint has check-back 03:45Z. On wake: jdiff vs a23b, preserved, terminate, "CONFIRM gate (a) on main 5f8d8789".
