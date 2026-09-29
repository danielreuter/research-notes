---
id: 20260929T0727Z-handoff-from-pous-influence-statement-regrants
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: influence statement re-grants are in (all granted, none refused)

POUS's statement reviewer (Phase 19i) granted every statement it was asked to re-read.

- **#375 at `de831e06`:**
  - `twoStage_influence` with `AnchorsSound₂`, the old inline premise now required for every strategy, which settles X-IC-2;
  - the five witness pins, whose namespace alone changed.
- **#378 at `46b8faf9`:** `card_influenceSet_le_harm` and `Gen.harm_witness`.
- **#379 at `fa4fb58e`:** `audit_exfiltration` with the location term.
  - It holds at `ded605b1` too, since no Lean file changed.
  - The reviewer compiled an instance that meets every new hypothesis.

**Checks behind the grants:**
- The ten unchanged statements keep their type hashes at every head.
- The Mathlib-only audit regenerates the committed records exactly.
- ArkLib wasn't buildable there, so the full soundness package runs only in the recorded check.

**None of the findings blocks a grant:**
- `Gen.harm_witness` was never a 19g grant, although the request and #378's description said it was. Both are being corrected (description only; heads unchanged).
- The 19g form, `audit_exfiltration_influenceSet`, is unpinned. It will be pinned only if something cites it.
- The two-stage theorem with `AnchorsSound₂` and the new exfiltration hypotheses have no pinned satisfiability witness. These go in a separate draft PR stacked on #381, with its own statement review, so the granted heads don't move.
- The grants are being copied into the PRs' merge-request tables.

The statement side is complete. The only thing the one-session check and the merge request still wait on is bc-f0bc7e75's re-record of #379 at `fa4fb58e` and #381 at `d237e60a` (note:20260929T0722Z-handoff-from-pous-379-regrant-at-fa4fb58e).
