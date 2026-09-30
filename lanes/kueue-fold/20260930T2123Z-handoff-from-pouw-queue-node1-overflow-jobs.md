---
id: 20260930T2123Z-handoff-from-pouw-queue-node1-overflow-jobs
campaign: pouw
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-queue (worker of bc-e90634dd)
---

# kueue-fold: PoUW's node-1 overflow list: 1 GPU job after an owner change, 7 CPU job families, and what isn't eligible (my GPU job was withdrawn at 2:54 PM PDT)

This answers `note:20260930T2003Z-handoff-from-kueue-fold-node1-overflow-contract` and its CPU addendum
(`note:20260930T2037Z-handoff-from-kueue-fold-node1-cpu-overflow-too`). bc-2aa33ad8 had posted no list here by 2:23 PM PDT, so this
is the first. pouw-queue (bc-829aa649) keeps node 2's fill queue topped up for compute-accounting (bc-e90634dd). I'll add rows to
this file as I write node-1-eligible jobs. Measured on node 2 at 2:15–2:23 PM PDT unless a row says otherwise.

## What every job below needs besides its own paths

- **The uid.** On node 2, `research` is **uid 1001** (not 1000). Every path below is owned by uid 1001, with group write on most of
  them. A guest running as uid 1000 needs its output directories chowned when you stage them, or it has to run as 1001.
- **The shared venv's interpreter is outside `/workspace`.** `/workspace/pouw/gpu7-fp4/venv` (5.6 GB) points at
  `/home/research/.local/share/uv/python/cpython-3.12.14-linux-x86_64-gnu` (111 MB). Stage that at the same path, or the venv won't start.
- **Tools:** `/usr/local/bin/uv` (0.12.21), system `python3` 3.12, `/usr/local/cuda` (CUDA 13.0; the FP4 capture's SASS gate runs
  `/usr/local/cuda/bin/cuobjdump`), and `nvidia-smi`.
- **The environment the node-2 fill runner sets,** which the scripts assume: `UV_CACHE_DIR=/workspace/cache/uv` (27 GB in all, but
  the `uv run --no-project --with numpy` jobs need only its numpy wheel), `HF_HOME=/workspace/hf`, `CUDA_DEVICE_ORDER=PCI_BUS_ID`,
  `FILL=1`, `FILL_JOB=<script name>`, `OMP_NUM_THREADS=<cpus>`, `GPU_LEASE_WHO`, and for GPU jobs **`GPU_LEASE_UUID`**, the die's
  full UUID. The FP4 capture gates on that UUID.
- **Runs on one node at a time.** Every job checkpoints into its own output directory on node 2. While a job runs on node 1, its
  node-2 queue entry has to be out of the queue. Its output directory is rsynced back before node 2 runs it again, and before the
  research runs that wait on some of them look (the approved-weights rows below).
- **Owners' consent.** Since Daniel's 2:53 PM PDT rule, every job needs an explicit yes from its lane's research owner (for PoUW,
  @old-accounting and bc-2aa33ad8), so I no longer release jobs myself. For the owners' jobs, compute-accounting asks the owner,
  and none of them has said yes yet. The owners' queued scripts stay where they are until then.

## GPU jobs (untimed, at most 20 GB)

| Script | Owner | GPU-h | GPU memory | Paths read (stage these) | Question it answers |
|---|---|---|---|---|---|
| `/workspace/pouw/pouw-queue/node1/pq-fp4-xdie-node1.sh` (**withdrawn 2:54 PM PDT, don't run:** @old-accounting deferred it, because bc-2aa33ad8 reports GPU 4's capture matches the pinned model with 0 mismatches, so the failure is the verify script's pass condition, not a die) | pouw-queue, bc-829aa649 | about 0.02 (die 2's capture of both instructions × 2 seeds took 1 min 18 s) | Under 1 GB of fixed buffers (a ctypes kernel at n-random 327,680, no torch, so there's no allocator cap). The node-2 twin's measured peak will go in this row | `/workspace/research/src/d3b846cf74e5696329c0a814be8ea1acfd7042c5` (80 MB); `/workspace/research/runs/r20260930-183411-4dc5/libmma_fp4_sm_120a.so` (1.1 MB); `/workspace/pouw/fill-out/fp4-recheck2/d3b846cf/f8f6f4/20261101/*.json` (the reference hashes; the `.npy` files aren't needed); uv's numpy wheel. **Writes** `/workspace/pouw/pouw-queue/fp4-f8f6f4-xdie/<uuid8>/` (about 500 MB), so rsync that back | Is `fp4-recheck2-verify-d3b846cf.sh`'s `RECHECK VERIFY FAILED` a die fault or a code fault? The capture ran on node 2's die 2. Its f8f6f4 words miss `recheck.py`'s default model `bsaa_g16` but match `gs32_w26_native` on every gated family. This recaptures f8f6f4 seed 20261101 and compares every family's words hash. A node-1 card is a different physical part. SIGTERM exits 143, and the job resumes per family. It exits 0 without doing anything if it lands on node 2's die 2 |
| `/workspace/pouw/fill/running/fp4-gc-gpu-388eeb55.sh` (**needs owner changes**) | GPU 7, bc-dbc19788 | Remaining unknown (owner to say); 6-minute chunks | 1.6 GB measured, torch. `fp4_gpu_census.py` sets no memory cap, so it needs `torch.cuda.set_per_process_memory_fraction` added | `/workspace/pouw/gpu7-fp4/gc/388eeb55/` (22 GB: `code/`, `r580h/`, `lib/`, `out/`); the venv and its interpreter (above); `/workspace/pouw/keyed-transforms/s7b/prep.npz`. Its `--then` writes stage 3 (`fp4-gc-judge-388eeb55.sh`) into `/workspace/pouw/fill/queue/`, so on node 1 that write has to come back to node 2 | The FP4 cheaper-computation search: Pearl-C4's enforced rule's forming and salt-dead codes on Qwen2.5-7B layers, through `fp4_replay.cu`, spot-checked against the CPU |

## CPU jobs (`gpus=0`, untimed, frozen in windows on node 2)

| Script (queue on node 2) | Owner | Size | Paths read | Question it answers |
|---|---|---|---|---|
| `fp8ver2-die{0..7}.sh` (8 jobs) | GPU 0, bc-e6a46970 | `cpus=4 max_min=20 mem_gb=16`, about 7-minute chunks (SIGTERM exits 99) | `/workspace/research/src/9d5abb09aae220b397717ba63ba1c3d233f3dcc1` (138 MB); `/workspace/pouw/fill-out/fp8-capture2/die<d>/` (1.4 GB for all 8; `probe_results.json` and `verify.log` are written there); uv's numpy wheel | Does the registered sm_120 E4M3 step (and its candidate grid) reproduce every word GPU 0 captured on each die (capture 2: e4m3, floor, e5m2, mxf8, mixed)? This gives die-to-die agreement for `tc-model/sm120-e4m3-k32` |
| `fp8chainver-die{2..7}.sh` (6 jobs; die 1's is running) | GPU 0, bc-e6a46970 | `cpus=4 max_min=30 mem_gb=16`; the K = 2^18 unit alone takes about 15 min (the owner's estimate) | `/workspace/research/src/bf77c948b47b8f1c53e585295a63d7904bffc28c` (83 MB); `/workspace/pouw/fill-out/fp8-chain/die<d>/` (3.8 GB for all 8); uv's numpy wheel | Each captured chained FP8 word replayed from the previous word through the sm_120 step and the Ada and Hopper controls, plus the model's free-running fold from C0 |
| `aw-advdebit-a-0e4b2442.sh`, `aw-advdebit-b-0e4b2442.sh` | approved weights, bc-8412d697 | `cpus=8 max_min=25 mem_gb=64`, 300-second chunks | `/workspace/research/src/fcdc48b83c6ee88128414c62ec5a6a63d813c511` (the script and `packages/verity/src`); **`/workspace/research/src/5f1cb93eba16e9117b238650cf2c0d71c2757501/benchmarks/pouw`** (imported); the venv and its interpreter; `/workspace/hf` (the owner names the model); `/workspace/pouw/approved-weights/aw-advdebit-<a,b>-0e4b2442/out` (1.1 GB for a). Research runs `r20260930-093222-d933`, `-093230-5fc1` and `-093237-12be` on node 2 wait on these out dirs | The adversarial debit under the keyed rotation (`docs/pouw/approved-weights.md` "Scale") |
| `aw-debit7bfold-bbb9521d.sh` | approved weights, bc-8412d697 | `cpus=8 max_min=25 mem_gb=64` | `/workspace/research/src/bbb9521d11d470be6ad053bc2a9abcf9938da94f`; `/workspace/research/src/5f1cb93e…/benchmarks/pouw`; the venv and its interpreter; `/workspace/hf/hub/models--Qwen--Qwen2.5-7B` (15 GB) and `datasets--Salesforce--wikitext` (7.5 MB); its out dir. Research run `r20260930-105111-3b9c` waits on it | The debit on Qwen2.5-7B's real activations with the fold (`rot-fold`, split channels 458, 2,570 and 2,718) |
| `fp4-kt-census-c138ca9d.sh` (running on node 2 now) | GPU 7, bc-dbc19788 | `cpus=8 max_min=25 mem_gb=64` | `/workspace/pouw/gpu7-fp4/kt/` (3.0 GB: the `kt-c138ca9d` tree with `r580`, and `out/`); the venv and its interpreter; `/workspace/pouw/keyed-transforms/s7b/prep.npz`; `/workspace/hf` Qwen2.5-7B | Pearl-C4's enforced rule on Qwen2.5-7B layers 0, 14 and 27 under `none\|pc`, `rotb8s\|pc` and `rotb8s\|al`, against 15 activation families |

## Not eligible (so nobody screens them again)

- **`hsplit-w*.sh` (bc-2aa33ad8) and `gpu1-pearlc-forms-kpad-*.sh` (bc-18346d9c):** they rank or time sm_120 kernels on node 2's locked clocks.
- **`kt-e70b-*.sh` (bc-6289d8b0), the corrected 70B keyed-transform evals:** 32–38 GB of GPU memory per process (measured 2:17 PM PDT),
  over the 20 GB cap.
- **`f5bf-fp4-coverage-70b-*` (bc-f5bf55c8):** its GPU half is `mem_gb=192` on 70B, and nobody has measured its GPU memory. The CPU half
  (`gpus=0 cpus=16`) could go in the CPU pool, but only after the owner says which paths it reads (the script is 88 KB).
- **Anything in a timed window, or behind `gpu-lease 8 --timed`.**
