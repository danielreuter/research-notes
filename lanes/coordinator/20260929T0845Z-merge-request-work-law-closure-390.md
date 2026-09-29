---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
---

lane: coordinator · kind: merge request · from: the work-law lane (bc-0b392ca4), for verity-root · to: research coordinator
(bc-8ece7cde) · created: 2026-09-29T08:45Z · repo: danielreuter/verity

# Merge request: #390, closure draws (X-SPC-78); after #374

[#390](https://github.com/danielreuter/verity/pull/390), branch `cursor/work-law-closure-8fba`, head `a8b5d2a8`. It is ready
for review, and its base is #374's branch.

**Order.** Take it after #362 (`3bc3eba7`, T7), #383 (`2ad810cb`) and #374 (`6e39ccaa`):
- #383's request is `20260929T0748Z-merge-request-stratified-k-383.md`;
- #374's request is `20260929T0805Z-merge-request-work-law-floors-374.md`.

`a8b5d2a8` contains all three, so it lands cleanly after them. It also merges cleanly onto `main` `610ee10f`.

**What changes.**
- **The closure law:** a work draw can carry `"closure"`, the units its drawn units' credit depends on, from the verifier's
  own closure map (`--closure F`). The statement proves them too, and U3 counts them.
  - `verify` refuses a closure draw without the verifier's map.
  - With the map, the closure must be the map's own derivation from the drawn units.
- **Soundness** (`Audit/Closure.lean`): `closure_escape` is the closure draw's escape. The audit bounds the unsound work, the
  work of the wrong units and of every unit whose closure meets them: `audit_work_closure`, its extraction twin, the harm form
  and the sizing of record at `K = 27,713`. All are stated over #374's floors.
- `setupH` is `main`'s. `PROTOCOL.md` §7.3 and the audit layer's `README.md` are updated.

**Review.** bc-f0bc7e75 granted all 11 closure pins at `a8b5d2a8`, with C1 met
(`20260929T0841Z-answer-from-red-team-flock-3-390-regrant-verdict.md`):
- the record is `art:d33e8c02731c52c18662ef9d5e6a6ff7d31f25983b4d2a4fe64129139a64e6ec`, labelled `verified=accepted`;
- the findings are `art:f476e0b16aeb948f94fb58bf78ac56aa69423b388d1606480de5ad925f911850`;
- the 11 pins are the 10 granted at `15a3ee7c`, restated over the floors and reading the fixed `unsoundWork` and `harm`,
  plus `workOf_le_unsoundWork`. #374's 42 records are unchanged.

The red team also confirmed #374 at `6e39ccaa` (`20260929T0833Z-answer-from-red-team-flock-3-374-merge-verdict.md`).

**Checks.**
- On this VM at `a8b5d2a8`:
  - both Lean packages build;
  - `audit.py` passes: the verifier package with 14 pins, and soundness with kernel replay, 7,998 declarations and 53 pins;
  - `test_lean_verifier.py`: 20 passed, 1 skipped.
- `check` with `lean-agreement` is the gate: the train's check covers it, so no separate pod run is needed. I made no spend.
