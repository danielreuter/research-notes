---
lane: research-papercuts
kind: state
repo: verity
origin: lane/research-papercuts
---
# research-papercuts state

- tip: lane/research-papercuts @ 9c908309 (base origin/main@0b0768ed)
- worktree: ~/projects/verity-wt/research-papercuts
- test pod: vyv-v2cpu2 (/workspace/papercuts, ramlock research-papercuts.json)
- done: item 1 (9c908309)
- running: items 2-4 (drain reason, machines.toml entry, targeted label push)
- next: item 5 (preserved default mode), 6 (mint-credential message), 7 (source shipping)
- baseline main@0b0768ed on the pod: 302 passed, 1 skipped, 6 failed (environmental: root ignores read-only modes x2,
  no rsync, PYTHONDONTWRITEBYTECODE in my wrapper [removed], directory-order ties x2)

## log
- 06:55Z started; worktree up at origin/main 0b0768ed
- 07:10Z item 1 committed + pushed 9c908309 (targeted tests 113 passed on the pod)
