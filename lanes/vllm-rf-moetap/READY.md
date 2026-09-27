# vllm-rf-moetap READY (2026-09-27 01:50Z)

- PR #96 `cursor/vllm-rf-moetap-82dc` @ `c574c4a5`, base `5b0835d4` (#92 with #86, merged with #90). Merge after #86, #90, #92.
- Merge-ready handoff: `lanes/vllm-coordinator/20260927T0136Z-handoff-from-vllm-rf-moetap.md` (the 0015Z conditions 1-6, run ids).
- Records (all preserved on R2):
  - router-tap exactness `r20260927-011454-7498`: ok, verify intact, digest e8fa0bcf...; 4 configs x 1024 rows tap==IR, ==installed, all written; live OLMoE/Qwen3-MoE shapes rows_ne_ir 0, tokens equal bare.
  - TP2 vocabulary-range exactness `r20260927-011644-9037`: ok, verify intact, digest 5acdc9f2....
  - partition report `r20260927-005720-ee97`: PARTITION-OK, 0 recomputed gates, committed words == tap words.
  - gate (b) base `r20260927-005731-9c35`, head `r20260927-011128-606f` (3146bc31): jdiff rc 0; recheck of c574c4a5 `r20260927-013459-f5f0`: rc 0.
- #86 comparison (CPU): `evidence/records/router86_compare.json` (20 of 96 edge rows differ; fmaxf is the substantive fix).
- Pods: g1 terminated 23:25Z, g2 terminated 01:49Z. Spend ~$6.0 of $8.
