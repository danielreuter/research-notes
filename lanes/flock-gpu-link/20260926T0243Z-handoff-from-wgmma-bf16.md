---
lane: flock-gpu-link
kind: handoff
from: wgmma-bf16
created: 2026-09-26T02:43Z
---

# wgmma-bf16 follow-up: flock-backend's bf16-hopper-wgmma pin 12c3c8d3 matches, and the hardware says the two BF16 instructions are one function

**To:** flock-gpu-link (bc-9209cb00).

- flock-backend's `bf16-hopper-wgmma` lowering pin, `12c3c8d3...`, is the digest I derived. Its rows are identical to `bf16-hopper`'s, and only the header's relation name differs.
- On the H100, `mma.sync` bf16 and `wgmma` bf16 write the same words on every captured input, NaN and infinities included.
  That holds on two devices and on both wgmma A paths (PR #49 @ `a040aecd`, run r20260926-023321-ecb5).
- So the `bf16-hopper` instance set and unit are valid for the wgmma subcircuit word for word. Reusing the set is still a coordinator decision, recorded as an `instance-equiv/v1` or a note.
