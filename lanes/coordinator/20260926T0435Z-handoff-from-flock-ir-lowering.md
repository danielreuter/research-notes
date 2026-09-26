---
lane: coordinator
kind: handoff
from: flock-ir-lowering
created: 2026-09-26T04:35Z
---

flock-ir-lowering: both RMSNorms (fused, Triton) now lower exactly and prove on C-Flock. All four #101 elementwise and row templates are proved on H100 (r20260926-042206-7932, CPU and GPU selftests all-pass).
- 256 RMSNorm rows at m32: 5.7 s / 6.6 s end to end, 0.5 s of which is GPU.
- PR #54. Handed to red-team-flock-2 and flock-backend.
- Spend about $1.7; no pods up.
