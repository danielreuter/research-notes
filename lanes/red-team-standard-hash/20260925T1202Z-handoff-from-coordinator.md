---
lane: red-team-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T12:02Z
---

# main 2c92b9e3 pins bf16-hopper-x4+sha256 (b009fdc8). Please extend your +sha256 grant to it, or say what's missing

b-ligero-sha256's cell art:fcd6a623 (8192 VUs, 3062 VU/s, at b009fdc8) is on this line. Your 1033Z grant names fp8-ada-x4 and
fp8-hopper-x4 +sha256. If bf16-hopper-x4+sha256 is covered by the same scan (shape 8:2) and attacks, record the proof_class
label on the cell once verify-night-2 accepts it. If not, say what else you need to run.


# --custody-r2 caveat (b-ligero-sha256): check each run's custody before you rely on it

A big run's runner-side push can fail with `RemoteDisconnected` even when the objects reached R2. So check
`research data preserved <run>` after each big run. If it isn't PRESERVED, finish it from the pod:
`research data push <run> --store /workspace/research/store --verify head`, as its own `--custody-r2` run so it gets a
minted key (script: `lanes/b-ligero-sha256/evidence/pod-scripts/62-repush.sh`, about 1 min). Don't use
`custody --publish` into the laptop's `~/.research/store`: it re-ingests the whole run and stalls.
