---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T23:28Z
---

# sha256/row/v1 leaves, ShaBf16 layout, on the A100 (bf16-ampere): CPU + GPU selftest all-pass; 4,096 and 8,192 VUs accepted (host-witness bound)

This covers the frame-v3 **SHA-256** line of A100 BF16. It is the same ShaBf16 layout as my 23:23Z note, with the
provisional bf16-ampere lowering (pin e97ecb9e…, see 22:50Z).

- **Binary:** `flock-pure-gpu` at `cursor/flock-gpu-link-797a` @ ad0aa41d. SM=80.
- **Evidence:** A100-SXM4-80GB (EPYC 7742 host), loopback verifier, run r20260925-231219-cf82, art:c7866a70.
  - The CPU and GPU selftests pass every case at 8 (m25) and 64 (m28) VUs.
  - Sessions at 4,096 VUs (m34): 30.9–32.5 s. At 8,192 (m35): 59–66 s. 272–274 rounds; 580–598 KB proof per rep.
  - **These timings are host-witness bound.** This run predates the reuse of the host witness for rep 1. About 15 s per
    rep is the A100 host's CPU building the SHA-256 and unit witness; the GPU's share is small. Not a cell-quality
    number until a device SHA-256 witness exists.
- **red-team-flock:** nothing new beyond the 23:15Z and 23:23Z notes, plus the Ampere pin of 22:50Z.
