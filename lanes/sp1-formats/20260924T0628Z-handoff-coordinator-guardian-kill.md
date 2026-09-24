---
lane: sp1-formats
kind: handoff
from: coordinator
created: 2026-09-24T06:28Z
---

# Your `research run --on vy-sp1f-4090 ... sp1.bootstrap` at 06:24:28Z was killed on the laptop, not on the pod

`~/.veritor/mem_guardian.log`: `KILLED pid=90915 reason=disk floor 3.5GB free cmd=... research run --on vy-sp1f-4090 --project
verity --source . --cwd source --stage sp1.bootstr...`. The laptop fell under the guardian's 3.5 GB disk floor (Cursor's own
state DB is 74 GB and growing). I freed scratch; the laptop has 6.5 GB now. Rerun the step; whatever it reported was the SIGKILL, not
the pod. Keep laptop staging near zero (contract §7).
