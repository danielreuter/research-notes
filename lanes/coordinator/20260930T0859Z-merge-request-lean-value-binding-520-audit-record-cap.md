---
id: 20260930T0859Z-merge-request-lean-value-binding-520-audit-record-cap
campaign: overnight-sep30
lane: lean-value-binding
kind: handoff
status: open
repo: danielreuter/verity
origin: lean-value-binding (bc-a84aadb3), at root's request
---

# Merge request (land in or before TLO): #520 at 55115141, the 2 MiB cap for Lean audit records

- **PR:** [#520](https://github.com/danielreuter/verity/pull/520), branch `cursor/audit-record-cap-8d81`, head
  `55115141b52fd42ac891c804d51d1bf472468856`, one commit on `main` `cc0f4688`.
- **Why now:** `soundness/lean-audit.json` is allowlisted at 512 KiB. #513 takes it to 512,567 bytes, and #452's re-recorded
  `Flock.Draw` entry (31 definitions, 22 pins) grows the same file. With both, `tests/test_repository.py` fails. Land #520
  before #513, and in or before TLO if #452 rides there.
- **Change:** `tests/test_repository.py` only.
  - Every tracked `*/lean-audit.json` is capped at `AUDIT_RECORD_LIMIT = 2 MiB`, with one comment giving the constraint.
  - The soundness entry leaves `ALLOWLIST`.
  - `BLOB_LIMIT` (256 KiB) and the other `ALLOWLIST` caps are unchanged.
- **Tests:** `tests/test_repository.py`: 12 passed on the head. The limit logic was also checked against #513's record plus
  #452-sized growth (passes), a record over 2 MiB (fails) and a 600 KiB non-record JSON (fails).
- **Cost in a train:** it changes only the repository's own suite. No Lean, circuit or `backends/flock/` change, so no
  `lean-agreement` and no reviewer needed.
- **Conflicts:** none expected. Any PR that edits `ALLOWLIST`'s soundness line would conflict on that one line; keep #520's
  side.
