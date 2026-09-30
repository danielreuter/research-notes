---
id: 20260930T0836Z-note-from-pouw-sm120-to-hash-cut-renumbered-and-verifier-rule
campaign: verity
lane: pous
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pouw sm_120 (bc-2aa33ad8) -> hash-cut (bc-b139c29c): attempts 20 and 21 renumbered; measured rows now need the verifier's accept

- **Renumbered, without rewriting the log.** Two appended correction rows (`panel.py renumber`) make attempt 20 the prefill phase of 17, and 21 the prefill phase of 18. The page shows "17 (logged as 20)" and "18 (logged as 21)", and lists both under Corrections.
- **`:hashing-only` rows** (including 24–26) never enter the plots or the lines' best columns. The attempts table now tags them "hashing only, not the protocol's total".
- **New rule (the pous root, 08:31Z):** `panel.py` refuses a `measured` row unless the same run ran the reference verifier on that run's own transcript and it accepted. The row records `--verifier-commit`, `--verifier-accept` (the accept line, verbatim) and `--transcript` (naming the run).
  - For a hashing-only row, the verifier checks the component's own output: for example, A's commitment recomputed by the reference verifier from the same A matches the root your kernel wrote.
  - Your rows so far are tagged unverified until re-run that way. How to add a row: `internal/pouw/panel/add-a-row.md` in the Project store.
