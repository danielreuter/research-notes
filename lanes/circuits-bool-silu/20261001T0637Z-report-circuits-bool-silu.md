---
lane: circuits-bool-silu
kind: report
created: 2026-10-01T06:37Z
status: open
---

CHECKPOINT 0079a2b22 (12:18Z) [open] 5:21 AM PDT: softcap PR 2 on MufuTanh_v2: bool-softcap-attn-e311 @ 0079a2b22 (abc153b55 + bool-switch 443538fed merged); 21 softcap tests, lints, coverage test pass; circuit-check root+head ok, blocks running; 80703ab0e merges clean (testing)
CHECKPOINT 7e5711a92 (11:47Z) [open] 4:47 AM PDT: 4:50 report is note:20261001T1125Z-report-from-circuits-bool-silu-silu-v4-exact; since then bool-silu head 7e5711a92 (main + bool-switch merged; one Bf16Tanh_v2, boolean_activation's, per the 0954Z collision handoff: elementwise's copy is theirs to drop); softcap side branch 0a2e6f7e2; no Boolean MufuTanh on any branch; inbox 0614Z/0622Z/0641Z already acted on; VM reset wiped ~ (worktrees, ~/.research), notes re-cloned
CHECKPOINT 37e1c90a8 (11:26Z) [open] 4:25 AM PDT: SiLU v4 done (37e1c90a8; branch head 39fea86c2 after my watch merged main): exact on 2^32 (art:7f6011c2), circuit-check green, report note:20261001T1125Z-report-from-circuits-bool-silu-silu-v4-exact
CHECKPOINT 0b1787843 (11:23Z) [open] 4:23 AM PDT: bool-silu @ 7e5711a92 = main (proofs-ir) + bool-switch merged in; Bf16Tanh_v2 collision already resolved by elementwise (9366d8afc); circuit-check 7/7 ok, coverage ok; told switch in note:20261001T1123Z-handoff-from-circuits-bool-silu-switch-merged-head
CHECKPOINT 0b1787843 (11:19Z) [open] proofs-ir landed on main: merged origin/main (217 commits, clean) into cursor/bool-silu-8c79 on top of 37e1c90a8 (the v4 pair) -> 39fea86c2, pushed (fast-forward). On the merged tree: test_boolean_activation + test_boolean_silu (not slow) + tests/lint 91 pass; circuit-check SiluMulBf16_v3/v4, SiluMul_v3/v4{I=8}, TanhBf16_v2, Bf16Tanh_v2{N=8} ok, 0 warnings; coverage test passes. No Boolean MufuTanh on origin yet (softcap side branch unchanged at 0a2e6f7e2). /home/ubuntu/bool-silu-wt is now one merge behind origin.
CHECKPOINT aa9acb14b (10:18Z) [open] SiluMulBf16_v4 / SiluMul_v4{I} (word _v2) at aa9acb14b on cursor/bool-silu-8c79: exact on all 2^32 pairs (art:7f6011c2), circuit-check green (art:af255d33), 1380 ANDs; ids handed to bool-switch (note:20261001T1018Z-handoff-from-circuits-bool-silu-silu-v4-ids); suites running
CHECKPOINT 59b134051 (08:43Z) [open] 1:43 AM PDT: Bf16Tanh_v2{N}/TanhBf16_v2 green (391 ANDs/elt, exact on 65,536 words, pinned); my GeLU + scalar rows retired as duplicates of elementwise's boolean_dense; attention softcap blocked on MufuTanh_v2 + proofs' v6 block; report 20261001T0843Z
CHECKPOINT 2b2e176f8 (07:13Z) [open] 12:14 AM PDT: both Boolean SiLU Definitions done on cursor/bool-silu-8c79 @ 2b2e176f8 (SiluMulBf16_v3 1372/7034/162, SiluMul_v3{I=8} 10976 ANDs); circuit-check 2/2 green, 0 warnings; P9 lint fixed; no word-id sub-Calls; report note:20261001T0658Z-report-from-circuits-bool-silu-both-green. (The 06:37Z checkpoint was 11:37 PM PDT.)
CHECKPOINT 98bc36342 (06:37Z) [open] SiluMulBf16_v3 + SiluMul_v3{I} Boolean on cursor/bool-silu-8c79 @98bc363: 1372 And/7034 Xor/162 Not, circuit-check green (0 warnings, --as-call), no MUFU sub-Calls needed
