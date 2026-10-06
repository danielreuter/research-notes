---
id: red-team-vbridge-c/20261006T1235Z-finding-vbridge-rename-regrant
campaign: proofs
lane: red-team-vbridge-c
kind: finding
status: final
repo: danielreuter/verity
origin: pr:1273@fd6af1d4356faf72bdff720d256d09dcdda42759 pr:1274@ca685b7af08de6735efc8da323e5aa423eeeaf73 pr:1283@91e8bdcb8a8b00a4cc2c19a03f5d06de4704ac56
---

# Red team, re-grant of #1273, #1274 and #1283 across the rename move: GRANT all three

My earlier grants were #1273 at `50bf1c080` and #1274 at `2434949b9`
(note:red-team-vbridge-c/20261006T0402Z-finding-vbridge-c-review), and #1283 at `3d9977368`
(note:red-team-vbridge-c/20261006T0708Z-finding-pr1283-review). vbridge restacked them across the rename move: main
`a7134c413`, move commit `afc9d352d`, base `b5ea0b193`. Each new head is its granted head plus the move, and nothing
else. The move changes none of their Lean sources or lock records. Verdicts: **#1273 at `fd6af1d43` GRANT**, **#1274 at
`ca685b7af` GRANT**, **#1283 at `91e8bdcb8` GRANT**. I checked this from git objects in my own `/tmp` worktree, since
removed, and ran no new Lean.

## 1. The restack reproduces from git objects

- **Base merges.** `git merge-tree <granted> b5ea0b193` has no conflicts for any of the three, and gives exactly the
  committed trees: `1407d7f7a` (#1273), `d3904464d` (#1274) and `37e5bc5da` (#1283).
- **Rename reruns.** In a clean worktree at each base merge, `python3 tools/move/rename.py` exits 0. Its staged trees equal
  the committed rename commits: `ac703aeed` (tree `49b40d12`), `ab5fc4387` (`2d4fdcb6`) and `ca07c1c7f` (`5590a9e7`).
  `rename.py`, `rename_map.toml` and `layout.py` are the same at all three base merges as at `afc9d352d`.
- **Final merges.** Each final merge reproduces exactly, with no conflicts:
  - #1273: `git merge-tree --merge-base=afc9d352d ac703aeed a7134c413` gives `fd6af1d43`'s tree.
  - #1274: `--merge-base=ac703aeed ab5fc4387 fd6af1d43` gives `ca685b7af`'s tree. The base is the parent's own rename
    commit.
  - #1283: `--merge-base=ab5fc4387 ca07c1c7f ca685b7af` gives `91e8bdcb8`'s tree, `3e570215`.
  - So no step has a hand resolution.

## 2. Each head's own diff is the granted diff

Each pair of diffs touches the same files with the same statuses:

| PR | Granted diff | New diff | Files |
|---|---|---|---|
| #1273 | `17cfcdae8..50bf1c080` | `a7134c413..fd6af1d43` | 3 |
| #1274 | `50bf1c080..2434949b9` | `fd6af1d43..ca685b7af` | 3 |
| #1283 | `2434949b9..3d9977368` | `ca685b7af..91e8bdcb8` | 5, B2's two files among them |

Every file except `verity/Security/lean-audit.json` is byte-identical at the new head to the granted head, and at the new
base to the old base. The rename map reaches no VBridge source, so no rename words appear in these diffs at all.

## 3. The locks

- **The PRs' lock deltas are unchanged.** The delta over the new base equals the granted delta over the old base, leaf
  for leaf, with `reads` lists compared as sets: 18 leaves (#1273), 18 (#1274) and 77 (#1283). No name in them needed
  mapping. The only guarantee keys in the deltas are each PR's own:
  - #1273: `FlockVBridge.sound_climbFrom`;
  - #1274: `sound_climbRow`;
  - #1283: `sound_mul128`, `sound_residualForms` and `sound_recOpen`.
- **No record changed.** Every `FlockVBridge.*` guarantee record and every VBridge `reads` entry is byte-identical
  between each granted head and its new head. Main has 1676 guarantees, and the heads have 1677, 1678 and 1681.
- **NetTiming.** The 10 lock entries that name `NetTiming` are byte-identical to main's at all three heads. The known
  `--moved` noise does not arise, because no run here used `--update --moved`.
- **vbridge's audit `r20261006-104411-dfcc`** (vy-nebius-2, rc 0) ran on `91e8bdcb8`, #1283's head (tree `3e570215`).
  - It ran `audit.py --build --no-replay --no-runs verity/Security`, in compare mode without `--update`. So it published
    no lock, and checked the committed one instead.
  - Both packages PASS, with 0 failures, 0 escapes and axioms `propext`, `Classical.choice`, `Quot.sound`. `security` has
    1681 guarantees in 6873 declarations.
  - The `guarantees` and `reads` in its report equal the committed lock's at `91e8bdcb8`, key for key.
  - No audit ran at `fd6af1d43` or `ca685b7af`. Their locks are `91e8bdcb8`'s minus the downstream deltas shown equal
    above.
  - It skipped the kernel replay. The sources are byte-identical to what my replay audits passed
    (`r20261006-030819-703e` for #1274's tree, `r20261006-044346-2f12` for #1283's), and `check` replays before merge.

## Labels

`grant=red-team` by red-team-vbridge-c, ref this note, on `pr:1273@fd6af1d4356faf72bdff720d256d09dcdda42759`,
`pr:1274@ca685b7af08de6735efc8da323e5aa423eeeaf73` and `pr:1283@91e8bdcb8a8b00a4cc2c19a03f5d06de4704ac56`, each read back
from the remote.
