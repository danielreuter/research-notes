# Table 2. Adversarial sweep / mechanism table

Both L and U at every point (8B, default point F_hat = 1.5, G_hat = 4, Q_inf = 8192, one axis varied). Bytes/token with the ratio to 4 B/token; `[L:hash]` = lower-module hash (current `ac6c3bb0e3`, `stale L` flagged). Status: measured / measured U / pod / analytic (closed-form fill of a blank, clearly marked; never a result) / [ ]. Legality: training U only from acyclic (convex-family) plans; the superseded cyclic witnesses appear in a separate comparison column only (their `[coarse:hash]` stamp is as recorded on the row -- seeded pod rows can carry a stamp newer than the plan, so the planner's own `U_detail.acyclic` marker decides). The `analytic` fills are the pre-acyclicity block model (`analytic.py`) and are known to be low for training after the legality correction (8B acyclic planner: 0.87 MB/tok at the default point, 3.1 MB/tok at Q_step = 8192, `coarse_8b.md`).

| Sweep | Values | Report | Security question | Expected signature | Measured (8B unless stated) |
|---|---|---|---|---|---|
| **Sequential training steps K** | 1, 2, 4, 8, 12, 16, 24, 32, 48, 64 (Q_step = 8192; 2-8 at 32768) | marginal L/Q, U/Q; fit r_L, r_U | Can accumulated state be amortised over arbitrarily many updates? | knee at K ~ 8-12, then a positive constant slope | Q_step=8192: K measured [2, 4, 8, 12, 16, 24, 32, 48, 64]; r_U = 3.09 MB/tok (all K (no knee seen: transient or steady throughout), n=9, resid 2.4e-15); r_L = 852 KB/tok (wp floor slope, n=9, resid 4.4e-15); knee not seen (pred. 15.6); steady pred. 438 KB/tok<br>Q_step=32768: K measured [2, 3, 4, 6, 8]; r_U = 1.17 MB/tok (all K (no knee seen: transient or steady throughout), n=5, resid 0); r_L = 373 KB/tok (wp floor slope, n=5, resid 6.2e-16); knee not seen (pred. 3.89); steady pred. 438 KB/tok |
| **Rollout volume Q_roll** | 8K, 32K, 128K, 1M (1B / 8B / 70B / 405B) | L/Q, U/Q for forward-nonfixed | Can one dynamic model be amortised over arbitrarily many rollouts? | weight-loading transient (P/Q), then a positive steady floor | 16 measured / 0 analytic / 0 pod-or-[ ] points; exponent U ~ Q_roll^-0.57 (r2 0.86, n=4); L ~ Q_roll^-0.65 (n=4) |
| **Training batch Q_step** | 8K, 32K, 131K, 524K, 1M, 4M (G_hat in {1, 10, 100, 1000}) | steady L/Q, U/Q | Does giant-batch training kill the result? | no collapse; possibly worsening once partial-gradient cuts dominate | 19 measured / 5 analytic / 0 pod-or-[ ] points; exponent U: [ ]; exponent L: [ ] |
| **Allowed inference context Q_inf** | 2K, 8K, 32K, 128K | inference U/Q; training and rollout L/Q, U/Q | How much security is lost by permitting longer chats? | inference stays 4 B/tok; dynamic cost falls as a power law (~Q_inf^-1/2 predicted) | 9 measured / 3 analytic / 0 pod-or-[ ] points; exponent U: [ ]; exponent L: [ ] |
| **F_hat** | 1, 1.5, 3, 10, 30, 100, 300, 1000 | L/Q, U/Q | How permissive can ancestral work be? | main security knob; identify exponent / knees | 7 measured / 7 analytic / 0 pod-or-[ ] points; exponent U: [ ]; exponent L: [ ] |
| G_hat | 1, 3, 4, 10, 30, 100, 1000 | L/Q, U/Q | Does parallel branching / batching defeat us? | flat once G exceeds the F-limited block size (measured: U identical for G_hat 4..1000) | 5 measured / 2 analytic / 0 pod-or-[ ] points; exponent U ~ G_hat^-0.05 (r2 0.44, n=5); L ~ G_hat^0.00 (n=5) |
| Model width d | syn-* family + 1B / 8B / 70B / 405B | L/Q, U/Q, fitted exponent | Does security strengthen with scale? | strong positive width scaling (measured U ~ d^1.1 at fixed P) | 4 measured / 6 analytic / 0 pod-or-[ ] points; exponent U ~ d^2.03 (r2 1.00, n=4); L ~ d^2.95 (n=4) |
| Depth L | syn-deep | L/Q, U/Q | Is depth important? | weak | 4 measured / 6 analytic / 0 pod-or-[ ] points; exponent U ~ d^2.03 (r2 1.00, n=4); L ~ d^2.95 (n=4) |
| Heads / GQA / FFN ratio | syn-attn, syn-manyheads, syn-ffn | L/Q, U/Q | Do architecture details change the mechanism? | weak vs width | 4 measured / 6 analytic / 0 pod-or-[ ] points; exponent U ~ d^2.03 (r2 1.00, n=4); L ~ d^2.95 (n=4) |
| Optional local input cap X | inf, 100 MB, 20 MB, 5 MB, 1 MB | L/Q, U/Q | Extra wedge from forcing tier-2 matmul sharding? | potentially very large; keep separate from the core F, G result | [ ] (not in the F/G matrix; X-capped dead end archived in results/xcap_deadend/) |

## K sweep detail (8B; U: marginal (U(K) - U(K_prev)) / ((K - K_prev) Q_step); L: certified wp rate (L_wp/(K-1) + tok)/Q_step -- differences of L are shown in the label only, they are not bounds)

| K | Q = K Q_step | L/Q | U/Q | U/L | cert. penalty | ach. penalty | status | superseded cyclic U/Q (not an attack; comparison only) |
|---|---|---|---|---|---|---|---|---|
| K = 1 (Q_step = 8192) | 8192 () | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | -- |
| K = 2 (Q_step = 8192) | 16384 (I/Q (first K: includes weights)) | 1.41 MB/tok (351,566x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 144/290 chained weights forced; L = root + tokens + L_wp]` | 3.15 MB/tok (787,452x inf) | 2.24x | 109,856x | 246,060x | measured | -- |
| K = 4 (Q_step = 8192) | 32768 (marginal vs K=2; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 852 KB/tok (213,002x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 432/870 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | measured | -- |
| K = 8 (Q_step = 8192) | 65536 (marginal vs K=4; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 852 KB/tok (213,002x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 1008/2030 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | measured | -- |
| K = 12 (Q_step = 8192) | 98304 (marginal vs K=8; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 852 KB/tok (213,002x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 1584/3190 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | measured | -- |
| K = 16 (Q_step = 8192) | 131072 (marginal vs K=12; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 852 KB/tok (213,002x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 2160/4350 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | measured | -- |
| K = 24 (Q_step = 8192) | 196608 (marginal vs K=16; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 852 KB/tok (213,002x inf) `[L: wp floor only, wp:ba12ab8bf8]` `[wp: 3312/6670 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | pod | -- |
| K = 32 (Q_step = 8192) | 262144 (marginal vs K=24; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 852 KB/tok (213,002x inf) `[L: wp floor only, wp:ba12ab8bf8]` `[wp: 4464/8990 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | measured | -- |
| K = 48 (Q_step = 8192) | 393216 (marginal vs K=32; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 852 KB/tok (213,002x inf) `[L: wp floor only, wp:ba12ab8bf8]` `[wp: 6768/13630 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | measured | -- |
| K = 64 (Q_step = 8192) | 524288 (marginal vs K=48; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 852 KB/tok (213,002x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 9072/18270 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | pod | -- |
| K = 2 (Q_step = 32768) | 65536 (I/Q (first K: includes weights)) | 431 KB/tok (107,862x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 252/290 chained weights forced; L = root + tokens + L_wp]` | 1.18 MB/tok (296,194x inf) | 2.75x | 33,704x | 92,553x | measured | -- |
| K = 3 (Q_step = 32768) | 98304 (marginal vs K=2; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 373 KB/tok (93,190x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 504/580 chained weights forced; L = root + tokens + L_wp]` | 1.17 MB/tok (292,186x inf) | 3.14x | 29,119x | 91,301x | measured | -- |
| K = 4 (Q_step = 32768) | 131072 (marginal vs K=3; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 373 KB/tok (93,190x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 756/870 chained weights forced; L = root + tokens + L_wp]` | 1.17 MB/tok (292,186x inf) | 3.14x | 29,119x | 91,301x | measured | -- |
| K = 6 (Q_step = 32768) | 196608 (marginal vs K=4; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 373 KB/tok (93,190x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 1260/1450 chained weights forced; L = root + tokens + L_wp]` | 1.17 MB/tok (292,186x inf) | 3.14x | 29,119x | 91,301x | pod | -- |
| K = 8 (Q_step = 32768) | 262144 (marginal vs K=6; L = wp rate (L_wp/(K-1) + tok)/Q_step) | 373 KB/tok (93,190x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 1764/2030 chained weights forced; L = root + tokens + L_wp]` | 1.17 MB/tok (292,186x inf) | 3.14x | 29,119x | 91,301x | pod | -- |

* Q_step = 8192: r_U = 3.09 MB/tok (all K (no knee seen: transient or steady throughout), n=9, resid 2.4e-15); r_L = 852 KB/tok (wp floor slope, n=9, resid 4.4e-15); U marginals per K pair: 4-2: 3.09 MB/tok, 8-4: 3.09 MB/tok, 12-8: 3.09 MB/tok, 16-12: 3.09 MB/tok, 24-16: 3.09 MB/tok, 32-24: 3.09 MB/tok, 48-32: 3.09 MB/tok, 64-48: 3.09 MB/tok; predicted knee K ~ 15.6 (2-layer chunk fails past K ~ 9.33), predicted steady 438 KB/tok.
* Q_step = 32768: r_U = 1.17 MB/tok (all K (no knee seen: transient or steady throughout), n=5, resid 0); r_L = 373 KB/tok (wp floor slope, n=5, resid 6.2e-16); U marginals per K pair: 3-2: 1.17 MB/tok, 4-3: 1.17 MB/tok, 6-4: 1.17 MB/tok, 8-6: 1.17 MB/tok; predicted knee K ~ 3.89 (2-layer chunk fails past K ~ 2.33), predicted steady 438 KB/tok.

## Rollout volume Q_roll (forward-nonfixed; four dense models)

| value | Q / mode | L/Q | U/Q | U/L | cert. penalty | ach. penalty | status |
|---|---|---|---|---|---|---|---|
| 1B Q_roll = 8192 | 8192; P/Q = 366 KB/tok (91,460x inf) | 366 KB/tok (91,461x inf) `[L:ac6c3bb0e3]` | 366 KB/tok (91,461x inf) | 1.00x | 91,461x | 91,461x | measured |
| 1B Q_roll = 32768 | 32768; P/Q = 91.5 KB/tok (22,865x inf) | 91.5 KB/tok (22,866x inf) `[L:ac6c3bb0e3]` | 91.5 KB/tok (22,866x inf) | 1.00x | 22,866x | 22,866x | measured |
| 1B Q_roll = 131072 | 131072; P/Q = 22.9 KB/tok (5,716x inf) | 27.7 KB/tok (6,916x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 39.3 KB/tok (9,813x inf) | 1.42x | 6,916x | 9,813x | measured |
| 1B Q_roll = 1048576 | 1048576; P/Q = 2.9 KB/tok (715x inf) | 19.6 KB/tok (4,892x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 38.2 KB/tok (9,562x inf) | 1.95x | 4,892x | 9,562x | measured |
| 8B Q_roll = 8192 | 8192; P/Q = 2.0 MB/tok (490,128x inf) | 1.96 MB/tok (490,129x inf) `[L:ac6c3bb0e3]` | 1.96 MB/tok (490,129x inf) | 1.00x | 490,129x | 490,129x | measured |
| 8B Q_roll = 32768 | 32768; P/Q = 490 KB/tok (122,532x inf) | 490 KB/tok (122,533x inf) `[L:ac6c3bb0e3]` | 490 KB/tok (122,533x inf) | 1.00x | 122,533x | 122,533x | measured |
| 8B Q_roll = 131072 | 131072; P/Q = 123 KB/tok (30,633x inf) | 134 KB/tok (33,524x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 155 KB/tok (38,826x inf) | 1.16x | 33,524x | 38,826x | measured |
| 8B Q_roll = 1048576 | 1048576; P/Q = 15.3 KB/tok (3,829x inf) | 84.7 KB/tok (21,187x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 125 KB/tok (31,201x inf) | 1.47x | 21,187x | 31,201x | measured |
| 70B Q_roll = 8192 | 8192; P/Q = 17.2 MB/tok (4,306,256x inf) | 17.2 MB/tok (4,306,258x inf) `[L:ac6c3bb0e3]` | 17.2 MB/tok (4,306,258x inf) | 1.00x | 4,306,258x | 4,306,258x | measured |
| 70B Q_roll = 32768 | 32768; P/Q = 4.3 MB/tok (1,076,564x inf) | 4.31 MB/tok (1,076,565x inf) `[L:ac6c3bb0e3]` | 4.31 MB/tok (1,076,565x inf) | 1.00x | 1,076,565x | 1,076,565x | measured |
| 70B Q_roll = 131072 | 131072; P/Q = 1.1 MB/tok (269,141x inf) | 1.11 MB/tok (276,390x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 1.14 MB/tok (285,526x inf) | 1.03x | 276,390x | 285,526x | measured |
| 70B Q_roll = 1048576 | 1048576; P/Q = 135 KB/tok (33,643x inf) | 315 KB/tok (78,663x inf) `[L:ac6c3bb0e3, gap 32.2%]` | 525 KB/tok (131,267x inf) | 1.67x | 78,663x | 131,267x | measured |
| 405B Q_roll = 8192 | 8192; P/Q = 99.1 MB/tok (24,771,325x inf) | 99.1 MB/tok (24,771,326x inf) `[L:ac6c3bb0e3]` | 99.1 MB/tok (24,771,326x inf) | 1.00x | 24,771,326x | 24,771,326x | measured |
| 405B Q_roll = 32768 | 32768; P/Q = 24.8 MB/tok (6,192,831x inf) | 24.8 MB/tok (6,192,832x inf) `[L:ac6c3bb0e3]` | 24.8 MB/tok (6,192,832x inf) | 1.00x | 6,192,832x | 6,192,832x | measured |
| 405B Q_roll = 131072 | 131072; P/Q = 6.2 MB/tok (1,548,208x inf) | 6.26 MB/tok (1,564,463x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 6.32 MB/tok (1,580,977x inf) | 1.01x | 1,564,463x | 1,580,977x | measured |
| 405B Q_roll = 1048576 | 1048576; P/Q = 774 KB/tok (193,526x inf) | 1.50 MB/tok (375,316x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 2.11 MB/tok (526,317x inf) | 1.40x | 375,316x | 526,317x | measured |

Power-law fit of b_U against Q_roll over 4 measured points: exponent -0.566 (r2 0.859); b_L exponent -0.650.

## Training batch Q_step x G_hat

| value | Q / mode | L/Q | U/Q | U/L | cert. penalty | ach. penalty | status |
|---|---|---|---|---|---|---|---|
| Q_step = 8192, G_hat = 1 | K marginal (3 - 2) at Q_step = 8192 -- may be pre-knee (predicted knee K ~ 10.4) | 1.12 MB/tok (279,564x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 378/580 chained weights forced; L = root + tokens + L_wp]` | 3.47 MB/tok (867,679x inf) | 3.10x | 87,357x | 271,129x | measured |
| Q_step = 32768, G_hat = 1 | K marginal (3 - 2) at Q_step = 32768 | 386 KB/tok (96,518x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 522/580 chained weights forced; L = root + tokens + L_wp]` | 1.32 MB/tok (329,562x inf) | 3.41x | 30,159x | 102,980x | measured |
| Q_step = 131072, G_hat = 1 | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3, gap 121.8%]` `[wp: 558/580 chained weights forced; L_wp below the coarse certificate]` | 1.25 MB/tok (312,999x inf) | 12.1x | 8,060x | 97,805x | measured |
| Q_step = 524288, G_hat = 1 | K marginal (3 - 2) at Q_step = 524288 | 25.8 KB/tok (6,450x inf) `[L:ac6c3bb0e3, gap 45.2%]` `[wp: 558/580 chained weights forced; L_wp below the coarse certificate]` | 1.34 MB/tok (334,471x inf) | 51.9x | 2,016x | 104,514x | measured |
| Q_step = 1048576, G_hat = 1 | K marginal (3 - 2) at Q_step = 1048576 | 12.9 KB/tok (3,226x inf) `[L:ac6c3bb0e3, gap 8.5%]` `[wp: 558/580 chained weights forced; L_wp below the coarse certificate]` | 1.33 MB/tok (331,644x inf) | 103x | 1,008x | 103,631x | measured |
| Q_step = 4194304, G_hat = 1 |  | [ ] | 1.14 MB/tok (285,142x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| Q_step = 8192, G_hat = 10 | K marginal (3 - 2) at Q_step = 8192 -- may be pre-knee (predicted knee K ~ 15.6) | 852 KB/tok (213,002x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 288/580 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | measured |
| Q_step = 32768, G_hat = 10 | K marginal (3 - 2) at Q_step = 32768 -- may be pre-knee (predicted knee K ~ 3.9) | 373 KB/tok (93,190x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 504/580 chained weights forced; L = root + tokens + L_wp]` | 1.17 MB/tok (292,186x inf) | 3.14x | 29,119x | 91,301x | measured |
| Q_step = 131072, G_hat = 10 | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 794 KB/tok (198,440x inf) | 7.69x | 8,060x | 62,008x | measured |
| Q_step = 524288, G_hat = 10 | K marginal (3 - 2) at Q_step = 524288 | 25.8 KB/tok (6,450x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 909 KB/tok (227,146x inf) | 35.2x | 2,016x | 70,978x | measured |
| Q_step = 1048576, G_hat = 10 | K marginal (3 - 2) at Q_step = 1048576 | 12.9 KB/tok (3,226x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 894 KB/tok (223,567x inf) | 69.3x | 1,008x | 69,859x | measured |
| Q_step = 4194304, G_hat = 10 |  | [ ] | 758 KB/tok (189,479x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| Q_step = 8192, G_hat = 100 | K marginal (3 - 2) at Q_step = 8192 -- may be pre-knee (predicted knee K ~ 15.6) | 852 KB/tok (213,002x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 288/580 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | measured |
| Q_step = 32768, G_hat = 100 | K marginal (3 - 2) at Q_step = 32768 -- may be pre-knee (predicted knee K ~ 3.9) | 373 KB/tok (93,190x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 504/580 chained weights forced; L = root + tokens + L_wp]` | 1.17 MB/tok (292,186x inf) | 3.14x | 29,119x | 91,301x | measured |
| Q_step = 131072, G_hat = 100 | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 786 KB/tok (196,392x inf) | 7.61x | 8,060x | 61,368x | measured |
| Q_step = 524288, G_hat = 100 | K marginal (3 - 2) at Q_step = 524288 | 25.8 KB/tok (6,450x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 859 KB/tok (214,858x inf) | 33.3x | 2,016x | 67,138x | measured |
| Q_step = 1048576, G_hat = 100 | K marginal (3 - 2) at Q_step = 1048576 | 12.9 KB/tok (3,226x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 839 KB/tok (209,749x inf) | 65.0x | 1,008x | 65,541x | measured |
| Q_step = 4194304, G_hat = 100 |  | [ ] | 758 KB/tok (189,479x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| Q_step = 8192, G_hat = 1000 | K marginal (3 - 2) at Q_step = 8192 -- may be pre-knee (predicted knee K ~ 15.6) | 852 KB/tok (213,002x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 288/580 chained weights forced; L = root + tokens + L_wp]` | 3.09 MB/tok (771,420x inf) | 3.62x | 66,558x | 241,050x | measured |
| Q_step = 32768, G_hat = 1000 | K marginal (3 - 2) at Q_step = 32768 -- may be pre-knee (predicted knee K ~ 3.9) | 373 KB/tok (93,190x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 504/580 chained weights forced; L = root + tokens + L_wp]` | 1.17 MB/tok (292,186x inf) | 3.14x | 29,119x | 91,301x | measured |
| Q_step = 131072, G_hat = 1000 | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 786 KB/tok (196,392x inf) | 7.61x | 8,060x | 61,368x | measured |
| Q_step = 524288, G_hat = 1000 | K marginal (3 - 2) at Q_step = 524288 | 25.8 KB/tok (6,450x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 859 KB/tok (214,858x inf) | 33.3x | 2,016x | 67,138x | measured |
| Q_step = 1048576, G_hat = 1000 |  | 12.9 KB/tok (3,226x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 279/290 chained weights forced; L = root + tokens + L_wp]` | 758 KB/tok (189,479x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| Q_step = 4194304, G_hat = 1000 |  | [ ] | 758 KB/tok (189,479x inf) *analytic* | [ ] | [ ] | [ ] | analytic |

Power-law fit: [ ] (< 2 measured points); b_L exponent [ ].

## Allowed inference context Q_inf (inference / training / rollout)

| value | Q / mode | L/Q | U/Q | U/L | cert. penalty | ach. penalty | status |
|---|---|---|---|---|---|---|---|
| Q_inf = 2048: inference (session) | 2048; one RU | -- | 4.00 B/tok (1.00x inf) | -- | reference | reference | measured U; L withheld (pre-fix lower) |
| Q_inf = 2048: training (Q_step = 32768) |  | [ ] | 909 KB/tok (227,261x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| Q_inf = 2048: rollout (Q_roll = 131072) | forward-nonfixed | 208 KB/tok (51,989x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 260 KB/tok (65,022x inf) | 1.25x | 51,989x | 65,022x | measured |
| Q_inf = 8192: inference (session) | 8192; one RU | -- | 4.00 B/tok (1.00x inf) | -- | reference | reference | measured |
| Q_inf = 8192: training (Q_step = 131072) | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 810 KB/tok (202,536x inf) | 7.85x | 8,060x | 63,288x | measured |
| Q_inf = 8192: rollout (Q_roll = 131072) | forward-nonfixed | 134 KB/tok (33,524x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 155 KB/tok (38,826x inf) | 1.16x | 33,524x | 38,826x | measured |
| Q_inf = 32768: inference (session) | 32768; one RU | -- | 4.00 B/tok (1.00x inf) | -- | reference | reference | measured |
| Q_inf = 32768: training (Q_step = 524288) |  | [ ] | 391 KB/tok (97,703x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| Q_inf = 32768: rollout (Q_roll = 131072) | forward-nonfixed | 123 KB/tok (30,634x inf) `[L:ac6c3bb0e3]` | 123 KB/tok (30,634x inf) | 1.00x | 30,634x | 30,634x | measured |
| Q_inf = 131072: inference (session) | 131072; one RU | -- | 4.00 B/tok (1.00x inf) | -- | reference | reference | measured |
| Q_inf = 131072: training (Q_step = 2097152) |  | [ ] | 212 KB/tok (52,970x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| Q_inf = 131072: rollout (Q_roll = 131072) | forward-nonfixed | 123 KB/tok (30,634x inf) `[L:ac6c3bb0e3]` | 123 KB/tok (30,634x inf) | 1.00x | 30,634x | 30,634x | measured |

Power-law fit: [ ] (< 2 measured points); b_L exponent [ ].

## F_hat

| value | Q / mode | L/Q | U/Q | U/L | cert. penalty | ach. penalty | status |
|---|---|---|---|---|---|---|---|
| F_hat = 1 (Q_step = 131072) |  | [ ] | 928 KB/tok (232,059x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| F_hat = 1: rollout (Q_roll = 131072) | forward-nonfixed | 134 KB/tok (33,573x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 155 KB/tok (38,826x inf) | 1.16x | 33,573x | 38,826x | measured |
| F_hat = 1.5 (Q_step = 131072) | K marginal (3 - 2) at Q_step = 131072; inference one RU: True | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 810 KB/tok (202,536x inf) | 7.85x | 8,060x | 63,288x | measured |
| F_hat = 1.5: rollout (Q_roll = 131072) | forward-nonfixed | 134 KB/tok (33,524x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 155 KB/tok (38,826x inf) | 1.16x | 33,524x | 38,826x | measured |
| F_hat = 3 (Q_step = 131072) |  | [ ] | 362 KB/tok (90,401x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| F_hat = 3: rollout (Q_roll = 131072) | forward-nonfixed | 134 KB/tok (33,573x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 155 KB/tok (38,826x inf) | 1.16x | 33,573x | 38,826x | measured |
| F_hat = 10 (Q_step = 131072) |  | [ ] | 362 KB/tok (90,401x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| F_hat = 10: rollout (Q_roll = 131072) | forward-nonfixed | 134 KB/tok (33,573x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 155 KB/tok (38,826x inf) | 1.16x | 33,573x | 38,826x | measured |
| F_hat = 30 (Q_step = 131072) |  | [ ] | 362 KB/tok (90,401x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| F_hat = 30: rollout (Q_roll = 131072) | forward-nonfixed | 134 KB/tok (33,573x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 155 KB/tok (38,826x inf) | 1.16x | 33,573x | 38,826x | measured |
| F_hat = 100 (Q_step = 131072) |  | [ ] | 362 KB/tok (90,401x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| F_hat = 100: rollout (Q_roll = 131072) | forward-nonfixed | 134 KB/tok (33,573x inf) `[L:ac6c3bb0e3, gap 0.0%]` | 155 KB/tok (38,826x inf) | 1.16x | 33,573x | 38,826x | measured |
| F_hat = 300 (Q_step = 131072) |  | [ ] | 362 KB/tok (90,401x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| F_hat = 1000 (Q_step = 131072) |  | [ ] | 362 KB/tok (90,401x inf) *analytic* | [ ] | [ ] | [ ] | analytic |

Power-law fit: [ ] (< 2 measured points); b_L exponent [ ].

## G_hat

| value | Q / mode | L/Q | U/Q | U/L | cert. penalty | ach. penalty | status |
|---|---|---|---|---|---|---|---|
| G_hat = 1 (Q_step = 131072) | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3, gap 121.8%]` `[wp: 558/580 chained weights forced; L_wp below the coarse certificate]` | 1.25 MB/tok (312,999x inf) | 12.1x | 8,060x | 97,805x | measured |
| G_hat = 3 (Q_step = 131072) |  | [ ] | 561 KB/tok (140,263x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| G_hat = 4 (Q_step = 131072) | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 810 KB/tok (202,536x inf) | 7.85x | 8,060x | 63,288x | measured |
| G_hat = 10 (Q_step = 131072) | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 794 KB/tok (198,440x inf) | 7.69x | 8,060x | 62,008x | measured |
| G_hat = 30 (Q_step = 131072) |  | [ ] | 561 KB/tok (140,263x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| G_hat = 100 (Q_step = 131072) | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 786 KB/tok (196,392x inf) | 7.61x | 8,060x | 61,368x | measured |
| G_hat = 1000 (Q_step = 131072) | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 786 KB/tok (196,392x inf) | 7.61x | 8,060x | 61,368x | measured |

Power-law fit of b_U against G_hat over 5 measured points: exponent -0.049 (r2 0.436); b_L exponent 0.000.

## Model width d (synthetic family at fixed P ~ 1.07e9 non-embedding, and the real dense models)

| value | Q / mode | L/Q | U/Q | U/L | cert. penalty | ach. penalty | status |
|---|---|---|---|---|---|---|---|
| syn-base (d = 2048, L = 16, P = 1.11e+09) |  | [ ] `[stale(4360a8f36e)]` | 225 KB/tok (56,259x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| syn-wide (d = 4096, L = 4, P = 1.14e+09) |  | [ ] | 441 KB/tok (110,271x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| syn-deep (d = 1024, L = 64, P = 1.09e+09) |  | [ ] | 151 KB/tok (37,633x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| syn-ffn (d = 2048, L = 8, P = 1.12e+09) |  | [ ] | 255 KB/tok (63,761x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| syn-attn (d = 2048, L = 16, P = 1.04e+09) |  | [ ] `[stale(4360a8f36e)]` | 226 KB/tok (56,379x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| syn-manyheads (d = 2048, L = 16, P = 1.11e+09) |  | [ ] | 225 KB/tok (56,259x inf) *analytic* | [ ] | [ ] | [ ] | analytic |
| llama3-1b (d = 2048, L = 16, P = 1.5e+09) | K marginal (3 - 2) at Q_step = 131072 | 13.9 KB/tok (3,482x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 270/292 chained weights forced; L = root + tokens + L_wp]` | 266 KB/tok (66,449x inf) | 19.1x | 1,063x | 20,287x | measured |
| llama3-8b (d = 4096, L = 32, P = 8.03e+09) | K marginal (3 - 2) at Q_step = 131072 | 103 KB/tok (25,795x inf) `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` `[wp: 558/580 chained weights forced; L = root + tokens + L_wp]` | 810 KB/tok (202,536x inf) | 7.85x | 8,060x | 63,288x | measured |
| llama3-70b (d = 8192, L = 80, P = 7.06e+10) | K marginal (3 - 2) at Q_step = 131072 | 1.01 MB/tok (251,335x inf) `[L: wp floor only, wp:ba12ab8bf8]` `[wp: 1386/1444 chained weights forced; L = root + tokens + L_wp]` | 3.91 MB/tok (977,564x inf) | 3.89x | 80,580x | 313,414x | measured |
| llama3-405b (d = 16384, L = 126, P = 4.06e+11) | K marginal (3 - 2) at Q_step = 131072 -- may be pre-knee (predicted knee K ~ 3.7) | 5.89 MB/tok (1,471,377x inf) `[L: wp floor only, wp:ba12ab8bf8]` `[wp: 2178/2272 chained weights forced; L = root + tokens + L_wp]` | 17.1 MB/tok (4,272,705x inf) | 2.90x | 479,542x | 1,392,534x | measured |

Power-law fit of b_U against d over 4 measured points: exponent 2.029 (r2 0.995); b_L exponent 2.945.

## Table 2b. Policy table (derived from the Q_inf and F_hat rows; 8B, rollout at Q_roll = 131072, pretraining K marginal at Q_step = 16 Q_inf)

| Allowed session Q_inf | Inference U/Q | Certified rollout penalty | Certified pretraining penalty | Achieved rollout | Achieved pretraining |
|---|---|---|---|---|---|
| 2K | 4.0 B/tok (1.00x inf) | 51,989x `[L:ac6c3bb0e3, gap 0.0%]` | [ ] | 65,022x | [ ] (pod (U superseded: cyclic planner; acyclic redo running)) |
| 8K | 4.0 B/tok (1.00x inf) | 33,524x `[L:ac6c3bb0e3, gap 0.0%]` | 8,060x `[L:ac6c3bb0e3 coarse MILP below the wp floor, wp:ba12ab8bf8]` | 38,826x | 63,288x |
| 32K | 4.0 B/tok (1.00x inf) | 30,634x `[L:ac6c3bb0e3]` | [ ] | 30,634x | [ ] (pod) |
| 128K | 4.0 B/tok (1.00x inf) | 30,634x `[L:ac6c3bb0e3]` | [ ] | 30,634x | [ ] (pod) |
