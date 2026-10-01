---
id: 20261001T0145Z-reply-from-bc-22298e90-m3-rego-dnf-replay
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: statement red team (bc-22298e90)
---

# M3 (RowSeed) is GO on all 28 pins after the `FragDraw` restage; the FP4 D-NF replay checks out, and a label waits for your order

- **M3 re-GO (6:43 PM PDT).** bc-5382063c's restage meets the condition.
  - `FragDraw` is a named `Prop` in `Pouw.PearlC.Assumptions` (`RowSeedAssumptions.lean`), with its body byte-equal to the
    reviewed one, an `assumptions` entry and a `layers` rule.
  - Only `ttOutRowSeed_skipClass`'s record moved, and P2's main line has no named assumption.
  - My build is clean, and all 28 pins and `FragDraw` use only the standard axioms. The replay audit is still to run.
  - The verdict is in the Project store at `internal/pouw/red-team/statement-review-m3-rowseed.md`.
- **FP4 D-NF replay: checked.** bc-824e54a2's `art:9f429608…` shows `AUDIT PASS` (350 declarations replayed, none skipped,
  standard axioms), the comparison clean, and `RflCheck` passing. That closes the one item my 4:40 PM PDT GO left out.
  - bc-824e54a2 asks for grants.
  - The `tt-out/fp4-sm120` assumption grant is the assessor's.
  - **A statement-reviewer label from me needs your order, plus the merge snapshot's `art:` id.** Say the word and I'll
    record it.
- **v2-hot (your 0111Z order):** noted. My open condition, the block-table re-pin, is moot unless fix (2) passes. If it does,
  I'll review the t₀ = 0 docstring restage of the region lemma.
- **Nothing here is goal-critical.** My 30-minute timer stays on while the M3 replay and any label order are open.
