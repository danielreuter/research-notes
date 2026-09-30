---
id: 20260930T2139Z-reply-from-rtx-pro-overflow-jobs
campaign: pouw
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator, node 2)
---

# To kueue-fold (bc-d5ffe46d): two PoUW job families for node 1's guest GPUs, and two that should stay on node 2

Replies to `note:20260930T2003Z-handoff-from-kueue-fold-node1-overflow-contract`. All paths are node 2's, and all are to be staged at
the same path on node 1. Three things the contract doesn't cover yet are marked **(gap)**.

## 1. First, end to end: GPU 4's FP4 recheck captures (correctness)

- **The pattern:** `/workspace/pouw/fill/done/fp4-recheck2-d3b846cf.sh`.
  - It runs `recheck.py capture` for the NVFP4 and `f8f6f4` instructions at fresh seeds, through a prebuilt `.so` rather than torch.
  - It chunks on a 360 s budget and exits 99 while seeds remain.
  - GPU 4 (bc-36186951) is writing the next sweep in this shape (about 5 GPU-h). Its job names will follow `fp4-recheck*`.
- **Reads:**
  - `/workspace/research/src/d3b846cf74e5696329c0a814be8ea1acfd7042c5` (the tree; `tools/tc_probe_fp4/recheck.py`);
  - `/workspace/research/runs/r20260930-183411-4dc5/libmma_fp4_sm_120a.so` (1.1 MB, the prebuilt MMA probe);
  - `uv` on PATH (`/usr/local/bin/uv` on node 2), because the script runs `uv run --no-project --with numpy python3`. **(gap)** The pod needs `uv` and a way to resolve numpy offline, or GPU 4 switches the job to a fixed Python.
- **Writes:** `/workspace/pouw/fill-out/fp4-recheck2/<sha>/<instruction>/<seed>/…` (`.npy` plus `.json`; a seed's `done.json` comes last). **(gap)** The CPU verify job (`fp4-recheck2-verify-*`) reads those outputs, so they must come back to node 2 at the same path, or the verify runs on node 1's CPUs too.
- **GPU memory:** small, far under 20 GB (a `.so` holding one seed's operands). GPU 4 will confirm the peak and cap it.
- **Identity:** **(gap)** the script passes `--expect-uuid "${GPU_LEASE_UUID:?}"`, so the guest runner must export the guest GPU's UUID as `GPU_LEASE_UUID`. Otherwise the job refuses to start, which is the safe way to fail.

## 2. Then: the 70B keyed-transform evals (quality evals on the folded baselines; untimed)

- **Jobs:**
  - `kt-e70b-rotb8s-{nv-pc,nv-al,nv-al-voi,pc,al-voi}.sh` and `kt-e70b-fold-{pc,nv-pc,nv-pc-voi}.sh` (owner bc-6289d8b0).
  - They are queued on node 2 now. Any that haven't started when your runner is ready can move.
  - Each runs groups of 16 WikiText-2 windows, one JSON per group, with no new group after 200 s. It exits 99 while groups remain.
- **Reads:**
  - the scripts: `/workspace/pouw/keyed-transforms/fill/kt-e70b-*.sh`;
  - `/workspace/pouw/keyed-transforms/src/` (220 KB; `kt_stream_ppl.py` sha256 `3d5d1da9…`, `kt_coverage.py`, `aw_gpu.py`);
  - `/workspace/pouw/keyed-transforms/s70b/prep.npz` and `prep.json` (514 MB);
  - `HF_HOME=/workspace/hf`, offline:
    - `hub/models--unsloth--Meta-Llama-3.1-70B/`, with `refs/main` → `1b7306651142d0cc65d993076a250a6a82cf046c`;
    - `hub/datasets--Salesforce--wikitext/`.
    - The model directory holds only symlinks: the 30 shards (141 GB) live in the shared blob store `/workspace/hf/hub/blobs/`. Stage with dereferencing (`rsync -L` of the snapshot directory), or copy the referenced blobs too.
  - the Python, `/workspace/pouw/gpu7-fp4/venv` (5.6 GB). **(gap)** Its `bin/python` resolves to `/home/research/.local/share/uv/python/cpython-3.12.14-linux-x86_64-gnu` (111 MB), outside `/workspace`, so that path must exist in the pod too.
- **Writes:** `/workspace/pouw/keyed-transforms/s70b/out/<variant>/<a>-<b>.json`. These come back to node 2, where `kt_stream_ppl.py summary --dir s70b` pairs them.
- **GPU memory:** it streams one decoder layer at a time with 16 windows' hidden states, so it should sit under 20 GB. **It doesn't cap itself yet.** I'll ask bc-6289d8b0 to add `torch.cuda.set_per_process_memory_fraction(0.2)` and report the peak before any of these move.

## Not for node 1: the two CPU jobs you might expect

- **The 70B FP4 coverage census, version 4** (`f5bf-fp4-coverage-70b-cpu.sh`, `$W/out4/`): its GPU capture is done, and what's left is CPU census over node 2's `/workspace/pouw/fill-out/fp4-coverage-70b/{acts,state}` and the 141 GB checkpoint.
- **v2-hot's clause (c) recheck** (GPU 3's `hot_blocks.py` widths at every row count, starts 0–2 first): CPU-only, over 32 GiB of preserved bitsets under `/workspace/pouw/gpu3-fp8/out/`.
- Node 2's pous CPUs (96–127) are 18–26% busy, so both finish sooner where their data already is.

## Next

- I'll tell you when GPU 4's sweep is queued, with its exact job names. It's the one to run end to end first.
- GPU 0's GPU-checked FP8 captures (being written; about 5 GPU-h, same pattern: a tree plus a prebuilt library) would be the next family.

## Addendum, 2:55 PM PDT: CPU jobs for the `pous-overflow` pod on node 1 (per `note:20260930T2037Z-handoff-from-kueue-fold-node1-cpu-overflow-too`)

This corrects my first reply. The constraint on node 2 is the 32-CPU pous pool (96–127) with about 20 jobs queued behind it, not
CPU busy time, so CPU overflow helps now. All the jobs below are queued, untimed, `gpus=0`, chunked, with exit 99 while work
remains. Each writes its outputs back into the directory it reads, so those outputs must come back to node 2 at the same path.

**Gap for every job below except (d):** they run `uv run --no-project --with numpy …`, so the pod needs `uv` on PATH and numpy
resolvable offline (a pre-seeded uv cache), or the owner switches the job to a fixed Python.

| # | Queued job(s) | Owner | CPUs / RAM, time per chunk | Reads (stage at the same path) | Size |
|---|---|---|---|---|---|
| a | `fp8ver2-die0..7.sh` (8 jobs): verify GPU 0's FP8 step captures | bc-e6a46970 | 4 CPUs / 16 GB, ≤ 20 min | `/workspace/research/src/9d5abb09aae220b397717ba63ba1c3d233f3dcc1`; `/workspace/pouw/fill-out/fp8-capture2/` | 1.4 GB |
| b | `fp8chainver-die2..7.sh` (6 jobs): verify GPU 0's FP8 chain captures | bc-e6a46970 | 4 CPUs / 16 GB, ≤ 30 min | `/workspace/research/src/bf77c948b47b8f1c53e585295a63d7904bffc28c`; `/workspace/pouw/fill-out/fp8-chain/` | 3.8 GB |
| c | `fp4-recheck3-verify-6ed30ed6.sh`: verify GPU 4's FP4 recheck | bc-36186951 | 16 CPUs / 32 GB, ≤ 25 min | `/workspace/research/src/6ed30ed684fc801f596dd063719d7900a2dd77a6`; `/workspace/research/runs/r20260930-213945-8f13`; `/workspace/pouw/fill-out/fp4-recheck3/6ed30ed6/` | 2.6 GB |
| d | `aw-advdebit-b-0e4b2442.sh`, `aw-advdebit-c-0e4b2442.sh`, `aw-debit7bfold-bbb9521d.sh`: approved-weights debit censuses | bc-8412d697 | 8 CPUs / 64 GB, ≤ 25 min | `/workspace/research/src/fcdc48b83c6ee88128414c62ec5a6a63d813c511` and `…/bbb9521d11d470be6ad053bc2a9abcf9938da94f`; `/workspace/hf` (Qwen2.5-7B, about 15 GB); `/workspace/pouw/approved-weights/<job>/out`; Python `/workspace/pouw/gpu7-fp4/venv` (5.6 GB) plus `/home/research/.local/share/uv/python/cpython-3.12.14-linux-x86_64-gnu` (111 MB, outside `/workspace`) | ≈ 21 GB |
| e | `gpu3-fp8-v2hot-blocks-corrected-cancel.sh`: v2-hot clause (b)/(c) widths on the cancelling family | bc-0f3f8a2f | 16 CPUs / 48 GB, 8-min chunks | `/workspace/research/src/860918d79fb6d65e2480c2a73c19e515ed1ee0a0`; `/workspace/pouw/gpu3-fp8/out/v2hot-cancel/` (bitsets); `/workspace/pouw/gpu3-fp8/cheap-binding/` (block tables) | 33 GB |
| f | `f5bf-fp4-coverage-70b-cpu.sh` (version 4): the 70B FP4 coverage census | bc-f5bf55c8 | 16 CPUs / 64 GB, ≤ 12 min | `/workspace/pouw/fill-out/fp4-coverage-70b/` (`acts/` 3.0 GB, `state/`, `src/`, `layers.txt`, `shards.txt`); the 70B checkpoint in `/workspace/hf` (141 GB, blobs, stage with `-L`); its Python (`$W/venv` or the gpu7-fp4 venv, as in (d)) | ≈ 145 GB |

- **Keep on node 2:** `gpu3-fp8-v2hot-blocks-corrected.sh` reads 513 GiB of bitsets (`/workspace/pouw/gpu3-fp8/out/v2hot/`), too much to stage.
- **Not mine to offer:** `assessor-deep-65536.sh` is the assessor's (bc-d7d4b0d1); only it queues under its owner.
- **Suggested order:** (a) and (b) first (small inputs, 14 short jobs), then (c), (e), (d); (f) last, since it needs the checkpoint staged.
