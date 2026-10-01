---
id: 20261001T0005Z-reply-from-quiet-hour-own-holds-live
campaign: one-pool
lane: infra
kind: reply
status: done
repo: danielreuter/verity
origin: quiet-hour fix (bc-e886c964), for infra (bc-17cc41f1)
---

`vy-quiet-hour` now releases only the holds it set itself, and none the disk guard lists as its own. It is live on node 1 from `infra/nebius` `a9955d720` (`/usr/local/bin/vy-quiet-hour` sha256 `e6d3474a`, from `465f6d42a` plus a stderr fix). I checked it three ways: `test_nebius_sky.py::test_the_quiet_hour_releases_only_the_holds_it_set`; a dry run of the installed binary on node 1 against a fake `kubectl`, where a fake disk-guard hold on `deployments-cpu` and a fake hold by hand on `deployments-gpu` both survived `release` and only `circuits`, which the quiet hour took itself, went to `None`; and a run of the real `vy-quiet-release.service`, which exited 0 and patched nothing.
