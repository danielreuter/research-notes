---
id: 20261001T1310Z-ready-from-c62f9726-served-window-2-bdedc145-verified
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726)
---

To compute accounting, cc bc-c066b30c. **READY for served window 2 (7:00 AM PDT): it carries bdedc145, and run 5 of that build is verified (untimed: decode 2.984×, prefill 1.633×).**
- Run 5's verdicts (verifier bdedc145, 6:07 AM PDT): prefill ACCEPT 13 tiles, decode ACCEPT 100, control REJECT 128, control-leaves REJECT 6. art:58b956a90e3ff29a98794ad34b0443d08a5fcbda114033119436792559add63a, PRESERVED. Its `check` r20261001-110405-347d passed (branch `cursor/served-whole-step-graph-e38e`). Pass deleted; disk 46%.
- Window 2 is r20261001-130909-dcae, waiting on node 2. It verifies inline on cores 48–123 until 14:55Z, before your 15:00Z window: decode with 48 processes, the other passes beside it. Anything left goes to fill.
- 70B diagnostic (art:119ee6b6c169722ef045db69d2a645071cdbab1ffa52943fab98c2407901a601): **yes, Pearl-C's per-GEMM slowdown falls at 70B's shapes.** Per layer (its four GEMMs), against vLLM's CUTLASS FP8 call: at m = 8192, 70B is 1.32× and 8B 1.68×; at m = 32, 70B is 2.47× and 8B 7.37×.
- Why it falls at m = 32: Pearl-C's call has a floor of about 0.14–0.16 ms (qkv and o, both models), while FP8's time grows with the weight. Both m = 32 ratios run high: run.py's call is ungraphed, and the baseline keeps FP8 weights under about 100 MB in L2 (8B's gate_up reads at 3.2 TB/s).
- Window 3 (8:30 AM PDT): your call, a repeat of bdedc145 or released. My 7:50 checkpoint will carry window 1's verified 3.097× and window 2's timed number.
