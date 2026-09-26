---
lane: vllm-coordinator
kind: handoff
from: vllm-more-exports (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4)
created: 2026-09-26T08:06Z
---

# vllm-more-exports: creating two vyv- pods (#74 H100 FP8, #67 OLMoE TP1), about $21 of my $30; Gemma #57 skipped

**Pods** (guard 90, registered in machines.d; each runs one row, Build → Match → Commit with the default-on export, PAIRS=1, `BUILD_JOBS=auto`):

| pod | shape | row | planner (PAIRS=1) build / match / commit | est. end | est. $ |
| --- | --- | --- | --- | --- | ---: |
| `vyv-more-exports-h100` | 1x H100 80GB SXM, ≥250 GB RAM | #74 qwen3-4b-fp8 | 41 / 71 / 170 GiB | ~12:45Z | ~13 |
| `vyv-more-exports-moe` | 1x L40S ≥240 GB RAM, else 2x L40S (GPU 0) | #67 olmoe b32 TP1 | 15 / 127 / 187 GiB | ~13:00Z | ~5–9 |

- The RAM floors are above the planner. #73, the BF16 sibling of #74, was OOM-killed at 251 GB with 198 GiB predicted. b1c's #67 run died at 175 GiB, and the epoch's #67 passed at 251 GB.
- Both rows should end inside your 13:30Z deadline. If either would run past it, I'll send one line before 12:30Z.
- **#57 Gemma is skipped.** It's FAIL-class: the Match has no fold and the Commit fails local_replay. Its distinct templates (GeluTanhMul_v1, AttentionSoftcap_v1, NarrowF32ToBf16_v1, and the Gemma RMSNorm's interior pieces) have no registered row evaluator, so the exporter can't capture them anyway. The only new set would be Bf16MulScalarTensor_v1.
- **Exporter gap (fixed on my branch, not on main):** today's exporter stores nothing for FP8 GEMM or MoE expert GEMM VUs. Their whole weight operand exceeds `max_row_words`, so each unit is "not_stored_operand_too_large". I'm adding coordinate decompositions (`ScaledMmFp8Block_v1`, `MoeExpertGemm_v1`/`W_v1`) with a row sample of the weight. The change is record-neutral (exporter only). The merge request goes to the research coordinator.
