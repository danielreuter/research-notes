---
cursor:
  subagentId: "bc-6da61042-1b56-5e51-964f-9ae86e909da4"
---

# Harness helper (second): verity baselines, BenchArm and step groups, host seconds

Branch `cursor/harness-helper-cd3d`, head `dd23c0c36`, on top of #491's `80bff34cc` (#583's `dump` as the one
poisoning path). The harness worker's withdrawn v0.5 (`9182e17d7`, `508c7b5ea`, merged in `e0fa1f0bb`) is reverted
(`d15f6bb05`). `verify.py` is byte-identical to #491's.

## Commits (`e22a2808f..dd23c0c36`)

| commit | what |
|---|---|
| `67096497d` | #570's `nvf4_plain.cu` and `mainloop_nvf4.cuh` at `025cc1f8`, byte-identical, under `benchmarks/pouw/nvfp4_sm120/` |
| `186c4c023` | task 3: the plain NVFP4 (#543) and FP8 (#570) GEMMs as registry baselines |
| `200897ad7` | task 2: `BenchArm` (`Arm` a deprecated alias) and phases named by the executor's step groups |
| `9114d4d59` | task 1: host seconds (`wall_s`) of every gate, negative control and shape stage |
| `598db8586` | merge of #491's head then (`--screen-only`, the SASS gate's semaphore skip) |
| `00c01c04a`, `25da5c492` | README: the `wall_s` paragraph and the screen-only shape's stages |
| `e0fa1f0bb` | merge of the worker's `508c7b5ea`; BenchArm and step groups become interface v0.6 |
| `a2da2b73c` | the twin item: `refs.py` (a process pool of the job's CPUs) and a `prefetch` hook before a flag set's gates |
| `d15f6bb05` | revert of `e0fa1f0bb` (`git revert -m 1`): the withdrawn v0.5 `transcript(dir, read)` replay goes |
| `27368133a` | merge of #491 at `80bff34cc`; the shape's `poison_dump` gets its own `wall_s` stage, `transcripts` |
| `207189436` | BenchArm and the step groups renumbered to interface v0.6, after #583's v0.5 |
| `dd23c0c36` | `prefetch` is an optional member of v0.6 in `arm.py`'s docstring; `check_arm` refuses a non-callable one |

## Task 3: verity baselines

- `cutlass_api.h`: a `phc_entry` takes either `query` (`const phc_args*`) or `query_fixed` (m, n, k), through two constexpr
  constructors, so `nvf4_plain.cu` compiles unchanged. `ph_cutlass_query_sched` returns -3, and `prepare_sched` refuses,
  when an order (swizzle, raster) is set on a fixed-order kernel.
- `cutlass_registry.cu`: one `entry()` table, CUTLASS entries under `#ifndef PH_NO_CUTLASS`, then `phc_table_nvf4` and
  `phc_table_fp8`.
- `build.sh`: `nvf4_plain` is a third unit; the key hashes it and the `.cuh` beside it. Because `cutlass_api.h` is in every
  CUTLASS object's key, the first build after this rebuilds all of them (about 4 min on node 2 at `JOBS=8`).
- `baselines.py`: source `verity` (`registry_source`), one tile order (`cutlass_tile` is None), and a per-call workspace of
  at least `PLAIN_WORKSPACE = 256` bytes: the kernels' CUtensorMaps live in the workspace from prepare to every launch,
  while the shared `lt_ws` is reused across calls. Every gate is unchanged and applies to them.
- Node 2: build `bab84c16` (art:01c2f39c1cfd79813f7b4843c030ac7a453a468ad52b3febaca72c1632daa382), SASS gate pass, and a
  one-GPU fill check of 8192³ NVFP4 and FP8 (art:4767f9591ab4edbe124519487840cfc44ff7b2110f5697934a510b78ceeefd0c) with
  every gate passing. The verity kernels win both families' tunes: NVFP4 `verity_nvf4_256x128_o_ew` 0.732 ms against
  `cutlass3x_nvfp4_256x128x128_coop` 0.792 ms (7.6%), FP8 `verity_fp8_256x128_o_ew` 1.433 ms against
  `lt13_fp8-e4m3_0_1_algo35_tile20` 1.458 ms (1.7%). Timed medians 0.7293 ms (NVFP4) and 1.4318 ms (FP8). The
  denominators drop, so every arm's slowdown against the baseline rises.

## Task 2: BenchArm and step groups (interface v0.6)

`arm.GROUPS = (a_tree, forming, gemm, cleanup, tile_hash, screen)`, `MOVABLE = {tile_hash, screen}`, `PARTS` folds them
into before (a_tree, forming), gemm (gemm, cleanup) and after (tile_hash, screen). The side-stream chain moves the movable
groups, which is `verity_pouw.serving`'s DEFERRED schedule (#567, `834f55e04`, not on main; the test compares when it
imports). v0.4's names (before, gemm, after) still work; mixing them with step groups is an `ArmError`, reported by the
chain as the arm's link error. `chain_report` gains `split_groups`, the groups timed under each split column.

## Task 1: operands outside the lease

The premise doesn't hold: operands are filled on the device (`k_fill`) and took 0.008 s of the check's shape. The lease
idles in the Pearl-C arm's gates, whose CPU twin takes about 6.8 to 8.5 s per 64×64 tile at k=8192 plus 2.4 s per job;
a headline run's 12 + 12 + 30 tiles come to 6 to 8 min. No operand cache was built. Instead each gate, negative control
and shape stage records `wall_s` (host seconds, injectable clock), so the next change can target the stage that costs.
The check's shape: baseline_gates 0.50 s, tune 0.96 s, warmup 1.88 s, timed 1.54 s.

## Task 4: bad_throttle

Nothing drops or rejects a timed item flagged `bad_throttle`. See the reply to the coordinator for the paragraph.

## The twin's tiles off the lease

- Harness `a2da2b73c` (this branch): `refs.py` holds `pool()`, a forked process pool with `cpus()` workers. `cpus()` is
  `OMP_NUM_THREADS` (the fill header's `cpus=`), limited to the CPUs the process may run on; with one CPU there is no
  pool. `refs.py` also holds `prefetch`, which syncs the device and then calls an optional arm hook,
  `prefetch(dev, call, shape, flags)`, on the flag set's gated calls. In `bench.py`, only `_arm_gate` changed (one
  `RF.prefetch` line) and one import was added. `arm.py` and `VERSION` are untouched. Tests are in `test_refs.py`.
- Arm `881eb05df` (branch `cursor/pearlc-twin-pool-9da4`, off `b6a919292`), for the Pearl-C sm120 worker to adopt:
  - `twin_submit` puts each sampled tile, `W.tile`, into the pool, keyed as before by (r0, c0, sha256 of the rows it
    reads and seed_A).
  - `twin_tiles` takes the results; if the pool is broken, it computes the tile inline. It compares exactly as before.
  - `prefetch` starts a call's tiles from the seeds on the device.
  - Without `refs`, the twin runs inline.
  - A slow test checks that pooled and inline give the same verdicts, including the corrupted tile.
- A step before the lease can't do this: the seeds come from the device's `root_A` and the beacon salt, and a chain gate
  reads the A that the chain derived.
- Measurement: node 2, `m32-n8192-k8192`, fill chunks at `OMP_NUM_THREADS=8`, on arm tree `9f1e33b16`. Both runs made the
  same 36 tile comparisons, every gate was ok, all 6 Pearl negatives were rejected, and both exited 0.

  | | arm_gates | chain_gates | gates total | lease |
  |---|---|---|---|---|
  | before, art:a31d6cfc448e9fc03112a77ca7786381eef89603b1934aeb7d22a7e3af81475c | 65.5 s | 163.5 s | 229.1 s | 4m28s |
  | after, art:8273a5fad7a89bf825168fe8470065e38973eeb85ae6c25ecb60135d21edbb16 | 34.2 s | 92.6 s | 126.7 s | 2m24s |

  Hash gates went from about 32 s to 15–18 s. Chain gates went from 14–19 s to about 9 s each.
- The remaining cost is the 10 chain gates, which run one at a time and each wait on their own 2 tiles. Two changes
  would bring this under a minute, and I made neither:
  - defer the twin's verdicts across the chain gates, which touches `chain.py`, the chain loop in `bench.py` and the
    gate API;
  - cache the B side, which is identical across set 0's gates, which touches `twin.py`.
- Ignore art:b2244168… and art:d9e1b327… (the same trees): their `arm` metadata is wrong.

## The broker, and #588 on #583's interface

- GitHub token broker adopted at 18:30Z, from `/workspace`: sha256 checked, `source = broker`, `git ls-remote` and `gh repo
  view` pass, and the PATH line is in `~/.bashrc`.
- `benchmarks/pouw` suite: 241 passed, 14 skipped, through `suites.py` (inputs guard). `tests/test_no_wall_clock.py`: 4
  passed.
- The arm branch `cursor/pearlc-twin-pool-9da4` needs no change: its `prefetch` is the v0.6 member as documented.

## Migration (Daniel, 6:55 PM PDT)

- My handoff is note:20261001T0213Z-handoff-from-6da61042-migration (`lanes/accounting/`). After it I start no new work,
  and nothing of mine is in flight.
- This VM's only copies of anything are now also in the store's `6b-harness-helper-handoff/` and on node 2's
  `/workspace/pouw/helper-cd3d/handoff/`.

## Files created or moved

- Migration: `6b-harness-helper-handoff/`, a new folder beside this file in the store, and node 2's
  `/workspace/pouw/helper-cd3d/handoff/`. Both hold the twin scripts, the fill-job scripts and the trees' git bundle.

- Repo: `benchmarks/pouw/nvfp4_sm120/nvf4_plain.cu`, `mainloop_nvf4.cuh`.
- Node 2: `/workspace/pouw/helper-cd3d/9114d4d59f6a/` (tree), its `gpu-check-9114d4d5/`, `sass-gate-bab84c16.json`, the
  shared build cache `/workspace/pouw/harness/build/bab84c1606a8553a`, three fill scripts now in `/workspace/pouw/fill/done/`
  (`helper-cd3d-build-186c4c02.sh`, `helper-cd3d-sassgate-200897ad.sh`, `helper-cd3d-gpucheck-9114d4d5.sh`).
- Local VM: `/tmp/harness-helper` (worktree), `/tmp/build-bab84c16`, `/tmp/gpu-check-9114d4d5`, `/tmp/bundle-491`,
  `/tmp/put-*.json`, refs `bundle491/*`.
- Twin item:
  - Repo: `benchmarks/pouw/harness/refs.py`, `benchmarks/pouw/tests/test_refs.py`, and the branch
    `cursor/pearlc-twin-pool-9da4`.
  - Node 2: `/workspace/pouw/helper-cd3d/twin-{14041d06c852,03df589b83fc}/` (trees) and
    `twin-{before,after}-m32-n8192-k8192/` (outputs); `/tmp/helper-cd3d-walls.py`; and
    `helper-cd3d-twin-{before,after}-m32.sh` in `/workspace/pouw/fill/done/`.
  - Local VM: `/tmp/pearlc-arm` and `/tmp/node2-tree` (worktrees; the second holds local commits `14041d06c`/`03df589b8`,
    which are not pushed), `/tmp/twin-profile/` and `/tmp/twin-wall/`.
- This file.
