---
id: 20261001T1516Z-finding-build-mem-trim
campaign: overnight-sep30
lane: circuits-grid-models
kind: finding
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# Build memory trimmed (8:16 AM PDT): 91 of 215 unsubmitted items, 16,340 GB of Build requests down to 12,574 GB

This answers item 2 of circuits' 7:55 AM PDT follow-up. The mapping, the leave-one-out check and the script are art:4c0352b969bcb8eec499ac39c25ced14315442fcf76c0c84432a77b8ac970222.

**What changed.**

- Node 1's `/workspace/jobs/gm-feed/items.json` at 15:16:00Z: only `item.resources.build.memory`, only for items `log.jsonl` doesn't name, and each only lowered. A diff against the backup confirms all three.
- Backup: `items.bak-1516Z.json`. Rollback: `cp items.bak-1516Z.json items.json` (the feeder re-reads it every tick).
- The script is `feeder/trim_build_mem.py`. Its dry run prints the same mapping; `--validate` runs the leave-one-out check.

**What a request is.** The dispatcher sets the memory request only, with no limit, and nothing in the Build reserves memory from it (`gpu-lease --mem-gb 0`). A low request can't OOM-kill a Build; it changes only what Kueue books against `deployments-cpu`.

**Measured peaks.** A Build's peak is its run's cgroup `memory.peak` (`kernel_memory_peak_bytes` in `/workspace/jobs/runs/<run>/failure.json`). There are 147 of them, from 2.7 to 91 GB.

A class is (model, TP, batch, 256/32 or 1024/128, kind), and the kind is one of:
- greedy;
- stoch, the sampler at the default MAX_GATES;
- stoch-1unit, with `VERITY_QWORD_MAX_GATES` raised. These Builds are the large ones, up to 91 GB.

Within a class the tree (models, plan or boundary) made no consistent difference.

**The rule.** No unsubmitted item is in a measured class: all of them are larger shapes than anything run so far. So each estimate starts from the same model's nearest measured classes of the same TP and kind, at smaller shapes. It multiplies by the largest growth seen across models for each step:

| Step | Factor |
| --- | --- |
| 256/32 to 1024/128 at B1 | 3.73 |
| 256/32 to 1024/128 at B8 (also used for B16 and B32) | 2.32 |
| Batch 1 to 8 | 3.01 |
| Batch 8 to 16 | 1.54 |
| Batch 16 to 32 | 1.45 |
| stoch over greedy at the same shape | 1.14 |
| stoch-1unit 256/32 to 1024/128 | 2.73 |

The batch factors come from 256/32 runs and are also used at 1024/128. That is conservative: the batch growth measured at 1024/128 (B1 to B8, 1.28–1.38) is smaller.

- New request: max(16, ceil(1.5 x the largest of those estimates)), applied only when it is lower than the current request.
- A class with no measured base keeps its request: TP2 (skipped by `skip_tp`), gemma2 (skipped by circuits' ruling), and qwen3-30b's stoch-1unit.

**Check.** Leave one out: each of the 67 measured classes that has a base was hidden from the bases and the factors, then estimated from the rest. None of the 67 measured peaks exceeds the request the rule would have set. The closest is qwen3-8b B8 256 greedy, measured at 16.9 GB against 22.

**Watch.** falcon3-1b B1 1024 stoch-1unit peaked at 91.4 GB against a 91 GB request, and the unsubmitted falcon3-7b row of that class is still at 91. It isn't trimmed, and it isn't raised either, because there is no limit to hit.

**The classes that changed** (old and new requests in GB):

| Model | Class | Items | Old | New | Estimate (base x factor) |
| --- | --- | --- | --- | --- | --- |
| falcon3_1b | B16 1024/128 greedy | 1 | 80 | 77 | 50.9 (b1/1024/greedy 11.0 x 4.63) |
| falcon3_1b | B32 256/32 greedy | 1 | 96 | 25 | 16.3 (b16/256/greedy 11.2 x 1.45) |
| falcon3_1b | B32 1024/128 greedy | 1 | 128 | 111 | 73.9 (b1/1024/greedy 11.0 x 6.73) |
| falcon3_1b | B32 256/32 stoch | 2 | 96 | 23 | 15.0 (b16/256/stoch 10.4 x 1.45) |
| falcon3_1b | B32 1024/128 stoch | 2 | 128 | 127 | 84.1 (b1/1024/greedy 11.0 x 7.66) |
| falcon3_7b | B8 1024/128 stoch | 2 | 48 | 16 | 10.4 (b8/256/stoch 4.5 x 2.32) |
| llama31_8b | B1 1024/128 greedy | 1 | 48 | 16 | 10.1 (b1/256/greedy 2.7 x 3.73) |
| llama31_8b | B8 1024/128 greedy | 1 | 48 | 23 | 15.0 (b8/256/greedy 6.5 x 2.32) |
| llama31_8b | B8 1024/128 stoch | 2 | 48 | 17 | 10.8 (b8/256/stoch 4.7 x 2.32) |
| llama32_3b | B16 256/32 greedy | 1 | 64 | 17 | 11.1 (b8/256/greedy 7.2 x 1.54) |
| llama32_3b | B32 256/32 greedy | 1 | 96 | 25 | 16.1 (b8/256/greedy 7.2 x 2.24) |
| llama32_3b | B16 256/32 stoch | 2 | 64 | 18 | 11.7 (b8/256/stoch 7.6 x 1.54) |
| llama32_3b | B32 256/32 stoch | 2 | 96 | 26 | 16.9 (b8/256/stoch 7.6 x 2.24) |
| mistral7b_instruct | B8 1024/128 stoch | 2 | 48 | 37 | 24.6 (b8/256/stoch 10.6 x 2.32) |
| mistral7b_instruct | B1 1024/128 stoch-1unit | 2 | 48 | 18 | 11.6 (b1/256/stoch-1unit 4.2 x 2.73) |
| olmoe_0125_instruct | B1 1024/128 greedy | 1 | 48 | 16 | 10.4 (b1/256/greedy 2.8 x 3.73) |
| olmoe_0125_instruct | B8 1024/128 greedy | 1 | 48 | 23 | 14.9 (b8/256/greedy 6.4 x 2.32) |
| olmoe_0125_instruct | B8 1024/128 stoch | 2 | 48 | 26 | 16.8 (b8/256/stoch 7.2 x 2.32) |
| olmoe_0125_instruct | B1 1024/128 stoch-1unit | 2 | 48 | 32 | 21.1 (b1/256/stoch-1unit 7.7 x 2.73) |
| qwen25_05b_instruct | B16 1024/128 greedy | 1 | 80 | 46 | 30.3 (b16/256/greedy 13.1 x 2.32) |
| qwen25_05b_instruct | B32 1024/128 greedy | 1 | 128 | 53 | 34.8 (b8/1024/greedy 15.6 x 2.24) |
| qwen25_05b_instruct | B8 1024/128 stoch | 2 | 48 | 27 | 17.7 (b8/1024/greedy 15.6 x 1.14) |
| qwen25_05b_instruct | B16 1024/128 stoch | 2 | 80 | 41 | 27.3 (b8/1024/greedy 15.6 x 1.75) |
| qwen25_05b_instruct | B32 1024/128 stoch | 2 | 128 | 60 | 39.7 (b8/1024/greedy 15.6 x 2.54) |
| qwen25_3b | B16 256/32 greedy | 1 | 64 | 23 | 15.1 (b8/256/greedy 9.8 x 1.54) |
| qwen25_3b | B32 256/32 greedy | 1 | 96 | 33 | 21.9 (b8/256/greedy 9.8 x 2.24) |
| qwen25_3b | B16 256/32 stoch | 2 | 64 | 20 | 13.0 (b8/256/stoch 8.5 x 1.54) |
| qwen25_3b | B32 256/32 stoch | 2 | 96 | 29 | 18.9 (b8/256/stoch 8.5 x 2.24) |
| qwen25_coder_15b | B32 256/32 greedy | 1 | 96 | 24 | 15.4 (b16/256/greedy 10.6 x 1.45) |
| qwen25_coder_15b | B32 256/32 stoch | 2 | 96 | 23 | 14.9 (b16/256/stoch 10.2 x 1.45) |
| qwen3_06b | B16 1024/128 greedy | 1 | 80 | 65 | 42.8 (b8/1024/greedy 27.8 x 1.54) |
| qwen3_06b | B32 256/32 greedy | 1 | 96 | 36 | 24.0 (b16/256/greedy 16.5 x 1.45) |
| qwen3_06b | B32 1024/128 greedy | 1 | 128 | 94 | 62.2 (b8/1024/greedy 27.8 x 2.24) |
| qwen3_06b | B16 1024/128 stoch | 2 | 80 | 74 | 48.8 (b8/1024/greedy 27.8 x 1.75) |
| qwen3_06b | B32 256/32 stoch | 2 | 96 | 33 | 21.5 (b16/256/stoch 14.8 x 1.45) |
| qwen3_06b | B32 1024/128 stoch | 2 | 128 | 107 | 70.8 (b8/1024/greedy 27.8 x 2.54) |
| qwen3_06b | B1 1024/128 stoch-1unit | 1 | 102 | 53 | 34.9 (b1/256/stoch-1unit 12.8 x 2.73) |
| qwen3_17b | B16 256/32 greedy | 1 | 64 | 22 | 14.4 (b8/256/greedy 9.4 x 1.54) |
| qwen3_17b | B32 256/32 greedy | 1 | 96 | 32 | 21.0 (b8/256/greedy 9.4 x 2.24) |
| qwen3_17b | B16 256/32 stoch | 2 | 64 | 25 | 16.4 (b8/256/stoch 10.7 x 1.54) |
| qwen3_17b | B32 256/32 stoch | 2 | 96 | 36 | 23.9 (b8/256/stoch 10.7 x 2.24) |
| qwen3_30b_a3b_2507 | B8 1024/128 greedy | 1 | 48 | 40 | 26.3 (b8/256/greedy 11.3 x 2.32) |
| qwen3_30b_a3b_2507 | B8 256/32 stoch | 1 | 24 | 20 | 12.9 (b8/256/greedy 11.3 x 1.14) |
| qwen3_30b_a3b_2507 | B8 1024/128 stoch | 2 | 48 | 45 | 29.9 (b8/256/greedy 11.3 x 2.64) |
| qwen3_8b | B1 1024/128 greedy | 1 | 48 | 32 | 20.9 (b1/256/greedy 5.6 x 3.73) |
| qwen3_8b | B1 1024/128 stoch-1unit | 2 | 102 | 58 | 38.6 (b1/256/stoch-1unit 14.1 x 2.73) |
| r1_distill_llama_8b | B8 1024/128 stoch | 2 | 48 | 37 | 24.7 (b8/256/stoch 10.6 x 2.32) |
| r1_distill_llama_8b | B1 1024/128 stoch-1unit | 2 | 86 | 67 | 44.3 (b1/256/stoch-1unit 16.2 x 2.73) |
| r1_distill_qwen_15b | B16 256/32 greedy | 1 | 64 | 19 | 12.6 (b8/256/greedy 8.2 x 1.54) |
| r1_distill_qwen_15b | B32 256/32 greedy | 1 | 96 | 28 | 18.2 (b8/256/greedy 8.2 x 2.24) |
| r1_distill_qwen_15b | B16 256/32 stoch | 2 | 64 | 17 | 11.3 (b8/256/stoch 7.3 x 1.54) |
| r1_distill_qwen_15b | B32 256/32 stoch | 2 | 96 | 25 | 16.4 (b8/256/stoch 7.3 x 2.24) |
| smol17b | B16 256/32 greedy | 1 | 64 | 19 | 12.3 (b8/256/greedy 8.0 x 1.54) |
| smol17b | B32 256/32 greedy | 1 | 96 | 27 | 17.8 (b8/256/greedy 8.0 x 2.24) |
| smol17b | B16 256/32 stoch | 2 | 64 | 19 | 12.4 (b8/256/stoch 8.1 x 1.54) |
| smol17b | B32 256/32 stoch | 2 | 96 | 28 | 18.1 (b8/256/stoch 8.1 x 2.24) |
| yi15_6b | B16 256/32 greedy | 1 | 64 | 17 | 11.0 (b8/256/greedy 7.1 x 1.54) |
| yi15_6b | B32 256/32 greedy | 1 | 96 | 24 | 16.0 (b8/256/greedy 7.1 x 2.24) |
| yi15_6b | B16 256/32 stoch | 2 | 64 | 17 | 11.0 (b8/256/stoch 7.2 x 1.54) |
| yi15_6b | B32 256/32 stoch | 2 | 96 | 24 | 16.0 (b8/256/stoch 7.2 x 2.24) |

## Afterwards (8:55 AM PDT)

- **The trim holds so far.** Seven trimmed items have run since 15:16Z, all of them B16 256/32 (gm241–247: qwen3-17b,
  r1-distill-qwen-15b and smollm2-17b). They peaked at 4.0–7.8 GB against new requests of 17–25 GB, at most 0.32 of the
  request. No Build has failed since the trim: 19 Builds, 21 Commits and 18 replays succeeded. The one failure was
  gm001-pk2's replay, the known SiluMul_v1 edge.
- **Builds no longer bind the quota; replays do.** At 15:47Z, `deployments-cpu` held 12 Builds (451 GB, at the feeder's
  `builds_cap` of 12, under its 600 GB `build_mem_gb`) and 3 replays (192 GB). Four more replays were pending at 64 GB each,
  and Kueue reported "insufficient unused quota for memory, 54164971008 more needed".
- **Replay requests stay as they are.** The 64 GB is config-run's template default, and `items.json`
  `resources.replay.memory` would override it (`dispatch.py` `task_resources`). Across the 171 gm replays that recorded a
  peak, it ranged from 4 to 87 GB: the median is 20.7 GB at B1 and 26.3 GB at B8. Four measured classes already exceed
  64 GB: qwen3-06b B8 1024 greedy at 87.0, yi15-6b B1 1024 greedy at 81.8, yi15-6b B1 1024 stoch-1unit at 81.8, and
  qwen3-14b B8 256 stoch at 70.9. None of the 193 unsubmitted items shares a measured class, so a trim would rest wholly on
  extrapolation, against a request some classes already overrun. Taking 1.5 times each model's maximum instead would raise
  the remaining total from 11,008 to 13,456 GB. Neither rule is worth applying.
