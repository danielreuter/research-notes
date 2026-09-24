---
lane: research-papercuts
kind: state
repo: verity
origin: lane/research-papercuts
---
# research-papercuts state

- tip: lane/research-papercuts @ 05912a80 (base origin/main@0b0768ed)
- worktree: ~/projects/verity-wt/research-papercuts
- test pod: vyv-v2cpu2 (/workspace/papercuts, ramlock research-papercuts.json)
- done: item 1 (9c908309), item 2 (25d4d155), item 4 (374c2997), item 3 (05912a80)
- running: item 5 (preserved default mode)
- next: 6 (mint-credential message), 7 (source shipping), full suite, ready note
- baseline main@0b0768ed on the pod: 302 passed, 1 skipped, 6 failed (environmental: root ignores read-only modes x2,
  no rsync, PYTHONDONTWRITEBYTECODE in my wrapper [removed], directory-order ties x2)

## log
- 06:55Z started; worktree up at origin/main 0b0768ed
- 07:10Z item 1 committed + pushed 9c908309 (targeted tests 113 passed on the pod)
- 07:20Z items 2, 4, 3 committed + pushed (drain/labels/store/remote targeted tests green on the pod, 2 known root-env fails only)
