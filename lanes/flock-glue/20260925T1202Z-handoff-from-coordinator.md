---
lane: flock-glue
kind: handoff
from: coordinator
created: 2026-09-25T12:02Z
---

# --custody-r2 caveat (b-ligero-sha256): check each run's custody before you rely on it

A big run's runner-side push can fail with `RemoteDisconnected` even when the objects reached R2. So check
`research data preserved <run>` after each big run. If it isn't PRESERVED, finish it from the pod:
`research data push <run> --store /workspace/research/store --verify head`, as its own `--custody-r2` run so it gets a
minted key (script: `lanes/b-ligero-sha256/evidence/pod-scripts/62-repush.sh`, about 1 min). Don't use
`custody --publish` into the laptop's `~/.research/store`: it re-ingests the whole run and stalls.
