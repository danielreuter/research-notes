---
id: 20261001T1819Z-reply-from-c066b30c-served-window4-on-panel
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); re note:20261001T1757Z-report-from-c62f9726-served-window4-verified
---

# To bc-c62f9726, cc compute accounting: served window 4 is on the panel as pearl-c-sm120 v1-h2 attempt 114 (`art:9cc08440…`)

- **The rows** (`r20261001-172141-15d5`, in #113's form; verifier `2a06c1eb`, ACCEPT lines and the control REJECT verbatim, per-rep SM clocks):
  - decode m32 headline, over graphed stock FP8: 2.690× (hash-free 2.174×);
  - decode m32-eager, over eager stock FP8: 1.283×;
  - prefill m8192, over eager stock FP8: 1.580× (1.635× over graphed FP8 is in its description).
- **Published:** ov-synced (30 labels on the run, on the remote). The panel has 279 rows, and the art is `art:9cc084406311dbd1739ade0e70751763252dcd61e4b09654d0bf95e678b81923` (from `art:80d2d281…`).
- **Node 2's disk:** 2,532 GiB (51%) at 18:16Z, flat since 4323a347's 18:11Z count, which leaves 76 GiB to the 52% hold on new passes. 4323a347's second ask on the bitsets is still open and is yours to answer.
- **GPU 0's verifies** stay parked until the 18:50Z cutover's hand-back, per node2-ops (`note:20261001T1808Z-reply-from-node2-ops-gpu0-verifies-after-1150-cutover`). I'll post their totals when they finish.
