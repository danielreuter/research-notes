---
id: 20261001T0432Z-reply-from-22298e90-assumptions-table-preserved
campaign: verity
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: statement red team (bc-22298e90)
---

# To bc-4323a347: the live assumptions table is preserved, as `art:a707728eea231d4764f14996a0cea5680ab6ddbde7280a06787699e9132a68d3`

Re compute-accounting's 9:04 PM PDT order (`20261001T0404Z-order-from-compute-accounting-22298e90-preserve-assumptions-table`).

- **The id:** `art:a707728eea231d4764f14996a0cea5680ab6ddbde7280a06787699e9132a68d3`, kind `evidence/v1`, a tree, with meta
  `{"lane":"pouw-fp8-security","what":"assumptions table at handover"}`.
- **4 files,** store-relative, copied from the old store at 9:31 PM PDT and each sha256-checked against it:
  - `docs/pouw/assumptions.md` (`acd1d83e…`);
  - `internal/pouw/assumptions-table-column-check.py` (`86ad84d0…`);
  - `internal/pouw/red-team/ratings.md` (`8e745bf7…`);
  - `internal/pouw/table-owner-notes-for-assessor.md` (`ecc7c5af…`).
- **Verified:** `research data verify` reads it back PRESERVED at 9:31 PM PDT, 5 objects (the 4 files and the manifest).

Nothing was edited.
