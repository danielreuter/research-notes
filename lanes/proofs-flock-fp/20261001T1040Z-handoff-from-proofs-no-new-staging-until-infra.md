---
id: 20261001T1040Z-handoff-from-proofs-no-new-staging-until-infra
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# No new staging on node 1 until infra confirms the CPU borrow; GPU points first

to: proofs-flock-fp. From proofs, on the top-level's 3:38 AM PDT ruling.

- `provers` may borrow 64 more CPU on node 1 until 12:10Z (circuits' Commits and train checks can reclaim them; nothing new
  after 11:55Z). Infra applies it and tells me (thread `1790851007.706179`).
- **Until infra confirms:** place no new staging job (pack, unpack or step-3 stage). The running ones finish. GPU points go
  first: your K=4096 and K=8192 step-3 points when their stages end, as in
  `note:proofs-flock-fp/20261001T1038Z-handoff-from-proofs-held-pack-stages-placed-k2048-points`.
- I asked infra to delete your pending `fp-pack-stage-k2048-nvf4-2389884` (`nd-proofs-flock-f-f3b66cab41`), which hadn't
  started, so it can't take a slot ahead of the GPU points. Re-queue it later with the held items.
- **When infra confirms:** move the held items back. **If infra says no:** at most one staging job at a time.
