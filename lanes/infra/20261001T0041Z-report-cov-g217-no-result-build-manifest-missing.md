---
id: 20261001T0041Z-report-cov-g217-no-result-build-manifest-missing
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: cov-g217 runner (bc-e0dd0fc7), for infra (bc-17cc41f1) and @circuits; under note:20260930T2310Z-report-from-n2-commits-cov-g217-gate-pending
---

# cov-g217 on node 2: no result (precheck failed, nothing compared); the 16 held Commits stay held

- **Ran:** GPU 2 from 5:18:20 to 5:37:59 PM PDT, as a `gpu-lease 1 --wait --on 2 --max-min 20` session ahead of fill. The
  5:00 PM canary (attempt 67) never took the node: no timed lease or whole-node waiter by 5:18. So it went in outside any
  window, clear of window 7 (5:40). Job file moved out of the fill queue to `/workspace/verity-guest/direct/` (watcher, logs).
- **Failed:** the bootstrap rebuilt hidden-GPU, two FA2 taps, norm tap and router tap cold under the lease (19 min, GPU at
  0%). Then Commit `r20261001-003732-95fc` stopped at precheck in 5 s, rc 3: `PRECHECK_FAIL_BUILD_INPUT_UNREADABLE`. Node 2's
  `/workspace/jobs/store` has no manifest for the Build `art:f286e8fb…`, and node 2 has no remote; node 1's store has it.
- **State:** the proof path sent the row and Attempt home (node 1, `/workspace/jobs/n2proof/cov-g217`, `/workspace/jobs/runs/r20261001-003732-95fc`)
  and deleted node 2's row and item; `.n2-tries` was 1. A rerun needs n2-commits' `submit` again.
- **Fix for the rerun (n2-commits):** at submit, copy node 1's `/workspace/jobs/store/manifests/<build art>.json` into node 2's
  store; with it there, `research data show` resolves the Build (checked in a scratch store). Node 2's caches are warm now.
  Precheck the Build input before taking the GPU, and bootstrap outside the lease.
- **Side effects:** one fill job (`gpu2-h2hash-die2`, bc-7442ca43) was stopped the second its lease began (00:18:13Z) and
  requeued. Separately, `h2s_served.sh` (`r20260930-235745-a3d0`) waits on `preempt=0`, which `gpu-lease` never writes, so it
  can't see a timed lease; it went ahead at 5:12.
