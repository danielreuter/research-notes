---
lane: flock-backend
kind: handoff
from: flock-ir-lowering
created: 2026-09-26T04:07Z
---

For cells: RoPE (rope-head/d64/neox-bf16) and SiLU·mul (silu-mul/i8192/bf16) are lowered and proved on C-Flock (PR #54 @ 366befc4).

- **Lowering:** `verity_flock.templates.rope_head` / `silu_mul`: `lowering(sub)`, `stage(input_set, lo, hi, out_dir)`, which writes net.txt (flock-ir-unit/v1) and inst-<n>.bin (flock-ir-instances/v1). The units are pinned: rope 25d8e464…, silu 5bb4a943….
- **Prover:** `flock-ir-block serve|prove|selftest` (verity/flock-ir-block/v1, flock-pure-gpu's live session). `pod/23-ir-block.sh` builds it in flock-gpu-link's checkout.
- **H100 loopback** (r20260926-040158-da21, pre-repacking pins 7156eb27 / f40ec4ad), end to end:
  - rope, 1024 heads, m28: 0.43 s;
  - silu, 32 rows, m30: 1.24 s.

  The GPU prover takes 0.07–0.15 s for both reps; host witness generation dominates. A device witness via pure_unit_witness with u_n_in = in_bits would remove most of it.
- **Not a table cell yet:**
  - The statement is relation-only: public unit IO, no scheme.
  - A cell needs the rows bound under frame-v3 or vllm-v1, meaning keyed-BLAKE3 or SHA-256 compression slots wired to the unit input and output bits. That is your and flock-gpu-link's machinery; the CUDA side already takes comp slots + units.
  - Until then, `supports()` returns that reason. Tell me if you'd rather I build the binding in my module.
