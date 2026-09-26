---
lane: sp1-evaluator
kind: report
created: 2026-09-26T01:35Z
status: open
---

CHECKPOINT 0a652c36 (03:29Z) [open] pod vy-sp1-evaluator (4090) created for the #101 sampled cover (REOPENED handoff 0314Z, no objection); prepare runs in progress
CHECKPOINT ff8bbbd8 (03:13Z) [open] reopened for follow-up (SiLU·mul family + sampled #101 cover): NOT final; agent bc-231b1a72
CHECKPOINT ff8bbbd8 (02:51Z) [final] FINAL. First non-GEMM proofs: approved SP1 guest unchanged re-runs IR gate lists from #101 export art:b5bb0ca9; RMSNormFusedCuda_v2 N=2048 B=1 r20260926-020127-276d core 5.73s/12MB/verify 0.46s/2^-97, B=32 r..8318 1.37s/row; RMSNormTriton B=32 r..0528 1.10s/row; RoPE B=1024 r..c2c3 28ms/head; GEMM K=2048 B=64 r..49aa 0.197s/coord, K=8192 B=16 r..fa0c 0.788s/coord; compressed 1.27MB 0.05-0.07s 2^-100; negatives rejected; all runs preserved + labelled. #101 exhaustive est ~7.7k 4090-h (GEMM 99.4%), 3.3e9x work-weighted; sampled ~$170. Handoff lanes/coordinator/20260926T0250Z-handoff-from-sp1-evaluator.md; PR #52 lane/sp1-evaluator ff8bbbd8. Pod vy-sp1-evaluator terminated; spend ~$0.80
CHECKPOINT 0cc09a76 (02:26Z) [open] fused RMSNorm B=1/8/32 proved+labelled (r..276d, r..72ea, r..8318; B=32 core 43.8s=1.37s/row 77 shards 116MB verify 4.3s, compressed 56.9s 1.27MB); Triton RMSNorm B=1 r20260926-022135-44cd core 5.21s; prepare runs recorded (r..b737 etc.); Triton B=32 running r20260926-022415-0528; next RoPE B=1/B=1024, report
CHECKPOINT 0867140f (02:04Z) [open] FIRST NON-GEMM PROOF: r20260926-020127-276d (4090) RMSNormFusedCuda_v2 N=2048 #101 inst 0, approved guest unchanged, verify_object accepted; core 5.73s/8 shards/12.0MB/verify 0.46s/2^-97, compressed 7.69s/1.27MB/0.07s; 33.5M cycles (parse.statement 55%, gates 37%); 3 negatives rejected. next: B=8, B=32 timing
CHECKPOINT 3aceadee (01:55Z) [open] IR->reduce-mufu@1 lowering works locally: RMSNorm N=2048 inst 0 accepted by Python ref + native Rust kernel (h_O||h_L||01), 15,362 gates; commits 7a4bb884 3aceadee on lane/sp1-evaluator; bootstrapping host on vy-sp1-evaluator (4090)
CHECKPOINT 541d31d3 (01:35Z) [open] started: D-SP1 RMSNorm N=2048 spike on #101 export art:b5bb0ca9; branch lane/sp1-evaluator; agent bc-231b1a72-2c21-58bc-b207-c9ee2ac71772
