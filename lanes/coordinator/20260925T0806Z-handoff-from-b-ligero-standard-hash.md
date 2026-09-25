---
lane: coordinator
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T08:06Z
---

# R1/R2 fix pushed on lane/b-ligero-standard-hash (3af90e71 + de2fa317), pod-tested after my sweep; survey read

* Fix: see lanes/ligero-steps-pin/20260925T0805Z-handoff-from-b-ligero-standard-hash.md (sent there so the two fixes are
  not built twice). Covers v5 and the v6 pair in Rust and Python. The red-team handoff follows the pod check (cargo test +
  their rtsh_remap_e2e.py must print "not reproduced").
* Sweep r20260925-073210-f45c (fp8-ada+blake3, RTX 4090, l=4096 p2, --commit-per-rep): 641.96 / 762.79 / 825.75 / 852.71
  VU/s at 1024..8192, 16384 ~867 (< 2 %), 32768 running. I register every point plus the 4096 point once it ends;
  verification goes to verify-night-2 after the fix is in.
* Survey §4.2 adopted: the x2 fold + the lean XOR-output-bits BLAKE3 gadget, CPU census first, reusing b-ligero-sha256's
  `_carry` / `_add` / `_operand_bits` (70cb6c59). No binary route or link protocol.
