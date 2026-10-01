---
lane: circuits-bool-silu
kind: report
created: 2026-10-01T06:37Z
status: open
---

CHECKPOINT aa9acb14b (10:18Z) [open] SiluMulBf16_v4 / SiluMul_v4{I} (word _v2) at aa9acb14b on cursor/bool-silu-8c79: exact on all 2^32 pairs (art:7f6011c2), circuit-check green (art:af255d33), 1380 ANDs; ids handed to bool-switch (note:20261001T1018Z-handoff-from-circuits-bool-silu-silu-v4-ids); suites running
CHECKPOINT 59b134051 (08:43Z) [open] 1:43 AM PDT: Bf16Tanh_v2{N}/TanhBf16_v2 green (391 ANDs/elt, exact on 65,536 words, pinned); my GeLU + scalar rows retired as duplicates of elementwise's boolean_dense; attention softcap blocked on MufuTanh_v2 + proofs' v6 block; report 20261001T0843Z
CHECKPOINT 2b2e176f8 (07:13Z) [open] 12:14 AM PDT: both Boolean SiLU Definitions done on cursor/bool-silu-8c79 @ 2b2e176f8 (SiluMulBf16_v3 1372/7034/162, SiluMul_v3{I=8} 10976 ANDs); circuit-check 2/2 green, 0 warnings; P9 lint fixed; no word-id sub-Calls; report note:20261001T0658Z-report-from-circuits-bool-silu-both-green. (The 06:37Z checkpoint was 11:37 PM PDT.)
CHECKPOINT 98bc36342 (06:37Z) [open] SiluMulBf16_v3 + SiluMul_v3{I} Boolean on cursor/bool-silu-8c79 @98bc363: 1372 And/7034 Xor/162 Not, circuit-check green (0 warnings, --as-call), no MUFU sub-Calls needed
