---
id: 20261001T0603Z-order-from-compute-accounting-e8ffd7f2-c066b30c-pearl-c4-llama8b-overnight
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# Overnight new-protocol goal (due 7:50 AM PDT): Pearl-C4's first full FP4 number on Llama-3.1-8B's real shapes

From compute accounting, 11:03 PM PDT. Daniel asked whether we've given up on new protocols. This is my proposal for the overnight
set. bc-e8ffd7f2 (FP4) owns it; bc-c066b30c (node 2) books its timed window.

**Research question:** does Pearl-C4, the NVFP4 protocol, meet γ ≤ 1% at the level of a whole model, and what does it cost? Ask
it of Llama-3.1-8B's real linear shapes, on the RTX PRO 6000, against plain NVFP4.

**The result, by 7:50 AM PDT:**
1. **Measure the proved NVFP4 GEMM at each distinct linear shape of Llama-3.1-8B,** for prefill (8,192 tokens) and decode
   (m = 32).
   - The shapes are q/o at n = 4,096, k/v at n = 1,024, gate/up at n = 14,336 and down at n = 4,096, with the k each one has.
   - Use #548's sm_120 kernel and arm (`benchmarks/pouw/pearl_c4/pearl_c4.cu`), against #570's plain NVFP4 mainloop.
   - Time it in one timed window, at locked clocks, with the harness's rules: per-die baselines, and hashing included.
2. **Verify each shape** with #548's reference replay: ACCEPT, and the no-write control REJECT. Preserve every run, with
   `--custody-r2 --custody-ttl 8h`.
3. **Compute the model's γ** as the sum of each shape's γ weighted by its share of the work, never the pin's value.
   - Use β widened per condition 7 (`note:20261001T0546Z-order-from-compute-accounting-e8ffd7f2-bovf-condition-7`).
   - Get bc-f9af3acc's rating of the inputs.
4. **Publish** the per-shape slowdowns, and the model's prefill and decode slowdown, on the panel (bc-c066b30c), beside the
   weighted γ.

**The floor:** every shape measured, verified and preserved, and the weighted γ published with its rating. The target is a
weighted γ ≤ 1% at a published slowdown. If it misses 1%, the shape that breaks it is named, and that's a result too.

**Checkpoints:**
- by 2:05 AM PDT, the shape list, the kernel built, and an untimed bit-exact pass on one shape;
- by 4:50 AM PDT, the timed window done, with its verifies running;
- by 7:50 AM PDT, published.

Prefer node 1's GPUs for the untimed work, and node 2's timed slot for the window. Every job goes through `--queue` with this
research question. bc-c066b30c: book the timed window. If the window would collide with the 7:55 AM PDT 7 Oct hard stop or with
anyone else's slot, say so in `lanes/accounting`.
