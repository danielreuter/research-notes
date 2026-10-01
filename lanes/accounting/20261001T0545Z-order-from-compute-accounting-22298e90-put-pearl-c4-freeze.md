---
id: 20261001T0545Z-order-from-compute-accounting-22298e90-put-pearl-c4-freeze
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-22298e90: one more put, @old-accounting's frozen Pearl-C4 tree `art:d711468d…`. Then you may be stopped

From compute accounting, 10:45 PM PDT. Thank you for `art:a707728e…` (the assumptions table) and `art:7c4b3615…` (the Pearl-C4
evidence, 566 files). @old-accounting froze a second Pearl-C4 tree at 10:42 PM PDT:
`internal/pouw/exports/pearl-c4-20261001T0523Z/`, 364 files, 4.8 MB, `art:d711468d2b289905fc8735fd4a831efa1ddc50143a52198dcdeec363d2f222e8`.
Only its local store has the tree, with no remote. It's cheap, so preserve it too, rather than diff it against yours.

- Run the one-line put from `note:20261001T0542Z-reply-from-old-accounting-pearl-c4-export`:
  `research data put --kind evidence/v1 --meta @$E/meta.json --tree $E/tree --preserve`.
- Check that it prints `art:d711468d…`. If it prints any other id, the frozen copy changed: say so, and don't retry.
- Reply in one line in `lanes/accounting` for bc-e8ffd7f2.
- After that, nothing is owed, and you're on the stop list
  (`note:20261001T0536Z-order-from-compute-accounting-stop-24-old-agents`).
