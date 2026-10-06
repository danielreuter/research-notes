---
id: proofs/20261006T1700Z-service-stack-restacked
campaign: proof-service
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs coordinator), for top's 11:30 AM PDT mark (the service on main)
---

# The service stack, restacked for one train

The four PRs land in this order, each at the head below. Each is owner-ready (`ready true --by proofs`, on `pr:N@<full sha>`, both stores) and out of draft.

| Order | PR | Branch | Head |
|---|---|---|---|
| 1 | #1316, the two-stage law in core | `cursor/two-stage-law-95d4` | `0a2ea76b30e923ea1dfdaea906b5a3cee0971d6d` |
| 2 | #1324, the proof service's Spec and Stream | `cursor/proof-service-95d4` | `b27c7658ef3608a7de0629be38e1b36cd953a32a` |
| 3 | #1340, TwoStage in a Stream | `cursor/proof-service-twostage-95d4` | `c033af84a20a30c4e46ae927ff48b983e3aea3b5` |
| 4 | #1319, PoUW's two-stage example | `cursor/two-stage-driver-95d4` | `94ecd664835dc4344862905cab22fcfdafcfb942` |

What the restack did:
- #1316 merged main `f5df3bbc5`. Its one conflict was a line of `verity/tests/test_boundaries.py`. Its own patch against main has the same added and removed lines as before: 16 files, 888 insertions and 518 deletions.
- #1324 merged main and then #1316's head, so it merges cleanly after #1316.
- #1340 merged both restacked heads. Its diff against #1324's head is still its own two commits: 4 files, 451 insertions and 94 deletions.
- #1319 merged #1340, adopted #1340's `Stream` (the driver module and its test file are gone), and merged #1340's final head. Against #1340 it is two files, 358 lines added: the README paragraph and `tests/test_service_two_stage.py` (11 tests). Its PR base is now `cursor/proof-service-twostage-95d4`, and its title is "sampled proofs: PoUW's two-stage example on the proof service's Stream".

Evidence, from the proof-service lane's VM:
- Main `cb50af5e8`, then the four in order, merge cleanly (`git merge-tree`).
- At #1319's head, the sampled-proofs suite passed (135 tests), and so did `verity`'s own suite (16) and the vllm tests of the files the stack changes (41).
- `suites.py --quick` didn't finish there: about 400 MB of memory was free and swap was 88% full. The train's `check` runs every suite.

The one grant: #1316 changes `integrations/vllm/`, so it needs `vllm-coordinator`. The grant at `cb4574780` doesn't carry under `queue.carry`, which compares each path's whole blobs against the merge base (the 2 Oct rule). Main has since changed `AGENTS.md`, `README.md` and `test_boundaries.py`, which #1316 also changes. Under Q5 (a grant carries when the PR's own patch is byte-identical), it carries: the five vllm files are byte-identical at `cb4574780`, `646d7f0fe` and `0a2ea76b3`. The other three PRs touch no path with a grant rule.
