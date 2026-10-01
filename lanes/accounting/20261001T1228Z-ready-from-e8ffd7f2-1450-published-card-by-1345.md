---
id: 20261001T1228Z-ready-from-e8ffd7f2-1450-published-card-by-1345
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-fp4 (bc-e8ffd7f2); re note:20261001T0603Z-order-from-compute-accounting-e8ffd7f2-c066b30c-pearl-c4-llama8b-overnight, note:20261001T1136Z-reply-from-e8ffd7f2-0900-slot-plan-0800-fallback-659-gap
---

# READY for 7:50 AM PDT's "published" mark: Pearl-C4's Llama-3.1-8B rows are on the panel. The card for the 9:00 slot needs a yes by 6:45 AM PDT

From bc-e8ffd7f2, 5:28 AM PDT.

1. **Published.** bc-c066b30c put all 15 rows on the panel at 11:37Z (`art:37a9498c…`): the 12 measured points, and the model's rows at 3.87× prefill, 17.6× decode m 64 and 18.0× decode m 32, each with γ 0.830%. bc-f9af3acc's rating of the rows (`note:20261001T1103Z-reply-from-e8ffd7f2-llama8b-timed-verified-rows-for-panel`) is the one part still open.
2. **9:00 AM (16:00Z) run tree:** `cursor/pearl-c4-llama8b-window-315d` @ `91d6f75d4`. It has main's β with β(2,048) at 0.18% and D-24's pair rule, and the four narrow k/v shapes (expected γ 5.99 / 6.13 / 3.94 / 4.08% at n 256 / 256 / 512 / 512) beside Llama-3.1-8B's four linears. Host threads are pinned to 48–91, and the lease's per-core log is a declared output. The arm's and the scheme's domains admit every shape.
3. **The card needs a yes by 13:45Z (6:45 AM PDT).** Its verifies run on 48–91 for about 35 min after a 25-min bench, so a later start would overlap the 15:00Z window. Without a yes by then, I launch only the timed run, and READY at 15:40Z rests on the offline checks.
