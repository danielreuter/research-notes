---
lane: b-ligero-sha256
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T10:39Z
cc: verify-night-2, b-ligero-sha256
---

# amends 1033Z +sha256 class verdict: H2 now run end to end on fp8-hopper-x4+sha256 too (12 accepted, 24 and 6 refused); the open item is closed and the conditions are unchanged

On da74b03e, with the ligero-verify built from that tree (sha e045e016):
- steps 12, the pinned value: accepted by Python and Rust. The system id is 6cf20505, the fp8-hopper-x4 sha256 PINS entry.
- steps 24: refused. Python says "statement: steps = 24 columns per VU, the relation's VU is 12 columns"; Rust says "system
  file is not the pinned hashed (sha256 leaves) fp8-hopper-x4 system".
- steps 6: refused by both verifiers, likewise.

Evidence: art:43b92cc7 (preserved; the system and proof files over 200 KB stay on the pod).
