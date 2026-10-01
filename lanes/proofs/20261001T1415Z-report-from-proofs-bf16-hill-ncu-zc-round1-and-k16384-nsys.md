---
id: 20261001T1415Z-report-from-proofs-bf16-hill-ncu-zc-round1-and-k16384-nsys
campaign: proofs-hillclimb
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-bf16-hill (bc-89f3138c)
---

# Zerocheck's first round is bound by its shared-memory tables; K=16384's extra time is lincheck's column fold, device allocations and host code between sessions (ncu and K=16384 nsys)

to: proofs (bc-8416bc72), for the owner's review and M0's (flock-netlist) agreement. It answers your 6:29 AM PDT ask and
refines items 1, 4 and 5 of `note:flock-netlist/20261001T1328Z-handoff-from-proofs-prover-profile-proposals-for-m0`.
**No C-Flock file was edited.** The only code change is the harness's `NCU=1` mode (`9770ec2fc`,
`backends/flock/pod/74-gemm-hill.sh`). Both jobs went in at 13:50:17Z under "at 13:50Z regardless": I can't read the Slack
thread, and at 13:50:01Z neither the notes nor my inbox held a no. Proofs had 1 node-1 GPU job in flight before them, 3 with
them.

## Summary

- **Zerocheck's first round is bound by its shared-memory lookups, not DRAM.** On the L1/shared-memory pipe it runs at 82%
  of peak, against 11% for DRAM. Each warp issues 154 shared loads per medium index j. 48 of them are the GF(2^8) log and
  antilog lookups, 48 the `s_t0` word-build table. Moving the products to the ALU pipe, which runs at 30%, should cut the
  kernel by up to about 30%. At m = 35 it reads 13–16 GB in 58.4 ms, 14–17% of DRAM peak.
- **Lincheck at K=16384 is GPU-bound.** Its kernels take 58 ms against 18 ms at K=2048. Of the 40 ms difference,
  `linear_check_compressed_column_fold` is 24 ms. It is a sparse gather from the eq table, one warp per column.
- **The 74 ms per session outside the phase timers (mean; 89 ms median in `f010`) has two parts**, each 3–8 times K=2048's:
  - The launching thread's own `cudaMalloc` and `cudaFree` calls, which leave the GPU idle. There are 17 calls of 22–253 ms
    in 9 of the 24 timed sessions, and none in the first five. This part is 39 ms per session on average, against 8–15 ms at
    K=2048.
  - 35 ms of host code at the session boundary, with no CUDA call and no transport wait (3–6 ms at K=2048). This trace can't
    name it.
- **Tracing cost nothing at K=16384.** Median e2e is 0.807 s traced, against 0.825–0.868 s untraced at the same step.

## Runs and evidence

| | `ncu` of zerocheck round 1 | nsys at K=16384 |
|---|---|---|
| Run | `r20261001-135118-4223` (K=2048, step 6, 64 GiB, 55 s) | `r20261001-135122-b18a` (step 4, 128 GiB, 144 s) |
| Result | rc 0, all sessions accepted | rc 0, 25/25 accepted |
| Evidence (preserved) | `art:e29d44132adc16977bb4d9aa6d7b8e821ddba4fb35793b89426ca8c9d21cf324` | `art:a370477cfe65a2b201b3a2d65e95c8fe0dbc5d4df13dc1cdcc8085af17243e60` |
| Tool | ncu 2025.3.1, `--clock-control none` | nsys 2026.1.3, CUDA trace only |

- Both runs are labelled `campaign`, `subcircuit`, `question` and `ncu.profile` or `nsys.profile`, and the labels are on the
  remote.
- Each artifact holds the reports, their CSV or SQLite exports, the run's stamps, and every analysis script with its output,
  listed in its `README.txt`.

**How `ncu` fit in 64 GiB.** Before a multi-pass replay, `ncu` saves every allocation the kernel can reach, spilling to host
memory once the GPU's is full. The m = 35 statement holds 72 GiB of GPU memory, so a multi-pass replay there would not fit
the job.

- The full section set (39 passes) ran on the preflight check's B = 16 statement: m = 28, grid 1171, both launches.
- On the m = 35 statement it took single-pass counters only, so nothing was saved: two launches after the warm session.
- m = 35 has exactly 128.0 times B = 16's warp instructions (50.4 G against 393.8 M), so B = 16's per-instruction
  profile carries over.
- m = 35's DRAM bytes were not collected: I asked for them by their Hopper names, and on sm_120 the counter is
  `dram__bytes_op_read`. They are scaled from B = 16 instead, as a range (`analysis/scaling.txt`).

## Zerocheck's first round (`zerocheck_first_round_cpu_structured<14>`)

From the B = 16 full set; the second launch matches the first.

| Measure | Value |
|---|---|
| Throughput, % of peak | L1/TEX 82.4, LSU pipe 82.4, ALU 30.0, FMA 6, DRAM 11.2, L2 5.5 |
| Issue | IPC 1.89 of 4 per SM (2.19 at m = 35), issue slots 44% busy, 1.09 eligible warps of 6.24 per scheduler |
| Stalls, cycles per issued instruction (of 13.2) | `mio_throttle` 3.62, `short_scoreboard` 2.82, `long_scoreboard` 2.41, `not_selected` 1.31 |
| Occupancy | 58% theoretical (72 registers and 45.4 KB of shared memory per 448-thread block: 2 blocks per SM), 52% achieved |
| Shared loads | 80.7 M warp instructions, 141 M wavefronts; 1.7-way bank conflicts (31.4 M wavefronts) |
| m = 35 | 58.4 ms per launch at 2.10 GHz (nsys: 58 ms); DRAM reads 13.0–15.7 GB (scaled), 222–269 GB/s, 14–17% of `ncu`'s 1.60 TB/s |

- **The shared loads per warp per medium index j are exactly 154**, and they match the source (80.7 M loads over 524,576
  warp-j iterations):

  | Loads | Count | What they read |
  |---|---|---|
  | `s_t0` | 48 | 8-byte entries indexed by a data byte: the 64-bit word build |
  | `s_log`, `s_antilog` | 32 + 16 | two GF(2^8) products per lane per k |
  | `wbuf`, `scol` | 54 | the warp's word exchange |
  | `s_phi` | 4 | 16-byte entries |

  The data-indexed byte and 8-byte lookups are where the bank conflicts are.
- So the kernel is limited by the issue of shared-memory instructions (`mio_throttle`) and their latency
  (`short_scoreboard`). Occupancy can't move: the launcher's comment documents the W = 14 register cliff.
- DRAM has 5–6 times headroom, so halving the bytes read would gain nothing. This replaces the "about 12% of DRAM
  bandwidth" in my K=2048 report, which used a 1.8 TB/s peak; `ncu`'s sustained peak is 1.60 TB/s.
- `ncu`'s tail estimate (25%) is an artifact of B = 16's 3.11 waves; m = 35 runs 398.

## K=16384 (step 4) against K=2048 (step 6)

Both statements are m = 35. At K=16384 there are 512 units of 8.95 M rows; at K=2048, 2,048 units of 1.12 M. The phase
timers come from the traced run (`analysis/phasecmp.txt`), and they match the untraced runs `f010`, `6c85` and `a0e0`.

| ms per session | K=16384, traced (`b18a`) | K=16384, untraced (`f010`) | K=2048, untraced (`9094`) |
|---|---|---|---|
| e2e (median) | 807 | 847 | 704 |
| zerocheck | 228 | 230 | 221 |
| ligerito | 184 | 182 | 197 |
| witness | 97 | 97 | 70 |
| encoding commitment | 93 | 93 | 93 |
| ring switch | 75 | 73 | 70 |
| lincheck | 72 | 72 | 28 |
| e2e − `prove_total_s`, mean | 35 | 42 | 6 |
| `prove_total_s` − timers, mean | 39 | 30 | 13 |
| coin wait (median) | 28 | 28 | 53 |

**Lincheck.** In the trace it is 70 ms wall and 62 ms GPU-busy, against 36 and 20 at K=2048. Its kernels, ms per session at
K=16384, with K=2048 in brackets:

| Kernel | K=16384 | K=2048 |
|---|---|---|
| `linear_check_compressed_column_fold` (8 launches) | 30.5 | 6.2 |
| `linear_check_partial_fold_shared` | 10.4 | 8.8 |
| `linear_check_fold_pair` (40 launches) | 8.1 | 1.8 |
| `linear_check_message_partial` (40 launches) | 6.4 | 1.6 |
| `fc_comb_expand` (not run at K=2048) | 2.3 | – |

- The column fold (`fc_fold` in `prove_circuit.cuh`, kernel in `lincheck.cuh`) computes α·Aᵀeq + Bᵀeq per unit type. It
  runs one warp per column and gathers 16-byte eq entries by row index.
- At K=16384 there are 8 times the rows per unit, and the kernel takes 5 times as long.
- The idle time inside lincheck is 8 ms, most of it coin rounds before `linear_check_fold_pair` (4.5 ms in 29 gaps).

**Outside the six timers.** `e2e_s` runs from just before Register to the end of rep 1's prove (`session_proved` in
`flock-circuit.rs`), so the time outside the timers splits in two.

- **Inside the prove calls (`prove_total_s` − timers):** 39 ms on average, with a heavy tail (28–260 ms in 10 of 24 sessions).
  - It is the launching thread's `cudaMalloc` and `cudaFree`: 17 calls of 22–253 ms in 9 of the 24 timed sessions, 1,062 ms
    in all (`analysis/alloc_stalls.txt`).
  - During these calls the GPU is idle and no other thread is in a CUDA call. The only other CUDA calls are the prebuild
    threads' six `cudaHostAlloc`, all at setup.
  - None falls in the first five timed sessions, so it grows with the process's history. The job's GPU memory peaks at 82 of
    95 GiB. The trace doesn't show the driver's side.
  - The long sessions match one for one: session 6 (65.9 ms against a 58.5 ms `cudaMalloc`), session 18 (151 ms against
    `cudaFree` calls of 101, 71 and 85 ms) and session 24 (260 ms against a 252.5 ms `cudaFree`).
- **Outside the prove calls (e2e − `prove_total_s`):** 35 ms on average, against 3–6 ms at K=2048. The sessions split into
  about 10 ms and 40–65 ms.
  - It isn't the transport's wait: the sessions with 40–65 ms of it have 19–42 ms of total coin wait, and that wait covers
    every call, Register and Hello included.
  - In the trace it is host code with no CUDA call, at the session boundary: from rep 1's last Ligerito kernel to the next
    session's first copy (`analysis/reps_ligerito.txt`). That stretch's mean idle is 79 ms in the second rep against 27 ms in
    the first.
  - The host isn't saturated: the job's slice uses about 2 of its 16 cores.
  - My hypothesis, unconfirmed: the session's host witness (`w0`) and its device data are dropped at the end of the table
    loop, which is inside `e2e_s`.
- **Witness.** Its kernels take 109 ms against 65 at K=2048: `fc_host_slots` 43 (26), `fc_sha_tape3` 39 (28) and
  `fc_sha_rows` 26 (11). Part of that overlaps other kernels. I propose nothing for it.

## Refined proposals (for the owner's review and M0's agreement; nothing edited)

Shares are of the K=16384 step-4 session (842 ms mean e2e) and the K=2048 step-6 session (705 ms). Every change must keep
proof bytes and verdicts identical.

- **1a. Zerocheck round 1: the GF(2^8) products on the ALU.**
  - Replace `s_antilog[s_log[a] + s_log[b]]` with a SWAR product: 8 byte-lanes per u64, shift and xor, reduced with xtime.
    The products are the same bytes, so the output is bit-identical.
  - This removes 48 of the 154 shared loads per warp per j, about 29% of the load wavefronts and most of the conflicted byte
    loads. It moves the work to the ALU, which is at 30%.
  - Expected, as an upper bound for a kernel that stays bound by the shared-memory pipe: 58 → 41–46 ms per launch. That is
    25–35 ms per session, 3.5–5% at K=2048 and 3–4% at K=16384.
  - First step: a variant in `bench_*` on node 1, against the current kernel's output.
- **1b. The `s_t0` word build (48 loads, about 45% of the wavefronts).** `t0` is the GF(2)-linear map `mcol` (64 × 64
  bytes, `upload_zerocheck_first_round_tables`).
  - If `mcol` sends each bit to a fixed GF(2^8) element per byte, the build becomes an 8×8 bit transpose plus 8 masked xors
    per word, all on the ALU.
  - With 1a, the kernel would then hit the ALU or DRAM limit, at most about 2× faster.
  - **Question for M0:** does `mcol` have that form?
- **4a. Lincheck's column fold at K=16384** (30.5 ms, 3.6%).
  - Compute the prover's comb from the block structure, as the verifier's structured lincheck already does (proofs-arch:
    `comb_partial`, C0 = I), instead of gathering Aᵀeq and Bᵀeq column by column.
  - Expected: most of the 30.5 ms at K=16384 and of the 6.2 ms at K=2048.
  - **Question for M0:** can the prover's comb use the same structure?
  - If not: one `ncu` pass on this kernel, the same `NCU=1` harness with `NCU_KERNEL=linear_check_compressed_column_fold`,
    to choose between gather locality (rows sorted within a column) and keeping the eq table in L2.
- **4b. Fuse lincheck's fold with the next round's message**, as zerocheck's tail already does and as item 3 proposes for
  Ligerito. `linear_check_message_partial` is 6.4 ms over 40 launches; expected 3–6 ms (0.5%).
- **5 (refined). No `cudaMalloc` or `cudaFree` in steady-state sessions.**
  - Size a per-process arena at the first session, or use a stream-ordered pool (`cudaMallocAsync` with a high
    `cudaMemPoolAttrReleaseThreshold`).
  - At K=16384 this is the largest single item outside the kernels: 39 ms per session on average (4.6%), plus the 1.0–1.1 s
    tail sessions. At K=2048, 6–9 ms (1%).
  - It doesn't depend on why the calls are slow.
- **9 (new). Name the host code at the session boundary** (35 ms at K=16384, 4%).
  - Time the end of `session_proved`'s table loop, where `w0` and the device data are dropped, and the start up to rep 0's
    stream open. That can be a timer bucket, or the NVTX ranges of item 7.
  - If it is the drop, move it to the session's finish thread.

Taken together, at K=16384: 1a, 4a, 5 and 9 add up to at most about 130 ms of 842 (15%), with little overlap; 1b would come
on top. At K=2048 the order stays as proposed: 1a, then item 2 (live coins), then item 3 (Ligerito).

## What I'd do next (only on a yes)

- A bench variant for 1a on node 1, with its output checked against the current kernel. This one is for M0 to own or
  approve.
- An nsys run at K=16384 with CPU sampling (`--sample=cpu`, OS runtime trace) to name the boundary host code. It's one job at
  128 GiB.
- If M0 says no to 4a: one `ncu` pass on `linear_check_compressed_column_fold`. It's ready in the harness, but I haven't
  placed it.
