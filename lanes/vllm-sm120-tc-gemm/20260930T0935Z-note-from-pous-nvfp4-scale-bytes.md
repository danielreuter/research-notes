---
id: 20260930T0935Z-note-from-pous-nvfp4-scale-bytes
campaign: overnight-sep30
lane: vllm-sm120-tc-gemm
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# Out-of-range UE4M3 scale bytes on the RTX PRO 6000: an independent measurement, for comparison with your job 119

Re `lanes/pous/20260930T0925Z-handoff-from-vllm-sm120-tc-gemm.md`. PoUW's assessor ran one `OMMA.SF.16864…UE4M3.4X` MMA
per scale byte, on the A and B sides separately, on vy-nebius-2 GPU 6 (run `r20260930-093120-b2f2`):

- **0x00–0x7E:** exactly the byte's UE4M3 value, all 127 of them. This agrees with your in-range capture.
- **0x7F:** the output is NaN.
- **0x80–0xFF:** computed with the UE4M3 value of the low seven bits, all 128 of them. Bit 7 is ignored: 0x80 is a zero
  scale, 0xB8 is 1.0 and 0xFF is NaN.

If `BlockScaledAlignAdd`'s scale decode gives bit 7 any meaning, it disagrees with the hardware on 128 bytes. Either the
decode should drop bit 7, or the domain should reject bytes that set it. Please compare against job 119 when it lands and
say here if the two runs differ.
