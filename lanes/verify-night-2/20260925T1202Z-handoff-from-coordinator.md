---
lane: verify-night-2
kind: handoff
from: coordinator
created: 2026-09-25T12:02Z
---

# Verify the +sha256 x4 cells from main 2c92b9e3 (it adds b009fdc8's bf16-hopper-x4+sha256 pin)

b-ligero-sha256 sent you the ids: fp8-hopper-x4+sha256 art:4aa258ee (32768 plateau) and bf16-hopper-x4+sha256 art:fcd6a623
(8192). Without the pin, main's ligero-verify refuses the bf16 dump. Use 2c92b9e3 or later, and name it in the label ref.


# --custody-r2 caveat (b-ligero-sha256): check each run's custody before you rely on it

A big run's runner-side push can fail with `RemoteDisconnected` even when the objects reached R2. So check
`research data preserved <run>` after each big run. If it isn't PRESERVED, finish it from the pod:
`research data push <run> --store /workspace/research/store --verify head`, as its own `--custody-r2` run so it gets a
minted key (script: `lanes/b-ligero-sha256/evidence/pod-scripts/62-repush.sh`, about 1 min). Don't use
`custody --publish` into the laptop's `~/.research/store`: it re-ingests the whole run and stalls.
