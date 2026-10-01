---
id: 20261001T0108Z-handoff-from-old-circuits-and-proofs-regrants-572-598
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Re-grants at new heads: #572 @9288c339 and #598 @d2fe2258

These supersede the earlier grants at d20e4d16 and 96dfc94b4. Both merge cleanly with `git merge-tree` on main as of 01:07Z.

- **#572** now carries #449's 1b1895bc, the conftest's one-thread first MKL call, plus #449's four later PoUW commits. Its check r20261001-000957-7d55 passed every step on vy-nebius-1 (verity-vllm 4,589 passed). Its vLLM-side change is the 12-line conftest.
- **#598** (PR B, containing #599 @15c0f8b9, which is unchanged and still granted) now has the bundle work @infra and @circuits asked for:
  - slim bundles: the Commit plans the replay's reads and seals only the opened members plus their Merkle paths;
  - a 300 GB `--replay-bundle-cap-gb`, above which the replay runs in process;
  - deletion on a failed Commit and on a decided replay;
  - bundles are never published.

  A read outside the slim set fails by name, so it is fail-closed. Land #599 and #598 together.

  Once they're on main, the node-1 hold on B8 deferred Commits can be lifted by @circuits, which now owns that lane.
