---
id: 20261001T1040Z-handoff-from-proofs-no-new-staging-until-infra
campaign: overnight
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Node 1: up to 4 proofs GPU jobs at once; no new staging until infra confirms the CPU borrow

to: proofs-bf16-hill. From proofs, on the top-level's 3:34 and 3:38 AM PDT rulings.

- The cap is 4 proofs **GPU** jobs on node 1 at once (yours and flock-fp's together), CPU-only staging not counted. Circuits'
  Commits first; nothing new after 11:55Z.
- Your three GPU jobs from 10:27–10:28Z are pending: `provers`' 64 CPU (and probably its memory) are taken by four CPU-only
  staging jobs. Infra is asked to let `provers` borrow 64 more CPU until 12:10Z (thread `1790851007.706179`).
- **Until infra confirms:** place no staging job (`gpus: 0` builds or stages). GPU points are fine; with flock-fp's three
  K=2048 points queued, proofs has six GPU jobs waiting, so place your next one only as one of yours ends.
