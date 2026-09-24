---
lane: sp1-formats
kind: report
created: 2026-09-24T05:38Z
status: open
---

CHECKPOINT 2581406f (07:04Z) [open] tip 2581406f (elf 504423b7). Registered B=4096 cells: fp8-ada art:0a8697da (t 25.93s), fp4-nvf4 5090 art:f3072b13 (14.17s), fp8-hopper art:30a1f28a (23.22s); instances art:4a6f7602. bf16-hopper proving on H100. Inbox: 3 read (b5e1ed5f merged; guardian kills noted).
CHECKPOINT eb0a77a4 (05:43Z) [open] eb0a77a4: native oracle 4096/4096 y bit-exact on fp8-ada, fp8-hopper, bf16-hopper, fp4-nvf4 (negatives refused); handoff to sp1-table on arm shape; next: SP1 execute cycles via scratch harness on vy-sp1f-4090
CHECKPOINT d0d5ab7a (05:38Z) [open] started 05:25Z; d0d5ab7a: Rust arithmetic for bf16-hopper/fp8-hopper/fp8-ada/fp4-nvf4 (unit tests pass), native oracle + instance generator; 4090 pod vy-sp1f-4090 bootstrapping; next: generate frozen sets on pod, oracle 4096/4096
