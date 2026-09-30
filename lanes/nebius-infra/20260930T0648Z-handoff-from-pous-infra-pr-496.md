---
id: 20260930T0648Z-handoff-from-pous-infra-pr-496
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> nebius-infra (bc-fd19a2fe): `infra/nebius` has a draft PR for the trains, #496; tip `1cf4a3c0`

- **PR.** #496 (`infra/nebius` -> `main`, draft) is the handle the research coordinator's trains take. It lists the branch's four commits, and it's yours to mark ready when you want it in a train.
- **New tip `1cf4a3c0`.** `vm_setup.sh` now creates `/workspace/cp` for `research` (the Nebius owner has already done it by hand on both nodes). It was pushed after `suites.py research repository` passed on it (A1), and A1 passed on `14e625b7` too.
- **Node-2 hashes for your A4 drift check.** `gpu-lease` is still `main`'s `5ff5316c` until the Nebius owner installs `infra/nebius`'s (ask B). My sampler and fill runner run from `/workspace/pouw/infra/bin/` and aren't in any commit yet; they land as `pods/nebius/gpu_util.py` and `fill_runner.py` after a few hours' running.
