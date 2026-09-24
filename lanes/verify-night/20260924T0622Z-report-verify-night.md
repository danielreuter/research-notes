---
lane: verify-night
kind: report
created: 2026-09-24T06:22Z
status: open
---

CHECKPOINT none (06:53Z) [open] 06:53Z. r2 reverify: 5/5 fused-phases 4090 results PASS (06be3b23 0.0963 v3x4, 2d685314 0.1799 frozen, 91c62994, d0789c44, 7f294d16; equivs d40f5065/574f3519 labelled 06:3xZ). SP1 host built from sp1-table b5e1ed5f reproduces elf cffc5eff/vk 0x000503d6; my statement (from my tree's frozen fixture) == dumped statement.bin; rep0 verify ok+statement_match, 1-byte-flipped y -> statement_match false; re-running reps 1-2. Next: A-GKR art:03e21c7f (build verity-gkr-verify @53bd441b on pod), re-render + delta. Inbox: agkr-table 0644Z (doing), coordinator 0646Z fused-cells (done: r2).
CHECKPOINT 1b3c7be6 (06:42Z) [open] reverify r1 5/5 PASS by verify-night: T2 H100bf16 5.2e7->2.0e7 art:44c768cd; H100fp8 5.6e7->2.1e7 art:1e73dc00; 4090 3.0e6->2.4e6 art:fb4934af; 4090+hash 1.8e7->1.0e7 art:9167ed22; 5090 9.5e6->5.1e6 art:885eec16. next: stmt-vs-frozen binding check, SP1 build
CHECKPOINT 1b3c7be6 (06:38Z) [open] 15/15 instance-equiv re-checked 3 ways (check, regen, own full-chain) -> verified=accepted (verdicts preserved). T2 4090 B-Ligero 6.6e6x->3.0e6x art:0d5b229a (equiv art:68466c4a). next: reverify U-only fastest per cell on pod
CHECKPOINT 1b3c7be6 (06:22Z) [open] 06:23Z started; pod vy-verify-night gyenhpbetf7xz8 (cpu3c 16vCPU $0.48/h) bound; next: bootstrap, re-derive 15 instance-equiv files starting art:68466c4a, then U-only candidates
