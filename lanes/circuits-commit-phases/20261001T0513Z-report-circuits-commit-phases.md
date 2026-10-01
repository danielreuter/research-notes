---
lane: circuits-commit-phases
kind: report
created: 2026-10-01T05:13Z
status: open
---

CHECKPOINT f8d39d2f9 (06:24Z) [open] report note:20261001T0625Z-report-from-circuits-commit-phases-gate-all-rows-equal: fixes 1+2 ready at f8d39d2f9 (every golden row equal, Qwen3-4B B32 GPU held 767->210 s); suites 21/22 (the TP2 MoE build test dies for memory here, passes alone); asking circuits before a PR; slim planner (cbfbf9384) merges with it on cursor/commit-gpu-phases-slim-planner-827a, fold-or-not is circuits' call; config-run plan task for infra on cursor/config-run-plan-task-827a
CHECKPOINT f8d39d2f9 (05:55Z) [open] fixes 1+2 gated on node 2 (tree 8aa9452df), every golden row equal to single-task (run root, Program, manifest, binding map, population, verdict, 460/460, replay seed and sample; perturbed plan -> plan_recomputed, same root and sample): GPU held 52->24 s SmolLM2 B1, 87->50 s Llama B8, 200->137 s OLMoE B8, 767->210 s Qwen3-4B B32 (art:795f8dda); branch at f8d39d2f9 (main merged in); suites running; config-run plan task on cursor/config-run-plan-task-827a for infra
CHECKPOINT 8aa9452df (05:13Z) [open] fix 1 prototyped on Qwen3-4B B32 (node 2, tree f6b39a2bf): GPU held 787 s single-task -> 255 s with the 0-GPU plan (561 s on CPU); run root, Program, manifest, binding-map and population digests equal; replays running; fix 2 (store written beside the checks) pushed at 8d1fa193c, full gate starting
