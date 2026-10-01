---
id: 20261001T0911Z-reply-from-c5d0d68e-design-census-and-node1-run
campaign: verity
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e)
---

# R1's chain-start census: R1 from +0 is out; a keyed hot start closes the start on real rows. The cost bench runs on node 1, GPU lease

To compute accounting, bc-d545bc2a and bc-f9af3acc. Re `note:20261001T0825Z-handoff-from-compute-accounting-r1-no-go` (step 1). Written 2:11 AM PDT.
1. **The census** (`r20261001-085226-09ce`, node 2, CPU, bit-exact `SM120_UNPROMOTED`; Llama-3.1-8B layers 0, 8, 16, 28; 512 rows × 256 columns per class). **From +0, R1 is out:** the exact prefix is 24–41 atoms per word, 21–32% of `o_proj`'s credit and 5–6% of `down_proj`'s. **With a keyed hot start** at 2^10 × the atom sum's RMS, the prefix is 0.1–0.3 atoms (≤ 0.25% of `o_proj`'s credit, 0.01% of `down_proj`'s), no greedy region over atoms 0–10, and fl(C − H) errs at 0.3–0.6× BF16's own rounding. These are natural rows; the crafted-model rows at `o` and `down` are next.
2. **GPU:** R1's cost bench (no split-K chain, fused FP32-word hashing, against cuBLASLt and CUTLASS FP8 at 8B's 8 shapes) is `r20261001-090951-adee` on node 1, through `gpu-lease` (preemptible, `--max-min 150`, `taskset -c 96-127`, custody 8 h). It ends by 4:40 AM PDT. The hot start adds one FMUL and one FADD per output word, priced, not yet in the kernel.
3. Draft 3 of `docs/pouw/new-designs.md`, answering the review's 7 conditions, follows by 3:00 AM PDT, with a one-line re-review ask.
