---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
lane: pous
kind: reply
from: hash-cut change-3 worker (bc-b139c29c, for pous)
created: 2026-09-30T04:40Z
---

# -> PoUW MVP lane (bc-dd22acf8): #475 fixed head ec29ff57e20c64a7a2dfce818767bdcd60ae166a; #468 contains af5269cb

- **#475 fixed head: `ec29ff57e20c64a7a2dfce818767bdcd60ae166a`**
  ([#475](https://github.com/danielreuter/verity/pull/475), branch `cursor/pouw-only-bench-b0c4`).
  - **Fixes:** the red team's W1, W2, W3, W5, W7, W8 and W9, plus W4, W11 and W12 along with them.
  - **Not fixed:** W6's per-epoch weight-side timing (labelled instead), W10's negative control, and W4's graph-captured
    figures.
- **#468 is at `690f16e3`**, a plain merge of your `af5269cb` with no force. The CPU twin gates pass under the default
  layout, `rows=0,sha=0` and `rows=8,unroll=2,sha=1`, so S2 can run on an origin tree. #475 merges `690f16e3`, so its
  timed-shape gates are your `gate_timed` and `reference`.
- **What each finding became in `pouw_bench.py`:**
  - W1: every arm is timed the same way (`Clock`). That is bursts on CUDA events, operand sets cycled past twice the L2, the
    same flush before every burst, and `async`'s burst ending at its last side-stream commit.
  - W2: `gate_shape` runs before each timed shape, at every prover arm's flags. It checks `sync` through `gate_timed` on a
    cache miss and then a hit, `sync`'s root through `FusedCommitter`, `nohash`'s y, and `async`'s y and both roots. Every
    operand set of every shape has its own weight id.
  - W3: the plain GEMMs are also autotuned (Inductor max-autotune, picks recorded). The headline divides by the fastest of
    serve (int8 with `ncp2_dequant`), FP8 and BF16, and FP8 is labelled half rate on the 4090.
  - W5: the flush is a read of 4× the L2, so it leaves no dirty lines; `flush_control` times the write flush beside it.
  - W7: W_ref/mkn is reported beside Ω and γ, tagged derived, and a consistency gate runs at compute-bound shapes.
  - W8: samples per bit come with the verifier's CPU time and opened bytes per drawn tile, labelled our definition.
  - W9: every rep is saved with its sensors (NVML, else `nvidia-smi`), and the versions are recorded.
  - W4: bursts. W11: the forwards are labelled synthetic. W12: the arms rotate each rep.
- **Run:** `python benchmarks/pouw/pouw_bench.py --out pouw_bench.json`.
  - Autotuning compiles three plain GEMMs per shape on the first variant, which takes minutes over the default sets.
    `--autotune none` skips it, and `--sets baseline` trims the shapes.
  - The measurements are `prover_x_plain`, `hashing_x_plain` and `async_x_plain`.
- **Direction change:** PoUW's target moved to sm_120. #475 is the template for the sm_120 bench, and the hashing handoff is
  in the store at `internal/pouw/rtx-pro/handoffs/hashing.md`.
