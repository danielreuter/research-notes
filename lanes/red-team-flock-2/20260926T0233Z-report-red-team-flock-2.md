---
lane: red-team-flock-2
kind: report
created: 2026-09-26T02:33Z
status: open
---

CHECKPOINT a57628fc (02:54Z) [open] WAITING r20260926-025249-6192 on vy-red-team-flock-2 (pkkkgds4e8unxt, A4000 as CPU box: no CPU stock), check after 03:25Z; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241; next: NVFP4 Fp4/ShaFp4 @7b3ba797 selftests on my gen_fp4 files + 12 rtf2 negatives + 3 gap demos (out!=y, schema relabel, fp4 netlist under Fp8)
CHECKPOINT a57628fc (02:37Z) [open] NVFP4 layout landed unhanded at flock-gpu-link 7b3ba797 (Fp4 blake3-keyed/row-nvfp4/v1 + ShaFp4 sha256/row-nvfp4/v1); starting paper review of diff vs 758a8edf. Also queued: flock-backend bf16-hopper-wgmma pin 12c3c8d3 (a9d13f68) pre-check. No pods.
CHECKPOINT a57628fc (02:33Z) [open] started; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241; scope: NVFP4 row-nvfp4 layout from flock-gpu-link + new flock-backend statements (incl. future row-sharing); red-team-flock keeps Chunk(n) item 1; reading contract + red-team-flock baseline; inbox: nothing new
