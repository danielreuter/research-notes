---
lane: lean-organization
kind: handoff
from: pous (Lean organization plan, bc-79934c4e)
created: 2026-09-28T20:55Z
---

# pous → lean-organization: tooling suggestions from the repo-wide Lean plan

Reconciled with `docs/lean-organization.md` (16:01Z). The plan is `store:pous/docs/lean-organization-plan.md`, and
Daniel's decisions are pending. No item changes a pinned statement.

- **Hash (agreed):** when you move to a cryptographic hash, consider also recording a content hash that ignores
  names. It would replace each constant a statement names with the hash of that constant's definition, recursively,
  so `--update` could print "renamed or moved only". Your §7 item 1 moves, and POUS's `PousX` → `Pous.*` renames at
  landing, would then need no hand review. Recording old and new hashes side by side for one transition keeps open
  grants checkable.
- **README citations (agreed):** a report-only lint for theorem names that a package's docs cite as proved but
  `pins` lacks would prevent a repeat. Your §7 item 15 is the structured form.
- **`--rerecord`:** after a merge, rewrite the records, and fail unless every type hash, named assumption and
  definition hash equals its value on one of the merged sides. Compare per definition, so a pure module move passes.
  That turns §4.2's "merge and re-run `--update`" into a check.
- **Witness check:** map each `Prop` in an `assumptions` module to a pinned satisfiability witness, and fail when one
  is missing (report-only for existing packages). This enforces POUS's proof-hygiene rule.
- **Statement `Prop`s as pins:** accept a pin on a `def … : Prop` and record its hash. A statement frozen on `main` is
  then checked when its proof lands: the grader's target, without a `sorry` on `main`.
- **Draft mode:** `audit.py --draft` counts `sorry` instead of failing, so research branches run `main`'s audit, not a
  copy. The POUS store's copy dates from `6746f408`.
- **Lints, report-only first:** `lake build --wfail`; Batteries' `runLinter`, with `docBlame` on trusted definitions
  and pins and `unusedArguments` on pins (an unused hypothesis is on the reviewer's checklist); and a test that reads
  lakefile `require`s (no protocol package requires another) and options (level3 and the verifier lack
  `relaxedAutoImplicit = false`).
- **Glob roots (waiting on Daniel's decision 2):** accept Lake `globs` in `roots`, expanded from the file tree, so
  adding a file edits no root or aggregator. Soundness's root import list is where #310, #287 and #293 conflict with
  #319.
- **Caching, with circuit-checks (your §7 item 7):** key the cached audit pass per package, so a train touching one
  package re-audits only that one. Also try one `packagesDir` per checkout, so every package shares one copy of
  Mathlib; merged trees reached 19 GB each on the check pod.
