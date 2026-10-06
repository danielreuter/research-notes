---
id: red-team-proofs-1261/20261006T1157Z-finding-rename-regrant
campaign: flock
lane: red-team-proofs-1261
kind: finding
status: final
repo: verity
origin: pr:1261@9c9828557c2ae26a5e23522b3744673d4d76786f pr:1330@59b68645a2af66ddd1e69944fbc9aa935c5142f1
---

# Red team, re-grant of #1261 and #1330 across the rename move: GRANT both

The previous grants were on #1261 at `b4784eb8e` (note:red-team-proofs-1261/20261006T0810Z-finding-pr1261-review) and on
#1330 at `8fb946c2d` (note:red-team-proofs-1261/20261006T1000Z-finding-pr1330-review). Both new heads are those granted
heads plus the rename move (main `a7134c413`, move commit `afc9d352d`, base `b5ea0b193`), with nothing else added.
Verdicts: **#1261 at `9c9828557c2a…` GRANT**, **#1330 at `59b68645a2af…` GRANT**.

## The restack, reproduced from git objects

- **Base merge** (`769a1e417`, `c289bef26`). `git merge-tree` against `b5ea0b193` conflicts only in
  `verity/Security/Proofs/Flock.lean` and `lean-audit.json`, and the committed trees differ from the conflicted ones only
  there. `Flock.lean` is the union of both sides' one-line imports: ours `Proofs.Flock.Recursive`, then main's
  `Proofs.Flock.VBridge`. In the lock, `meaning` is ours plus (main minus base). The 64 `reads` modules that differ are
  unions of guarantee lists. `guarantees` and `reads_exempt` are clean three-way merges, and the other keys come from one
  side only.
- **Rename** (`d0128e580`, `935751733`). Rerunning `b5ea0b193`'s `tools/move/rename.py` (its tree is the same at the
  base, the move and both merges) yields trees `a964ec60` and `2efa42cc`, byte-identical to the committed ones.
- **Onto merge** (`c07b194fb`, `89f9cb4e0`). `git merge-tree --merge-base=afc9d352d` reproduces trees `2373680e` and
  `122e8765` exactly. The "ours" merges `4a50f03b7` and `59b68645a` have the trees of their first parents. The lock
  commits `9c9828557` and `93b1baad4` touch only `verity/Security/lean-audit.json`.

## Source: rename words only

- **#1261.** `7b410fbf6..b4784eb8e` and `a7134c413..9c9828557` give the same 20 files with the same statuses. 15 files
  are identical. The rest differ only by gateway→firewall in prose (14), `gatewayLeaf`→`firewallLeaf` (8: the def,
  6 uses inside `RecursiveZK`'s statement, 1 in `Recursive/Guarantees.lean`), "GPU workers"→"workers" (1), and the
  `VBridge` import (1). `firewallLeaf`'s body is unchanged.
- **#1330.** Its diff over `9c9828557` equals its diff over `b4784eb8e` except in prose lines (the same words).
  `Recursive/Flock.lean` and `Stage.lean` are byte-identical to `8fb946c2d`.
- No `gatewayLeaf` remains in any `.lean` file at either head, and no "gateway", "Warden" or "GPU worker" in either lock.

## The locks

- **#1261's lock commit** (`c07b194fb`→`9c9828557`) changes exactly 4 leaves, all in
  `Specs.Flock.Guarantees.Recursive`: `RecursiveZK` `68bb5616`→`6f95e6da`, `gatewayLeaf` `f1b305e9` gone,
  `firewallLeaf` `fddc41ec` new, and the module digest. #1330's lock commit (`4a50f03b7`→`93b1baad4`) changes the same
  4 leaves (its digest `c9eb97c9`→`005bd3a1`).
- **#1261 over main.** The delta `a7134c413`→`9c9828557` (331 leaves) equals the reviewed delta
  `7b410fbf6`→`b4784eb8e` (331 leaves) under the name map, with list leaves compared as added and removed sets. The only
  differences are the 3 hash leaves the rename changes (`RecursiveZK`, `firewallLeaf`, the digest). Every guarantee
  record is equal, including `Flock.SecurityProofs.RecursiveZK`'s (type hash `444c0683`).
- **#1330 over #1261.** The delta `9c9828557`→`59b68645a` (13 leaves) equals the reviewed delta `b4784eb8e`→`8fb946c2d`
  (13 leaves) leaf for leaf, except that module's digest.
- **NetTiming.** Every record naming `NetTiming` or `NetworkCertifier` is byte-identical to main's at both heads: 100
  leaves under my count (81 `reads`, 16 `guarantees`, 3 `layers`); the coordinator counted 103 by another scheme.

## The runs, `r20261006-104228-de49` and `r20261006-104228-397e` (vy-nebius-1)

- Source commits `c07b194fb` (tree `2373680e`) and `4a50f03b7` (tree `122e8765`), rc 0. Each published
  `lean-audit.json` is byte-identical to the committed lock (`9c9828557` and `93b1baad4`, which equals `59b68645a`).
- Both print `AUDIT … PASS`: 6873 declarations in 217 modules, axioms `propext`, `Classical.choice` and `Quot.sound`,
  1678 guarantees, no failures in the Proofs package.
- The moves file is main's `tools/move/rename_moves.json` plus `Flock.Guarantees.gatewayLeaf`→`firewallLeaf`.
- `review.txt` (identical in both runs) has 18 lines, all `NetTiming`, and nothing for the lane except
  "reads: 1 definitions … the same under their old names", which is `firewallLeaf`. `review()` in `audit.py` compares
  texts under the old names. Main's lock already records `NetTiming` after its own move, so mapping them back produces
  pairs marked gone and new, plus texts marked changed. The records written are main's. `RecursiveZK`'s and
  `firewallLeaf`'s texts under the old names equal their records, so no lane statement changed.

## Correction

Both runs used `audit.py --build --no-replay --no-runs --update --moved`, so the kernel replay (`Replay.lean`) did not
run, although the request described them as full audits with replay. This doesn't change the verdict: the question was
whether the heads are rename-only, which the lock and source comparisons settle. The `check` before merge replays every
declaration.
