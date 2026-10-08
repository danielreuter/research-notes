---
id: red-team-vbridge-c/20261008T0803Z-finding-pr1419-h3p-lock-check
campaign: proofs
lane: red-team-vbridge-c
kind: finding
status: final
repo: verity
origin: [pr:1419@bd93b2ccc43a85870c0b6833c9672560f58fd99f]
---

# Red team lock-only check of #1419 at H3' `bd93b2ccc`: grant

Addendum to `note:red-team-vbridge-c/20261008T0624Z-finding-vbridge-restack-regrant`, which found #1419's code sound at
H3 `7d0adc625` and left its grant for H3', after the re-record. H3' is H3m `ba0bb6e02` (H3 plus a clean merge of #1391's
H2' `2ade21342`) plus one commit writing `Security/lean-audit.json`. Everything below was checked from the files and from
the runs' records in the evidence store. Nothing blocks.

## The diff from H3 to H3' is the two locks

- `git diff 7d0adc625 bd93b2ccc` touches only `Security/lean-audit.json` (+248/−26) and
  `verity/core/service/flock/lean-audit.json` (−11, the `Flock.RecOpen.check_ok` record).
- `ba0bb6e02^{tree}` equals `git merge-tree --write-tree 7d0adc625 2ade21342` (`ae4dd365c`): the merge is clean and adds
  nothing of its own.
- The verifier lock at H3' is blob `13f182bc2`, the same as main `93b5e95a9`'s, H1's and H2''s.
- `Verifier.lean` and `VBridge.lean` are H3's blobs. Nothing under `verity/ml/flock/` or `verity/core/service/flock/`
  changes from H2' to H3' except the lock.

## The Security lock

Compared with main's: only `guarantees` and `reads` differ. `layers`, `assumptions`, `dependencies` and the other keys are
main's.

- **Guarantees, 267 → 273.** G's six are added: `recOpenNet_eq`, `laidRows_layout_congr`, `length_recOpenOuts`,
  `laid_unit`, `unit_check`, `keyProg_parse`. Each has owner `@proofs` and no assumptions, and each signature matches its
  statement in `Security/Proofs/Flock/VBridge/Verifier.lean` in elaborated form. None is removed, and the 267 existing
  records are byte-identical.
- **Reads groups, 376 → 379.** The new groups are `Flock.RecOpen` (61 definitions), `Proofs.Flock.VBridge.Keyed`
  (`keyGates`, `keyInst`) and `Proofs.Flock.VBridge.Verifier` (`portsOf`, `unitIn`). 41 existing groups gain only G's
  guarantees as readers; none loses one.
- **Definition records: 1 changed, 68 new, 0 removed.**
  - The changed one is `Flock.HmRow.parse`. Its hash at H3' (`814a8839f0c06317`) differs from main's
    (`2e4d59ed77c954d6`), #1428-alone's (`3377675e4fca18c1`) and #1391-alone's (`9ca4ad346569b553`). `review.txt` shows
    its body as the merged `parse`: `kLog := ← kLogOf mj` from #1428, then `check`, `HmNets.check`, `RecOpen.check` from
    #1391.
  - `MAX_K_LOG` and `kLogOf` hash as in #1428 alone. The `Flock.RecOpen` definitions hash as in #1391 alone. The `Keyed`
    and `Verifier` definitions and `Const.Prog.oneAt` hash as in old G's lock.

## The re-records

- **`r20261008-055539-db9c`** ran at H3 (tree `977c90790`): `check.py --build --update --owner @proofs --no-runs Security
  verity/core/service/flock`, rc 0, `audit.json` passed.
  - Its `audit-Security/lean-audit.json` is byte-identical to H3''s Security lock (sha256 `a1137c8c…`).
  - Security: PASS, 7,071 declarations in 226 modules, 273 guarantees. Security/Proofs: PASS, 59,497 declarations in 936
    modules. The kernel replay accepted 6,990 and 58,874 constants, with only the axioms `propext`, `Classical.choice`
    and `Quot.sound`.
  - Its `review.txt` has 69 definition records: 1 changed (`parse`) and 68 new.
- **`r20261008-061252-21e0`** ran at `8645b0ef4`, which has the same tree as H2' `2ade21342` (`bb37224d7`). Its
  `audit-verity_core_service_flock/lean-audit.json` is byte-identical to main's and H3''s verifier lock (sha256
  `c5b2b596…`). The audit passed: 6,372 declarations in 52 modules, 7 guarantees, the same three axioms.

### Why H3's Security record stands at H3'

H3 and H3' differ in the Lean only by the verifier lock's `check_ok` guarantee record, so the question is what one audit
reads of another package's lock (`tools/verity/lean/check.py` at H3'):

- The Security audit reads the verifier package's lock only through `homes` → `spec_of`, which is its `layers`. Those are
  the same at H3 and H3'.
- The verifier audit reads its dependents' `reads` only through `read_by_dependents`. That feeds `unread_spec`, an
  advisory note in the report, never a failure or a lock entry. So `21e0`'s verifier lock, recorded against main's
  Security lock, stands beside H3''s.

## Tests

- **`r20261008-065806-59dd`** at H3' itself: `flock-verify` built, and `verity-flock` had 819 passed and 0 failed,
  including all 41 tests of `test_lean_verifier.py`. All 6 suites passed.
- **`r20261008-063145-aa85`** at H3m: 30/30 suites passed. H3m differs from H3' only in the Security lock.

## Findings (none blocking)

- `21e0`'s source commit is `8645b0ef4`, not H2' `2ade21342`, but the two have the same tree.
- The runs declared no outputs (`--cwd clone`, `result` and `run_files` null), so `review.txt` and the locks are reachable
  only inside each run's `run_record` artifact. They are fetched with `research data fetch art:… --path …`.

## Label

`pr:1419@bd93b2ccc43a85870c0b6833c9672560f58fd99f grant red-team`, by `red-team-vbridge-c`, referencing this note.
