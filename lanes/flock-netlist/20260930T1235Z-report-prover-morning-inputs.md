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
| `flock-m0-v3` (flock-v2-design, then this lane) | v2's tiles plus the host-witness levers; v1's kernels from #11 | — | #8: 7.91e6 / 1.75e5 (`r20260930-103535-64c1`, 18 vCPU) | #10: 8.56e6 / 1.91e5 |

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
