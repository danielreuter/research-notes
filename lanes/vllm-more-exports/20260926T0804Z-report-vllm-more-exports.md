---
lane: vllm-more-exports
kind: report
created: 2026-09-26T08:04Z
status: open
---

CHECKPOINT e3a2d81d (08:11Z) [open] WAIT vyv-more-exports-h100 r20260926-080641-f752 check-back 08:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4: bootstrap (B0,QWEN3_4B_FP8); WAIT vyv-more-exports-moe r20260926-080751-376f check-back 08:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4: bootstrap (B0,OLMOE); next: #74/#67 rows; hard stop $30 ~13:20Z (handoff 0812Z ack)
CHECKPOINT e25e3614 (08:04Z) [open] started (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4): #74 FP8 H100 + #67 OLMoE TP1; exporter drops FP8/MoE-expert GEMM VUs today (weight > max_row_words) -> adding coordinate decompositions on cursor/vllm-more-exports-0df4; #57 skipped (FAIL-class, no evaluators); pods next; handoff vllm-coordinator 0806Z
