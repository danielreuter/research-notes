---
id: 20260930T2256Z-handoff-from-proofs-m0-chart-answers
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Re Daniel's M0-chart questions: one statement scaled up; m = 35 is a size; keep Overview and Progress separate; the line has stalled at #20

Re `note:20260930T2209Z-handoff-from-console-progress-questions`. The full answers, with sources, are in the Project store
at `internal/proofs/m0-chart-answers.md`.

1. **Coverage:** one m = 35 statement's time per coordinate (the median of 3 runs, on synthetic words), scaled up. It doesn't
   prove every coordinate. 256x16384x2048 = 512 statements × 0.780 s = 399 s against 80.3 µs native, giving 4.97e6. Llama's
   number is a ratio of sums over 16 layers × {qkv, o, gate_up, down} plus lm_head (14,552 s ÷ 3.03 ms). The whole-row check
   agrees to within about 7%.
2. **Shapes:** fused gate/up (N = 2 × 8,192) and down, at M = 256; decode sums M = 1–8. "m = 35" is a statement's *size*
   (2^35 witness bits, the spec's maximum), not a count. It's 12% cheaper per coordinate than m = 34. 4×4 is the largest tile
   that fits a 2^26-bit block, and it hashes a tile's rows once for 16 coordinates. The tile statement isn't reviewed yet.
3. **Overview vs Progress: keep them separate.** Label Progress exactly: "Σ prover seconds ÷ Σ native torch bf16 `linear`
   seconds over Llama-3.2-1B's GEMMs on one RTX PRO 6000."
   - M0's native time is *measured and memory-bound*, which is why decode reads 1e5 against prefill's 5e6.
   - Neither number counts the verifier. M0 leaves out 10.5 s (K = 2,048) and 27.4 s (K = 8,192) of loopback verification
     per statement.
4. **The line** has stalled at #20 (4.80e6 / 1.05e5); #22's status is unknown. v3 runs at **48 vCPU per GPU**.

**Coming next (Daniel, 3:55 PM PDT):** proofs replaces this chart with per-subcircuit hillclimb plots. There's one plot per
`GemmCoordinate_v2{K}` at K = 2,048, 4,096, 8,192 and 16,384, with overhead against the RTX PRO 6000's spec-sheet peak,
throughput and GPU utilization per optimization step. I'll send the format when the first baseline lands.
