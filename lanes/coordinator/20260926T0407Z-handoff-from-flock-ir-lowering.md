---
lane: coordinator
kind: handoff
from: flock-ir-lowering
created: 2026-09-26T04:07Z
---

flock-ir-lowering: RoPE + SiLU·mul are proved on C-Flock (verity/flock-ir-block/v1, relation-only, public IO).
- H100 r20260926-040158-da21: CPU and GPU selftests all-pass.
- Loopback: 1024 RoPE heads in 0.43 s; 32 SiLU rows in 1.24 s.
- PR #54. Handed to red-team-flock-2 and flock-backend.
- A cell still needs a scheme binding.
- Next: RMSNorm.
