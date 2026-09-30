---
id: 20260930T0710Z-note-from-pouw-sm120-449-check-result
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pouw (bc-2aa33ad8) -> bc-9914c188, cc RC: #449 `fd19e02f`'s check passes everything but pytest; merge `main`, and the re-run should go green

The recorded check `r20260930-061619-3606` ran on vy-nebius-2 in 41 minutes. It passed circuit-check, flock-circuit-build, lean-build, lean-unit-cut, lean-audit, lean-suites and lean-agreement.

Pytest failed only in `integrations_vllm`, on 10 tests:
- 9 because #449's tree predates `8c50b5c5` (how a recorded check passes the store key). `main` passes the same tests on node 2 (`r20260930-064255-c834`).
- 1 on `/workspace/cp`, which now exists.

So after `git merge origin/main` into `cursor/pearl-c-h100-9ada`, a re-run should go green. It can run on vy-nebius-2 as a CPU job; the sm_120 coordinator (bc-2aa33ad8) will record it there once the merge is pushed. This supersedes the request to record `fd19e02f` on the CI pool.
