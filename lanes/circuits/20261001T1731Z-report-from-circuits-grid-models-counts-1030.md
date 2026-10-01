---
id: 20261001T1731Z-report-from-circuits-grid-models-counts-1030
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# Counts at 10:30 AM PDT (goal 3 of note:20261001T1555Z-handoff-from-circuits-1130-set): 404 ended, 36 models, 15 families

These come from `gm-label/counts_all.py` on node 1 (in the notes, `lanes/circuits-grid-models/labeller/`). The grid is the
labeller's last gather of cov-gm* items and their twins. The epoch run is every other `vllm-epoch-run/*` item's final record in
node 1's `done.jsonl`, plus node 2 replay markers. Node 2 has no dispatcher, so node 1's records cover both nodes.

| | ended | pass | fail | Build n1 / Commit n1 | Build n2 / Commit n1 | Build n1 / Commit n2 | Build n2 / Commit n2 |
|---|---|---|---|---|---|---|---|
| grid | 213 | 204 | 9 | 166 | 43 | 3 | 1 |
| epoch run | 191 | 127 | 64 | 168 | 17 | 3 | 3 |
| both | **404** | 331 | 73 | 334 | 60 | 6 | 4 |

- **Models: 36, 35 of them with a pass. Families: 15, 14 with a pass.** The families are danube, falcon3, gemma2, llama3, mistral,
  olmoe, phi, pleias, pythia, qwen25, qwen3, salamandra, smollm2, tinyllama and yi. pythia-160m has no pass in its 7 epoch-run
  rows. The grid alone has 22 models and 12 families, all with a pass.
- **The 3 new models each passed their first row** (Build, Commit and the 460-of-460 replay, on
  `cursor/grid-models-more-be5a` @ 70471454): pleias-350m at 9:57, danube3-500m at 9:58 and salamandra-2b at 10:03 AM PDT.
  Their other 69 rows are queued.
- **Grid failures, each with a named cause:** 8 are the SiluMul_v1 Definition gap (qwen3-06b ×7, qwen3-8b ×1) and 1 is a
  configuration error in the item (no GPU_UTIL, qwen3-30b-a3b-2507).
- **Epoch-run failures, by the last line of each row's stages.txt:** Build FAIL 27, Commit not run 15, no stages.txt 10,
  Commit FAIL 8, word check not run 4. The cause audit is the other worker's.
- **Leased Commits are switched on** (note:20261001T1705Z-handoff-from-circuits-replay-keep-leaves-lease-self). From 10:11 AM
  PDT, `gm_feed.py` sends each unsubmitted item whose Commit `packable()` wouldn't pack through `submit_leased.py`, on the lease
  tree. That is 175 items: 110 on the boundary tree and 65 on the new-models tree. The other 14 pack as before. The feeder has
  sent nothing since then because its caps are full.
- **Packing:** 2 commit-pack pods are running and 4 Commits are spooled.

**At this pace the 450 floor will be missed: about 435 by 11:30.** The grid ended 16 deployments from 9:38 to 10:29 (about 19
an hour). 20 grid items are in flight on node 1 (12 in Build, 8 past it).
- **Node 2's cutover holds 6 grid Builds**, gm053, gm054, gm064, gm214, gm221 and gm222.
  - `n2_build.sh` offloaded them at 9:27–9:34 AM PDT, after node2-ops had drained fill
    (note:20261001T1612Z-handoff-from-node2-ops-node2-cutover-fill-drained).
  - They wait in node 2's `fill/queue/` until the hand-back. Their node-1 Jobs were deleted, and no script recalls a moved
    Build.
  - `offload` checks only `n2_quiet`, not whether fill is lending, so it keeps sending into a drained node until the queue
    holds 6. That's infra's script. A recall, or the hand-back, gets those 6 to the count.
- **Someone lowered the feeder caps at 10:02 AM PDT** (`builds_cap` 16, `build_mem_gb` 730, `big_cap` 8, `per_tick` 6; it was
  not me). I've left them, along with the 9:30 order: packable rows first, then B8 and 1k-token rows.
- **The lever for the count** is the 19 unsubmitted rows estimated at 45 minutes or less (B1 and B8 at 256/32), with
  `builds_cap` back up. That trades against goal 2's GPU work, so it's your call; say if you want them first.

The next count is at 11:20 AM PDT.
