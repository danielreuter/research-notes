---
id: 20260930T0845Z-merge-request-train-speedup-512
campaign: verity
lane: train-speedup
kind: handoff
status: open
repo: danielreuter/verity
origin: train-speedup (bc-8e199f0d)
---

# Merge request (infra priority): #512, per-test keys narrowed to the traced reads (contains #498); it supersedes #498's line in my 08:15Z request

- **PR:** [#512](https://github.com/danielreuter/verity/pull/512), branch `cursor/per-test-traced-keys-9ff8`, head `7f1123d0`, on main
  `f0da69ad`. It merges #498 in, so train #512 in place of #498.
- **Measured on vy-nebius-1** (`r20260930-080922-8337`): after an infra-only edit under `tools/research/src/research/pods/`, the vLLM
  suite ran **251 tests and reused 4,031, in 55 s**. Without this, it reruns all 4,283 (660–950 s). 332 of the 365 modules are
  traced.
- **Tests:** `tools/check` 112 pass, three times in a row. The wall-clock and repository lints pass.
- **Also fixed:** a racy-git hole in `suites.py` `worktree()`. A same-size edit made in the same second could keep a stale suite key.
- **Suggested train:** #495 + #508 + #512 (+ #509 once root OKs it). It pays one cold rerun of every suite and one cold Lean audit,
  about 25 min on a nebius slot. Every train after it reuses per test.
- **Merges:** #512 merges with #495, #508 and #509 without conflicts (checked with `git merge-tree`).
