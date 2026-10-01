---
id: 20261001T1636Z-handoff-from-circuits-grid-models-pk3-three-models-reorder
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

9:36 AM PDT, on your 8:55 set (note:20261001T1555Z-handoff-from-circuits-1130-set):

- **Both `-pk3` twins packed and match.** gm005-pk3 (r1-distill-qwen-15b) and gm008-pk3 (qwen25-3b) built on node 1 and ran in
  pack pod `ada3883d77`. Each matches its base on run root, binding map and verdict, with 460 of 460 replay units equal
  (note:20261001T1540Z-finding-pk2-twins-packed-match, last section). All 9 twinned models are now shown to pack
  transparently.
- **Three more ungated TP1 models are registered and queued, smallest first.** They are Pleias-350m (family pleias),
  h2o-danube3-500m (danube) and salamandra-2b (salamandra), all Llama-architecture BF16. The registration branch is
  `cursor/grid-models-more-be5a` @ 704714544, based on the boundary tree: 3 checkpoints, hf_configs, derived fixtures,
  weights.tsv lines and 72 workloads. Node 1 has it as `/workspace/research/trees/cursor-grid-models-more-be5a`, and the
  weights are staged in `/workspace/hf`. It is feeder wave 5 (cov-gm373 to cov-gm444), and their 3 cheapest rows were
  submitted at 16:31–16:33Z. Once those end, the grid has 22 models and 12 families. I haven't opened a PR for the branch;
  say if you want one.
- **The 3 new models won't pack until they are on `PACK_MODELS`.** That needs infra. dispatch.py says a model joins once a
  packed twin matches its unpacked row. If infra adds them, I'll submit `-pk` twins of their first rows. Until then, their
  ≤ 4B, b ≤ 8 rows run unpacked.
- **The 9:30 reorder is written** (`reorder.py --pack`). The order is: each model's first row while it has no deployment;
  then the 18 rows dispatch's own `packable()` would spool; then the 160 B8 or 1024-token rows; then the 60 others. Gemma-2
  stays held.
- **Someone raised the feeder caps after 14:13Z** (`builds_cap` 20, `build_mem_gb` 1000, `cpu_pending_max` 16). Its
  all-day `burst` entry still sets `cpu_pending_max` to 12, so the effective value is 12. I haven't changed it.
- **Counts at 9:31 AM PDT:** the grid has 192 ended deployments, 183 pass and 9 fail, each with a named cause. 8 are the
  SiluMul_v1 Definition gap and 1 is a missing GPU_UTIL in the item. That is 19 models and 9 families. The full counts
  follow at 10:30 and 11:20.
