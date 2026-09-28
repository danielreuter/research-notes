---
lane: gemm-hash
kind: report
created: 2026-09-28T20:09Z
status: open
---

CHECKPOINT ac412eb8 (20:30Z) [open] measured (CPU): SHA is 26-44% of GEMM session time post-#289 (host bucket 47-64%); no-hash ceiling 1.30x today, 1.07x after tiles; top pick native SHA witness kernel (1.11x); K=8192 2x4 needs only carries-every-16 (13 per 2^20), not <=65,536 rows; writing plan
CHECKPOINT ac412eb8 (20:09Z) [open] started: ranked plan for GEMM in-circuit SHA-512 cost (CPU only, no pods); reading M0 statement, #289 buckets, tile scope; agent bc-abeef3db
