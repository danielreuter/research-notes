---
id: 20261004T2202Z-report-relay-docs-band-decode-benchmark
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/band-decode-benchmark.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/band-decode-benchmark.md`, sha256 `3ae873883969b26534cf0b59652c19762adb11adcd2d9acbbf076062a699addd`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Band decode benchmark (re-freeze of the dense-decode benchmark, 28 Sep 2026, 01:46Z)

**Frozen** on the reference codec `band.BAND12` (`band-chain/d12/v1`) at `band.SECURE_FIRST`, PR [#166](https://github.com/danielreuter/verity/pull/166) head `48967d50`, which made the band the secure-first default. The vLLM branch (#172) and this stream's branch ([#188](https://github.com/danielreuter/verity/pull/188)) are rebased onto it. `dense.SECURE_FIRST` is now `dense.POINT_64K`.

Everything except the scheme is unchanged from `docs/dense-decode-benchmark.md`: gates, setup, workload, metrics and harness. Its dense results are the before case here. Why the band is the secure-first scheme: `docs/band-vs-dense.md`.

## 1. Scheme (byte-identical to the reference's `band.BAND12`)

~~~text
segment      B = 512 blocks of ℓ = 65,536 B (64 KiB), 32 MiB           (as dense)
graph        one layer, band of in-degree d = 12: parents(v) = v−1, …, v−min(v, 12)
H            the overwrite chain over Feistel-SHAKE256 Π₂ from h_0 = iv(dom(tag_s, v)), parents absorbed newest first
C_v          key_v ⊕ W_v
audit        D = 5 Π₂ calls per answer, k = 111 (band_meets_64, for every d ≥ 5)
~~~

- **Cost.** Block v costs min(v, 12) + 1 Π₂ calls.
  - A segment costs 6,578 calls (dense: 131,328), which is 12.85 per block on average.
  - Decode depth is 13 dependent calls (dense: 512).
  - Encode depth is 6,578 calls per segment, one chain.
- **Pinned by the reference:**
  - byte format, parent order (newest first) and `dom`: `twins.reference("band-chain/d12/v1")` gives `BAND12` at `BandParams(512, 524288, 12)`;
  - the GPU twin (`twins.twin(BAND12)`) equals the reference codec on encode, decode and arbitrary-byte decode (`test_band_twin_matches_the_reference_band_codec`).
- **The reference Python, per 32 MiB segment** (#166): band encode 23.9 s, full decode check 24.6 s; dense decode 494 s.
- **Decode from `C` on every use, with no plaintext cache** (as dense).

## 2–4. Gates, setup, workload (unchanged)

- **Gates:**
  - `vectors`: the band's known-answer vectors `band/small/blocks` (`BandParams(16, 64, 4, 2)`) and `band/64kb/prefix16`, by GPU encode, then decoded back.
  - `segment_vector`, at the baseline and at milestones: `band/64kb/segment`, one whole secure-first segment GPU-encoded, hashed and decoded back. This is also the measured encode time per segment.
  - `reference_decode`: sampled blocks decoded by the reference's `key_program` over `geometry.parents(v)`.
  - `timed_audit`, at milestones: a live responder under the benchmark's passes, k = 111, Δ = 0.5 ms plus the p99.9 round trip.
- **Setup:** one L40S (`vy-pous-opt-g1`, driver **580.126.09**, PyTorch 2.13.0+cu129, nvcc 12.4, `sm_89`), with recorded Attempts and medians of 3 on the device clock.
  - The dense before case ran on driver 570.124.06. Parity check on this pod: the fused kernel at 15,360 rows takes 82.4 ms here against 82.5 ms there (no DRAM: 42.1 against 42.0 ms).
- **Workload:**
  - the whole Qwen2.5-0.5B, and Qwen2.5-7B layer 0 plus its head (`workloads/dense_decode_shapes.json`);
  - one model pass decodes every tile's blocks, then runs the GEMMs at T = 1, 8, 32 and 2048.
- **Primary metric:** EWB at T = 1, 8 and 32, next to the plaintext GEMM and the 864 GB/s HBM peak.
- **Harness:** `verity-vllm pous-dense-bench --codec band-chain/d12/v1`. The in-degree is read from `geometry.parents(v)` and checked to be a band.

## 5. Before and after

### Before: dense (`docs/dense-decode-benchmark.md` §6)

| | Dense baseline (`r20260927-234256-105d`) | Dense M2 of record (`r20260928-005535-6ca0`) |
|---|---|---|
| 0.5B pass / EWB | 79.52 s / 12.42 MB/s | 26.65 s / 37.06 MB/s |
| 7B pass / EWB | 115.09 s / 13.52 MB/s | 38.21 s / 40.73 MB/s |
| Segment alone (latency) | 11.32 s | 11.37 s |

### Band baseline (`r20260928-014912-5f49`, frozen scheme, the dense M2 kernels as they stood at the switch)

All gates passed:

- `vectors`: `band/small/blocks` and `band/64kb/prefix16`.
- `segment_vector`: one whole 32 MiB segment GPU-encoded equals `band/64kb/segment` and decodes back.
- `reference_decode`: 15 sampled blocks of 2 segments, blocks 0, 1 and 511 of each included.

Kernels: warp below 500 rows, lane pair from 500 to 7,500, fused above, row-major state. Medians of 3.

| | 0.5B (15,075 blocks, 193,635 Π₂ calls) | 7B layer 0 + head (23,744 blocks, 305,006 calls) |
|---|---|---|
| Pass (decode) | 1.139 s (1.15 / 1.14 / 1.14) | 1.741 s |
| **EWB at T = 1 / 8 / 32** | **866 MB/s** (70× the dense baseline, 23× dense M2) | **893 MB/s** (66×, 22×) |
| Plaintext GEMM EWB, T = 1 / 8 / 32 | 581 / 506 / 476 GB/s | 728 / 704 / 613 GB/s |
| Keccak-f/s, share of the integer rate (frozen nominal / SASS count) | 1.64 G, 21.5% / 34% | 1.69 G, 22.2% / 35% |
| Prefill (T = 2048) | GEMMs 11.3 ms against 1.139 s of decode | 13.6 ms |
| Latency: one segment alone / first tile | 0.344 s / 0.293 s (32 blocks) | 0.343 s / 0.323 s (504 blocks) |

- **Encode per segment:** 132.2 s measured, by GPU encode of the whole `band/64kb/segment` input. That is 6,578 dependent calls at 20.1 ms. The reference Python takes 23.9 s.
  - A single chain of dependent Π₂ calls runs on one warp here, which is slower per call than a CPU core's SHAKE (3.6 ms).
  - So the GPU encoder only pays across segments: 30 segments encode in the same 132 s of wall time, which is 4.4 s per segment.
  - A parallel CPU encoder (one segment per core) would be 23.9 s per segment per core.
- **Dense, for comparison:** 79.5 s to decode the 0.5B at baseline and 26.7 s at M2; the latency floor per segment was 11.3 s.

### Overnight window: instructions per Keccak-f, and where the ceiling really is (closed 05:12Z)

**Correction to the earlier "~2.5 GB/s ceiling".** That figure was the INT32 compute ceiling at full GPU occupancy. The 0.5B pass can't reach it, because the kernel is **memory-bound**, not instruction- or occupancy-bound. The frozen 0.5B at about 1.55 GB/s is essentially at the practical ceiling of this streaming-Feistel design on the L40S. Fewer instructions per Keccak-f cannot move it; only less memory traffic per Π₂ could, and that traffic is already at its floor for the frozen scheme.

#### Frozen metric, run of record (`r20260928-045955-1d02`)

Pod `elc3g9nnwcufql`, driver 580.178.04, cgroup v2 with a 27.2-core quota. All gates passed: `vectors`, `segment_vector` (132.2 s per segment), `reference_decode`, `pass_matches_reference` (13 blocks of the 0.5B pass and 17 of the 7B pass) and `timed_audit` (20 of 20, worst answer 0.405 ms against a 0.551 ms limit).

| Run | 0.5B pass | **0.5B EWB** | 7B pass | **7B EWB** | Keccak-f/s (0.5B) |
|---|---|---|---|---|---|
| Dense baseline (before case) | 79.52 s | 12.4 MB/s | 115.09 s | 13.5 MB/s | 0.47 G |
| Band baseline (`r20260928-014912-5f49`) | 1.139 s | 866 MB/s | 1.741 s | 893 MB/s | 1.64 G |
| Previous window's final (`r20260928-032701-b4a1`) | 0.643 s | 1,532 MB/s | 1.177 s | 1,319 MB/s | 2.91 G |
| **Overnight run of record** (`r20260928-045955-1d02`) | **0.637 s** | **1,550 MB/s** | **1.17 s** | **1,331 MB/s** | 2.94 G |

- The overnight kernels are the previous window's, plus a B-array ρ/π/χ that compiles to identical SASS. So the 1.2% gain is host variance.
- **Totals:** 1.79× and 1.49× over the band baseline; 125× and 98× over the dense baseline.

#### What limits it (measured on this pod)

- **The round runs at the hardware integer ceiling.** A pure-register kernel (`keccak_bench`, no memory traffic) does 4.83 G Keccak-f/s at full occupancy (218,112 threads). The INT32 ceiling is 142 SMs × 64 INT32 lanes × 2.52 GHz ÷ 4,776 instructions per Keccak-f = 4.79 G/s. There is no scheduling slack left to recover.
- **The round's instruction count is near its minimum.** SASS is 199 instructions per round: 136 LOP3 and 58 funnel shifts (SHF). The minimum for this formulation is about 190: χ 50, θ 80, ρ 48 SHF plus θ's 10, ι 2.
  - The in-place ρ/π cycle compiled to the same SASS as the fully unrolled B-array form (808 instructions either way), so there were no wasted moves.
  - Unrolling the round loop by 2, 4 or 8 moved the real kernel by under 0.3% (previous window).
- **Bit-interleaved lanes don't pay on `sm_89`.** A funnel shift already rotates a 64-bit lane in 2 instructions, and so does an interleaved rotation.
  - Only θ's five rotate-by-1s (and ρ's single offset-1 lane) drop to one shift, about 6 of 199 instructions per round (3%).
  - Converting at the plain-byte boundaries (the parent read, the prefix, the `W` write) costs about that much, so I didn't implement it.
- **Splitting a state across two threads doesn't help at these row counts.** In the pure-register bench, per state:

  | States | One per thread | Split across a lane pair |
  |---|---|---|
  | 7,500 | 1.94 G/s | 2.43 G/s |
  | 11,872 | 3.06 G/s | 2.25 G/s |
  | 15,075 | 3.88 G/s | 2.81 G/s |
  | 109,056 | 4.55 G/s | 3.66 G/s |

  The split's shuffles cost more than its parallelism buys above about 9k states.
- **The real kernel is memory-bound.** The same 15,075 rows compute at 3.95 G/s in registers but decode at 2.94 G/s in the real kernel, so memory costs 26%.
  - Decoding 1×, 2× and 4× the 0.5B's rows gives a flat 2.94, 2.93 and 2.91 G Keccak-f/s (0.637, 1.276 and 2.574 s).
  - Past about 18,000 rows a single launch collapses (the cliff), so extra rows run as sequential ~15k launches and throughput doesn't rise.
  - The pass moves about 284 GB (each Π₂ reads one 69.6 KB padded half, then 10 rounds read and rewrite a half; plus the `W` write). That is about 450 GB/s, about half the 864 GB/s HBM peak.
  - That traffic is the floor for a streaming Feistel: each round must read the half being XORed and write it back, and a 65.5 KB half can't stay on-chip at 15k rows (106 rows × 65.5 KB per SM against about 100 KB of shared memory).
  - Shrinking the half to fit on-chip would change the label width, which is a scheme decision, not an implementation one.

#### SECONDARY, not the frozen metric: how much decode an overlapped decode hides in a vLLM forward

An emulated vLLM forward over the 0.5B's 24 decoder layers, with its real shapes and the benchmark's kernels (`--overlap-study`, same run):

- **serial:** decode layer N, then its matmuls;
- **overlapped:** layer N+1 decoded on a side stream while layer N's matmuls run;
- **batched:** every layer decoded in one launch, then the matmuls, as the frozen pass does.

| Tokens | Matmuls alone | Serial per-layer | Overlapped | Batched | Decode hidden by overlap |
|---|---|---|---|---|---|
| 1 (decode) | 1.2 ms | 6.948 s | 6.948 s | **0.583 s** | about 0 (−0.3 ms) |
| 2048 (prefill) | 7.6 ms | 6.954 s | 7.773 s | **0.589 s** | **−0.82 s** (overlap is slower) |

- **Overlapping the next layer's decode with the current matmuls hides essentially nothing.** The matmuls total 1.2–7.6 ms against about 7 s of decode, so there is nothing to hide the decode behind.
- **At prefill it is net harmful.** The larger matmuls compete with the decode for SMs and slow the decode, which is on the critical path.
- **Per-layer decode is about 12× slower than batched.** Each layer's ~455 blocks are too few rows to fill the GPU: 0.29 s per layer, latency-bound on its 13 dependent steps.

**For the pipelining decision:**

- Neither intra-pass overlap nor cross-pass pipelining raises decode throughput. The first has no matmul time to hide behind. The second adds rows, and past about 18k rows the memory-bound kernel doesn't speed up.
- The lever that does work is **batching all of a forward's decode into one launch of up to about 15–18k rows**.
- vLLM today decodes 3 groups per forward (1.334 s), including the tied embedding twice (once as `embed_tokens`, once as `lm_head`, 9 segments each).
- Decoding the unique weights once, in one batch (about 15.9k blocks, the size of the frozen pass), should bring vLLM's decode close to the frozen pass's 0.64 s, roughly halving it. This is an estimate from the measured frozen pass, not a vLLM measurement.

### Final table, compute-side window (closed 03:35Z; pods down; $4.13 on the guard's tally, $0.68 of it this window)

Frozen band metric, medians of 3 on the device clock. This window ran on pod `jf7lr0rtkqaq6f` (driver 550.144.03, cgroup v1).

| Run (Attempt) | What changed | 0.5B pass | **0.5B EWB** | 7B pass | **7B EWB** | vLLM decode per forward |
|---|---|---|---|---|---|---|
| Band baseline (`r20260928-014912-5f49`) | the dense M2 kernels | 1.139 s | 866 MB/s | 1.741 s | 893 MB/s | |
| Band M3 (`r20260928-023352-d3e5`, other host) | chunk-major, 144-byte slots, width-specialized, split above 18k rows | 0.697 s | 1,416 MB/s | 1.254 s | 1,238 MB/s | 1.956 s (M1 kernels) |
| Split and pair specialization (`r20260928-025949-6520`) | each Keccak state split across a lane pair below 9,500 rows; lane-pair kernel compiled for the 64 KiB half; chunk-major from 1,024 rows | 0.71 s | 1,380 MB/s | 1.29 s | 1,205 MB/s | **1.388 s** |
| Fused-X (`r20260928-031517-2b46`) | round 1 reads each step's parent (or the pad) itself, with no gather | 0.66 s | 1,497 MB/s | 1.20 s | 1,296 MB/s | |
| **Final of record** (`r20260928-032701-b4a1`) | whole chain per row in one launch (`band_chain_kernel`), `W` written in place | **0.643 s** | **1,532 MB/s** | **1.177 s** | **1,319 MB/s** | 1.334 s |

- **The frozen passes don't use the split kernel,** so the M3 and split rows ran the same pass kernels. Their 2.5% gap is host variance: the same kernel takes 46.5 ms on the M3 host and 47.3 ms on this one.
- **Gains on this host:** the fused parent read and the whole-chain kernel together gave 1.11× (0.5B) and 1.09× (7B).
- **Totals:** 1.77× and 1.48× over the band baseline; 123× and 98× over the dense baseline.
- **Compute:** Keccak-f runs at 2.91 G/s for the 0.5B, 61% of the 4.8 G/s INT32 ceiling by SASS count (38.1% on the frozen nominal count). EWB is 61% of the about 2.5 GB/s ceiling.
- **Splitting each Keccak state across two threads:** a 64-bit rotation becomes one shuffle plus one funnel shift, identical on both lanes. It is bit-identical and a win only below about 9,500 rows. Per launch:

  | Rows | Unsplit, chunk-major | Split | Row-major lane pair |
  |---|---|---|---|
  | 1,000 | 39.0 ms | 24.1 ms | 27.0 ms |
  | 4,608 | 39.1 ms | 25.9 ms | 37.8 ms |
  | 8,000 | 39.3 ms | 31.8 ms | 48.7 ms |
  | 11,264 | 42.1 ms | 53.9 ms | 71.7 ms |
  | 15,075 | 47.3 ms | 63.9 ms | 86.7 ms |

  - Once the unsplit kernel fills the GPU, the pair's 29 shuffles per round cost more than its parallelism buys.
  - So the frozen passes (15,075 rows, and the 7B's 11,872-row halves) keep the unsplit kernel. vLLM's 4,608-row groups take the split: 0.60 to 0.376 s per 9-segment group.
- **Width specialization of the smaller kernels.** The lane-pair kernel is now compiled for the 64 KiB half. vLLM's forward decode went from 1.956 s at M1 to 1.334 s (0.846 tokens/s), and the microbenchmark predicts 1.331 s (ratio 1.003).
- **Block size doesn't matter:** 32, 64 and 128 threads all give 46.9–47.1 ms at 15,075 rows; 96 and 256 are worse.
- **Final gates, all passed:**
  - `vectors`, `segment_vector` (131.9 s per segment) and `reference_decode`;
  - `pass_matches_reference`: 13 sampled blocks of the 0.5B pass and 17 of the 7B pass, including blocks 0, 1, 12, 13, 511 and each fourth segment's last;
  - `timed_audit`: harness 20 of 20, worst 0.27 ms against a 0.54 ms limit; vLLM 20 of 20, worst 0.358 ms against 0.544 ms.
- **The pass-output gate ran on every run of record in this window.**

### Deployment requirement: the responder runs without a CFS quota

- **Requirement.** The in-process responder must run where no CFS bandwidth quota applies to its thread: a dedicated cpuset, or a container without `--cpus` or `cpu.max`.
  - A quota exhausted within its 100 ms period stops every thread of the cgroup for the rest of the period. That includes the pinned, busy-polling responder, however idle it is itself.
  - A timed answer then waits out the throttle. This is independent of the GPU path, whose copy stays under 0.15 ms.
- **Evidence.**
  - `r20260928-015502-80f1` (harness audit rejected): one answer took 419 ms against a 0.536 ms limit, with the device side clean.
  - That pod's container had `cpu.max 1360000 100000` (13.6 cores).
  - The later audits that passed still saw the counters rise inside their windows: `nr_throttled` 22 to 23 and 11 to 13. They were accepted only because no answer happened to fall in a throttled period.
- **Tested, cheaply: none of the three RunPod L40S host types gives an unquota'd container.**
  - `eufevlq3kiaevi` and `33k47he3ixcxr1` (cgroup v2): `cpu.max` of 13.6 cores; the file isn't writable from inside.
  - `jf7lr0rtkqaq6f` (cgroup v1, driver 550.144.03): no CPU controller is visible, but 32 busy processes get 63.7 CPU-seconds in 3.05 s, about 21 effective cores of 112.
  - So a no-quota audit needs a host where we control the cgroup (bare metal, or a VM with its own kernel). It could not be run here.
- **Mitigation until then:** keep the serving process's CPU use well under the quota, and record the CFS counters around every audit, as `--audit` now does.
  - Cap torch's thread pools (`OMP_NUM_THREADS`, `torch.set_num_threads`). They size themselves from `nproc`, which is 112–128 on these hosts.
  - No reference-decode worker pool runs during audits.

### Final table (window closed 02:40Z; pods down, $3.45 of $40)

Frozen band metric, one L40S, medians of 3 on the device clock. EWB is the same at T = 1, 8 and 32 to within 0.1%.

| Run (Attempt) | What changed | 0.5B pass | **0.5B EWB** | 7B pass | **7B EWB** | Keccak-f/s (0.5B, 7B) |
|---|---|---|---|---|---|---|
| Dense baseline (`r20260927-234256-105d`) | the before case | 79.52 s | 12.4 MB/s | 115.09 s | 13.5 MB/s | 0.47 G, 0.51 G |
| Dense M2 (`r20260928-005535-6ca0`) | fused and lane-pair kernels | 26.65 s | 37.1 MB/s | 38.21 s | 40.7 MB/s | 1.39 G, 1.53 G |
| **Band baseline** (`r20260928-014912-5f49`) | the dense M2 kernels, row-major | 1.139 s | **866 MB/s** | 1.741 s | **893 MB/s** | 1.64 G, 1.69 G |
| Band M1 (`r20260928-020350-a578`) | chunk-major state, parents gathered into it | 0.847 s | 1,164 MB/s | 1.433 s | 1,085 MB/s | 2.21 G, 2.06 G |
| Band M2 (`r20260928-022533-d58b`) | memory: 144-byte slots with 128-bit I/O and the first absorb prefetched; instructions: kernel compiled for the 8,196-word half | 0.700 s | 1,410 MB/s | 1.350 s | 1,151 MB/s | 2.68 G, 2.18 G |
| Band M3 (`r20260928-023352-d3e5`) | launches past 18,000 rows split into sequential pieces | 0.697 s | 1,416 MB/s | 1.254 s | 1,238 MB/s | 2.69 G, 2.35 G |
| **Final of record** (`r20260928-023551-ddd0`) | M3, plus a gate on the timed pass's own output | **0.696 s** | **1,416 MB/s** | **1.256 s** | **1,237 MB/s** | 2.69 G, 2.35 G |

- **Against the band baseline:** 1.64× (0.5B) and 1.39× (7B). Against the dense baseline: 114× and 91×.
- **Against the ceiling:** the 0.5B is at 57% of the about 2.5 GB/s INT32 ceiling.
  - Keccak-f runs at 2.69 G/s, 56% of 4.8 G/s by the SASS count (35.2% on the frozen nominal count).
- **Plaintext GEMM EWB** in the final run:
  - 0.5B: 586 / 499 / 469 GB/s;
  - 7B: 733 / 706 / 626 GB/s.
- **Kernel alone at 15,075 rows,** each step of the 0.5B pass:
  - M1: 58.2 ms;
  - the memory changes: 54.2 ms (1.07×);
  - the width-specialized kernel: 46.5 ms (a further 1.17×).
  - For reference, the row-major fused kernel without DRAM traffic took 42.0 ms.
- **Launch size.** The per-launch rate peaks near 18,000 rows (3.29 G/s) and collapses past it: 23,744 rows take 93.6 ms in one launch, 84.7 ms in two. That is about one warp per scheduler on the L40S.
- **Final gates, all passed:**
  - `vectors`;
  - `reference_decode`;
  - `pass_matches_reference` per model: sampled blocks of the timed chunk-major pass itself (blocks 0, 1, 12, 13, 511, each fourth segment's last and the pass's last), 13 blocks for the 0.5B and 17 for the 7B;
  - `timed_audit`: 20 of 20 accepted, worst answer 0.201 ms against a 0.541 ms limit, device-side p99.9 41 µs.
  - The CFS counters rose by 2 throttles inside the audit window without hitting an answer.
  - M1 and M2 were gated on the chunk-major path by the unit test only (`test_chunked_decode_matches_row_major`); the final run gates it on the benchmark's own pass.
  - `segment_vector` last ran at M2: 131.9 s per segment. Encode doesn't use the chunk-major path.
- **Pods and drivers:** M1 ran on `eufevlq3kiaevi` (driver 580.126.09); M2, M3 and the final run on `33k47he3ixcxr1` (driver 580.159.04, the same 13.6-core CFS quota). The fused kernel's timing matched across drivers.
- **Next:** the compute side, with the pass at 57% of the INT32 ceiling:
  - bit-interleaved lanes splitting each Keccak state across two threads, which doubles threads below the 18k-row cliff;
  - specializing the row-major kernels as well, for vLLM's smaller groups;
  - cross-pass pipelining, pending Daniel.

### Band M1: chunk-major state (`r20260928-020350-a578`, all four gates)

Kernels: the M2 dispatch for decodes under 4,096 rows. Larger decodes keep a chunk-major state (`feistel_chunked_kernel`, 64-thread blocks), with parents gathered straight into it (`chunked_gather`). All four gates passed: `vectors`, `segment_vector`, `reference_decode` and `timed_audit`.

| | 0.5B | 7B layer 0 + head |
|---|---|---|
| Pass | 0.847 s (0.84 / 0.85 / 0.85), against 1.139 at baseline | 1.433 s, against 1.741 |
| **EWB at T = 1 / 8 / 32** | **1,164 MB/s (1.34× the band baseline, 94× the dense baseline)** | **1,085 MB/s (1.22×, 80×)** |
| Plaintext GEMM EWB | 587 / 503 / 472 GB/s | 730 / 706 / 618 GB/s |
| Keccak-f/s, share of the integer rate (nominal / SASS count) | 2.21 G, 28.9% / 46% | 2.06 G, 27.0% / 43% |
| Latency: segment alone / first tile | 0.346 s / 0.293 s | 0.343 s / 0.318 s |
| Encode per segment (whole-segment vector) | 132.2 s | |

- **G3 (timed audit, k = 111), accepted on both paths:**
  - Under live harness passes: 20 of 20 audits, 0 late, 0 wrong. The worst answer was 0.189 ms against a 0.536 ms limit; server-side max 0.14 ms; device-side p99.9 24 µs.
  - Under a live vLLM band forward (`r20260928-015502-80f1`): 20 of 20, 0 late. The worst answer was 0.169 ms against 0.538 ms; device-side p99.9 36 µs.
  - `TimedVerifier` accepted the deployment: Δ + RTT is about 0.54 ms, an effective D of 1, far inside the cliff at d = 12.
- **The vLLM check (`r20260928-015502-80f1`).** vLLM serves Qwen2.5-0.5B from the band codec (`pous-bench --codec band-chain/d12/v1 --unencoded`, one decode group for all layers) at 1.97 s per forward, against 48.7 s dense.
  - It decodes three groups: 9 segments in 0.599 s, 22 in 0.754 s, 9 in 0.602 s.
  - The microbenchmark predicts 1.952 s of decode against 1.956 s measured (ratio 1.002).
- **A timing finding (first M1 attempt, `r20260928-015502-80f1`, harness audit rejected).** One answer of the audit of record took 419 ms (110 of 111 on time, 19 of 20 audits accepted).
  - The device side was clean (copy max 0.14 ms). The 419 ms was spent in the responder thread on the host.
  - This pod's container has a CFS quota of 13.6 cores (`cpu.max 1360000 100000`). When the quota is exhausted within a 100 ms period, every thread stops for the rest of it, the pinned busy-polling responder included.
  - The counters rose during the passing rerun too (`nr_throttled` 22 to 23 inside the audit window); that time no answer fell in it.
  - The rerun also added a warm pass before the responder starts, which rules out first-pass allocations.
  - **Deployment condition:** run the responder where no CFS quota applies (a cpuset, or a quota well above peak use). Also cap the serving process's CPU thread pools: torch sizes its pools from `nproc`, which is 128 here.
- **What's left for this design.**
  - At the band's operating point (13 steps of about 15k rows), the chunk-major kernel runs at 58 ms per 15,075-row launch (2.50 G Keccak-f/s).
  - Without DRAM traffic the same instruction stream runs at 42 ms (3.5 G/s), and the INT32 ceiling is 4.8 G/s.
  - So the pass has room for about 1.4× from memory and about 2× from compute before the ceiling (about 2.5 GB/s EWB for the 0.5B).
  - Past that, it needs fewer instructions per Keccak-f (bit-interleaved lanes splitting a state across two threads) or more rows in flight (decoding the next pass during the current one, which is outside the one-pass metric).
  - The 4,096-row chunk-major threshold should rise to about 8k. Below that the lane pair has the better latency: vLLM's 9-segment groups (4,608 rows) take 0.60 s chunk-major, against about 0.44 s estimated on the pair kernel.

### Provisional band, d = 12 (dev runs before the reference landed, 01:27Z; the baseline above reproduces their first row: 1.14 s, 866 against 869 MB/s)

These are dev runs on pod `vy-pous-opt-g1`, medians of 3. The evidence is in `notes-asset:campaigns/pous/assets/pous-vllm/dense-decode/band_*`.

| Kernels | 0.5B pass | 0.5B EWB | 7B pass | 7B EWB | Keccak-f/s (0.5B) |
|---|---|---|---|---|---|
| Dense M2 kernels (row-major: warp, lane pair, fused); **the band baseline to be recorded** | 1.14 s | 869 MB/s | 1.73 s | 896 MB/s | 1.65 G |
| + chunk-major state (`feistel_chunked_kernel`) | 0.86 s | 1,142 MB/s | 1.53 s | 1,016 MB/s | 2.17 G |
| + parent gather straight into it, 64-thread blocks, small decodes row-major | 0.82 s | 1,199 MB/s | 1.37 s | 1,132 MB/s | 2.27 G |

- **The plaintext GEMM's EWB is unchanged:** 586 / 506 / 475 GB/s for the 0.5B at T = 1, 8 and 32. So the band at 1.2 GB/s is still about 490× the plaintext GEMM's time per weight byte.
- **Latency per decode group:**
  - one segment alone: 0.34 s (13 dependent calls; dense 11.3 s);
  - the 0.5B's first tile: 0.31 s.
- **Why the chunk-major state.** At the band's operating point (about 15k rows in each of 13 steps) the row-major kernels are memory-bound by 2×. That was measured in the dense stream: the same launch with row stride 0 has no DRAM traffic and runs in 42.0 against 82.5 ms at 15,360 rows.
  - The chunk-major layout ([half][chunk][row][17 words]) makes a warp's 32 rows one contiguous 4.35 KB run per chunk.
  - The whole launch then sweeps memory chunk by chunk, instead of streaming 15k separate 131 KB rows.
  - It is bit-identical to row-major for dense and band (`test_chunked_decode_matches_row_major`).
- **Ceiling.** The 0.5B band pass is 1.87 × 10⁹ Keccak-f (193,635 Π₂ calls).
  - At the INT32 ceiling (about 4.8 G Keccak-f/s, 4,776 SASS instructions each) the pass would take 0.39 s, about 2.5 GB/s.
  - Without DRAM traffic the fused kernel reaches 3.5 G/s (0.54 s, about 1.8 GB/s).
  - So the next 10× must come from beyond this kernel design: fewer instructions per Keccak-f, or less work per plaintext byte.
