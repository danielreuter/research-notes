---
lane: red-team-flock-2
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T04:19Z
---

# NV5 is fixed at e84e3fe2 (fast-forward on flock-backend 20082dcb). Please re-review for NVFP4

- **The fix:** `admit` now pins the y leaf from the netlist, via `y_leaf(net)`: `u16` over 2 bytes for epilogue
  relations (and it refuses any y ≥ 2^16), `u32` over 4 bytes otherwise. So fp4-nvf4 takes u32 over 4 bytes.
  - It refuses before any coin, after NV2 / NV3 and before NV1.
  - `commit()` still reads `y_bytes` from the header, but admission has already forced it to the pinned width.
- **Negatives:** every selftest run now has `y_leaf_other_width`. On u32 relations it re-encodes the leaf as u16 over
  2 bytes, which is your fp8 and fp4 G4 cases.
- **Evidence:**
  - CPU selftests pass on Fp4 and ShaFp4, NV5 case included.
  - An Fp4 file with its y leaf relabelled `u16` / 2 exits 2 with `REFUSED NV5`.
  - The statement digests are unchanged.
