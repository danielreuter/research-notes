---
id: 20261001T0738Z-report-proofs-flock-fp
campaign: overnight
lane: proofs-flock-fp
kind: report
status: open
repo: verity
origin: proofs-flock-fp (bc-15199603-ae1e-5aa0-9da4-6be8dedb83e6)
---

FP hill-climb (E4M3, NVF4, MXF4), newest first. Each step is a byte-identical point against the format's clean step 0 at the
same K; a gain under 20% is re-run once (clean FP4 samples spread 12-19%). Branch `cursor/proofs-flock-fp-95d4`.

CHECKPOINT cde1c7ac1 (08:24Z) [open] 1:24 AM PDT: step 1 (column-major verifier fold) done on node 1 at all K, every point clean and byte-identical. Against clean step 0, K=16384/8192/4096/2048: E4M3 4.49e8/2.22e8/1.39e8/8.68e7 (-38/-43/-35/-32%: 9fd9, afc8, b5b0, 40d6); NVF4 7.49e8/4.26e8/2.55e8/1.75e8 (-32/-33/-18/-29%: d596, c6c9, 929d, c70f); MXF4 7.40e8/4.38e8/2.56e8/1.71e8 (-35/-30/-27/-22%: 3631, 6800, 2c74, e94a). Five first samples under 20% were re-run. Three of them came from one slow first timed session; NVF4 K=4096 gave -12% then -18%, real but within the spread. Step 2 (overlap, ea4513262) is staging on node 1 for E4M3 and NVF4. MXF4's step 1 + step 2 curve is on node 2 (node-2-only). Step 3 (structured lincheck, ba008a442, binary 7bc7d61030d0d23e) is synced as proofs-flock-fp-s3 and reuses step 2's statements.
CHECKPOINT cde1c7ac1 (07:38Z) [open] 12:38 AM PDT: step 1 (column-major verifier fold, bf16-hill d1775df80) E4M3 K=16384 4.49e8 vs step 0 7.23e8 (-38%, verify 11.4 -> 6.6 s/statement), clean, r20261001-072900-9fd9. NVF4 and MXF4 K=16384 running; step 2 (overlap, ea4513262, binary 557b507079078cc7) synced as tree proofs-flock-fp-s2, its staging next.
