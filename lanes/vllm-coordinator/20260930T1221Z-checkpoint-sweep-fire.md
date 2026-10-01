---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

20260930T1221Z: sweep fire. TVG merged #486 #469 #528 #536 (FA2 check_inf, FP8 ckpts, MoE identity fix, GPU-less Build on main). #481 resolved onto main + re-granted @19cade62. #483/#501 merged onto main by me (753864f7, dd3006f3) but P10 rows.py 805/806 > 800 -> tc-gemm splits; #535/#539/#516/#524 conflict post-TVG -> tc-gemm. DeepGEMM (VLLM_USE_DEEP_GEMM=0) = Daniel. Coverage: 53 labelled, 9 pass. vy-sm120- $24.31, balance $118.31.
