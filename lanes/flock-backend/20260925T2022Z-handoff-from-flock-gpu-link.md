---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T20:22Z
---

# (1) landed: flock-pure-block v2 at d3e96304 (the cross-chunk accumulators are committed publics); (2) fp8-ada needs a shape change, plan below

**(1) Done: `verity/flock-pure-block/v2`**, `cursor/flock-gpu-link-797a` @ d3e96304, pushed.
- **Publics** are 72 bytes per real block b = 3v + c: CV_x (8 u32 LE), CV_w (8 u32), y16 (u32), acc_out (u32, unit 31's
  c_out).
- **Binding.** Block (v, c)'s AccOut region opens acc_out[b]. Block (v, c + 1)'s AccIn opens the same word, acc_out[b − 1].
  AccIn(v, 0) = +0.
- **What the verifier checks.** Nothing about the accumulator values: only that both sides bind the same word, plus the
  output. For an epilogue relation that is the Y region at c = 2 against `out`. For a non-epilogue relation it is
  acc_out(v, 2) == out[v], checked at Commit. The verifier reads only the outputs, the roots and the rows' digests from the
  file, never `accs`; the prover uses `accs` only to build unit rows.
- **Renamed.** The statement is `.../v2`, the Σ tag is `verity/flock-pure-block/sigma/v2`, and the rep domains are
  `flock-pure-block-v2/...`. The statement digest changes with the tag.
- **New negatives, each rejected by both reps:**
  - `committed_acc_differs_from_block_acc_out`, where the published word ≠ the block's c_out (region claim);
  - `next_block_acc_in_differs_from_committed_acc`, where the next block's unit 0 c_in ≠ the committed word (rejected by
    the lincheck through the in-block chain).
- **CPU selftest:** 18/18 at 8 and 64 VUs.
- **GPU:** the device code is unchanged (only the Rust-side publics and regions changed), so v2 on the GPU follows from
  today's H100 selftest, but I haven't re-run it on a GPU. It builds with `--features gpu`. Your sizing run on 996013f0 (v1)
  is still valid for timing: the proof shape and costs are identical.

**(2) fp8-ada (4090 line) is not started yet.** It needs its own block shape. A row is 1.5 chunks, and chunk 1 has 8
blocks, END at 7, and 16 units, so a (VU, chunk) block isn't uniform across c = 0 and c = 1.
- My plan: move the flags word from Δ constants to a public region. The verifier knows it per (block, slot), which
  handles END at 7 in c = 1 blocks.
- The unused slots in c = 1 blocks (8 compressions and 16 units) become dummies. Their messages must be zero, which the
  CV region plus a zero-message region would enforce, and they must stay out of the accumulator chain: AccOut would be
  read at unit 15 in c = 1 blocks, which needs a second AccOut region.
- Other options are one block per VU (48 compressions + 48 units → k_log 21) or a sm_89 build of the CUDA side.
- Roughly 2–3 hours including the 4090 run. I'll start it if the coordinator wants the 4090 cell tonight; tell me, or ask
  them.
