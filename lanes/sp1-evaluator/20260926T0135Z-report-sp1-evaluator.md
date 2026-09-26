---
lane: sp1-evaluator
kind: report
created: 2026-09-26T01:35Z
status: open
---

CHECKPOINT 0867140f (02:04Z) [open] FIRST NON-GEMM PROOF: r20260926-020127-276d (4090) RMSNormFusedCuda_v2 N=2048 #101 inst 0, approved guest unchanged, verify_object accepted; core 5.73s/8 shards/12.0MB/verify 0.46s/2^-97, compressed 7.69s/1.27MB/0.07s; 33.5M cycles (parse.statement 55%, gates 37%); 3 negatives rejected. next: B=8, B=32 timing
CHECKPOINT 3aceadee (01:55Z) [open] IR->reduce-mufu@1 lowering works locally: RMSNorm N=2048 inst 0 accepted by Python ref + native Rust kernel (h_O||h_L||01), 15,362 gates; commits 7a4bb884 3aceadee on lane/sp1-evaluator; bootstrapping host on vy-sp1-evaluator (4090)
CHECKPOINT 541d31d3 (01:35Z) [open] started: D-SP1 RMSNorm N=2048 spike on #101 export art:b5bb0ca9; branch lane/sp1-evaluator; agent bc-231b1a72-2c21-58bc-b207-c9ee2ac71772
