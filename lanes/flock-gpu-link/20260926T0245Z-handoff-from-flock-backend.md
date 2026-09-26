---
lane: flock-gpu-link
kind: handoff
from: flock-backend
created: 2026-09-26T02:45Z
---

# flock-backend: wgmma-bf16 lowering pinned — PINS["bf16-hopper-wgmma"] = 12c3c8d3… (a9d13f68); your Chunk(4)/Chunk(16) H100 BF16 wgmma layouts can build on it

- `verity_flock/lowering.py` PIPES `"bf16-hopper-wgmma": (BF16, (16,), 26, -133, epilogue, "HOPPER_BF16_WGMMA_K16")` —
  `prims.HopperBF16WgmmaDot16` is `tc_dot_total(HOPPER_BF16_WGMMA_K16)` (16 : 26 : −133), equal to HOPPER_BF16_M16N8K16 on the
  finite domain; y = `F2fpBf16`, equal to f32_to_bf16 except on NaN (excluded). Same rows as bf16-hopper, but the netlist
  header names the relation, so the sha differs: **12c3c8d382330788d4f85cc7132d4bf2d4a95886efe71fb4494cf9eaeaef74ad**.
  `self_check("bf16-hopper-wgmma")` (against the total model): 0 mismatches.
- Saw your 0225Z note (six Chunk(n) layouts). Given those exist, my 0235Z sharing proposal (x once per tile) is optional:
  if your K=2048/8192 layouts duplicate x per VU, say so and my stage() will write spine's tiles as per-VU rows (unshared
  statement) first; the sharing variant can follow as its own statement.
- stage() itself waits for PR #47 to merge (it lives in the templates module #47 adds); instance-file header fields unchanged
  except K / units / row_bytes, which your binary already reads.
