---
id: 20260930T2153Z-report-ranking-and-split
campaign: verity
lane: proofs-n2-guest
kind: report
status: open
repo: danielreuter/verity
origin: proofs-n2-guest (bc-c951b059), worker of @proofs (bc-8416bc72)
---

# proofs-n2-guest: the Llama-3.2-1B whole-row ranking and the node-1/node-2 split; node 2's rows add up to about 14 GPU-h, not 60

**Row:** `llama32-1b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__greedy__bi-eager`. The shapes come from node 1's
`/workspace/jobs/sweep2/<row>/{shapes.tsv,counts.json}` (cut `r20260930-172942-e0ce`), ranked by `row_units`, largest first, ties by
digest. Each shape is sized with backend-sweep-2's per-shape extrapolation: statements = ceil(row units / (n × coordinates per
instance)), times the one-statement record's e2e seconds (`/workspace/jobs/runs/*/out/**/results.jsonl`, median of 3). `#` is the
line of `shapes.tsv`.

**Only 2 of the 2,578 shapes are GEMM coordinates:** K=2048 (#1551) and K=8192 (#1936). So "ranks 1–3 of the rest" reads as ranks
over every shape, and the table uses that reading. **proofs-rows, check that it matches yours.**

| Rank | # | Shape | Definition | Row units | Statements | s a statement | GPU-h est. | Owner |
|---|---|---|---|---|---|---|---|---|
| 0 | 1551 | f1e4d147 | GemmCoordinate K=2048 | 412,434,432 | 50,346 | 1.017 | 14.2 | node 1, backend-sweep-2 (b): excluded |
| 1 | 0 | 40e34040 | AttentionHead T=1 | 339,443,712 | 331,488 | 0.065 | 6.0 | node 1, proofs-rows |
| 2 | 23 | ef3a5a77 | AttentionHead T=2 | 339,443,200 | 331,488 | 0.083 | 7.7 | node 1, proofs-rows |
| 3 | 10 | 191fb6e5 | AttentionHead T=2 | 339,439,104 | 331,484 | 0.311 | 28.6 | node 1, proofs-rows |
| 4 | 2 | 78199905 | SiluMulBf16 | 150,863,872 | 147,328 | 0.079 | 3.22 | **node 2** |
| 5 | 21 | b044e943 | RMSNormFusedCuda | 75,431,936 | 73,664 | 0.091 | 1.85 | **node 2** |
| 6 | 6 | e66c4b79 | RMSNormFusedCuda | 75,431,936 | 73,664 | 0.066 | 1.35 | **node 2** |
| 7 | 1936 | 7a1fc1a9 | GemmCoordinate K=8192 | 37,715,968 | not yet (untiled; ~36,832 if n=1024) | not yet | ~5 (guess) | **node 2**: its gate measures it |
| 8 | 3 | 9254fd7a | RopeOut | 23,572,480 | 23,020 | 0.127 | 0.81 | **node 2** |
| 9 | 4 | a5eb3fa1 | RopeOutAdd | 23,572,480 | 23,020 | 0.094 | 0.60 | **node 2** |
| 10 | 12 | f3f5b321 | AttentionHead T=130 | 2,416,128 | 2,360 | 0.082 | 0.05 | **node 2** |
| 11 | 20 | ad3cddec | RMSNormTriton | 2,357,248 | 2,302 | 0.088 | 0.06 | **node 2** |
| 12 | 7 | e92624aa | GatherBf16x128256 | 2,357,248 | none | none | none | excluded: broke at staging on node 1 (a 2^28-bit block, the limit is 2^26) |
| 13 | 15 | 6f199b21 | AttentionHead T=129 | 2,355,200 | 2,300 | 0.310 | 0.20 | **node 2** |
| 14 | 1546 | 7924a330 | AttentionHead T=257 | 2,289,664 | not yet | not yet | ~0.2 | **node 2** |
| 15 | 9 | e0dee35f | AttentionHead T=129 | 458,752 | 448 | 0.063 | 0.01 | **node 2** |
| 16 | 5 | cf92ed14 | AttentionHead T=257 | 393,216 | 384 | 0.063 | 0.01 | **node 2** |
| 17 | 1549 | d8b005f3 | AttentionHead T=129 | 65,536 | not yet | not yet | ~0 | **node 2** |
| 18+ | | | 2,560 shapes, ≤ 36,832 row units each | | ≤ 36 each | | | not whole-row: the shape sweep covers them |

**The split:**
- **Node 1:** 42.3 GPU-h (ranks 1–3), plus (b)'s 14.2.
- **Node 2:** 8.16 GPU-h measured, plus about 5 for K=8192, the gates' selftests and about 1 min of start-up a chunk. That's about
  14 GPU-h. Llama-3.2-1B doesn't have ~60 GPU-h beyond rank 3.

**Closing the ~45 GPU-h gap is @proofs's call.** Rank 3 (#10, 28.6 GPU-h) could move to node 2 if proofs-rows agrees, or node 2
could take the next models backend-sweep-2 has cut (smollm2-135m and smollm2-360m). I've done neither.

## How it runs on node 2 (`/workspace/verity-guest/wholerow/`; scripts in `tools/`, copies byte for byte)

- **Inputs:**
  - `tree/`: node 1's backend-sweep-2 tree, `70e99f57e`, clean.
  - `flock/flock-circuit/bin-4d568a3cb558b005-g1-sm120/`: flock-circuit `e484a335…`, the binary #1551's gate used.
  - A uv venv with numpy 2.5.3 and blake3 1.0.10.
  - `sweep2/<row>/counts.json`.
  - No weights: the lanes are synthetic. The build key is `4d568a3cb558b005` on node 2 too, and `ldd` resolves node 2's
    `libcudart.so.13`, so nothing is rebuilt.
- **Jobs (`job.sh`):** they reuse `73-sweep-shape.sh` as (b) does.
  - Stage: `MODE=stage`, gpus=0 cpus=16, with a stub `nvidia-smi`.
  - Chunk: `MODE=shape RUNS=<count> WARM=1 FLOCK_KEEP_SESSIONS=3`, gpus=1 cpus=16.
  - Each loopback verifier gets a free port. The fill runner runs every GPU job on the host network, where a fixed port 7710
    would collide.
  - `verify.py` writes `done/<id>.json` only when:
    - rc is 0;
    - `<count>` statements were timed and all were accepted;
    - the prover is the pinned binary;
    - for a gate, every selftest passed, including `gpu_paths_agree` and `gpu_proofs_match_cpu`.
  - A job whose done record exists exits 0. Every attempt starts in a fresh run dir.
- **Chunk size:** about 10 min of statements, not 2,500 (about 40 min). The fill runner caps GPU jobs at `max_min` 30 (only Verity
  CPU jobs get 360), so a 40-min chunk would be stopped and requeued forever. Windows stop GPU fill jobs about 1–2 times an hour,
  and a stopped chunk restarts from scratch.
- **Staging:**
  - Six rows staged in ≤ 8 s on node 1 (#2, #21, #6, #3, #4, #20). Their gates stage inline and fill the stage cache.
  - The other seven wait for a CPU stage job. All six Verity CPU slots were held by kueue-fold Builds at 2:52 PM PDT.
- **The gate:**
  - Chunk r0 of each row runs the GPU selftest over about 240 s of statements (20 when a shape has no record).
  - The rest of the row is queued only once r0 is verified.
  - A script in `fill/failed/` stops its row.
- **Refill loop (`refill.py`, `loop.sh`):**
  - It runs in tmux `proofs-n2-guest` on node 2.
  - It queues stage jobs and gates as soon as each is ready. Other chunks are topped up to 12 whenever fewer than 8 are queued.
  - Every 5 min it logs PT time, queued, running, done, failed, GPU-h used (the runner's exit events) and GPU-h ready to
    `/workspace/verity-guest/feed.log`.
  - To stop it: `touch /workspace/verity-guest/wholerow/STOP`. The loop then exits, and queued scripts exit 0 at once.
- **Custody:** node 2 has no `research` CLI.
  - The loop rsyncs each verified job to vy-nebius-1 `/workspace/jobs/proofs-n2-guest/{runs,done}/`, outside windows.
  - From an agent VM, `tools/custody.sh` puts each one as `run-record/v1` with `--preserve` and lists it in node 1's `custody.tsv`.
- **Labels:** every record says *measurement on #554's draft prover key (4d568a3cb558b005); the 4×4 tile statement isn't reviewed
  yet; not a verified table row*. It also gives the row, the shape, the chunk range, the node (vy-nebius-2) and the GPU (the
  `CUDA_VISIBLE_DEVICES` index, the lease UUID and the name).
- **When the gates will run:** at 2:52 PM PDT, PoUW held all 8 GPUs, with 12–22 PoUW GPU jobs queued. Verity GPU jobs start only
  when that queue is empty and 2 or more GPUs are free, so the gates may not run until the overnight gap.
