---
id: 20261001T1355Z-finding-golden-twins-unpacked-all-match
campaign: overnight-sep30
lane: circuits-grid-models
kind: finding
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# Golden twins (6:55 AM PDT): all 9 match their base rows, but none packed, so the packing comparison is still open

This answers item 3 of `note:20261001T1158Z-handoff-from-circuits-refill-node2-pack-goldens`.

**Setup.**

- Each twin `cov-gmNNN-pk` has the same ROW and env as its base `cov-gmNNN`. It ran on `cursor-grid-plan-gm-827a` with its own sweep dir.
- All 9 were submitted at 12:55:20Z and admitted when the Hold lifted at 13:30Z. Their replays ended between 13:43 and 13:54Z.
- **None of them packed.** Each Commit went out as an ordinary Job in `deployments-gpu`. There was no `spool` event and no `packed` field on any of them.
- The cause: `PACK_MODELS` in node 1's `dispatch.py` (unchanged since 08:18Z) lists none of these 9 models, so `packable()` returns
  "model … is not on the packing list" (`note:20261001T1258Z-handoff-from-circuits-grid-models-twins-not-on-pack-models`).
- So these results show that the unpacked runs reproduce exactly. They say nothing yet about packing.

**What each comparison checks.** For each twin, `feeder/twin_compare.py` compares:

- `run_roots` from `commit/verdict.json`;
- the binding map digest from `commit/binding_map_p0.json`;
- `commit_pass`, after the deferred replay;
- the `stages.txt` config line.

| Twin | Model | Packed | Run root | Binding map | Verdict (base / twin) |
| --- | --- | --- | --- | --- | --- |
| cov-gm002-pk | qwen25-05b-instruct | no | same `fe8b4fe99c4d476b` | same `ae4c3f13a430873b` | PASS 460/460 / PASS 460/460 |
| cov-gm003-pk | falcon3-1b | no | same `a0ce6b1b0d3dc40e` | same `69ae532fb90965fc` | PASS / PASS |
| cov-gm004-pk | qwen25-coder-15b | no | same `a739323cd9ea2e0e` | same `e4f5fe01400ef418` | PASS / PASS |
| cov-gm005-pk | r1-distill-qwen-15b | no | same `82ce5ff0a2c960d4` | same `1c4f631b2ca9b914` | PASS / PASS |
| cov-gm006-pk | qwen3-17b | no | same `50e98ba4c4d95be9` | same `524d984863acda1d` | PASS / PASS |
| cov-gm007-pk | smollm2-17b | no | same `7d4e930a6c606065` | same `5a9676098ec27b15` | PASS / PASS |
| cov-gm008-pk | qwen25-3b | no | same `de4d8ecd42eb22fa` | same `fb53d179cc0e160f` | PASS / PASS |
| cov-gm009-pk | llama32-3b | no | same `03abfcb391217db9` | same `458f2778a27f69a4` | PASS / PASS |
| cov-gm001-pk | qwen3-06b | no | same `81b63e73e8f08afa` | same `7850ffdc06a13bdb` | FAIL `sampled_replay` / FAIL `sampled_replay` |

**qwen3-06b.** Its twin fails the same way its base does, on the same word:

- `labeller/silu_check.py` finds one mismatch in both runs: `model.layers.27.mlp.act_fn` r0 step 0 row 15, element 107.
- At that element, gate is `0xc2c2` (-97.0) and up is `0x4183`.
- The committed value is `0x8000` (-0). SiluMulBf16_v1 gives `0x8010`; the quarantined v2 gives `0x8000`.
- Named cause: a Definition gap, SiluMul_v1's expf-overflow edge. It isn't a Commit fault.

**Stop list:** no mismatch, so no model is stopped.

**Still to do:** the packing comparison itself. When infra adds these 9 models to `PACK_MODELS` and restarts the dispatcher, I'll
submit `cov-gmNNN-pk2` (same config) and compare it the same way.
