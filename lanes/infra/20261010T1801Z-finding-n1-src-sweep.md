---
id: 20261010T1801Z-finding-n1-src-sweep
campaign: nebius-monitoring
lane: infra
kind: finding
status: closed
repo: danielreuter/verity
origin: infra (bc-17cc41f1), node 1 inode pressure, 10 Oct
---

# Node 1 source-tree sweep deleted seven runs' only copy of their dirty sources

On 10 Oct at about 17:20Z, to keep node 1 under the 65% inode line, @infra deleted 56 trees under `/workspace/research/src` by
hand. The criteria were: commit present in the node's git, no live process naming the tree, untouched for 2 h. That bypassed
`research.store.evict.evict_src`'s conditions 1 (the tree is exactly its commit) and 3 (no run record holds it as its source's only
copy). Inodes went from 65.08% to 60.4%; the closing train's check was untouched.

## What was lost

The runs below ran in a tree that held files beyond its commit (left by earlier runs in the shared per-commit tree, or in a tree
an explicit `--cwd` pointed into), so `store.conditions.source.dirty` is true. The commit of each is still on
`refs/research/src/<sha>` in node 1's `git/verity.git`. Only the extra files are gone. Every run's record (logs, job.json,
outputs) is preserved on the remote.

| tree (commit) | runs | dirty_digest |
|---|---|---|
| 91b1f5bd4347 | r20261003-060005-f0e4 | 91e86dd616a7... |
| 91b1f5bd4347 | r20261003-060127-5310 | f8eccc101051... |
| a9c858edb909 | r20261006-185048-c193, r20261006-185201-3275, r20261006-185221-bb78 | 2033d5856a46... |
| d916c75c13d6 | r20261003-065057-6be9 | ddab3a948f32... |
| d916c75c13d6 | r20261003-065211-e84f | 5c5139a1c317... |

Not lost: the five other trees whose deletion time is unknown (62e3c42b7737, 12ca48ac9dde, ed3efd4e3fae, e6854f07cd2d,
112f5fae2355) are clean commits on refs, and the one dirty run among their users (r20261001-232140-9ec1) has the empty
digest (`e3b0c442...`): nothing beyond its commit.

No launching agent's checkout can match these digests: each was computed on node 1 from the node's tree, not from a launcher, and
all seven records name no lane. None of the eleven runs is cited by a store label, a manifest, the frozen ledger, a merged PR's
body or `Checked:` line, or a commit on main. Each of the seven is labelled `source-lost true --ref note:infra/20261010T1801Z-finding-n1-src-sweep`.

## Fix

danielreuter/verity#1729: the runner captures a dirty source into the run dir (`source-dirty.tar`, the exact bytes the digest
hashes), custody always uploads it, `evict_src`'s condition 3 lets the tree go only once the preserved record holds it, and
`node_sweep.sh` no longer deletes whole source trees. Source trees on a node are `vy-store-evict`'s alone; no hand sweeps.
