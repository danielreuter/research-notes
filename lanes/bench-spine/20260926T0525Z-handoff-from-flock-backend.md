---
lane: bench-spine
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T05:25Z
---

# FP8 input sets at K = 2048 / 8192: my four Flock cells used this recipe. Tell me if your sets are byte-identical, or when they land

The coordinator's 05:21Z instruction: I re-run the four FP8 real-K Flock cells on your sets unless you show that your x / W
bytes equal mine.
- **The cells:** 4090 fp8-ada K2048 art:43986c5d and K8192 art:c0999f7f; H100 fp8-hopper K2048 art:c200eef3 and K8192
  art:c4d03dd5.
- **The recipe:** `verity_flock.instances.write_synth` at flock-backend 08a28a1b. For VU i:
  - `rng = np.random.default_rng([20260922, i])`, then x = `_e4m3_operands(rng, (K,))`, then W = `_e4m3_operands(rng, (K,))`.
    Both relations use the same seed, so their operands are identical at the same K.
  - `_e4m3_operands`: `rng.integers(0, 256, size, int64)`; each byte with `(b & 0x7F) == 0x7F` has bit 0x08 cleared.
  - The cells used VUs [0, 4096) at K2048 and [0, 2048) at K8192 on the 4090. On the H100 they used [0, 8192) at K2048
    and [0, 4096) at K8192.
  - Accumulators come from the relation's `tc_dot` chain (ADA_E4M3 / HOPPER_E4M3). The cell's out is the FP32 word, and
    y = out >> 10.
- **Please send me** the set art ids once they are registered (vllm-vu-set/v1 or input-set/v1, with x.u8 / w.u8 or u16
  words and y). I will run `write_set` on them, which needs a small 8-bit extension.
