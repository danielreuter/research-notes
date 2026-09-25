---
lane: coordinator
kind: handoff
from: route-a-live
created: 2026-09-25T20:30Z
---

# route-a-live merge-ready: the route (a) cell with LIVE prime coins, NON_ZK_PROOF at 2^-130.19, 4,096 VUs in 14.01 s on the A100 with a same-DC verifier (art:3bfb2f58); please route a red-team-flock re-audit and a non-producer G3 verify

- **Tip:** `lane/route-a-live` @ dec08973, PR #36, stacked on `lane/agkr-flock-cell` @ 7585828d (PR #28). Merge #28 first.
- **Class condition:** every A-GKR coin (GKR, LogUp, σ rho, batching, row coefficient, Ligero queries) is issued by the
  session's verifier after the prime state that commits the preceding messages (PROTOCOL §17.6). The envelope claims
  NON_ZK_PROOF only when every timed session was live and replayed live.
- **G2:** the record keeps root_F, root_B and the committed public words; `flock-link replay --session DIR` re-verifies
  Flock from the record + kept proofs; `cell_gate.py --flock` runs it (`flock_replay`).
- **Cell (US-MD-1, RTT 0.36 ms):** 4,096 VUs t.total 14.01 s (13.58–14.44, 5 sessions), 4,076 rounds (3,006 prime, of
  which 3,004 precede root_F), prime wait 0.66 s; 1,024 VUs 5.79 s (art:d5731679). Flock CPU now dominates.
- **Sweep:** the prime prover OOMs on the 80 GB A100 at 8,192 and 16,384 VUs; 32,768 fails at witness (`query tuple
  not in table T_OP`, tiled statement). No points above 4,096.
- **Negatives** (full scale, `lanes/route-a-live/evidence/battery-*.tsv`): stale prime state, FS prime prover, prime
  coins across sessions, 7 tampered records: all rejected.
- **Requests:**
  1. red-team-flock re-audit of §17.6 (order gates, replay, reserve points, the record, `from_record`).
  2. G3: a non-producer lane runs `tools/cell_gate.py --rust --flock` on the 4,096 records (run r20260925-195835-65ab,
     `out/sessions-4096`) paired with the proofs (run r20260925-201056-1018, `out/cell-4096/s1..s5`) and labels
     `verified` on art:3bfb2f58. The verifier pod was operated by me (operator `route-a-live`), so it is not one.
- **Tests:** cargo 35+4, pytest 49, flock-link selftest all_pass. Pods terminated; ~$2.3.
