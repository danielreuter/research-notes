---
id: 20261001T0135Z-reply-from-2aa33ad8-ask-divisor-window
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator); for compute-accounting
---

# Ask: one timed window, after tonight's goals, to confirm the plain-GEMM divisor

- **The question:** is the honest denominator of every FP8 and NVFP4 slowdown on the panel a verity plain GEMM rather than cuBLASLt?
  - The harness's untimed divisor window (`r20260930-224059-cb8d`) has FP8 `verity_fp8_256x128_ew` at 1.4148 ms against cuBLASLt's
    1.4531 ms at 8,192³. Adopting it would put every FP8 prefill slowdown about 2.6% higher.
  - At m = 32 decode, cuBLASLt's chain may be about 1.4% faster than the divisor in use.
- **What it decides:** whether the panel adopts the new divisor (the rule: the fastest plain GEMM of the same precision), and the decode
  divisor's chain. Adopting it moves every slowdown figure toward its honest value; no γ or rating changes.
- **The run:** one `gpu-lease 8 --wait --timed --max-min 20` window, about 10–15 min, `--no-sampler`, after tonight's goal windows (and
  after `-h2+s`, #610).
  - **Arms:** Pearl-C4 `PearlC4Nv` (NVFP4) and GPU 1's `PearlCSm120` (FP8), each with its poisoned dump and verifier.
  - **Timing:** both shapes, with every library's best timed as a finalist and, at decode, as a dependent chain. The frozen FP8 decode
    names are enforced: since #491 `9db36fe7d` the run fails rather than silently dropping them.
  - **Verify:** `verify.py --tier 2b`, with per-rep SM clocks on both sides.
- **Cost:** about 0.25 GPU-h of whole-node time. Staging the run tree is CPU only, and I've asked the harness (bc-0de2d624) to stage
  it now.
- **Nothing is queued** until you say yes.
