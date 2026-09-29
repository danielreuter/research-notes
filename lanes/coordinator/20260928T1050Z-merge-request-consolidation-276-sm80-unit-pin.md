---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T10:50Z
---

# Merge request: PR #276, the sm80 GEMM coordinate's unit pin (a follow-up to #221, after #201)

- **PR:** [#276](https://github.com/danielreuter/verity/pull/276), branch `cursor/sm80-unit-pin-ac68`, head **`c84e6254`**, on `main` `64f94732`. Ready, $0, small.
- **Contents:** one `pins.json` entry, `units["gemm-coordinate/k64/sm80-mma-bf16"] = {and: 8660, xor: 55268, not: 2041}`, written by `--update-pins` on that target alone. It equals the pinned `attention-head/d64-bn128/sm80-fa2-bf16` unit, since both are the same Ampere step. It clears the `lowering/unpinned` warning #221 left.
- **circuit-check:** 5 targets, 0 failures. `test_ampere_dot_ids.py` and the gemm-coordinate pin cases pass.
- **Epoch:** moves no digest; it doesn't touch `integrations/vllm`.

**Also:** #250 (MUFU into core) now sits on `main` at `99f2beaa`, with `tail_pieces.py` reading core's tables. It stays a draft until the epoch's rows are written.
