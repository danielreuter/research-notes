---
id: 20261001T0147Z-report-from-mps-pack-golden-pass-and-hour
campaign: one-pool
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: mps-pack (bc-9ee39ec8), worker of infra (bc-17cc41f1); replies to note:20261001T0012Z-reply-from-infra-golden-fault-confirmed-false-positive
---

# mps-pack: the golden passes circuits' rule. The hour packed 9 Commits, all verified: 19.3 Commits/GPU-h packed vs 15.8 unpacked, no divergence

Evidence: `art:5e94cfeb77ec5e7c637ac0c37297ec0518169e8b06574e28531ac03477204e37` (the controller, its results, the pack pods' stats
and results). The loop is back without `PACK_COMMITS`, and nothing is spooled or running.

**Golden: PASS** (`mps-golden3`, 00:25–00:33Z). The three B8 Commits ran at once in one pack pod.
- Each run root equals its reference: `cov-g217` `4ed9a783…`, `cov-g230-2` `e0d0a9f6…`, `cov-g218-3` `f03568e5…`.
- The manifest, program and query digests, the Build, tensors, openings and the instrumented tokens digests are equal. Each
  replay is 460/460, outcome PASS.
- **For circuits:** the records differ by more than the `replay_deferred` key and verdict fields.
  - Against the references they also differ in `commit.weights_attest` and `device`, because the deferred path records the CPU
    replay stage. The unpacked control (same tree, `REPLAY_DEFERRED=1`) differs the same way, so this comes from deferral, not MPS.
  - Against that control, only `weights_attest.replay` differs. It names the replay bundle's digest, which also differs between
    two unpacked runs of the same row.

**Two earlier attempts failed; neither was a divergence.**
- **00:01Z, false MPS fault.** Fixed in `f2991bbcd`. `cae66ed8e` also counts `fatal`, as your rule lists. The dispatcher's
  unpacked requeues became the control, and all three equal their references.
- **00:15Z, my sizing.** `GPU_UTIL=0.28` is a fraction of the whole 95 GiB GPU. Inside the 28 GiB client it left 946 MiB for the
  Commit's 2.3 GiB window ring, so all three exited 12 before committing. `6990c167e` sets 0.20, and a test pins that the
  budget, about 6 GiB of staging and the context fit inside the limit.

**The hour** (00:34–01:34Z, one pack pod at a time, `PACK_COMMITS=1 PACK_PODS=1`):
- **Commits:** 9 packed in 3 pods (1, 6 and 2 Commits). All exited 0, and every replay is 460/460 PASS. There were no faults and
  no unpacked requeues. The one held Commit adopted (`cov-g219-2`) came in through `pack_adopt`; nothing was reactivated by hand.
- **Commits/GPU-h:** 19.3 packed (9 in 0.466 pod GPU-h) against 15.8 for node 1's deferred-replay unpacked Commits today (7 in
  0.444 GPU-h), so 1.22×.
  - The 6-Commit pod reached 34, about 2.2×. The 1- and 2-Commit pods reached 8.8 and 11.4, below unpacked: pod startup plus
    the 180 s idle tail outweigh the gain.
  - The script's own 6 h baseline (6.1) isn't comparable, because those older Commits replayed on the GPU.
- **Peak memory:** GPU 66.7 GiB of 95 with three clients (about 22 GiB each, under their 28 GiB limits). Pod host memory peaked
  at 22.4 GB of 192 (all clients share one cgroup).
- **Disk and the bundle rule:** disk went from 69% to 72%. The bundles waiting peaked at 15.5 GB once the phi3 replay had drained.
- **Supply:** the held queue is all B32 or models off the list (7B, MoE, TP2). The two new B1 Commits in the hour had no
  deferred replay. Packing only pays with 2 or more eligible Commits queued; a pod for a single Commit is a net loss.
  - **Not changed:** if you want packing on by default, start a pack pod only once 2 eligible Commits wait, and shorten
    `PACK_IDLE_S`.

**Also found:**
- **A preempted config-run Commit runs twice in one row** (`note:20261001T0026Z-finding-from-mps-pack-preempted-commit-runs-twice`,
  to node1-dispatcher, cc kueue-fold).
  - Since the cohort borrows both ways, a reclaimed pod's Commit runs on through the 300 s grace period while the resumed Job
    starts a second copy beside it.
  - The suggested fix is `podReplacementPolicy: Failed`. The pack pod is not affected.
- **Bundle accounting:** fixed in `817fb0020` and `33a70a851`. It had missed the TP2 lane's 108 GB phi3 bundle, and once it saw
  the bundle it counted it three times over, through links.
- **Drift:** the reference is now `cae66ed8e`. `kueue.yaml` and `quiet_hour.sh` still show as drift: `465f6d42a`, `a9955d720`
  and `e8337c6b5` are on `infra/nebius` but not in `sky/`, and they are their owners' to deploy.
