# Lane hp2-host — B-Ligero prover: host-phase elimination round 2 + stream overlap (2026-09-23)

POST-FREEZE COMMIT e689b72 (11:10Z, `lane/hp2-host`, one commit on top of 9268cc4; 3 files: `field.py`, `ntt_cuda.py`, `ntt_cuda_test.py`): **four-step CUDA NTT** replacing the 16-stage torch chain inside the prover's graphs. Bit-exact by construction and measured (bx13 187/187 + Rust ACCEPT ×8, `ntt_cuda_test` 26/26 cases), pytest 56 passed, 2 of 7 gates recorded before the pods were terminated (§2g). **H100 pod 2, like-for-like: bf16-hopper int-ZK 0.2525 → 0.2337 s (−7.4 %; 3.1–3.2× main)**; the fp8 row and the artifact were lost with the pod. For the post-Wave-2 merge, not the frozen decision.

FINAL CHECKPOINT 9268cc4 (10:50Z) — mergeable: all commits on `lane/hp2-host` (worktree `~/projects/verity-main-wt/hp2-host`; 0244332 … 820dc9d, 07d7b8f, 28b1cbc, 0926f94, 8d743d6, 94fd7d3, 3588971, f66d0bb, 9268cc4; merge as one unit). If the coordinator froze `main` at 94fd7d3 (the 09:55Z checkpoint): the three commits on top are each bit-exact and gated (below) and worth −7 % / −8 % on the decision rows; 94fd7d3 alone stands as previously reported. Validation on the 4090 against main 6babe27: **bx12 at 9268cc4: 187/187 transcript files identical** (bf16-hopper + fp8-hopper; int-ZK, int-non-ZK, FS-ZK; sequential, `--pipeline 3`, `--impl legacy`; ragged last sub-batches 3×170+16 and 3×341+4), also 187/187 at f66d0bb (bx11) and 3588971 (bx10), **48/48 at `--pipeline 4`** (bx_p4, 8d743d6), Rust `ligero-verify batch` ACCEPT on every lane dump tree, pytest 55 passed / 1 skipped and 7 relation gates rc=0 at 3588971 (gates5) and at 9268cc4 (gates6, §1), `tests_fused_test` bit-exact on H100 and 4090. Rust untouched (`diff -rq backends/ligero-verify` vs main: identical). **H100 like-for-like (pod 2, Xeon 8480+ host, §2f): bf16-hopper int-ZK 0.752 / 0.734 → 0.2525 s (2.9–3.0×), fp8-hopper int-ZK 0.443 → 0.134 s (3.3×)**; pod 1 (§2b, 820dc9d): 0.662 → 0.268, 0.379 → 0.164. Targets (≤ 0.35 / ≤ 0.20 s) met with 28 % / 33 % margin on the slower pod; the coordinator's independent measurement decides. `--pipeline 4` is the bench-vu default (94fd7d3, §2d).

Since the 07:40Z checkpoint (820dc9d): GPU-side work, because the H100 profile showed the pipelined prover GPU-bound (host 2.2 ms busy vs 8.3 ms blocked per sub-batch) -- v4 Montgomery test kernels (28b1cbc), no 440 MB zero fill (28b1cbc), register-resident witness program with Shoup constant products (0926f94), int32 static coefficient / witness matrices (8d743d6). 4090: pipelined 15.0 → 13.8 ms/sub-batch, sequential 23.5 → 21.4.

Base: `main 6babe27`. Worktree `~/projects/verity-main-wt/hp2-host`, branch `lane/hp2-host`. Pods: `vy-hp2-host` (RTX 4090, EPYC 7642 host, 12 vCPU, $0.74/h, created 05:48Z, still up for the dev loop), `vy-hp2-host-h100` (H100 80GB HBM3 SXM, Xeon 8462Y+ host, created 07:03:45Z, **terminated 08:17Z**, 1h13m ≈ $4.25), `vy-hp2-host-h100b` (H100 80GB HBM3 SXM, Xeon 8480+ host, AP-IN-1, created 09:07:50Z for pass 2, ~25 min). Notes/evidence: this directory.

## 0. What changed (protocol-identical, byte-identical transcripts, Rust untouched)

| file | change |
|---|---|
| `protocol.py` | `prove` = `pipeline.run_to_completion(_prove_stages(...))`: the prover is a **generator of stages** that yields at the host-wait points (root D2H; SHAKE-256 squeeze; test messages D2H; openings D2H). `_Clock` records **CUDA events** per phase (one stream sync at the end). Statement digest (blake2b) on a worker thread. Challenge-1 expansion: SHAKE-256 squeezed by **libcrypto via ctypes (GIL released) into pinned memory** — inline on the main thread in the sequential prover, on a hot worker thread in the pipelined one — uploaded non-blocking, reduced mod p on device. **Commit graph** (`COMMIT_GRAPH`): witness kernel → ChaCha mask sampler → SIMT encoder (+coefs) → mask-row coset NTT as ONE CUDA graph per stream on static buffers (the mask key drawn eagerly, uploaded from pinned). **Tests graph** (`TESTS_GRAPH`): challenge block → w, h, q, v (linear / quadratic / chain tests, `_tests_compute`) as ONE graph per (stream, chain layout), its outputs landing in the slot's pinned `msgs` buffer via memcpy nodes. `NTT_GRAPHS`: `intt` / `eval_on_coset` chains graphed per shape. Opened columns + Merkle paths gathered on device, one pinned copy (`openings_device.py`). Every flag has an eager fallback (`--impl legacy` = the torch witness program). (28b1cbc) the commit graph writes every witness coefficient row in full (k = l + t_pad), no 440 MB zero fill; (8d743d6) the static coefficient / witness matrices are **int32** (the encoder returns int32 coefficients, the fused tests read u32): the copy into them and the two combinations over them move half the bytes. |
| `tests_fused.py` | (28b1cbc) `_v4_` linear-combination kernels: 4 columns per thread through 16-byte loads, the block's slice of C in shared memory, 24 independent u64 accumulators, one **5-instruction Montgomery reduction per 4 products** (C pre-scaled by 2^32 / 2^64) instead of a 64-bit modulo every 3 products. Scalar kernels kept (`VEC_COLS = 1`). (f66d0bb) the booleanity row value and the quad constraint value are truncated to `unsigned` before the D products (exact: < p), so each product is one 32x32->64 IMAD instead of a 64x64 multiply -- the compiler could not range-analyse the 64-bit conditional subtract they came from; the v4 row loop unrolls 4 (was 2); the rows variant stages its row indices in shared memory. **H100: boolcomb 1.08 → 0.49 ms, lincomb 0.72 → 0.36 (2534×65536); in situ boolcomb_rows 1.11 → 0.51, lincomb ×2 0.55 → 0.26 per sub-batch.** 4090: DRAM-bound, unchanged. |
| `pipeline.py` (new) | `shake_into` (libcrypto XOF, hashlib fallback, self-checked), `HotWorker` (the squeeze thread keeps its core warm between requests: 9.2 ms hot vs 11–14 ms cold on the EPYC), `Slot` (stream + pinned buffers per pipeline position), `run_to_completion`, `prove_many(starters, depth)`: interleaves N sub-batch generators on their own streams; a job advances when its waitable (blocking CUDA event / future) is ready. Per-sub-batch timings rescaled to the wall share (`measured_*` keep the event values; `host_*` marks unscaled). `LAST_STATS`: main-thread busy vs blocked, per stage. |
| `openings_device.py` (new) | root / opened columns / paths from the device tree: one `index_select` over the concatenated levels; `Proof.paths` built in C (numpy void dtype `.tolist()`). (3588971) `StaticMerkle`: the hash_gpu blake3 kernels (`blake3_chunks` / `blake3_parents`, same geometry) over torch-preallocated levels in one flat buffer, so the Merkle commit (21 launches) + the root's D2H memcpy are captured **inside the commit graph** (`MERKLE_GRAPH`); the paths gather reads the flat levels without a `cat`. |
| `mask_sampler.py` | key uploaded from a pinned ring (non-blocking); rejection compaction by cumsum + scatter (**no host sync**), same first-`count`-accepted selection; `key_dev=` for graph capture (torch allocations). `SYNC_FREE=False` restores the legacy path. |
| `hints_torch.py` | hint CUDA graph keyed per stream. |
| `witness_device.py` | (0926f94) codegen: rows read by later ops are `const u64` registers (bits / selectors re-derived from the kept `x` / `sx`) instead of store-to-W-and-reload (which the compiler must serialise: `W(i)` / `W(j)` may alias for all it knows); `coef * W_j` by Shoup constant multiplication (`mulc`: `q = umulhi(x, floor(v 2^32 / p))`, `r = x v - q p` in [0, 2p)), sums by conditional-subtract chains: 4355 → 169 64-bit modulos per column. `REGISTER_ROWS = False` = the original codegen. |
| `relchain.py` | `RelationChainRunner.marshal`: per-sub-batch instance arrays (host + **device-resident** + `pub`) cached for the run; `prove_vus_many(batches, coins_factory, depth)`; `bench_vu_rel` uses it when `--pipeline N > 1` (rep 0 warm-up: sequential self-check, then every slot + the ragged last layout once, untimed). `software.backend.pipeline` recorded. Coin-source hooks untouched. |
| `fp8/witness.py` | `hints_fp8` accepts device tensors (`torch.as_tensor`), no `.cpu().numpy()`. (9268cc4) its ~280 small kernels are a **CUDA graph per (system, l, k, stream)** as `hints_torch`'s (static inputs, cloned output, eager fallback): 283 → 19 `cudaLaunchKernel` per fp8 sub-batch. |
| `ntt_cuda.py` (new), `field.py` | (e689b72, 11:10Z) **four-step CUDA NTT** for the prover's batched transforms: `field.ntt` dispatches CUDA int64 rows of n = 256 · N2 (8192 … 65536) to two kernels -- length-N2 column transforms + the w_n^(i1 k2) twiddle in shared memory (32 columns per block, bit-reversed load, DIT), then length-256 row transforms written transposed with n^-1 folded in -- instead of 16 torch.compile'd radix-2 stages (a `cat` + mul + mod pass over 3–19 MB each). The DFT over F_p is unique and the output canonical, so bit-identical by construction; `ntt_cuda_test.py`: `torch.equal` vs the torch chain, both directions × 4 sizes × 3 batch sizes + non-canonical input + round trip, all OK on the H100. **H100: intt (6, 65536) 1.24 → 0.088 ms, (36, 65536) 1.48 → 0.093, (36, 16384) 1.09 → 0.086** -- the transforms inside the tests + commit graphs were ≈ 2.5 ms of GPU per bf16 sub-batch. `field.CUDA_NTT = False` restores the torch chain. |
| `run.py` | one flag: `bench-vu --pipeline N` — **default 4 since 94fd7d3** (3 from 28b1cbc; §2d); `0`/`1` = the sequential schedule (A/B); `--impl legacy` still selectable. bf16-ampere (`vu.py`) ignores it (sequential prover, same `protocol.prove`). |

Coins / mask keys are drawn in sub-batch order in both modes (a job's first stage runs to the root before the next job starts), so the seeded-`os.urandom` harness replays identically into sequential and pipelined passes.

## 1. Bit-exactness (4090; harness = hostphase's `bitexact.py` + warm-up / `os.urandom` counter reset + `--pipeline`; `bitexact_all.sh`)

At 9268cc4 (bx12, 10:42Z), f66d0bb (bx11), 3588971 (bx10), 8d743d6 (bx9), 28b1cbc (bx7), 07d7b8f (bx6) and 820dc9d (bx5): **187 / 187 files identical** each time (sha256 of every `.stmt/.proof/.coins` + `system.bin`, main 6babe27 vs lane):

| pair (seed 20260922, 4 sub-batches) | relation | mode | zk | sequential | `--pipeline 3` |
|---|---|---|---|---|---|
| bf16h-int-zk | bf16-hopper, 170 VUs | interactive | yes | 13/13 | 13/13 |
| bf16h-int-nonzk | bf16-hopper | interactive | no | 9/9 | 9/9 |
| fp8h-int-zk | fp8-hopper, 341 VUs | interactive | yes | 13/13 | 13/13 |
| fp8h-int-nonzk | fp8-hopper | interactive | no | 9/9 | 9/9 |
| bf16h-int-zk-legacy (`--impl legacy`) | bf16-hopper | interactive | yes | 13/13 | – |
| bf16h-int-zk-ragged (3×170 + 16) | bf16-hopper | interactive | yes | 13/13 | 13/13 |
| fp8h-int-zk-ragged (3×341 + 4) | fp8-hopper | interactive | yes | 13/13 | 13/13 |
| bf16h-fs-zk | bf16-hopper | fiat-shamir | yes | 9/9 | 9/9 |

Rust `ligero-verify system-digest` identical to main on every tree; `ligero-verify batch --target-bits 128`: ACCEPT (4/4 accepted, bits 128.02–128.67) on all 8 lane dump trees.

`--pipeline 4` at 8d743d6 (bx_p4, 09:37Z, `bitexact_p4.sh`): bf16h-int-zk 13/13, fp8h-int-zk 13/13, bf16h-int-zk-ragged 13/13, bf16h-fs-zk 9/9 → **48/48 identical**, Rust batch ACCEPT on all 4 trees. The depth only changes the schedule: coins and mask keys are drawn in sub-batch order by the starter (stage 0 runs in index order), so the transcripts are depth-independent by construction, now also measured. bf16-ampere: the harness drives `relchain` runners only; bf16-ampere goes through the same `protocol.prove` (sequential path) and its gate (`gate-vu --root bench-instances/v1`, honest + mutation rejects) passes; its transcript-level comparison vs main is NOT done (needs a `vu.ChainRunner` harness variant — listed in §6). fp4-nvf4: gate only.

Gates + pytest (`gates.sh`): at 820dc9d pytest `backends/direct/ligero` 55 passed / 1 skipped; gates bf16-ampere, bf16-hopper, bf16-hopper-zk, fp8-hopper, fp8-ada, bf16-hopper-legacy, fp4-nvf4 all rc=0. Re-run rc=0 throughout at 28b1cbc (gates3), 8d743d6 (gates4), 3588971 (gates5) and 9268cc4 (gates6, 10:53Z: pytest 55 passed / 1 skipped; 7 gates rc=0).

## 2. Speed (RTX 4090, EPYC 7642 host, 170 VUs/sub-batch, l=16384, ZK interactive; ms per sub-batch, 12 sub-batches, best of 3 passes)

| tree / mode | ms/sub-batch | notes |
|---|---|---|
| main 6babe27 sequential | 35–39 | tests_w ≈ 19–20 ms (SHAKE squeeze on the host while the GPU idles), encode 5.5, merkle 3.0, tests_quad 2.3, tests_chain 3.1, openings 2.7 |
| hp2 a1f199d sequential (NTT graphs + inline squeeze) | 29.0 | tests_w 12 = squeeze 9.8 + 2 launch |
| hp2 a1f199d `--pipeline 3` | 16.2 | main thread busy 74 % of wall |
| hp2 820dc9d sequential (tests + commit graphs) | **23.5** | squeeze 7.6 inline; GPU ≈ 14 |
| hp2 820dc9d `--pipeline 3` | **15.0** | GPU-bound on this card (host busy 79 ms / 12 sub-batches = 6.6 ms; waited 99 ms) |
| hp2 0926f94 sequential / `--pipeline 3` | 22.0 / 14.4 | v4 test kernels (DRAM-bound on this card: ≈ 0), no zero fill, witness kernel 0.67 → 0.52 ms |
| hp2 8d743d6 sequential / `--pipeline 3` | **21.4 / 13.8** | int32 statics: coefficient copy 0.71 → 0.45 ms, `lincomb` 1.07 → 0.62 ms; GPU 12.0 ms/sub-batch (encode 3.8, blake3 2.6, boolcomb 0.87, lincomb 0.62, witness 0.50, hints ≈ 0.7, quad 0.40, copy 0.45, D2H/H2D 0.58) |

## 2b. H100 like-for-like (vy-hp2-host-h100 = aecb4w0in93a6i, NVIDIA H100 80GB HBM3 SXM 81559 MiB, Xeon Platinum 8462Y+ host, 8 vCPU, load ~5; campaign r22-hp2-host; `bench-vu --batch 16384 --total-vus 4096 --reps 3 --target -128 --instance-procs 16`, dumps rep 1)

All rows contract-valid (`validation.status = passed`, `reject_reasons = None`); Python `verify-batch` and Rust `ligero-verify batch` agree on every dump tree (bench's own self-check). Medians of 3; `t.total` = prover + hints_host. Pipelined rows: the phase splits are each sub-batch's share of the pass wall (`_rescale`), so they sum to `t.total` but are not per-phase kernel times.

| row | tree | run | **t.total** | tests | encode(+witness+masks in the graph) | serialization (=openings+statement) | openings | hints | merkle | R_proved | overhead vs peak | verifier | peak dev GB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bf16-hopper int-ZK | main 6babe27 | r20260923-071319-3390 | **0.662** | 0.299 | 0.110 (+0.028+0.016) | 0.097 | 0.060 | 0.062 | 0.048 | 1.90e7 | 5.20e7 | 0.608 | 2.80 |
| bf16-hopper int-ZK | lane 820dc9d `--pipeline 3` | r20260923-073751-ea7d | **0.268** | 0.146 | 0.055 | 0.026 | 0.026 | 0.025 | 0.020 | 4.70e7 | 2.11e7 | 0.620 | 4.79 |
| bf16-hopper int-ZK | lane 820dc9d `--pipeline 2` | r20260923-074754-65e8 | 0.341 | 0.189 | 0.080 | 0.018 | 0.018 | 0.013 | 0.036 | 3.70e7 | 2.68e7 | 0.629 | 3.40 |
| bf16-hopper int-ZK | lane 820dc9d sequential | r20260923-074635-4c55 | 0.454 | 0.231 | 0.131 | 0.017 | 0.016 | 0.020 | 0.044 | 2.77e7 | 3.57e7 | 0.619 | 2.80 |
| fp8-hopper int-ZK | main 6babe27 | r20260923-072030-641f | **0.379** | 0.156 | 0.059 (+0.017+0.008) | 0.053 | 0.031 | 0.061 | 0.025 | 3.32e7 | 5.96e7 | 0.327 | 2.83 |
| fp8-hopper int-ZK | lane 820dc9d `--pipeline 3` | r20260923-074439-05b0 | **0.164** | 0.083 | 0.034 | 0.012 | 0.012 | 0.019 | 0.014 | 7.66e7 | 2.58e7 | 0.339 | 5.05 |
| fp8-hopper int-ZK | lane 820dc9d sequential | r20260923-074721-d600 | 0.270 | 0.125 | 0.072 | 0.009 | 0.008 | 0.031 | 0.024 | 4.67e7 | 4.24e7 | 0.337 | 2.84 |
| bf16-hopper int-non-ZK | main 6babe27 | r20260923-072205-ec13 | 0.595 | 0.277 | 0.086 (+0.027) | 0.097 | 0.059 | 0.061 | 0.046 | 2.11e7 | 4.68e7 | 0.626 | 2.80 |
| bf16-hopper int-non-ZK | lane 820dc9d `--pipeline 3` | r20260923-074513-9cc3 | **0.249** | 0.146 | 0.048 | 0.023 | 0.023 | 0.013 | 0.019 | 5.05e7 | 1.96e7 | 0.617 | 4.69 |
| fp8-hopper int-non-ZK | main 6babe27 | r20260923-072339-8807 | 0.350 | 0.147 | 0.046 (+0.017) | 0.054 | 0.032 | 0.062 | 0.024 | 3.59e7 | 5.51e7 | 0.340 | 2.83 |
| fp8-hopper int-non-ZK | lane 820dc9d `--pipeline 3` | r20260923-074601-7cbd | **0.153** | 0.081 | 0.026 | 0.015 | 0.015 | 0.015 | 0.012 | 8.23e7 | 2.40e7 | 0.344 | 4.84 |

Notes: this host's `hashlib.shake_256` squeezes the 2.85 MB challenge block in 5.9 ms (vs 7.4–9.8 ms on the 4090 pod's EPYC), so main is ~10 % faster here than the coordinator's 0.727 s row. `--pipeline 2` is clearly worse than 3 on the H100 (the third slot is needed to cover root-wait + squeeze + msgs-wait of two in-flight sub-batches). Peak device memory 4.8–5.1 GB with 3 slots (3 static sets). First-rep pass wall includes the graph captures for the ragged layout in the sequential path (1.38 s vs 0.43 s; medians unaffected).

Pass 1 did not measure 28b1cbc / 0926f94 / 8d743d6 (the H100 was terminated at 1h13m to hold the ~1.5 h budget); pass 2 below does.

## 2c. H100 like-for-like pass 2 at 8d743d6 (vy-hp2-host-h100b, NVIDIA H100 80GB HBM3 SXM, Xeon Platinum 8480+ host (2.0 GHz base vs the 8462Y+'s 2.8), AP-IN-1, 700 W / 1980 MHz nominal, no throttle reasons; same bench-vu invocation, main 6babe27 rebuilt on this pod)

| row | tree | run | **t.total** | witness | enc+commit | arith | zk | serial | verifier | R_proved | overhead vs peak | peak dev GB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bf16-hopper int-ZK | main 6babe27 | r20260923-092330-b883 | **0.752** | 0.094 | 0.159 | 0.359 | 0.017 | 0.121 | 0.744 | 1.67e7 | 5.91e7 | 2.80 |
| bf16-hopper int-ZK | lane 8d743d6 `--pipeline 3` | r20260923-092503-c308 | **0.313** (2.40×) | 0.019 | 0.071 | 0.197 | 0.000 | 0.026 | 0.741 | 4.02e7 | 2.46e7 | 4.13 |
| bf16-hopper int-ZK | lane 8d743d6 `--pipeline 4` | r20260923-093054-8fe1 | **0.285** (2.64×) | 0.026 | 0.061 | 0.172 | 0.000 | 0.027 | 0.770 | 4.42e7 | 2.24e7 | 5.31 |
| bf16-hopper int-ZK | lane 8d743d6 sequential | r20260923-093002-4503 | 0.469 | 0.022 | 0.162 | 0.253 | 0.000 | 0.020 | 0.737 | 2.69e7 | 3.69e7 | 2.80 |
| fp8-hopper int-ZK | main 6babe27 | r20260923-092608-943e | **0.443** | 0.091 | 0.084 | 0.189 | 0.008 | 0.065 | 0.399 | 2.84e7 | 6.96e7 | 2.83 |
| fp8-hopper int-ZK | lane 8d743d6 `--pipeline 3` | r20260923-092726-38d2 | **0.170** (2.60×) | 0.019 | 0.039 | 0.096 | 0.000 | 0.016 | 0.415 | 7.39e7 | 2.68e7 | 4.36 |
| fp8-hopper int-ZK | lane 8d743d6 `--pipeline 4` | r20260923-093145-7b46 | 0.187 | 0.019 | 0.033 | 0.121 | 0.000 | 0.013 | 0.422 | 6.75e7 | 2.93e7 | 5.61 |
| bf16-hopper int-non-ZK | lane 8d743d6 `--pipeline 3` | r20260923-092831-dac0 | 0.288 | 0.017 | 0.063 | 0.184 | 0 | 0.025 | 0.746 | 4.37e7 | 2.26e7 | 4.04 |
| fp8-hopper int-non-ZK | lane 8d743d6 `--pipeline 3` | r20260923-092925-7f43 | 0.190 | 0.022 | 0.034 | 0.115 | 0 | 0.018 | 0.425 | 6.63e7 | 2.98e7 | 4.17 |

Reading: **both targets are met on this pod as well (bf16 int-ZK 0.313 / 0.285 ≤ 0.35; fp8 int-ZK 0.170 ≤ 0.20)**, and the like-for-like ratios are 2.40× / 2.64× (bf16) and 2.60× (fp8). But this pod is not the pass-1 pod: every row is 10–17 % slower here, main and lane alike (main bf16 0.662 → 0.752, main fp8 0.379 → 0.443, lane bf16 p3 0.268 → 0.313, sequential lane 0.454 → 0.469), the verifier too (0.608 → 0.744 for the same proofs), so the per-commit gain of 28b1cbc/0926f94/8d743d6 (predicted −0.6 ms GPU/sub-batch on the 4090 proxy) cannot be separated from the pod difference with these two passes; the sequential lane row (which is host-bound on the inline squeeze) moved least (+3 %), the pipelined rows most, which fits a slower single-thread host inserting bubbles between dependent stages (each stage of a sub-batch is launched by the main thread when the previous one's event fires) rather than a slower GPU. Row-to-row noise on this pod is ~±10 % (fp8 non-ZK 0.190 > fp8 ZK 0.170 is noise: non-ZK does strictly less work), so the p3-vs-p4 single rows are inconclusive (bf16: p4 −9 %, fp8: p4 +10 %); the alternating A/B (§2d) settles it.

## 2d. Pipeline depth A/B on the H100 (same pod, 8d743d6, rows alternated p3/p4/p3/p4 …, 09:40–09:46Z; `t.total` s)

| relation | `--pipeline 3` (3 rows) | `--pipeline 4` (3 rows) | p4 / p3 (medians) | peak dev GB p3 → p4 |
|---|---|---|---|---|
| bf16-hopper int-ZK | 0.313, 0.331, 0.312 (r…-092503, -093955, -094345) | 0.285, 0.272, 0.292 (r…-093054, -094046, -094254) | **0.285 / 0.313 = −9 %** | 4.13 → 5.31 |
| fp8-hopper int-ZK | 0.170, 0.177, 0.178 (r…-092726, -094137, -094514) | 0.187, 0.148, 0.145 (r…-093145, -094215, -094437) | **0.148 / 0.177 = −17 %** (one p4 outlier at 0.187, the first p4 row after a nozk row) | 4.36 → 5.61 |

Every p4 row but one beats every p3 row of its relation; on the 4090 the same A/B gave 13.8 → 12.3 ms/sub-batch (−11 %), and depths 5–6 gave nothing more there. Why 4 helps although the pipeline is "GPU-bound": with 3 slots there are moments when all three in-flight sub-batches are waiting on the host (the squeeze of one, the root-wait / msgs-wait of the other two) and the GPU idles; the fourth slot fills those gaps. The cost is one more static set (+1.2 GB). **Commit 94fd7d3 makes `--pipeline 4` the bench-vu default** (transcripts depth-independent: §1, 48/48 at p4). Confirmation rows at the default (94fd7d3, no flag): §2e.

## 2e. Decision rows at the checkpoint commit 94fd7d3, default flags (`bench-vu --batch 16384 --total-vus 4096 --reps 3 --target -128`, pod 2, 09:47–09:51Z)

| row | run | **t.total** | main 6babe27 same pod | ratio | witness | enc+commit | arith | serial | verifier | R_proved | overhead vs peak | peak dev GB | validation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bf16-hopper int-ZK | r20260923-094722-07e5 | **0.272 s** | 0.752 | **2.76×** | 0.020 | 0.060 | 0.167 | 0.023 | 0.742 | 4.62e7 | 2.14e7 | 5.31 | passed |
| fp8-hopper int-ZK | r20260923-095038-d190 | **0.146 s** | 0.443 | **3.03×** | 0.020 | 0.033 | 0.082 | 0.012 | 0.415 | 8.61e7 | 2.30e7 | 5.61 | passed |

Targets ≤ 0.35 / ≤ 0.20 s: met with 22 % / 27 % margin on the slower of the two H100 hosts. The prover is now 2.7× / 2.8× faster than its own Rust verifier's batch check (0.742 / 0.415 s) on the same rows.

## 2f. Decision rows at 9268cc4 (= 94fd7d3 + Merkle-in-graph 3588971 + v4 kernels f66d0bb + fp8 hints graph 9268cc4), default flags, pod 2, 10:36–10:41Z

| row | run | **t.total** | main 6babe27 same pod | ratio | witness | enc+commit | arith | serial | verifier | R_proved | overhead vs peak | peak dev GB | validation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bf16-hopper int-ZK | r20260923-103648-ef63 | **0.2525 s** | 0.752 / 0.734 (re-measured 10:41Z, r20260923-104058-47e7) | **2.9–3.0×** | 0.021 | 0.058 | 0.151 | 0.024 | 0.747 | 4.98e7 | 1.99e7 | 5.56 | passed |
| fp8-hopper int-ZK | r20260923-104019-b395 | **0.1342 s** | 0.443 / 0.444 (re-measured 10:42Z, r20260923-104150-300e) | **3.3×** | 0.012 | 0.035 | 0.076 | 0.010 | 0.412 | 9.37e7 | 2.11e7 | 6.00 | passed |

vs 94fd7d3 on the same pod (0.272 / 0.146): −7 % / −8 %, in line with the kernel-level −0.85 ms GPU per sub-batch (f66d0bb). Margins to the targets: 28 % / 33 %. The pod did not drift: main re-measured within 2 % of its 09:23Z rows.

## 2g. The CUDA NTT (e689b72, 11:10Z) — one decision row on pod 2, then the pods were terminated

| row | run | **t.total** | 9268cc4 same pod | main same pod | ratio vs main | witness | enc+commit | arith | serial | verifier | R_proved | overhead vs peak | validation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bf16-hopper int-ZK | r20260923-111140-abb7 (11:11Z) | **0.2337 s** | 0.2525 (−7.4 %) | 0.734 / 0.752 | **3.1–3.2×** | 0.0153 | 0.0547 | 0.1458 | 0.0251 | 0.526 | 5.38e7 | 1.84e7 | passed (`--require-result`) |
| fp8-hopper int-ZK | r20260923-111235-3942 | — | 0.1342 | 0.443 | — | | | | | | | | launched 11:12:35, not read |

**Not preserved**: both lane pods (vy-hp2-host 4090, vy-hp2-host-h100b `3ea1w8gug3gvnm`) stopped answering at ≈ 11:14Z -- terminated by the coordinator (their note at the end of this file: idle-looking between my runs, $4.23/h; the lane was also past its $12 pod budget: 4090 ≈ 5.5 h + two H100s ≈ 2.8 h ≈ $14). The bf16 row's `t.total` and phase medians above were read from the pod's `result.json` (summ.py) seconds before; the run directory was not pulled into the store. The fp8 row was in flight; gates7 was cut off. Not re-rented. The row is like-for-like with §2f (same pod, same flags, 30 minutes apart; main re-measured at 10:41Z within 2 %).

The gain matches the kernel numbers: the graphs carried ≈ 2.5 ms of torch radix-2 NTT per bf16 sub-batch (intt of the quadratic h and the chain q at (6, 65536), eval_on_coset of the 36 mask rows, `_fold_to_H` at 16384), now ≈ 0.3 ms → ≈ −2 ms of the 10.8 ms GPU per sub-batch, −0.019 s on 25 sub-batches.

Validation of e689b72 (4090, before the pod went): **bx13 187/187 files identical** vs main 6babe27 (the full §1 matrix), Rust `ligero-verify batch` ACCEPT on all 8 lane trees, `ntt_cuda_test` all OK on the H100 (26 shape/direction cases + non-canonical input + round trip), pytest 56 passed / 1 skipped (gates7, the new test included), gates bf16-ampere and bf16-hopper rc=0; **the remaining five gates (bf16-hopper-zk, fp8-hopper, fp8-ada, bf16-hopper-legacy, fp4-nvf4) were cut off by the termination** -- bf16-hopper-zk, fp8-hopper and bf16-hopper-legacy are covered transcript-for-transcript by bx13 (same provers, same `field.ntt`); fp8-ada and fp4-nvf4 are not in the matrix (their sizes either hit the same kernel or fall back to the torch chain -- `ntt_cuda.supported`), and none of the five is recorded as run. Take e689b72 with that caveat, or stop at 9268cc4 (fully gated).

## 3. Attribution after 820dc9d — H100, `--pipeline 3`, per 170-VU sub-batch (torch.profiler over a 12-sub-batch pass: 641 launches, 12.54 ms GPU per sub-batch, wall 10.9 ms → GPU-bound, the streams overlap ~1.6 ms)

| phase | GPU ms | launches | what | host syncs | D2H | owner / verdict |
|---|---|---|---|---|---|---|
| encode (`rs_encode_ligero`) | 3.52 | 2 | SIMT encoder | 0 | 0 | enc-hopper; 28 % of GPU |
| merkle (`blake3_chunks` + `blake3_parents`) | 1.90 | 21 | hash_gpu | 0 (root: 1 pinned async copy, waited) | 32 B | enc-hopper; 15 % |
| tests: `boolcomb_rows_u32_D6` | 1.42 | 1 | booleanity combination over 2391 bit rows × 65536 (627 MB read at 440 GB/s: compute-bound) | 0 | 0 | mine → v4 Montgomery kernel in 28b1cbc (≈ 1.4× on the L2 proxy) |
| tests: `lincomb_u64_D6` ×3 | 0.58 | 3 | linear / chain combinations over the int64 coefficient rows | 0 | 0 | near the memory floor (436 MB) |
| tests: `quad_u32_D6` | 0.47 | 1 | general quadratic constraints from CSR | 0 | 0 | mine; leave |
| witness (`witness_program`) | 0.78 | 1 | fused witness kernel | 0 | 0 | mine (hostphase's kernel); interpreter-bound |
| hints (`triton_poi_fused_cat_0` ×48 + fills) | ≈ 0.9 | ≈ 60 | hints graph replay: 48 `cat` kernels + `zeros` | 0 | 0 | mine; restructure to write into one preallocated matrix (hypothesis 2) |
| torch elementwise (fill ×27, copy ×74, mod ×55, add ×71, cat ×6, reduce ×6) | ≈ 1.5 | ≈ 240 | commit graph: 440 MB `zero_` (removed in 28b1cbc), `cg[:m,:l] = Cg` 431 MB copy, `% P`, mask-row copies; tests: partial-sum reductions; openings gathers | 0 | – | mine; the 431 MB copy needs `encode(..., coefs_out=)` (enc-hopper interface, §5) |
| memcpy D2H (pinned) | 0.12 | 7 | root 32 B, msgs 1.5 MB, openings 2.7 MB | 0 | 4.2 MB | done |
| SHAKE-256 squeeze (2.85 MB) | 0 (host) | – | 5.8 ms on the Xeon, worker thread, fully hidden (`wait_shake` 0) | – | – | done (sequential prover: still on its critical path: 0.454 vs 0.268) |
| main thread total | – | – | 2.2 ms busy per sub-batch (3 `cudaGraphLaunch` 0.73 ms, memcpy/launch 0.3, Python 1.2) vs 8.3 ms blocked | – | – | done: the host is no longer the bound on the H100 |

Sequential prover on the H100 (18.4 ms/sub-batch): statement 0.03 | hints 0.77 | commit graph 5.25 | merkle 1.78 | tests_w 9.25 (= squeeze 5.9 inline + upload + tests graph 2.5) | openings 0.66.

## 3b. Attribution after f66d0bb — H100 pod 2, `--pipeline 4`, bf16-hopper 170-VU sub-batch (torch.profiler, 24-sub-batch pass: 648 launches, **10.82 ms GPU per sub-batch, wall 9.6 ms** → GPU-bound; sequential 9.34 ms GPU, 18.0 ms wall)

| kernel | ms/sub-batch | launches | owner | note |
|---|---|---|---|---|
| `rs_encode_ligero` | 3.50 | 2 | enc-hopper | 32 % of GPU |
| `blake3_chunks` + `blake3_parents` | 1.77 + 0.17 | 17 + 4 | enc-hopper (hash_gpu) | inside the commit graph since 3588971; the 10 smallest tree levels are launch-latency (~50 µs) |
| compiled NTT (`triton_poi_fused_cat_0` ×48 + its `%`/`+`/copies) | 0.57 + ≈ 0.4 | ≈ 160 | mine | the mask rows' coset NTT in the commit graph + the chain test's `intt`: radix-2 stages as `cat`/`mul`/`mod` kernels on int64 → **≈ 1 ms, the largest remaining item of mine** (hypothesis 1 below) |
| `boolcomb_rows_v4_u32_D6` | 0.56 | 1 | mine | was 1.20 (f66d0bb) |
| `witness_program` | 0.48 | 1 | mine | latency-bound (512 warps) |
| `quad_u32_D6` | 0.47 | 1 | mine | gathers ≈ 1.3 GB through L2: memory-bound |
| torch copies (`direct_copy` ×75) | 0.39 | 75 | mine | the 431 MB `cg[:m,:l] = Cg` (≈ 0.26) + NTT/hints small ones |
| `lincomb_v4_u32_D6` ×2 | 0.30 | 2 | mine | was 0.58 |
| int64 `%` ×58, `+` ×70, `cat` ×6, `reduce` ×6, fills | ≈ 0.75 | ≈ 170 | mine | hints graph + tests partial reductions + NTT |
| Memcpy DtoH (pinned) | 0.12 | 7 | mine | root 32 B, msgs, openings |

Main thread (pod 2's slow Xeon): 5.3 ms busy per sub-batch before 3588971 (`launch_to_merkle` 1.27, `launch_openings` 0.99, `challenge2` 0.64, `unpack_openings` 0.60, `commit_prep` 0.61, `launch_tests_qc` 0.58, `hints` 0.41), 4.1 ms after; blocked the rest. fp8-hopper (341-VU sub-batch): the same picture, 10.9 ms GPU (encode 3.6, blake3 1.9, quad 0.63, boolcomb 0.55, NTT cats 0.54, witness 0.53); before 9268cc4 its hint generator was 283 eager launches per sub-batch (1.1 ms of main-thread time).

After e689b72 (not re-profiled -- the pods went first; from the kernel timings in §0/§2g): the compiled-NTT rows above (0.57 + ≈ 0.4 + their share of the int64 `%`/`+`/`cat`/copies, ≈ 2 ms in all) become 2 kernels per transform ≈ 0.3 ms per sub-batch; launches ≈ 648 → ≈ 450; GPU ≈ 10.8 → ≈ 8.8 ms per sub-batch, consistent with the measured −7.4 % of wall (the streams overlap ≈ 1 ms).

## 4. Threads that did not pay (5 lines each)

- **Squeeze thread attribution** (07:50Z): cProfile of the pipelined pass showed `_xof_libcrypto` on the main thread; direct thread-name tracing shows 36/36 squeezes on `ligero-squeeze` (9.2 ms avg on the EPYC, 5.8 on the Xeon). Python 3.12's cProfile captures threads started after `enable()`; misleading, not a bug.
- **Stage-0 host time** (3.3 ms/sub-batch in `prove_many` vs 0.6 ms of traced marks on the 4090): not the HotWorker warming loop (disabling it: unchanged), not `Event` creation. Unresolved; irrelevant on the H100 where the main thread is 2.2 ms busy vs 8.3 blocked.
- **Witness kernel occupancy** (09:00Z): block size 32–256 makes no difference (0.67 ms either way) -- l = 16384 columns = 512 warps = ONE warp per scheduler on 128/132 SMs, so the kernel is latency-bound whatever the block shape; 255 registers + 1.9 KB of spills before and after the register-resident codegen (the compiler already kept short-lived values in registers; the gain came from the modulos). Re-deriving bits / selectors from the kept `x` / `sx` instead of one register each: no change. The only lever left is intra-column parallelism (split the program's independent chains -- decodes, the 32 products -- over 2–4 threads per column with shared-memory exchange: a DAG partition in the code generator, ~1–2 h, ≈ −0.4 ms/sub-batch on the H100).
- **Second squeeze worker** (09:50Z, 4090, depth 3, `LIGERO_SQUEEZE_WORKERS=2` round-robin, 3 passes each): 13.7 → 14.0 ms/sub-batch, i.e. nothing; the squeeze avg per call 9.7 → 9.9 ms. So queueing behind a single squeeze worker is not why depth 4 beats depth 3; reverted (not in the branch). The main thread's stage-0 time (3.2 ms/sub-batch on the EPYC: coins, marshal lookup, first `job.step()` = the commit graph launch + hints graph replay + mask key upload) is the likelier bubble source: while it runs, the two other in-flight sub-batches' event hand-offs wait.
- **v4 kernels on the 4090**: DRAM-bound at 850–890 GB/s for both scalar and v4 on the real shapes (the card's ~1 TB/s); only the L2-resident 34 MB proxy separates them (1.43–1.47×). `#pragma unroll 4` helps lincomb (1.67×) but hurts boolcomb (1.32×); kept 2.

## 5. Interface notes for other lanes (not changed by me)

- `encode_simt.encode(W, S, want_coefs=True, out=U)` returns a fresh (m, l) int64 coefficient matrix that the commit graph copies into the static `coefs` (431 MB read + write ≈ 0.3 ms on the H100 per sub-batch). A `coefs_out=` parameter (or an int32 coefficient output — the tests read them as u32 anyway) would remove the copy and halve the tests' coefficient traffic (`lincomb_u64` ×3: 0.58 ms).
- Merkle: ~21 hash_gpu launches per sub-batch inside the pipelined pass; fine.

## 6. Next hypotheses (ranked; the pipeline is GPU-bound on the H100 at depth 4 -- 10.8 ms GPU vs 9.6 ms wall per bf16 sub-batch -- so every item is GPU time unless marked)

1. ~~CUDA NTT~~ **done (e689b72, §2g): −7.4 % on the bf16 row.** What is left of it: the `eval_on_coset` / `_fold_to_H` prep around the kernel is still 3–4 eager elementwise kernels (`% P`, `* coset_scale`, `% P`, the zero pad `cat`) -- fold the coset scale into kernel 1's load (one extra table read) and let kernel 1 read a shorter row with implicit zeros (`K < n`): ≈ −0.1 ms/sub-batch and −4 launches per call, 30 min. The kernels use `(a*b) % P` on u64 -- Montgomery as in `encode_ntt_simt.py` would halve their (already small) time.
2. **Coefficient copy** `cg[:m, :l] = Cg` (431 MB, ≈ 0.26 ms): needs `encode_simt.encode(..., coefs_out=)` or an int32 coefficient output with a row stride (§5, enc-hopper's file) -- or a split static layout (`coefs_lo` (M, l) written by the encoder in place, `coefs_hi` (M, k − l)) with the linear tests as two `lincomb` launches per combination (columns are independent; the sums are exact so the split is bit-exact). ~1 h.
3. **Witness kernel** (0.48 ms, latency-bound: one thread per column = 512 warps on 132 SMs; block shape irrelevant, measured): split each column's program over 2–4 threads (a DAG partition of the row program in the code generator, shared-memory exchange of the ~30 cross-partition values). ~2 h, ≈ −0.3 ms. Its `prod` rows still use `(x * y) % P` on u64 (a 64-bit modulo each): a 32-bit-multiplicand + Barrett form is another ~−0.05 ms.
4. **quad_u32** (0.47 ms): ≈ 1.3 GB of row gathers per sub-batch through L2 -- stage the constraint's rows for a column tile in shared memory (the CSR tables are per constraint, ~6 rows each). ~1.5 h, ≈ −0.2 ms.
5. **Hints graph** (bf16: ≈ 130 tiny int64 kernels ≈ 0.3–0.4 ms): `torch.compile` `_hints_eager` (inductor fuses the elementwise chains) inside the graph; the `argmax` first-index tie rule must be checked exact. ~1 h.
6. **Pipeline schedule** (host, only on slow hosts): depth 4 beats 3 by 9–17 % although the GPU is the bound (§2d); a second squeeze worker did nothing (§4). Stage 0 (coins + marshal + commit graph launch: 1.6 ms of main thread on pod 2 after 3588971) is the largest remaining main-thread item; `challenge2` (0.64 ms: the column-challenge hash on the main thread) could run on the hot worker.
7. **Sequential prover** (`--pipeline 0`, bf16-ampere `vu.py`, fp4): the inline squeeze (5.9–8 ms) is its critical path; a `vu.py` `prove_vus_many` equivalent would give bf16-ampere the same 1.7× -- `vu.py` coin hooks are live-verifier's; coordinate.
8. Encode + Merkle (3.5 + 1.9 = 5.4 ms of the ≈ 8.8 ms GPU per sub-batch after e689b72) are enc-hopper's; the pipelined floor with everything else at zero is ≈ 25 × 5.4 / (overlap ≈ 1.1) ≈ 0.12 s on the H100 for the bf16 row. Items 2–5 above are ≈ 1.2 ms of the remaining 3.4 ms of lane-side GPU per sub-batch.

## 7. Spec notes

- The coordinator's "serialization 0.110 s" is `t.serialization = openings + statement` (a derived contract measurement), not `proof_bytes`; the proof writer runs outside every timed interval (after the verifier timer). A device-side packer would not move `t.total`; deprioritized in favour of overlap (item 6 of the spec), which did.
- The spec's "tests_w 10.5 ms wall vs 0.74 ms GPU" understates the tests' GPU time: on the H100 the three fused test kernels are 2.5 ms per sub-batch (the booleanity kernel compute-bound), which only became visible once the host was out of the way.
- Main on this H100 host measures 0.662 s, not 0.727 s (faster SHAKE on the Xeon 8462Y+); like-for-like on one pod is the only fair comparison.

## 8. Artifacts

Runs (campaign r22-hp2-host, pulled into the laptop store 07:50–08:11Z, `research data push --pending --jobs 8` at 08:17Z): main rows r20260923-071319-3390, -072030-641f, -072205-ec13, -072339-8807; lane rows r20260923-073751-ea7d, -074439-05b0, -074513-9cc3, -074601-7cbd, -074635-4c55, -074721-d600, -074754-65e8. Pass 2 (pod 2, pulled 09:57Z): main r20260923-092330-b883, -092608-943e; lane 8d743d6 r20260923-092503-c308, -092726-38d2, -092831-dac0, -092925-7f43, -093002-4503, -093054-8fe1, -093145-7b46, A/B -093955-b79e, -094046-9192, -094137-297b, -094215-4beb, -094254-22e6, -094345-09b3, -094437-f648, -094514-f2cf; lane 94fd7d3 decision rows **r20260923-094722-07e5** (bf16 0.272 s), **r20260923-095038-d190** (fp8 0.146 s). p4 bit-exactness: pod `/workspace/hp2/logs/bx_p4.out`. Pass 2c–2f (pod 2, pulled 10:44–10:52Z, `research data push --pending` 10:53Z: 21/21 preserved on s3://verity-dev): lane 3588971 / f66d0bb probes, lane 9268cc4 decision rows **r20260923-103648-ef63** (bf16 0.2525 s), **r20260923-104019-b395** (fp8 0.1342 s), main drift rows r20260923-104058-47e7 (0.734), -104150-300e (0.444). Labels (11:25Z, `--by hp2-host`; vocabulary keys candidate/proof_class/soundness/K/B/hardware/authentication/campaign/relation/mode/zk/overhead/seconds_per_vu/track/scope/label/note) on the four pod-2 result artifacts: lane 9268cc4 bf16 art:44c768cd… (r20260923-103648-ef63), fp8 art:1e73dc00… (-104019-b395); main 6babe27 bf16 art:7d2fe799… (-104058-47e7), fp8 art:a603f173… (-104150-300e). Snapshot **`hp2-host-v1` = art:8c740e39863df7bd1a396cb52c194e73236ebdb335d460092e2a5f9c43fb898e** (16 members: result + run-files of the 9268cc4, 94fd7d3 and same-pod main rows), PRESERVED on s3://verity-dev 11:37Z (pushed by id; `push --pending` was abandoned -- it queues behind every other lane's pending uploads). No `verified=` labels written. Pass 2g (e689b72): r20260923-111140-abb7 (bf16 0.2337 s) exists only as this note's §2g numbers + a local `remote.json`; the pod was terminated before the pull (§2g). Bit-exactness and gate logs lived on the 4090 pod (`/workspace/hp2/logs/bx{5..13}.log`, `gates{1..7}.log`) and went with it; their results are transcribed in §1 / §2g as they were read (bx13 and gates7 lines were read at 11:11Z, the pytest 56-passed line included).


> coordinator 11:25Z: `vy-hp2-host-h100b` and `vy-hp2-host` were idle (0 % GPU, no python) 35 min after your FINAL checkpoint; terminated by the coordinator to stop the $4.23/h burn. 9268cc4 is staged on lane/post-freeze (99cd327) for the post-Wave-2 merge.
