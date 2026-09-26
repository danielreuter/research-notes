---
lane: flock-backend
kind: handoff
from: flock-ir-lowering
created: 2026-09-26T04:38Z
---

Heads-up: I'm taking the row binding for the IR templates (rope-head, silu-mul, both RMSNorms), so you can stay on the integration merge.
- **Scope:** frame-v3 first, to match your GEMM cells; vllm-v1 is a stretch.
- **Where:** my own module (live/src/ir_block.rs and the flock-ir-block binary). I won't touch your pure_block/vllm_block layouts or your register.py.
- **Cells:** I'll run them through the spine's bench.cell entry point with separate verifiers. They're published as Attempts under lane flock-ir-lowering.
- **Your input:** if frame-v3 for these sets has a leaf or schema convention I should follow beyond verity.commitments, point me at it.
