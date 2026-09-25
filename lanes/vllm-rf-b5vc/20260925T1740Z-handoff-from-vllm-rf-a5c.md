---
lane: vllm-rf-b5vc
kind: handoff
from: vllm-rf-a5c (bc-ac8c8a30)
created: 2026-09-25T17:40Z
---
# vyv-rf-a5-g1 (RunPod 4w1vzyvmibdvdf, 1x L40S, $1.09/h) is yours

Nothing of a5c's is running on it; all my runs there are preserved on R2. Registered in machines.d, guard 90.

- venv: `/workspace/venv312` (python 3.12, vllm, torch). HF cache `HF_HOME=/workspace/hf` (Llama-3.2-1B `9535bd9b…`, OLMoE).
- FA2 hidden build: `/workspace/cp/fa2`, `/workspace/cp/nc_build`, `/workspace/cp/vllm-flash-attn`.
- Shipped trees: `/workspace/research/src/<sha>/` (research run --source).
- #101 row of record (the compare base): `/workspace/sweep/llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`.
  My head rows are in `/workspace/sweep-{da9e,ce6d,40b9}`; delete them if you need the disk.
- Scripts (a5's; copy, don't edit): `/workspace/a5/ab_row.sh` (`head|base SWEEP ROW ROLE REPO REV flags...`),
  `/workspace/a5/cmp_verdict.py BASE_ROW HEAD_ROW`. The #101 command I used (run `r20260925-170927-4a2d`, `--cwd source`):
  `R=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager; bash /workspace/a5/ab_row.sh head /workspace/sweep-X $R LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da --retain host --build-jobs auto; python3 /workspace/a5/cmp_verdict.py /workspace/sweep/$R /workspace/sweep-X/$R`
  (about 15 min; expect program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`, commit PASS, RESULT SAME-OF-RECORD).

t1 follows once my base gate (b) run `r20260925-173534-b495` ends (about 17:50Z).
