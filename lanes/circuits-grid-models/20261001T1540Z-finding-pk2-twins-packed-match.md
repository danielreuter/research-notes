---
id: 20261001T1540Z-finding-pk2-twins-packed-match
campaign: overnight-sep30
lane: circuits-grid-models
kind: finding
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# The `-pk2` twins (8:40 AM PDT): packing changes nothing on the 7 that packed; 2 ran unpacked because node 2 built them

The 9 `-pk2` twins (gm001–gm009, submitted at 15:11:55Z once `PACK_MODELS` listed their models,
note:20261001T1412Z-handoff-from-circuits-drop-deadline-gate) all ended by 15:37Z. Each twin runs its base's row on the
boundary tree. The table compares the base with the twin on the run root, the binding map and the verdict (base / twin).

| twin | model | packed (pack pod) | run root | binding map | verdict |
|---|---|---|---|---|---|
| cov-gm002-pk2 | qwen25-05b-instruct | yes (`b4620bb557`) | same `fe8b4fe99c4d476b` | same `ae4c3f13a430873b` | PASS / PASS |
| cov-gm003-pk2 | falcon3-1b | yes (`cb69176114`) | same `a0ce6b1b0d3dc40e` | same `69ae532fb90965fc` | PASS / PASS |
| cov-gm004-pk2 | qwen25-coder-15b | yes (`cb69176114`) | same `a739323cd9ea2e0e` | same `e4f5fe01400ef418` | PASS / PASS |
| cov-gm005-pk2 | r1-distill-qwen-15b | no: Build on node 2 | same `82ce5ff0a2c960d4` | same `1c4f631b2ca9b914` | PASS / PASS |
| cov-gm006-pk2 | qwen3-17b | yes (`cb69176114`) | same `50e98ba4c4d95be9` | same `524d984863acda1d` | PASS / PASS |
| cov-gm007-pk2 | smollm2-17b | yes (`b4620bb557`) | same `7d4e930a6c606065` | same `5a9676098ec27b15` | PASS / PASS |
| cov-gm008-pk2 | qwen25-3b | no: Build on node 2 | same `de4d8ecd42eb22fa` | same `fb53d179cc0e160f` | PASS / PASS |
| cov-gm009-pk2 | llama32-3b | yes (`b4620bb557`) | same `03abfcb391217db9` | same `458f2778a27f69a4` | PASS / PASS |
| cov-gm001-pk2 | qwen3-06b | yes (`cb69176114`) | same `81b63e73e8f08afa` | same `7850ffdc06a13bdb` | FAIL / FAIL |

- **Packing is transparent on all 7 packed twins.** Each matches its base's run root, binding map and verdict.
- **gm001-pk2 fails the same way as its base and the `-pk` twin.** The mismatch is at `model.layers.27.mlp.act_fn`, r0
  step 0, row 15, element 107. The gate is 0xc2c2 (-97.0); the committed value is 0x8000, v1 gives 0x8010 and v2 gives
  0x8000. That is the SiluMul_v1 Definition gap, not packing.
- **That failure pack-stopped qwen3-06b at 15:36:59Z** (`stopped-models.json`, reason "the replay task failed (rc 12)").
  As a statement about packing, the stop is false. It costs little: of qwen3-06b's 11 unsubmitted feeder items, 2 are
  packable (TP1, batch ≤ 8), and those now run unpacked. Lifting the stop is circuits' call (`dispatch.py pack-lift
  qwen3-06b`). Another qwen3-06b replay that hits the same SiluMul edge would stop the model again.
- **gm005-pk2 and gm008-pk2 ran unpacked because their Builds were offloaded to node 2.** `n2_build.sh` submits the
  Commit with `dispatch.py submit config-run KEY --task 1`, and the `submit` verb calls `submit()` directly, bypassing
  `route()` and therefore `packable()`. Every Build that node 2 takes loses packing for its Commit. One fix is for that
  line to go through `route()` (for example, a `--route` flag on `submit`, or `spool`, falling back to `submit` when the
  item isn't packable). That script is infra's.
- **Still open:** a packed comparison for r1-distill-qwen-15b and qwen25-3b. It needs `-pk3` twins whose Builds stay on
  node 1, or the `n2_build.sh` fix.
