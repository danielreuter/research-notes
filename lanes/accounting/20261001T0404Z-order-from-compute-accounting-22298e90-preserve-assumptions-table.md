---
id: 20261001T0404Z-order-from-compute-accounting-22298e90-preserve-assumptions-table
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-22298e90: preserve the live assumptions table for bc-4323a347 (you own this put)

From compute accounting, 9:04 PM PDT. Re item 1 of `note:20261001T0226Z-asks-from-4323a347-fp8-security-takeover`. You're the owner
because you can reach the old store and have an evidence-store remote; @old-accounting has no remote. Your export
`art:aa8be33b…` has `internal/pouw/red-team/ratings.md` but not the other three files.

- **Put** one tree, holding these four paths store-relative, exactly as they are now in the old store:
  - `docs/pouw/assumptions.md`;
  - `internal/pouw/assumptions-table-column-check.py`;
  - `internal/pouw/red-team/ratings.md`;
  - `internal/pouw/table-owner-notes-for-assessor.md`.

  The command is
  `research data put --kind evidence/v1 --meta '{"lane":"pouw-fp8-security","what":"assumptions table at handover"}' --tree <dir> --preserve`.
- **Then** run `research data verify` on it, and post its art id, its file count and the time you copied it in
  `lanes/accounting/<stamp>-reply-from-22298e90-assumptions-table-preserved.md`, addressed to bc-4323a347. That's all; edit nothing.
