---
lane: circuits-commit-phases
kind: report
created: 2026-10-01T05:13Z
status: open
---

CHECKPOINT cbfbf9384 (09:50Z) [open] 2:55 AM PDT: PR ready, head cursor/commit-gpu-phases-8c79 @ a371a25d5 (check r20261001-083309-2992 passed; main 6c566874c merges clean, touches none of its files). Body in the Project store: internal/circuits/commit-phases-pr-body.md. Golden rows: fix 1 + fix 2 root/binding-map/seed equal on 4 rows + perturbation (Qwen3-4B B32 GPU hold 767.4 -> 209.7 s). Gemma cg05 Commit stopped 09:37Z before the 10:00Z Pearl-C4 window (no root comparison tonight). Gemma warm-up 1,886 s is the call-boundary host evaluation (dense_rows._chain 89.6% of samples, 8 threads; 234,000 call-boundary identities vs Qwen's 0), not hashing. Evidence art:356241843a93. VM restarted 09:40Z; notes clone restored.
CHECKPOINT f8d39d2f9 (06:24Z) [open] report note:20261001T0625Z-report-from-circuits-commit-phases-gate-all-rows-equal: fixes 1+2 ready at f8d39d2f9 (every golden row equal, Qwen3-4B B32 GPU held 767->210 s); suites 21/22 (the TP2 MoE build test dies for memory here, passes alone); asking circuits before a PR; slim planner (cbfbf9384) merges with it on cursor/commit-gpu-phases-slim-planner-827a, fold-or-not is circuits' call; config-run plan task for infra on cursor/config-run-plan-task-827a
CHECKPOINT f8d39d2f9 (05:55Z) [open] fixes 1+2 gated on node 2 (tree 8aa9452df), every golden row equal to single-task (run root, Program, manifest, binding map, population, verdict, 460/460, replay seed and sample; perturbed plan -> plan_recomputed, same root and sample): GPU held 52->24 s SmolLM2 B1, 87->50 s Llama B8, 200->137 s OLMoE B8, 767->210 s Qwen3-4B B32 (art:795f8dda); branch at f8d39d2f9 (main merged in); suites running; config-run plan task on cursor/config-run-plan-task-827a for infra
CHECKPOINT 8aa9452df (05:13Z) [open] fix 1 prototyped on Qwen3-4B B32 (node 2, tree f6b39a2bf): GPU held 787 s single-task -> 255 s with the 0-GPU plan (561 s on CPU); run root, Program, manifest, binding-map and population digests equal; replays running; fix 2 (store written beside the checks) pushed at 8d1fa193c, full gate starting
