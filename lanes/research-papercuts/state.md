---
lane: research-papercuts
kind: state
repo: verity
origin: lane/research-papercuts
---
# research-papercuts state

- tip: lane/research-papercuts @ bdb2a7fc (base origin/main@0b0768ed)
- worktree: ~/projects/verity-wt/research-papercuts
- test pod: vyv-v2cpu2 (/workspace/papercuts, ramlock research-papercuts.json)
- done: item 1 (9c908309), item 2 (25d4d155), item 4 (374c2997), item 3 (05912a80), item 5 (75b9fcdf), item 6 (bdb2a7fc)
- running: item 7 (source shipping: ship only missing files by content hash, then verify manifest + READY)
- next: full suite on 7, ready note to coordinator
- baseline main@0b0768ed on the pod: 302 passed, 1 skipped, 6 failed (environmental: root ignores read-only modes x2,
  no rsync, PYTHONDONTWRITEBYTECODE in my wrapper [removed], directory-order ties x2)

## log
- 06:55Z started; worktree up at origin/main 0b0768ed
- 07:10Z item 1 committed + pushed 9c908309 (targeted tests 113 passed on the pod)
- 07:20Z items 2, 4, 3 committed + pushed (drain/labels/store/remote targeted tests green on the pod, 2 known root-env fails only)
- 07:25Z item 5 committed + pushed 75b9fcdf
- 07:27Z item 6 committed + pushed bdb2a7fc
- 07:31Z full tools/research suite on the pod @ bdb2a7fc: 315 passed, 1 skipped, 5 failed -- all 5 also fail on main (no lane-only failure)
- CHECKPOINT pc-ready MET 07:31Z items 1-6 fixed with tests, pushed lane/research-papercuts@bdb2a7fc; suite 315p/5f (the 5 fail on main too)
