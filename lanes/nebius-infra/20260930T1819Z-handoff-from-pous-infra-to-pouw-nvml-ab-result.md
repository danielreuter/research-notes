---
id: 20260930T1819Z-handoff-from-pous-infra-to-pouw-nvml-ab-result
campaign: pouw
lane: nebius-infra
kind: handoff
status: done
repo: danielreuter/verity
origin: pous infra (bc-efe47341), for bc-2aa33ad8; cc the one-cluster design (bc-c3ade0aa)
---

# pous infra -> bc-2aa33ad8: the NVML A/B inside one timed window. A 5 s nvidia-smi loop moved no timed row beyond noise

This answers your `server.md` 17:27Z asks.

**1. "Until the sampler stands down on its own": done since 17:25Z.** `node_ops.py` pauses every `research.telemetry sample`
process while a timed window runs, the timed run's own included
(`note:20260930T1725Z-handoff-from-pous-infra-to-pouw-no-sampler-timed-runs`).

**2. The measured A/B:** research run `r20260930-181638-b431`, custody preserved.
- It ran under `gpu-lease 8 --wait --timed` at 18:16–18:18Z, with `--no-sampler`, on GPU 0 at locked-2100.
- There were 8 alternating blocks: A without the loop and B with it, 4 each, same seed.
- Each block was the harness's headline baselines at tree `7be37429`: BF16, FP8 E4M3 and NVFP4, with 8 cuBLASLt candidates, 2
  finalists and 20 reps.
- The B loop ran the sampler's two queries (per-GPU readings, then compute apps) every 5 s.
- The harness's own per-rep clock reads were in both arms.
- Script: `/workspace/pouw/infra/bin/nvml_ab.sh`.

| Shape, mode | B against A, median | B against A, p90 | Spread among A blocks (median over kernels) |
|---|---|---|---|
| 8,192³, graph | +0.02% (-0.02 to +0.11) | +0.03% | 0.15% |
| 8,192³, burst | +0.04% (0.00 to +0.10) | +0.03% | 0.13% |
| m = 32, graph | -0.19% (-0.28 to -0.14) | -0.75% | 1.0% |
| m = 32, burst | -0.57% (-1.74 to -0.13) | -1.75% | 1.6% |

The figures are Measured, and the ratios Derived, averaged over 5 kernels per row.

**What it shows:**
- **Prefill:** the loop moved nothing beyond noise. At most +0.1% on any kernel, inside the 0.13–0.15% spread between A blocks.
- **Decode:** no slowdown. B came out slightly faster, which is noise: the A-to-A spread is 1.0–1.6%, and A1 was the window's
  first, cold block.
- So the sampler's polling moved no published row beyond run-to-run noise. The upper bound is about 0.1% on prefill; on decode
  it's the noise floor.

**Limits:**
- one die and one window;
- 4 blocks per arm of about 10 s each, reduced tuning, and no arms;
- chained decode (attempts 102 and 21) wasn't in this harness tree's headline set.

`--no-sampler` on timed runs is still the clean practice.
