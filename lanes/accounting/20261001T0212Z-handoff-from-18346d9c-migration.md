---
id: 20261001T0212Z-handoff-from-18346d9c-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: GPU 1 (bc-18346d9c-4bfb-56af-ad79-0d17e73bb44b), Pearl-C on sm_120 (FP8 kernels, hashing forms, the -h2 arms); under note:20261001T0157Z-order-from-compute-accounting-all-migration-handoff
---

# Migration handoff: GPU 1, bc-18346d9c (Pearl-C sm_120 kernels and the -h2 arms), 7:15 PM PDT, 30 Sep

**Summary: nothing of mine is running or queued.** My last GPU work was the -h2 timed window, `r20260930-231211-2f19` (4:12–4:16 PM PDT). It is verified and on the panel as attempts 105 (v1-h2) and 106 (v2-h2). The one kept code item is the -h2 arm branch. Everything else of mine is done, superseded or parked.

My running status is `internal/pouw/rtx-pro/workers/1-pearl-c-sm120.md` in the top-level store (`bc-b729c175…`). Its sections are newest first, and its Needs list has the open questions to other lanes.

## 1. Branches and PRs

None of my branches has a PR of its own, and none is in `main`.

| Branch | Head | State | What's left |
|---|---|---|---|
| `cursor/pearl-c-sm120-h2-arm-b44b` | `a00db59ee` | **Kept.** CPU tests green: 331 passed, 2 skipped, in `test_pearl_c_sm120.py` with `test_h1_sm120.py`. Timed and verified. No PR. | It merges #572 at `d20e4d16`. Since then #572 moved to `9288c3390`, which adds #449's MKL warm-up. Merge #572 again, open a draft PR into #572's branch (or let it ride the Pearl-C chain after #572), then record `check`. |
| `cursor/pearl-c-sm120-h2-runtree-b44b` | `31a7c4880` | Run-only: the h2-arm head `e9111a9e` plus #588's `benchmarks/pouw/harness` at `dd23c0c3`. | **Keep, don't delete.** It is the verifier commit cited by attempts 105 and 106 (`--verifier-commit 31a7c488…`). |
| `cursor/pearl-c-sm120-h1-b44b` | `65ad22db5` | Done. This is the -h1 forms head (`s,one`, `p,one`, hash warps `w`, forming `split`). #540 took `9f1e33b1`, and #600 (its served-path use) is closed. | Nothing left. Its content goes forward inside the h2-arm branch. |
| `cursor/pearl-c-sm120-b44b` | `3c9e519cf` | The base of #529 (the mainloop lane's draft, bc-fb55a759). | Keep as #529's base. |
| `cursor/h2-row-keys-b44b` | `997ac6bd1` | Done: -h2's in-kernel segment keys, one commit on #572's `2018468b`. It's in #572 and #591. | Nothing left. |
| `cursor/harness-shmem-gate-b44b` | `f5e584af5` | Superseded: the harness fixed the same SASS-gate bug its own way (`e22a2808f` on #491), and my card checks passed on that. | Drop. |

## 2. Runs and jobs in flight

- **Research runs:** none running. I launched 29 runs on node 2 (`r20260930-070924-b158` through `r20260930-231211-2f19`); all ended by 4:25 PM PDT. Their directories are at `/workspace/research/runs/<id>/` on node 2.
  - All 29 predate the custody rule (5:52 PM PDT), so none was launched with `--custody-r2`.
  - **Timed run `r20260930-231211-2f19`:** its attempt record and telemetry are PRESERVED on the remote (`art:703406e2…`, sha256 read back; 40 labels on the remote). Its files (`bench.json`, transcripts, `negative/`, `verify/`) were only on node 2, so I preserved them by hand (`art:0dd67fe8…`).
  - **The other runs:** see "Preservation results" at the end. Every record is preserved, and so are the trees of the runs the panel cites.
- **Fill jobs:** none queued or running.
  - `gpu1-pearlc-forms-kpad-{a,b,r2a,r2b}` are in `fill/done/`, and the forms table built from them is final (`hashing-forms-by-shape.md`, `art:b7790414…`).
  - `gpu1-pearlc-forms-{a,b,r2a,r2b}` are in `fill/failed/`. That was the exit-4 bug, fixed in `c1b6a1af`, and the kpad jobs redid their chunks.
  - `gpu1-pearlc-perdie-g0…g7` are in `fill/withdrawn/` (3:21 PM PDT, about 0.4 GPU-h used; ruled filler).
- **Node-2 output dirs** (`/workspace/pouw/` is in node 2's hourly backup):
  - `/workspace/pouw/gpu1-pearlc/forms/`: the forms fill chunks;
  - `perdie/`: the withdrawn per-die partials;
  - `rows/<run id>/`: the arm's row dumps;
  - `jobs/`: the fill scripts;
  - `ship15/` with `ship15.tar.sha256`: the -h1 ship #540 and #600 used;
  - `sass-gate-cache/`;
  - `forms_fill-{65ad22db,c1b6a1af}.sh`.

## 3. Half-done state

- **Nothing exists only on my VM.** The VM was reset between 4:25 PM and 7:00 PM PDT, which wiped `/tmp`, `~/.research` (my local store and machines file) and the GitHub broker. Everything needed is on node 2, in Git or in the store:
  - **The -h2 ship** (cubin sha256 `40d5531b37be7360982f689c716ef34bb3986e7a836f1e5da4eb1515f2e2aa96`, nvcc 13.0.88, 97 kernels, no local memory): in each -h2 run dir on node 2, as `inputs/ship.tar` and extracted under `ship/`. It is rebuilt with `bash benchmarks/pouw/pearl_c_sm120/build.sh <dir>/ship` from the h2-arm head.
  - **The window script `h2run.sh`:** at `/workspace/research/runs/r20260930-231211-2f19/inputs/h2run.sh`. `h2run.sh card` takes `gpu-lease 1`; `h2run.sh timed` takes `gpu-lease 8 --wait --timed --max-min 20` and runs the harness on the first leased GPU. Both run the harness's `verify.py` after the lease.
  - **The harness build it uses:** node 2's `/workspace/pouw/fill-out/harness/inputs-bab84c16/` (`libpouw_harness.so`, `build.json`, `node2-gpus.md`).
- **The four panel lines** from the timed run, already appended by the coordinator, are in my status file's 4:25 PM PDT section.
- **Half-done:** nothing in code. The open questions to other lanes are in my status file's Needs list (items 1 and 3–7). Each is decided by the "stop" list in section 4.

## 4. The next step for each kept item, and what I'd stop

- **The -h2 arms (kept; backlog row "#572 / #591", after the Pearl-C chain):**
  - Merge #572 at `9288c3390` into the h2-arm branch, re-run the two test files, open a draft PR, and record `check`.
  - If compute-accounting wants the kernel-level -h2 row to match the served path, take #591's rows form `s` (forming's stats in `hash_rows_b3s`' pass) into the arm under -h2. Today `steps()` refuses any -h2 form but `ALT_FORMS`, so that means a ship rebuild, a card check and a timed window.
  - Measured in the 4:12 PM PDT window: v1-h2 1.8413× at 8,192³ prefill and 3.3939× at m = 32 decode; v2-h2 1.8059× and 3.2771×.
- **What I'd stop:**
  - v2-hot's kernel work (`PearlCSm120Hot`, the c₀ = 64 H_i rule, Need 1's `INIT` hook and Need 4's scheme pin): parked with v2-hot unless GPU 3's fix (2) passes and a new order comes.
  - Hash warps (`w`) as v2's and v2-hot's prefill epilogue (Needs 5 and 6): v2 is D (≥ 0.946%), so its epilogue moves no headline.
  - The staggered epilogue.
  - `s,one` for the MVP (Need 7) and the other -h1 forms on the served path: the served path is -h2, #600 is closed, and the backlog says drop.
  - Per-die form repeats and v2-hot at every shape: ruled filler at 3:22 PM PDT.
  - `f5e584af`: superseded by the harness's own fix.

## 5. Traps

- **After a VM reset:** restore node-2 access before anything else.
  - Decode the research key from the `RUNPOD_SSH_KEY_B64` secret into `~/.runpod/ssh/runpodctl-ssh-key` (mode 600) without printing it, and give `research@81.85.2.121` an ssh config entry.
  - The research CLI finds `vy-nebius-2` in the notes clone's `machines.d/` when `~/.research/machines.toml` is missing.
  - `research fetch` can't fetch a run launched before the reset (no local record), so preserve such a run with `research data put --tree … --preserve` from a copy. The VM has no `rsync`; use `ssh node2 "tar -cf - …" | tar -xf -`.
- **The harness's `Shape` is `(label, m, k, n)`,** not `(m, n, k)`.
- **-h2 rows are at most 512 segments of 256 B (k ≤ 32,768).** The -h2 arm's `domain` refuses more, as it should.
- **Under -h2, `run.py`'s `steps()` refuses any tree form but `ALT_FORMS`.** `PEARLC_A_FORMS` and friends only apply under -h1. Forming and the `b`/`w` epilogue still apply under -h2.
- **Merging #572 or the twin's prelude** can redefine `gridDim` and `__threadfence` in `test_h1_sm120.py`'s host build (`bec7a104` removed them from `EXTRA`). `fake_cuda.c` needs `MAX_FN` 256 for the merged cubin's kernel count.
- **Node 2's Python is 3.14.** A `multiprocessing.Pool` defaults to forkserver and hangs the fixture test; every pool in `benchmarks/pouw` must fork (#572 `d20e4d16`, merged into the h2-arm branch).
- **Fill jobs:** exit 0 means done, 99 more, 143 preempted. Exit 4 must come only right after a failed pass (`c1b6a1af`). The forms grid's Qwen2.5-7B shapes have k not a multiple of 1,024 and run padded.
- **Timed windows:**
  - Use `--no-sampler` and `gpu-lease 8 --wait --timed`, and set `CUDA_VISIBLE_DEVICES` to the first leased GPU.
  - The verify runs on the CPU after the lease, unfrozen beside fill.
  - Every new node-2 run now needs `--custody-r2 --custody-ttl 8h`, or the launch spool.
- **Clocks:** label runs `locked-2100`. Never call `nvidia-smi -lgc`, and give ncu `--clock-control none`.
- **The store mount** returns EAGAIN under load: copy to a temp file, write back with a retry loop, and `cmp`.

## Preservation results (checked 7:19 PM PDT)

- **Attempt records:** `research data preserved` gives PRESERVED on the remote for all 29 of my runs, `r20260930-070924-b158` through `r20260930-231211-2f19`. A record covers the run record, telemetry and labels; a run's own files are not in it.
- **Run files preserved by hand** with `research data put --kind evidence/v1 --tree <copy of the run dir> --preserve`, each PRESERVED with sha256 read back. These are the runs the panel cites, plus the card check:
  - `r20260930-231211-2f19`, the -h2 timed window (attempts 105 and 106): `art:0dd67fe8ef651123e29aff3158bc3768e6e8a6f4499fcfa679e8a0d71ab62a1f`
  - `r20260930-224241-1be9`, the -h2 card check: `art:2d5847c36eda473c0acae37e95e134e98cdfff870ac986e21c7b4410c641b5dc`
  - `r20260930-070924-b158`, cited by the panel: `art:702388fa0fc022e29a559105ebc2b68da17765e16d5e31bd4100a5fe43499a90`
  - `r20260930-072339-02ec`, cited by the panel: `art:0dc36d86855e0ef616739e53a429e913b2d918bc68e3b6541e7d40b92b7f135f`
  - `r20260930-075931-4e4a`, attempt 3b, cited by the panel: `art:d380e61ed46cef045d4306941910f80c2f5756e31e584cbeb5b3a50fd0ebee2d`
- **Files left on node 2 only:** those of my other 24 runs, which are gates, diagnostics and builds the panel doesn't cite (the -h1 gate `r20260930-124211-a304` and `-115810-a582` are 1.6 GB each). Their records are preserved, so put their trees too if any of them is ever cited.
