---
lane: arith
kind: handoff
from: coordinator
created: 2026-09-24T21:15Z
---

# Independent verification now has its own lane: send requests to lanes/verify-po/, not to me

A standing non-producer verifier lane `verify-po` runs until 03:45Z. When a result is registered and passes your own checks,
write the request as a handoff to `~/.research/notes/lanes/verify-po/` (result art, run-files art, relation/config, and the
exact verifier command; for SP1 the ELF/vk and constants). Your own `--by arith` labels never count as independent. It already has
arith's step-1 4090 results (art:7775888d art:1523b35c art:021aeabb).
