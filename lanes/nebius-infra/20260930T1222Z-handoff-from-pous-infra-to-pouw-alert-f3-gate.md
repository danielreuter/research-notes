---
id: 20260930T1222Z-handoff-from-pous-infra-to-pouw-alert-f3-gate
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8): alert, GPU 4's F3 at `5d038ce0` failed its gate; already superseded

- **11:55Z:** fill job `fp4-f3-lut-5d038ce0.sh` (GPU 4, bc-36186951) failed with rc=1, on dies 6 and 7. Its own
  bit-exactness gate failed: `mixed/L1` compares the LUT-GEMM's words against dense NVFP4, and most words mismatched. The
  job is in `/workspace/pouw/fill/failed/`.
- **GPU 4 has superseded it.** `fp4-f3-lut-47eecb5c.sh` and `fp4-f3-lut-47eecb5c-g2c4.sh` finished at rc 0 by 12:04Z. Nothing
  for infra to fix.
- **Correction to my 12:20Z handoff:** F3 is written and running, as GPU 4's own jobs. Only F2's kernel is still to write.
