---
id: 20260929T2300Z-finding-red-team-452-flock-draw
campaign: verity
lane: red-team-flock-3
kind: finding
status: final
repo: danielreuter/verity
origin: red-team-flock-3
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75) · to: verity-root / the research coordinator
(bc-8ece7cde) · created: 2026-09-29T23:00Z

# PR #452 at `afbe5c95`: GRANTED (red team)

It restores the soundness record's `Flock.Draw` entry, as described.

[PR #452](https://github.com/danielreuter/verity/pull/452), branch `cursor/restore-flock-draw-meaning-974a`, is on `main`
`33828711`. I fetched its head directly. Evidence is in the store's `private/red-team-reviews/pr452-evidence.log`.
CPU only, $0.

## What it changes

It is one commit, `backends/flock/verifier/lean/soundness/lean-audit.json` only, +30/−1.
- **`meaning`:** `Flock.Draw` is appended after `Flock.Library`, the position #412's record had it in.
- **`reads`:** the `Flock.Draw` entry is restored, byte-identical to #412's (`da1e703a`, which I granted).
  - digest `5ae7f5688bdbe28e07a075ab227134ba`;
  - 14 definition hashes, among them `stratified`, `stratumK`, `subset`, `uniform`, `width` and `workK`;
  - 7 pins: `countRule_eq_draw`, `execStratified_escape_le`, `stratified_exec_escape_le`, `subset_exec_escape_le`,
    `workRule_eq_draw`, `flock_e2e_count_exec` and `flock_e2e_drawn_exec`.
- **Nothing else changes.** Every other section of the record equals `main`'s, as do all the other `reads` entries.
- **Why it matters.** On `main` today, `Flock.Draw` is in neither `meaning` nor `reads`. So a change to the executable
  draw would move no record, and the audit would not flag it to the statement reviewer or me. #452 puts that tracking
  back.

## Checks

These cover what the independent statement review (`note:20260929T2300Z-finding-statement-review-452-flock-draw`) left
out: it compared text only, and recomputed no hash.
- **The hashes are right for `main`'s code.** Both packages build at `afbe5c95`. `audit.py` passes with kernel replay on
  the record as committed: 10,976 declarations in 155 modules, 108 pins, standard axioms. So the restored hashes are
  what the audit derives from the current `Flock.Draw` definitions.
- **The record is exactly what `--update` writes.** `audit.py --update` on the same tree also passes, and it regenerates
  a record byte-identical to the committed one. That settles the PR's "still to do: regenerate in the next Lean train",
  and the expected no-change result holds.
- **The source didn't move.** `Flock/Draw.lean` is identical between `da1e703a` and `main`, so the restored entry
  re-records definitions my #408 and #412 grants already covered.
- **Tests:** `tests/test_repository.py` and `tests/test_lean_packages.py` give 15 passed. At 271 KB, the record is
  inside `main`'s 512 KiB allowlist.

## For the queue

- **My grant is recorded.** It's the store label `grant = red-team` on
  `pr:452@afbe5c9547ffdcbd6279ca940f635f1ccfbb48ff`, the full head sha the queue reads, and it's pushed to the remote.
  A new push needs a new grant.
- **The statement grant is there too.** It is the `statement-reviewer` grant `queue.toml`'s `lean_audit` rule asks for,
  since #452 changes a `reads` section. The coordinator recorded it on the same target for bc-78117a1c.
