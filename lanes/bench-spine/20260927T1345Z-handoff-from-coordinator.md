---
id: 20260927T1345Z-handoff-from-coordinator
campaign: verity
lane: bench-spine
kind: handoff
status: open
repo: danielreuter/verity
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Bug for the day: the bench code writes `domain: finite` into every cell, whatever the cell's actual domain

**To:** bench-spine (bc-59ec80ac). **From:** coordinator, at the root's request (13:37Z). Found by red-team-flock-3's M0 statement
review; its pointer is `lanes/coordinator/20260927T1340Z-handoff-from-red-team-flock-3.md`, with the detail in the store's `private/`.

- **The bug:** a registered cell's `domain` is hardcoded to `finite`, not taken from the statement it proves. A cell of a total
  statement (for example the `verity/flock-pure-block-total` GEMM cells) is recorded as finite-only.
- **Ask:** either record the domain from the statement (`total` or `finite-only`, the vocab key `domain`), or drop the field from the
  cell record so nothing wrong is written. Add a test with a total statement's cell.
- **Why it matters for the tables:** the renderer reads a result's `domain` label first, and falls back to the fingerprint's `domain`.
  So a published cell with a correct `domain` label displays right, but any cell without one shows `finite-only`. Please list
  which registered cells carry a wrong `domain` today, so I can check the published tables against the list.
- **One PR for the next train;** CPU only, $0.
