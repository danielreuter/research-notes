---
id: 20260930T1235Z-report-prover-morning-inputs
campaign: overnight-sep30
lane: flock-netlist
kind: report
status: open
repo: danielreuter/verity
origin: cursor/ov-gemm-slowdown-4d6a
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

CHECKPOINT a4256be0 (19:30Z) [open] flock-m0-v3 #20 r20260930-184956-61fe: prefill 4.80e6, decode 1.05e5 x native (GPU 2, gate pass), level with #19 across runs; its same-job control (fc_sha_rows reading the tape directly) gave 4.89e6 / 1.07e5. #21 next: the zerocheck's second-round and tail kernels at two blocks an SM (FC_ZT_LB2).
CHECKPOINT 18d37423 (18:47Z) [open] flock-m0-v3 #19 r20260930-181717-b71e: prefill 4.82e6, decode 1.04e5 x native (GPU 2, gate pass), from #18's 5.19e6 / 1.14e5: rep 0's witness kept inside the arena (the zerocheck's buffers, its peak, are freed first), so rep 1 reuses it at the tile's m=35 too; now the default. GitHub push auth still failing: unpushed commits bundled on request.
CHECKPOINT f91d6393 (18:15Z) [open] flock-m0-v3 #18 r20260930-174255-ff91: prefill 5.19e6, decode 1.14e5 x native (GPU 4, gate pass), from #17's 5.54e6 / 1.23e5: the 4x4 tile at m=34, where rep 1 reuses rep 0's witness (at m=35 the keep doesn't fit the arena). Next, #19: m=35 with the keep counted inside the arena (FC_KEEP_EXTRA_W=0, f91d6393, in a bundle while GitHub auth is down).
CHECKPOINT ec49a99e (17:39Z) [open] flock-m0-v3 #17 r20260930-171200-a14b: prefill 5.54e6, decode 1.23e5 x native (GPU 1, gate pass), from #15's 5.75e6 / 1.27e5: the lincheck's quirky eq table factored and the compression tape a thread per compression, both the same bytes. #16 r20260930-163852-0b50 (host slots staged by copy-engine DMA) was a loss at the tile and is reverted.
CHECKPOINT ac08812e (15:43Z) [open] flock-m0-v3 #15 r20260930-151018-d5ed: prefill 5.75e6, decode 1.27e5 x native (GPU 7, gate pass), from #13's 6.79e6 / 1.51e5: the ring switch rewritten with the same bytes (the row fold reads each row once, the basis combination by nibble tables, both 2^28 suffix eq tables formed from their halves), 0.095 to 0.034 s a rep. #14 (prefetch in 8 MB pieces) was not a win: its same-job control was faster. A host prebuild for jobs doesn't work (glibc 2.39 against the image's), so builds stay in the job.
CHECKPOINT 8f80915a (14:38Z) [open] flock-m0-v3 #13 r20260930-140504-c27c: prefill 6.79e6, decode 1.51e5 x native (GPU 5, gate pass, noisy: a14 shared its CPUs 160-191 for part of its timing), from #12's 7.89e6 / 1.76e5: 8,192 K=2048 coordinates defined, so the 4x4 tile reaches m=35. Benches one at a time from now; a14's evicted partial run r20260930-141201-5231 has no labels.
CHECKPOINT ea83e0a2 (13:55Z) [open] flock-m0-v3 #12 r20260930-132237-cee7: prefill 7.887e6, decode 1.763e5 x native (noisy, GPU 7, gate pass), from #10's quiet 8.56e6 / 1.91e5: K=8192 statements at m=35 as v1's (the K=2048 tile stays at m=33). #11's four cells timed after circuits' 13:13:30Z early release are ov.noisy=true; its two K=2048-only cells stay quiet; no re-measure, since #12 beats #11 on every cell.
CHECKPOINT ea83e0a2 (13:22Z) [open] v1 merged into flock-m0-v3 (ce7eb155 at e241ea21, history at ea83e0a2); v1 ends at #8 (quiet 1.497e7/3.507e5 and 1.476e7/3.464e5, ov.note on r20260930-124807-a26a). v3 #11 r20260930-130213-717f (quiet window, GPU 0, gate pass): 8.68e6 / 1.96e5, level with #10. #12 (m=35 statements) queued. GitHub auth was down 12:52-13:15Z: the merge used the host's synced ce7eb155 tree (hash-checked c77eadcf) and one submit used --allow-stale (sky/ matched infra/nebius at 12:47Z).
lane: flock-netlist · kind: report · from: flock-netlist / M0 (bc-ff572e70) · to: the morning report (prover workstream) · created: 2026-09-30T12:35Z

# Prover overhead overnight: inputs for the morning report

**Metric:** prover seconds ÷ native GEMM seconds (torch bf16 `linear`) on the same RTX PRO 6000 (sm_120). It covers Llama-3.2-1B's 16 layers plus `lm_head`, at M = 256 for prefill and M = 1–8 for decode.
- The steady-state bound applies: a pipelined prover costs the slower of its device time and its host witness builds divided by the depth.
- Byte identity is the gate on every attempt: the GPU's proofs and transcripts equal the CPU prover's, and the device paths agree, on both GEMM coordinates.

## Lines

| Line | What it is | #0 prefill / decode | Best prefill / decode | Quiet re-measure |
|---|---|---:|---:|---|
| `flock-m0-v1` | untiled M0 (#336, #419) plus tonight's host and kernel levers | 3.48e7 / 7.91e5 | #8: 1.39e7 / 3.279e5 (`r20260930-112558-0238`, GPU 0) | 1.497e7 / 3.507e5 (`r20260930-123313-2090`, GPU 2) and 1.476e7 / 3.464e5 (`r20260930-124807-a26a`, GPU 4); ended, merged into v3 |
| `flock-m0-v2` | 4×4 column-batch tiles at K = 2,048 | 2.61e7 / 5.3e5 | #1: 8.40e6 / 1.80e5; ended, folded into v3 | — |
| `flock-m0-v3` (flock-v2-design, then this lane) | v2's tiles plus the host-witness levers; v1's kernels from #11 | — | #12: 7.887e6 / 1.763e5 (`r20260930-132237-cee7`, 48 vCPU, noisy; K = 8,192 at m = 35) | #10: 8.56e6 / 1.91e5 |

- **The same binary varies about 6% between runs.**
  - v1#8's noisy run on GPU 0 proved a statement in 0.811 s at K = 2,048 and 0.939 s at K = 8,192.
  - Its two quiet runs, on GPUs 2 and 4, took 0.857–0.865 s and 0.980–0.994 s.
  - The quiet runs agree with each other to within 1.5%.
  - The native baseline moved by 1%, so the spread is in the prover: GPU slot or pod placement, not Builds.
- **The lines are merged.** v1 ended at #8 and was merged with v3's `ce7eb155` at `e241ea21` (tiles, no device prefetch), then carried on as `flock-m0-v3` #11 with v1's `hm96` fix added.
- **At K = 8,192, which is untiled on both lines,** v1#8 gave 1.22e7 (prefill) and 6.57e4 (decode) at 48 vCPU, against v3#8's 1.50e7 and 8.16e4 at 18 vCPU, noisy.

## The three biggest inefficiencies, and what was done

1. **The host witness serialized with device proving, plus first-use pinning.**
   - Each session's witness was built on the host after the previous proof. In a 4-session process, every prebuilt pack pinned fresh memory, costing 6–8 s.
   - Done: v1#1 to #5 build witnesses ahead to depth 4, move to m = 35 statements, add a one-pass host unit evaluation and a warm pinned pool. v1 went from 3.48e7 to 1.67e7.
   - Both coordinates are now device-bound: a K = 8,192 statement's 0.82 s build divided by 4 is below its 0.94 s of proving.
2. **Our own device kernels ran far below bandwidth.**
   - The lincheck's z transpose stored bytes at a 128-byte stride: 0.077 s per rep at m = 35, run twice per statement.
   - The hm96 leaf finish spilled its salt to a 192-byte stack frame: 28 ms against the level-0 leaf hashes' 11 ms.
   - Done: `a121fefe` rewrites the transpose as 8×8 bit transposes with 16-byte stores (0.008 s), and `5a3e151f` unrolls the hm96 salt loop so it stays in registers. Both give the same bytes.
   - v1#7 and #8 moved from 1.67e7 to 1.39e7 (prefill) and from 3.97e5 to 3.28e5 (decode).
3. **Per-coordinate hashing and statement layout at K = 2,048.**
   - Done: 4×4 tiles (v2, then v3) share each tile's activation rows across 4 coordinates. At K = 2,048 that's about 2× over the untiled line.

**What remains**, from the Nsight table in `note:20260930T1110Z-handoff-from-flock-netlist-nsys-m35` (an m = 35 statement is 0.75–0.86 s of kernels, with the GPU 89–90% busy):
- About 60% of device time is upstream Flock kernels:
  - the zerocheck first round (14%);
  - the two ring-switch kernels (13–15%);
  - the NTT (8%);
  - the zerocheck tails and Ligerito folds.
- Rep 0's witness is bound by the PCIe read of the host slots: 26 ms at K = 2,048 and 44 ms at K = 8,192.
- Device prefetch, as tried tonight, slowed the kernels it overlapped: 25% worse at K = 8,192 in v1#6.

## Decisions for Daniel

1. **Statement and pin review of the 4×4 tile layout** (`FLOCK_GEMM_TILE=4x4`, `GemmCoordinate` class at k_log 26). It is a new staged statement shape, gated by byte identity, not yet pinned or reviewed.
2. **K = 8,192 needs a circuit change to go further**, because its tile would need 2^27-bit blocks. The options:
   - a denser SHA slot;
   - packed unit slots;
   - K_MAX 27.
   Each changes pinned statement bytes.
3. **The vCPU basis.** v1 measures at 48 vCPU per GPU against the node's 24 (192 cores for 8 GPUs), and v3 measures at 18.
   - At 24, a K = 8,192 statement's host build (0.82 s at 48 vCPU, divided by depth 4) roughly doubles, bringing it close to the device's 0.94 s.
   - The reported number depends on which basis is chosen.
4. **Whether to invest in upstream Flock's kernels.** The remaining big device costs are theirs; the zerocheck first round is already hand-tuned for occupancy.
