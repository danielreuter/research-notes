---
lane: coordinator
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T09:52Z
---

# red-team SH: b-ligero-sha256 fp8-ada-x4+sha256 (`sha256/row/v1`) at be1a3bcb: FAIL (R1 + R4 inherited); every +sha256 Table 2 cell is pulled until ligero-steps-pin's fix is merged and the dump is re-verified

These are e2e runs on pod vy-red-team-sh against the pinned system d6b0cd8d. Details are in
`lanes/b-ligero-sha256/20260925T0952Z-handoff-from-red-team-standard-hash.md`.

- **be1a3bcb** (art:0e8faae7):
  - an R1 remap forgery is accepted by Python, Rust pinned and reverify (the counterexample is preserved);
  - R4: reverify PASS with 2 of 3 VUs unproven;
  - H2 PASS.
- **be1a3bcb + ligero-steps-pin c8a16e2b**, local merge, clean (art:57a22acb): R1 and R4 are refused and H2 passes. The fix
  covers +sha256 without changes.
- The sha256 gadget: no finding.

**This pulls every +sha256 cell** (fp8-ada-x4, fp8-hopper-x4) until b-ligero-sha256 merges the fix and each dump is
re-verified with the fixed reverify or verify-night-2's 06.

Also, as a mechanical check of the BLAKE3 gadget, a mutate-and-recompute scan of `leaf/blake3.py` at 806a2f73 is running.
It overrides every computed row, recomputes everything downstream and re-checks. So far it finds 0 free rows over 3
column shapes, including fp8-ada+blake3's half-block (about 61k mutations each). The positive control, one dropped
decomposition, is caught with 18 free rows.
