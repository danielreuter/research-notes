---
lane: red-team-flock
kind: handoff
from: coordinator
created: 2026-09-25T11:29Z
---

# flock-128 is FINAL: its audit list is your scope; the live-coin forwarding isn't built, so audit the protocol as specified

flock-128 FINAL at 11:33Z. See its report `$RESEARCH_NOTES/lanes/flock-128/20260925T1018Z-report-flock-128.md` and
`lanes/coordinator/20260925T1128Z-handoff-from-flock-128.md`. Points for you:
- **The cost runs used Fiat–Shamir** with a separate transcript domain per rep (`flock-128/fast100x2/rep{0,1}`), because the
  piece that forwards each challenge to a live verifier doesn't exist. The 2^-195.5 claim holds only with live coins, so
  audit the protocol as specified, and list what the forwarding implementation must satisfy.
- **Today's bound is 2^-110.0** with live coins (2^-50 under FS), not the ~2^-100 in red-team-link's report.
- **Its audit list (report, "What a Flock red team must audit"):**
  1. The live-coin rep-independence lemma.
  2. The 7 protocol-fixed inner zerocheck coordinates.
  3. The per-site degrees: multipoint K-1, skip, lincheck 63, jagged 255, Merkle-shift 3, the F128^7 ring switch.
  4. Ligerito proximity: Johnson regime at eta 0.02, subfield descent, the F256 MCA term, and the union over lists.
  5. Two-point OOD binding in the list regime.
  6. The `Fast100` schedules against the ledger, plus the downgrade negative.
  7. The hash per line: BLAKE3 on CPU, SHA-256 in Flock-CUDA.
  8. GPU and CPU schedule parity.
  9. The union and m30 padding.
  10. Out of scope: link C1, C2 and C4.
- **Patches:** `lanes/flock-128/evidence/flock-128-r2-{cpu-harness,gpu}.patch`.
