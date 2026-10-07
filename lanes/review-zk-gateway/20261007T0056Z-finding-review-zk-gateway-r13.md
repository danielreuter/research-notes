---
id: review-zk-gateway/20261007T0056Z-finding-review-zk-gateway-r13
campaign: proofs
lane: review-zk-gateway
kind: finding
status: final
repo: verity
origin: [pr:1270@2980f95d568655d1ab70c320d1b5ce997f13a04d, pr:1343@5306c63bf4ae2839146f706c0d8387e9c495239b, pr:1349@86bb4d202bd6d2fa3c245953b635b3d82b4d8d02, pr:1303@6fb5a5db0dc08fab25c26871d1209878c153c25a, pr:1323@611a85b24014bfb81522588a526a60287143e188, pr:1339@300baafe39d975da3e76e02845cfa91408907853]
---

# Red-team round 13: six relabels at route 2's heads, GRANT

Only forward merges of `main` changed these heads. #1412's gate compares a stacked PR with `main`, so it counts the
parents' changed patches against the child, and its fix (#1422) won't be on `main` in time. So I relabelled by hand,
with each PR's parent as the base. I already reviewed the patches (rounds 9–12); this round checks only that they are
unchanged and that they merge.

**Verdict: GRANT** on all six heads:

| PR | Granted at | New head | Parent (new head) |
|---|---|---|---|
| #1270 | `2f2a58de5` | `2980f95d5` | #1347 `c35a427d1` |
| #1343 | `3399b71f5` | `5306c63bf` | #1270 `2980f95d5` |
| #1349 | `83a3f5f43` | `86bb4d202` | #1343 `5306c63bf` |
| #1303 | `ceb25c35a` | `6fb5a5db0` | #1270 `2980f95d5` |
| #1323 | `7c965ddc5` | `611a85b24` | #1303 `6fb5a5db0` |
| #1339 | `a1adb7a17` | `300baafe3` | #1323 `611a85b24` |

- **Each own patch is unchanged.** I compared `git diff OLDPARENT OLD` with `git diff NEWPARENT NEW`, where OLDPARENT is
  the merge base of OLD with the parent's new head. After dropping index lines and hunk offsets the two are identical:
  the same paths, added lines, removed lines and context, and the same shortstat. #1270 changes 17 files (+2010/−186),
  #1343 4 (+680/−28), #1349 9 (+2057/−142), #1303 10 (+828/−13), #1323 11 (+1859/−6) and #1339 8 (+1306/−2).
- **#1412's own rule agrees.** `research.queue.carry(repo, PARENT, OLD, NEW)`, run from a worktree of `origin/main`
  `e255a4efb`, returns True for all six: "merge of main; no lean-audit.json change" for #1270, #1343, #1349 and #1339,
  and "merge of main; lean-audit.json change identical" for #1303 and #1323. Under Daniel's 6 Oct ruling, an identical
  `lean-audit.json` change carries.
- **Every head merges cleanly.** `git merge-tree --write-tree` of each new head onto its parent's new head and onto
  `origin/main` `e255a4efb` exits 0, with no conflicts, in all twelve cases. Each parent's new head is an ancestor of
  its child's.
- **The heads are final.** I checked them with `git ls-remote origin` at the start and again before returning.

Process note: by Daniel's carry ruling, all six grants should carry without a reviewer. They didn't only because
#1412's `carry` takes `main` as a stacked PR's base. #1422 fixes that, and once it lands this kind of round goes away.
