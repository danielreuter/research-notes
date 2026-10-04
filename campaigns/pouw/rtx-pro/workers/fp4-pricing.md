---
cursor:
  subagentId: "bc-f5bf55c8-213d-5f31-8906-0b78916ecf5b"
---

# FP4 pricing (bc-f5bf55c8): status

broker: source=broker 2026-09-30T17:43Z

migration: handoff written 2026-10-01T02:03Z (research-notes `lanes/accounting/20261001T0203Z-handoff-from-f5bf55c8-migration.md`); VM-only results preserved as art:1418cd489a01dd46fe6d6b477b4891261edb92441f889a5728d5d41db61c0e60 and `internal/pouw/rtx-pro/fp4-pricing-results/`; starting no new work, answering my replacement in `lanes/accounting/`

coordinator: compute-accounting (bc-e90634dd) from 2026-10-01T00:55Z (Daniel, 5:52 PM PDT); orders in research-notes `lanes/accounting/`, acknowledged in `20261001T0100Z-reply-from-f5bf55c8-ack-and-standing-items.md`

- **Deliverable:** `docs/pouw/pearl-c4-fix.md` (F1′ + F2 priced, the verifier's cost, term 3 under the split unit, the
  every-tile census).
- **Done 18:15Z:** the crossed-split census for the assessor's 17:25Z condition (`pearl-c4-fix.md` §10).
  - No tile is rejected, and the worst credited tile is 0.23–0.45 of the cap on 3B and 7B.
  - No V-EX rows are needed.
  - No runs are going now.
- **For the ops lane:** version 4 of the 70B coverage job is `internal/pouw/rtx-pro/fp4-coverage-70b/` (`job.md`, 19:35Z).
  It counts the rows #556's `volunteer` gives up.
- **Reporting rule (19:35Z):** every FP4 coverage run reports the rows `volunteer` gives up, per model.
- **22:40Z:** the Qwen2.5-3B/-7B census captures for `pearlc4-vex-coverage.sh` are in `internal/pouw/rtx-pro/pearlc4-captures.md`
  (four preserved `art:` ids, with the node-2 install steps).
- **For bc-a8466279:** term 3 per element for #556, in `internal/pouw/rtx-pro/handoffs/term3-per-element.md`.
