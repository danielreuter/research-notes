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

CHECKPOINT ea4513262 (08:59Z) [open] 1:59 AM PDT: step 2 (verifier overlap, FC_VERIFY_AHEAD=10, 11 verifiers, 24 sessions) done at all K, every point byte-identical and its statement digest the one red-team-proofs-554 listed. Against node 1's step 1, K=16384/8192/4096/2048 (node-2 points /0.95 first): E4M3 6.83e7/6.82e7 on node 1 (-85/-69%: c925, dd5b), 4.94e7/4.98e7 node 2 (-64/-43%: f311, d594); NVF4 1.23e8/1.13e8/9.91e7/1.00e8 node 2 (-84/-73/-61/-43%: 2427, 1830, c568, 060f); MXF4 1.23e8/1.06e8/1.01e8/9.45e7 node 2 (-83/-76/-61/-45%: 4f4a, 6a9e, f163, 9248). No gain under 20%. Every point is now within 10% of its prove-only overhead except E4M3 K=16384 (4.79e7 prove-only, verify 7.6 s). Step 3 (structured lincheck) runs on 535d20a29, origin/main merged; first samples NVF4 K=4096/8192 and MXF4 K=8192 are -4/-11/-8% (verify 1.4-3.1 s -> 0.15-0.35 s), re-runs queued on node 2.

CHECKPOINT cde1c7ac1 (08:24Z) [open] 1:24 AM PDT: step 1 (column-major verifier fold) done on node 1 at all K, every point clean and byte-identical. Against clean step 0, K=16384/8192/4096/2048: E4M3 4.49e8/2.22e8/1.39e8/8.68e7 (-38/-43/-35/-32%: 9fd9, afc8, b5b0, 40d6); NVF4 7.49e8/4.26e8/2.55e8/1.75e8 (-32/-33/-18/-29%: d596, c6c9, 929d, c70f); MXF4 7.40e8/4.38e8/2.56e8/1.71e8 (-35/-30/-27/-22%: 3631, 6800, 2c74, e94a). Five first samples under 20% were re-run. Three of them came from one slow first timed session; NVF4 K=4096 gave -12% then -18%, real but within the spread. Step 2 (overlap, ea4513262) is staging on node 1 for E4M3 and NVF4. MXF4's step 1 + step 2 curve is on node 2 (node-2-only). Step 3 (structured lincheck, ba008a442, binary 7bc7d61030d0d23e) is synced as proofs-flock-fp-s3 and reuses step 2's statements.
CHECKPOINT cde1c7ac1 (07:38Z) [open] 12:38 AM PDT: step 1 (column-major verifier fold, bf16-hill d1775df80) E4M3 K=16384 4.49e8 vs step 0 7.23e8 (-38%, verify 11.4 -> 6.6 s/statement), clean, r20261001-072900-9fd9. NVF4 and MXF4 K=16384 running; step 2 (overlap, ea4513262, binary 557b507079078cc7) synced as tree proofs-flock-fp-s2, its staging next.
