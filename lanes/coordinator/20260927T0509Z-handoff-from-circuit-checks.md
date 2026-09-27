lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-27T05:09Z

# PR #100: check passed on 999eb9e2 (r20260927-042926-b9e3), but main took #85 and #89 at 04:39Z; re-recording on fe196b6c as r20260927-050901-72c2

- **r20260927-042926-b9e3** (999eb9e2) **passed**: pytest 2834 passed; circuit-check 798 targets, 0 new failures, 22 known. The gate
  still refuses it because main moved to 8515c79e (#85 Lean verifier, #89 soundness).
- **Merged main at fe196b6c.** With #85 on the tree, check's Lean hook is on: `lake build` (the pinned Lean 4.34 toolchain installed
  through elan when missing, as ci-pod.sh does) and `unit_cut_agree.py` (the Lean partition check against
  verity.ir.partition) are required.
- **Decision for you or Daniel:** the upstream cross-check (ci-pod.sh / ci.py) needs `ci-bundle.tar.gz`, which is upstream flock
  sources plus store inputs fetched with credentials, made by `ci-bundle.sh`. A pod can't build it inside check. For now check runs
  the cross-check when the run is sent the bundle (`--send ci-bundle.tar.gz`) and otherwise skips it by name, leaving the cross-check
  as the recorded `flock_agreement` job. To make it required on every merge, the bundle has to go with every check run, and the
  cost is one `--send` flag plus cargo builds of upstream on each run. Say which and I'll change it.
- **Now:** r20260927-050901-72c2 on vy-circuit-checks-cpu4, expected about 05:50Z, since the Lean build runs last. The attempt id follows
  when it passes. A Lean pretest build is running on the same pod, so a failure would surface early.
