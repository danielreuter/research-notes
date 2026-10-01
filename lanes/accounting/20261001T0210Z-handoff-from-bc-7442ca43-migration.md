---
id: 20261001T0210Z-handoff-from-bc-7442ca43-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: GPU 2, the hashing module on sm_120 (bc-7442ca43)
---

_Relayed verbatim from the Cursor store by old-accounting (bc-b729c175): the author's VM gets a 403 pushing to research-notes._

# Migration handoff from bc-7442ca43 (GPU 2, hashing on sm_120): the `-h2` hash bench finished on all 8 dies, every gate passed, and the output is preserved by hand (`art:ad4999c6…`); nothing is in flight

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. Written 7:11 PM PDT. My notes push got a 403
(`cursor[bot]`), so this is staged in the store outbox `internal/pouw-fp8/accounting-outbox/` for @old-accounting to copy in.

GPU 2 owns the shared sm_120 hashing module (`benchmarks/pouw/pouw_hash/`), its fusion into GPU 1's (bc-18346d9c) Pearl-C FP8
pipeline, and the `-h2` hash bench (backlog line 82). My status file is the Project store's
`internal/pouw/rtx-pro/workers/2-hashing.md`.

**Node-2 access:** my VM lost node-2 access after a restart (backlog line 94). It came back at 7:06 PM PDT, once I recloned the
notes repo into `~/.research/notes`: `research pods ssh vy-nebius-2` reads `machines.d/vy-nebius-2.toml` (provider ssh, user
`research`) and uses the research SSH key from the Project's secrets. A successor needs those three things: the `research` CLI
(the `/workspace/.venv` of a verity checkout), the notes clone, and the key. Line 94 can be dropped.

## 1. Branches and PRs

- **`cursor/pouw-hash-sm120-9569`, head `4a4fde4f9`, [draft #506](https://github.com/danielreuter/verity/pull/506)**
  (base `cursor/pearl-c-h100-9ada`, #449's branch, also an open draft). This is the module: `pouw_hash.cuh` (header-only, namespace
  `ph`), `vectors.cuh`, `pouw_hash_check.cu` (161 check rows against hashlib, `blake3`, `verity.commitments.turboshake` and Pearl-C's
  `leaf`), `pouw_hash_bench.cu`, `check.py`, `sass.py`, `build.sh` and `run.sh`. No `check` recorded.
  - #596 (the served path, `cursor/served-gap-h2-spread-76ee`) already carries the module up to `cbe4a3a8e`, with its own edits to
    5 of its files. #506 has two commits beyond that: `ceac4f139` (keyed BLAKE3 under `-h1`'s pinned message key) and `4a4fde4f9`
    (`QUAD_SCRATCH`).
  - Left: once #596's chain lands, rebase those two commits onto `main` as a small PR, or close #506 if the served kernel doesn't
    use them. The served path takes its `-h2` keys from GPU 1's in-kernel keys (`997ac6bd`), not from `ceac4f13`.
- **`cursor/h2-hash-bench-9569`, head `f4f4bb8c6`, no PR.** It's stacked on #596's head `05ce9ce49`, and holds
  `benchmarks/pouw/pouw_hash/h2_bench.py`, `h2_ship.sh`, `h2_fill.sh` and `benchmarks/pouw/tests/test_h2_bench.py` (18 pass, 1
  skipped). It is the code for the fill jobs in section 2, and their job is done.
  - Left: keep it as the code behind the per-die numbers. Open it as a draft stacked on #596 only if the bench is kept (line 82);
    otherwise leave the branch as the record.
- **`cursor/pearl-c-sm120-h1-commit-9569`, head `e0902b4a0`, no PR.** It's the Pearl-C arm on harness interface v0.5 (the
  `dump`, `transcript_buffers` without the tree counters, `variant` and `lineage`), one commit on GPU 1's `b6a91929`. My status
  file's Needs 0 asks GPU 1 to fast-forward with it. It is **not** an ancestor of GPU 1's `cursor/pearl-c-sm120-h1-b44b`, of #596
  or of `main`.
  - Left: GPU 1's successor takes it or says it's superseded.
- **`cursor/pearl-c-sm120-pilot-run-9569`, head `0cb23bfd6`, no PR.** The run tree of the pilot run `r20260930-174917-2585`
  (`e0902b4a` merged with #491 `e22a2808` and #583 `65e70059`). Done; keep it for provenance, never merge.
- **`cursor/pearl-c-sm120-h1-9569`, head `98b142c0e`, no PR.** The earlier `-h1` fusion, superseded by `-h1-commit`. Stop; the
  branch can go.
- **`cursor/pearl-c-sm120-h1-fused-9569`, head `500363502`, no PR.** The `pearl_c_sm120` fixture after #449 (`-h1`'s expected
  buffers and keys, `crosscheck_h1`). Superseded by the `-h1-commit` stack. Stop.

## 2. Runs and jobs in flight

- **Nothing is in flight.** I have no research run going, and no fill job of mine is queued.
- **The fill jobs `gpu2-h2hash-die0.sh` … `gpu2-h2hash-die7.sh` all finished**, rc 0 (node 2's `/workspace/pouw/fill/events.jsonl`).
  - Each die ran 26 chunks: the 13 panel shapes, twice. Each chunk ran both variants (sm120 and sm120-unpromoted) and both
    formats (`-h2`, then `-h1`).
  - Every chunk exited 0. **All 832 bit-exact gates passed and none failed.** There are 5,097 `h2bench` rows. There were 21
    preemptions, all by timed windows, all requeued.
  - End times: die 0 at 6:33 PM PDT; dies 3 and 7 at 6:39 PM PDT; die 6 at 6:40 PM PDT; dies 2 and 5 at 6:55 PM PDT; die 4 at
    6:57 PM PDT; die 1 at 7:00 PM PDT.
  - GPU time: about 8.7 GPU-h of completed chunks (208 × 2.5 min), plus the preempted partial chunks.
- **Output:** `/workspace/pouw/fill-out/gpu2-h2hash/die<N>/` on node 2, 20 MB in all. Per chunk, `<shape>-p<1|2>.jsonl`
  (`kind` `check`, `gate`, `h2bench`), `.err`, `.done` and `.starts`, plus `chunks.txt` (the start and end, die UUID and rc of every
  chunk).
- **Custody: none, so I preserved it by hand: PRESERVED at 7:10 PM PDT as
  `art:ad4999c6205fba59a28db6aea0ec9e9a41503cc86b56123c10713b00b215b6d0`** (`evidence/v1`). That artifact is `gpu2-h2hash.tar`
  (sha256 `3d7455813f7ddff5665c8e84032dbb72da71fbcd380a81677eea07ed9280a0db`, 849 entries: the whole `gpu2-h2hash/` tree), with
  meta giving the code, ship and cubin shas and the gate counts. Node 2's copy can be deleted once a successor has fetched it.

## 3. Half-done state, and what was only on my VM

- **Nothing exists only on my VM.** Every branch is pushed, and the `/workspace` checkout is clean on `main`. The restart already
  took my `/tmp` worktrees, and they were all pushed.
- **The per-die table isn't written yet.** The numbers are only the raw rows on node 2 (and the tar). The status file's 3:43 PM PDT
  section has the first numbers (dies 1 and 7: 32×8192×8192, 2048×8192×8192, 32768³).
- **To get the output:** `research data fetch` on the `art:` above. A fresh copy from node 2 is
  `research pods ssh vy-nebius-2 -- 'tar -C /workspace/pouw/fill-out -cf - gpu2-h2hash' > gpu2-h2hash.tar`. Its sha256 matches the
  one above only while nothing in the tree changes.
- **On node 2:**
  - `/workspace/pouw/gpu2-h2hash/ship` and `h2ship.tar` (sha256 `189c8bf5…`): built at `05ce9ce49` with nvcc 13.0.88, no FTZ flag,
    SASS gate passed, cubin `8acc10ea…`. It carries stdlib-only `verity` sources under `py/` and a `MANIFEST.sha256`.
  - `jobs/`: copies of the 8 job scripts, with `jobs.sha256`.
  - `validate/`, `validate2/` and `validate.sh`: the two pre-queue validation leases, on dies 7 and 1.
- **In the Project store:**
  - `internal/pouw/rtx-pro/workers/2-hashing.md`: the status file. Its v2 γ figures were struck at 4:28 PM PDT, since v2 is D.
  - `internal/pouw/rtx-pro/2-hashing/pearl-c-sm120-fused-v2-1633f476.patch`: the old TurboSHAKE128 fusion, applied by GPU 1 as
    `6d9ac0e8`. History only.

## 4. The next step for each kept item, and what I'd stop

- **The `-h2` hash bench (line 82, "Daniel decides").** The GPU part is done and the output is preserved (section 2). Next: reduce the
  `h2bench` rows to one table, CPU only, and store it with `--ref` to the `art:` above.
  - The table: per shape, variant, format and die, the call's hashing chain, A's commitment, the digests (fused = `gemm_pearlc_b`
    less `gemm_pearlc_s`) and the tile leaves and tree, against `gemm_plain`/`gemm_fast`.
  - Use the `ms_graph` minima and medians, with each row's clock record.
  - Label it "Measured, diagnostic untimed screen" and carry the shortcuts below.
  - Queue no more GPU for it.
- **#506 (the module):** after #596 lands, the two-commit rebase above, or close it.
- **`e0902b4a` (the arm on v0.5):** GPU 1's successor's call.
- **Stop:**
  - anything on v2 (v2 is D, at least 0.946% packed; no figure of mine cites v2 any more);
  - the superseded branches `-h1-9569` and `-h1-fused-9569`;
  - the old `pouw-hash-ship-cbe4a3a8` bench bundle;
  - the TurboSHAKE128 fusion patch.
  - My status file's Needs 2 and 3 (the SASS gate's `discover()` fix and the negative-control run) are done: #491 `e22a2808` and
    the pilot run, where the controls were rejected.

## 5. Traps

- **`run.py`'s own check is `-h1` only.** `-h2` is checked only by `h2_bench.py`'s gate (frame-b3s trees with `blake3-s256`, and
  `-h2`'s segment keys).
- **The bench's shortcuts:** stand-in domain bindings, E_B's line key and unit block (the digest keys are Pearl-C's real ones). The
  CUDA graphs replay L2-warm back-to-back copies. The CPU gate samples the wide tree levels and checks the narrow ones in full.
  `seed_line_a` is timed but gated only by `run.py`'s fixture check.
- **Grepping the output for "fail" matches `"failed": []`.** Count `"kind": "gate"` rows whose `"ok"` isn't `true` instead.
- **Clocks:** the clocks are locked at 2,100 MHz, but 32768³ GEMM rounds were power-capped at 1,965–1,980 MHz (throttle 0x4). Use
  each row's `clk_before`/`clk_after`.
- **Node 2's `python3` (3.12.3) has no numpy.** The ship carries stdlib-only `verity` sources. Set `PYTHONDONTWRITEBYTECODE=1`, or
  a stray `__pycache__` breaks the manifest check.
- **The SASS gate's nvcc 13.0 tools:** `nvidia-cuda-cuobjdump==13.0.*` isn't on PyPI. Install 13.4 (and the `nvdisasm` wheel) and
  symlink them into the toolkit's `bin/`.
- **ssh:** `research pods ssh … -- 'a && b &'` backgrounds the whole list, so ssh hangs to its timeout. Use `(… &)` with full
  redirection, or better, a fill job. `pkill -f PATTERN` also matches its own shell.
- **Timed windows preempt all fill.** Keep chunks at 2.5–3 min. rc 143 doesn't count toward a job's 5-start limit.
- **Harness:** a `poison()` that fills the atomic tree counters (`ctr_a`, `ctr_b`, `ctr_t`) with 0xA5 breaks the one-launch
  trees. A pod run can't publish its own `ledger/` records, so run `ledger.py publish RUN --by … --push` from a machine with the
  store. `panel.py render` needs `VERITY_REPO` pointing at a tree with #583's `ledger.py`.
- **#449's `fake_cuda.c` drops kernel names past 64 silently.** The fix is my `ea17cefb`, on the `-h1-commit` stack.
- **The store's FUSE mount returns EAGAIN.** Retry with a sleep, and `cmp` after copying.
