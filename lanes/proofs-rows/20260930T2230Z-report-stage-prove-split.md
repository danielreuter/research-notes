---
id: 20260930T2230Z-report-stage-prove-split
campaign: verity
lane: proofs-rows
kind: report
status: open
repo: danielreuter/verity
origin: proofs-rows (bc-25950a06), worker of @proofs (bc-8416bc72)
---

CHECKPOINT afb4bd35 (22:25Z) [open] split built; CPU stage byte-identical to GPU stage, saves 201 s GPU per cache miss; its one GPU chunk split-prove-f1e4d147-m1 queued in backfill since 3:13 PM PDT; no feeder (note:20260930T2230Z-report-stage-prove-split)
# proofs-rows: the stage/prove split works and stages byte-identical statements on CPU; its one GPU chunk is queued in backfill

Replies to `note:20260930T2142Z-handoff-from-proofs-replan-stop-rows-do-stage-split`,
`note:20260930T2147Z-handoff-from-proofs-gumbel-unit-reporting` and `note:20260930T2153Z-handoff-from-proofs-name-the-question`.
Question: "does staging a chunk in a CPU-only job cut GPU-held minutes, with byte-identical proofs?"

**1. Feeder.** None was started: no tmux `proofs-rows-feed`, and no next-coordinate items. Nothing to stop. The brief's scope
doesn't hold anyway: Llama-3.2-1B's only GEMM coordinate after K=2048 is K=8192 (#1936), which node 2 now covers.

**2. The split.** `tools/73-sweep-shape.sh` is backend-sweep-2's at `70e99f57`, plus:
- `MODE=shape STAGE_ONLY=1`: `MODE=stage`'s exact statement on CPU. It writes a marker with the files' sha256, via `tools/stage_mark.py`.
- `REQUIRE_STAGED=1`: the GPU job exits 3 before the prover when there's no marker, and after it when the job staged the
  shape itself or proved other bytes.
- The split's SUMMARY fields.

Recipes: `note:20260930T2225Z-handoff-from-proofs-rows-stage-prove-split-recipe` (node 2) and
`note:20260930T2225Z-handoff-from-proofs-rows-stage-prove-split` (sweep2-feed).

**3. Measured** (K=2048, #1551, node 1, prover `e484a335…`; driver `tools/split_measure.py`, tmux `proofs-rows-split`):

| | GPU held before the prove | GPU held per statement | Statement files |
|---|---|---|---|
| current way, cache missed (r0, `r20260930-210621-2a46`) | 231 s | 8.23 s | reference |
| current way, cache hit (r5000, `r20260930-214647-a70b`) | 30 s | 8.40 s | r0's |
| split: CPU stage job (`r20260930-220702-2e96`, gpus 0) | 0 | none | identical to r0's (sha256 of all three) |
| split: its GPU chunk (`split-prove-f1e4d147-m1`, 10 statements) | queued | queued | queued |

- **The CPU job:** 198 s of staging on 2 CPUs, 8.8 GB peak, 227 s job. It wrote the same cache key as r0's GPU job (`cdef5bd8…`).
- **Saving:** 201 s (3.4 GPU-min) on each chunk that would miss the cache (every tree change), and 0 on a hit.
- **The bigger cost:** the loopback verifier's round (about 6.5 s of `wait_s`) runs in series in the GPU job, and the prove is
  1.02 s. The K=2048 row is therefore about 115–117 GPU-held hours, not 14.2.
- **The GPU chunk** (backfill) has waited since 3:13 PM PDT. All 8 GPUs are in use (`deployments-gpu` 5 of 5, `provers` 3 of 3),
  with 16 `deployments-gpu`, 2 `provers` and 1 earlier backfill workload ahead. When it runs, the driver writes
  `/workspace/jobs/proofs-rows/measure/split-m1.json`. It holds GPU-held seconds, before-prove seconds and the statement digest
  against r0's (`2b7bd0d9…`).
- **Withdrawn:** I had also queued a current-way GPU chunk, `current-f1e4d147-m1`, before reading Daniel's 2:53 PM PDT rule. I
  deleted its Job at 3:14 PM PDT, before admission. So `log.jsonl` shows its submit with no end.

**4. Gumbel.** In `MODE=sampled`, the SUMMARY lists `sampled_units`, `units_proved`, `units_not_proved`, `units_excluded` (name and
why) and `fully_provable`. Tested on the b8 top-p deployment's draw, with synthetic results. The coordinator's recipe, with the
greedy `TokenSelect` caveat: `note:20260930T2225Z-handoff-from-proofs-rows-gumbel-unit-reporting`.

**Labels:** `label`, `question` (off-vocab: `note:proofs-rows/20260930T2230Z-friction-question-label-not-in-vocab`) and `note` on
the stage run. The GPU chunk's run gets the same once it exists.

**Node 1 state:**
- `/workspace/jobs/proofs-rows/`:
  - `tools/` (73 at `d349d1e2`, the measured version; the notes copy adds only `MODE=sampled`);
  - `flock/` (copies of the pinned binaries, uv, and its own venv);
  - `cache-a/` (empty, unused), `cache-b/`, `sweep/`, `summaries/` and `measure/`.
- `/workspace/jobs/ready/proofs-rows/` (empty); `/workspace/research/trees/proofs-rows/` (the tree).

**To stop:** `tmux kill-session -t proofs-rows-split`, then `kubectl delete job nd-proofs-rows-c38abf8279-prover-b-0` (my own).
