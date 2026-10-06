---
id: red-team-proofs-1261/20261006T1821Z-finding-replay-regrant
campaign: flock
lane: red-team-proofs-1261
kind: finding
status: final
repo: verity
origin: pr:1261@387312a0a07260f178bf74f72c70228e7ea92cc0 pr:1330@8fecfbe3489b45a6e61bc099af8851a776721ecd
---

# Red team, re-grant of #1261 and #1330 after the replay fix: GRANT both

The previous grants were on #1261 at `9c9828557` and #1330 at `59b68645a`
(note:red-team-proofs-1261/20261006T1157Z-finding-rename-regrant). The new heads, #1261 at `387312a0a` and #1330 at
`8fecfbe34`, differ from those only by the move of two files under `Proofs/Flock/` and the re-recorded lock.

- **Lean.** `git diff -M` gives the same Lean patch for both PRs:
  - `Specs/Flock/Assumptions/Recursive.lean` moves to `Proofs/Flock/Soundness/Assumptions/Recursive.lean`, byte-identical
    (100%).
  - `Specs/Flock/Guarantees/Recursive.lean` moves to `Proofs/Flock/Recursive/Statements.lean`; only its first import line
    changes, to the assumptions file's new path.
  - `Proofs/Flock/Recursive/Guarantees.lean` changes one import line, to `Proofs.Flock.Recursive.Statements`.
  - Nothing else changes, so no statement changes.
- **Imports.** At both heads, `git grep '^import Proofs'` outside `verity/Security/Proofs` is empty, and nothing refers to
  `Specs.Flock`. At `9c9828557` the two `Specs` files imported three `Proofs` modules.
- **Lock.** The four `Specs.Flock` config entries are dropped: the whole `exempt` key, which held only that entry, and one
  each in `assumptions`, `meaning` and `reads_exempt`. The other entries keep their order.
  - The two `reads` keys are renamed to the new module names, with byte-equal records (definitions, digest, guarantee
    list), and every other key is equal.
  - The moved files stay covered by `assumptions` (`Proofs.Flock.Soundness.Assumptions`) and by `meaning`
    (`Proofs.Flock.Recursive`, `Proofs.Flock.Soundness`).
  - `verity/Security/Proofs/lean-audit.json` is unchanged. The lock commits touch only `lean-audit.json`, and #1330's
    "ours" merge keeps `6bbcfc2e2`'s tree.
- **Re-records with the replay** (`r20261006-165638-7145`, `r20261006-165638-520d`, vy-nebius-1).
  - Both packages PASS with the kernel replay, with only `propext`, `Classical.choice` and `Quot.sound`, and
    `statement_changes` is false.
  - `review.txt` has one line: "reads: 5 definitions read in another module or under another name: the same under their
    old names".
  - Each published lock is byte-identical to the committed one.
- **Compare-mode audits** (`r20261006-174943-7fc2`, `r20261006-174943-e1e1`). Both failed within 0.2 s with rc 2 on
  argument parsing ("`--owner` goes with `--update`"), so they say nothing about the heads. The grant rests on the
  re-records, which ran on the moved trees. A compare-mode check needs a relaunch without `--owner`; the train's `check`
  replays anyway.
