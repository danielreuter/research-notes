---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# NVFP4 scale bytes outside UE4M3 on sm_120: bit 7 is ignored

30 Sep 2026, 09:35Z. Independent assessor (bc-d7d4b0d1). This is evidence held for the FP4 rows, which wait on the Pearl-C4 replay; no rating yet. It independently re-checks one question the vLLM sm120-tc-gemm lane's job 119 is probing (research-notes `lanes/pous/20260930T0925Z-handoff-from-vllm-sm120-tc-gemm.md`).

## The probe

`scale_bytes_sm120.cu` and `.sh`, `r20260930-093120-b2f2`, GPU 6.

- **What it runs:** `mma.sync … kind::mxf4nvf4.block_scale.scale_vec::4X.m16n8k64 … .ue4m3`, which is SASS `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`, the instruction vLLM's `cutlass_scaled_fp4_mm` uses.
- **The setup:** A and B are E2M1 1.0 everywhere, and the other side's scales are 1.0. Every scale byte on the probed side is s, so D = 64 · decode(s) at every coordinate. It covers all 256 bytes on each side.

## The result (A and B sides alike, every D element uniform)

| Scale byte | What the device computes with |
|---|---|
| 0x00–0x7E | Exactly UE4M3's value, 127 of 127 (0x00 is a zero scale; 0x01–0x07 are subnormals) |
| 0x7F | NaN: D is NaN |
| 0x80–0xFF | **UE4M3 of the low 7 bits**, 128 of 128 (bit 7 is ignored): 0x80 → 0, 0xB8 → 1.0, 0xFE → 448, 0xFF → NaN |

## What it means for the FP4 rows

- **Two encodings per scale.** Every scale has two byte encodings that compute the same product. The pinned `BlockScaledAlignAdd` replay has to do one of two things:
  - ignore bit 7 as the device does;
  - have the domain reject any byte with bit 7 set.

  If it gives such a byte another meaning (a sign, for instance), honest hardware and the replay disagree.
- **Where it could matter:** only where a prover supplies scale bytes that the verifier doesn't recompute, which means unsampled tiles or anything hashed without a forming check. There, flipping bit 7 changes committed bytes without changing C̃ (malleability). It gives no free grinding over tickets drawn from C̃, and no change to the work.
- **Zero and NaN scales:** a zero scale (0x00 or 0x80) zeroes a block's products. The Pearl-C4 domain or forming must keep honest scales nonzero, or a block's chain is free. 0x7F and 0xFF poison D with NaN, which the chain's finiteness check rejects.

The vLLM lane's in-range result (131,072 of 131,072 quantizer blocks and 295,936 of 295,936 GEMM coordinates exact, `r20260930-091510-b35b` and `r20260930-091735-c29b`) is consistent with the 127 of 127 in-range bytes here. I haven't re-run their chain check. That waits for the FP4 rows.
