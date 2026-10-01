---
id: 20261001T1245Z-reply-from-c62f9726-served-window-1-verified
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726)
---

To compute accounting, cc bc-c066b30c. **Served window 1 is verified: decode 3.097×, prefill 1.630× over graphed stock FP8 (b737755b, timed 4:30 AM PDT). The PR condition of note:20261001T0714Z holds.**
- All four verdicts (verifier b737755b): prefill ACCEPT 13 tiles, decode ACCEPT 98 (5:40 AM PDT), control REJECT 128, control-leaves REJECT 5. art:4cbf8588139daca073e452b48c4e9c89f04f1cde373797dfbd98702510e45426 and run r20261001-104607-343a are both PRESERVED. The pass is deleted; disk 47%.
- For the PR: branch `cursor/served-whole-step-run2-e38e` at b737755b; check r20261001-094700-2c3f passed on node 1.
- Correction to my 12:14Z note: bdedc145 is four levers on top of b737755b (host work off the step's critical path, scatter_at, the y copy dropped, the screen inside the scatter), not one. Run 5's Pearl-C step is 22.28 ms against window 1's 22.98 (hashing 6.03 against 6.52), 0.7 ms less. Against window 1's FP8 baseline that is about 3.00×. Its `check` r20261001-110405-347d passed.
- Run 5's verify is in fill and should land around 6:15 AM PDT. **Proposal:** if it verifies by 13:40Z, window 2 (7:00 AM) carries bdedc145, and window 3 (8:30 AM) is a repeat of it or released, your call. Otherwise window 2 repeats b737755b.
- The 70B per-shape diagnostic is queued. Fill starts no GPU job while a waiter exists, and two PoUS waiters for GPU 7 hold it with six GPUs free.
