---
lane: proofs-circuits-review
kind: report
created: 2026-10-01T01:46Z
status: open
---

CHECKPOINT 21a3915e (07:16Z) [open] t2 skipped (all merged, 0602Z handoff); t3 circuit-check pass, 0 reach (0627Z, art:72db1abc); t1 re-pin on main = cursor/557-tp2-moe-repin-on-main-8b2d@3968e73f4, OLMoE passed, Qwen3 retry r20261001-071624-d74e
CHECKPOINT c1e920090 (05:51Z) [open] resumed 05:51Z after billing stop (VM reset, /tmp lost); task1 evidence in the store; checking what moved on #557/#619-#624/tp2 before task 2
CHECKPOINT e5b720899 (02:06Z) [open] task1: cause found in code (#557 adds 2 rows to NAMED_RESIDUALS, serialized in every manifest's query header); OLMoE main rebuild = pin 3322490b; Qwen3 rebuilds r20261001-020559-b144 (main), -020629-6f09 (main+#557) on node1; task2 circuit-check --all on main running
CHECKPOINT e5b720899 (01:46Z) [open] started: task 1 (#557 TP2 MoE manifest move) first, then circuit-check for #619-#624 and tp2-commit-token-budget; agent bc-5abc75bd-2881-5699-b396-f5f4d2fd8b2d
