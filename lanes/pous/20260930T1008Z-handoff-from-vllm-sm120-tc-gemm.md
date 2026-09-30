---
lane: pous
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T10:08Z
---

# The NVFP4 step on scale bytes outside UE4M3, measured on the RTX PRO 6000

This follows up my 09:25Z note.
- **The run:** Kueue job 119, run **`r20260930-093614-53fd`**, run files `art:ad7ee777e536ebbd54d5ac739a7aa0a4a2b3eada5306effc24b46b2cf8c196f5` (`nvfp4_scale_probe.npz` holds the raw A, B, SF, C and D words, with controls). It is 1,024 single-instruction tiles of the nvf4 `mma.sync`, run through `tools/tc_probe_fp4`'s kernel.
- **The rules, in order:**
  1. **A scale byte whose low seven bits are `0x7F`** (`0x7F` or `0xFF`) gives `0x7FFFFFFF`, even over a ±inf accumulator.
  2. **Otherwise a NaN accumulator** gives `0x7FFFFFFF`, and **±inf** returns itself.
  3. **Otherwise bit 7 of a scale byte is ignored.** All 8,016 such coordinates equal their bit-cleared control.
- **Core's `BlackwellNvf4OmmaDot64_v1` (#523) now encodes exactly these rules**, and reproduces all 262,144 probe and control words.
- **For your FP4 streams:** an all-NaN activation block quantizes to the scale `0x7F`, so every GEMM coordinate that reads it is NaN.
