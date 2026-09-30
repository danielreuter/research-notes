---
id: 20260930T1600Z-draft-b-host-slot-dma
campaign: overnight-sep30
lane: flock-v4-design
kind: draft
status: open
repo: danielreuter/verity
origin: cursor/hs-dma-eb58@8393a3e2
cursor:
  subagentId: "bc-8a7dff1c-37ef-5954-b12e-caa928daeb58"
---

# Attempt B: rep 0's host slots over the copy engine, in the session (`FC_HS_DMA=1`)

For M0 (bc-ff572e70). Branch `cursor/hs-dma-eb58`, one commit `8393a3e2` on your tip `ac08812e`; it changes only
`fc_witness` in `backends/flock/cuda/prove_circuit.cuh` (+37 −15). It is off by default. **Not compiled here** (this VM has
no nvcc), so the bench's build is its first compile.

**What changes.** With `FC_HS_DMA=1`, when rep 0's host slots are mapped a, b words (not already on the device):

1. Right after the memsets, before the compression rows' pageable copy, one `cudaMemcpyAsync` on `hs_stream` copies the
   whole `host0_zab` buffer into a device staging buffer. The buffer is kept for the process (it only grows; a `cudaFree`
   would sync the device).
2. `fc_host_slots` is unchanged and still waits for the memsets (`hs_zeroed`), but it reads the staged copy, as it does a
   prefetched `device-ab` copy today.

`hs_stream`'s creation moved up so the copy can start first. If `cudaMalloc` of the staging buffer fails, it falls back to the
mapped reads.

**Why.** The Nsight table (`note:20260930T1110Z-handoff-from-flock-netlist-nsys-m35`) has `fc_host_slots` at 26 ms
(K=2,048) and 44 ms (K=8,192) at m=35, and the first `fc_sha_tape` launch running beside it for the same 26.5 ms while the
second launch takes 2.4 ms.

- **The link is already near its limit.** At m=35 the a, b slots are about 2.3 GB at K=8,192 (1.14 GB at m=34, from
  flock-v2-design's #5). 44 ms for that is about 52 GB/s, close to what PCIe Gen5 x16 delivers by DMA. So the copy engine
  won't move the words faster.
- **What it can change is the SMs.** The mapped reads keep 2 blocks per SM stalled on PCIe loads. These most likely fill
  the SMs' outstanding-miss slots, which would explain why the SHA tape kernel beside them runs about 10 times slower.
- **The copy engine uses no SM.** So the compression chain (`fc_sha_tape`, then `fc_sha_rows`) could run at its own speed
  while the DMA runs. Rep 0's witness then takes max(DMA, compression chain), instead of the contended chain.
- **It complements attempt A.** It needs no overlap with the previous session, so it can't disturb that session's device
  waits, which is what cost the unchunked prefetch. If attempt A works, the slots are already on the device and B does
  nothing. If A doesn't, B is the in-session alternative.

## Predicted gain

It depends on whether `fc_sha_tape`'s 26.5 ms first launch is contention, which the table can't separate from a large first
batch.

| case | K=2,048 rep 0 witness (m=35) | K=8,192 | metric |
|---|---|---|---|
| contention (the likely case) | about 44 → 27 ms (−17 ms) | about 81 → 45 ms (−36 ms) | −3% to −4% |
| the first batch really is that large | +1 ms (the staged read) | +1 ms | 0 |

- **How the contention row is derived.** Today, K=2,048 is 29 ms of tape (both launches) plus 15 ms of rows, against 26 ms
  of host slots. With DMA it becomes 26 ms of DMA plus about 1 ms of reading the staged words, against about 20 ms of chain.
  K=8,192 is 52 + 29 today, against 44 + 1 with DMA.
- **At m=34 halve the milliseconds.** The share of the metric stays about the same, since the proves halve too.
- **Most likely: −2% to −3%** in both prefill and decode against the same-job control.
- **Memory:** the staging buffer is the size of the a, b slots, up to about 2.3 GB at m=35. That is small against the RTX
  PRO 6000's 96 GB, but it is held for the whole process.

## Byte-identity gate

The statement, pins, circuits and protocol are unchanged, and `fc_host_slots` reads the same words from another address.

1. 71's gate with `FC_HS_DMA=1` exported: `gpu_paths_agree` and `gpu_proofs_match_cpu` (proofs and transcripts equal the
   CPU prover's) on both GEMM coordinates.
2. The gate's statement digests equal those of your last v3 attempt at the same m (m=34: `86b48502…`, `72ba2879…`,
   `4998fffc…`).
3. `CHECK=1`'s statements all accepted with `FC_HS_DMA=1` in the environment.

A failure stops the attempt. The likely failure is a compile error: send it back to me.

## The bench

There is no cross-session effect, so your usual v3 depth is fine. RUNS=5 lowers the run-to-run noise (about ±0.03–0.05 s
in the Ligerito and zerocheck phases).

~~~bash
git fetch origin cursor/hs-dma-eb58 && git merge origin/cursor/hs-dma-eb58    # one file, one hunk in fc_witness
tools/research/src/research/pods/nebius/sky/submit.sh prover-bench m0-v3-a<N>-hsdma \
  --env CMD='research run <your v3 flags: --tool, --campaign overnight-sep30, --cwd source> -- \
    bash backends/flock/pod/72-host-unit-eval.sh <your v3 knobs: FLOCK_GEMM_TILE=4x4 FC_HOST_PREPIN=1, m, depth, BATCH_ANDS, MAX_STATEMENT_BITS> \
      FC_HS_DMA=1 FC_DEV_PREFETCH=0 WARM=1 RUNS=5 BASE=1 BASE_ENV=FC_HS_DMA=0 NOPIPE=0 CHECK=1'
~~~

- **Read:** `out/result.json` against `out/base/result.json`, and rep 0's `t.witness` per K in `classes/*/prove.err`.
- **Labels:** `ov.line flock-m0-v3`, your next `ov.attempt`, `ov.noisy true`, and
  `ov.note "rep-0 host slots by copy engine into a staging buffer (8393a3e2); same-job control FC_HS_DMA=0"`.
- **If the delta is inside the noise:** one profile resolves the case. Run `71-gemm-slowdown.sh NSYS=1 FC_HS_DMA=1` on the
  same tree, as `r20260930-105134-1707`. If `fc_sha_tape`'s first launch stays near 26 ms, there is no contention and the
  line stops. If it falls to a few ms, the gain is real and more runs will show it.
- **Success:** gate pass, and rep 0's `t.witness` down at least 10 ms at K=8,192 with the other phases unchanged. Then
  `FC_HS_DMA=1` is the default whenever prefetch is off.
