---
lane: coordinator
kind: handoff
from: route-a-live
created: 2026-09-25T22:10Z
---

# route-a-live reopen done: re-derived results art:4b52879f (4,096) / art:aa9223c2 (1,024) with rounds.sequential_depth 4,076 / 3,607, but they FAIL views.interaction_problem at the 1 ms reference (-18% / -32%) because the run's RTT was 0.36 ms; they pass at the measured RTT (-3% / -9%). Decision needed. Fail-fast verifier done (PR #36 @ 504f75b6)

**1. Result.** `tools/cell.py rederive` (no pod) from art:3bfb2f58's embedded sessions (runs r20260925-201056-1018, r20260925-195835-65ab): the contract's live split (`t.total` = prover without its network waits, `t.total_live` = wall), `rounds.sequential_depth` = the session's rounds (3,006 prime + 1,070 Flock = 4,076), `net.rtt_ms` 0.356 + method, `net.wait_seconds`, `net.bytes_out/in`; each supersedes its old envelope (`refs.supersedes`); contract problems [].

| VUs | new art | t.total (compute) | t.total_live | rounds | wait | formula @1 ms | vs measured | formula @ measured RTT | vs measured |
|---|---|---|---|---|---|---|---|---|---|
| 4,096 | art:4b52879f | 12.59 s | 13.63 s | 4,076 | 1.03 s | 16.67 s | **-18%** | 14.05 s | -3% |
| 1,024 | art:aa9223c2 | 4.95 s | 5.78 s | 3,607 | 0.83 s | 8.55 s | **-32%** | 6.34 s | -9% |

- `interaction_problem` (main a2bad079) compares measured wall to the formula AT 1 ms; a same-DC run at 0.36 ms with ~4,000 rounds is necessarily ~3 s under it, so no honest re-derivation of these runs passes ±10%. The formula itself is validated at the measured RTT (-3%).
- Note: the OLD art:3bfb2f58 was classified non-interactive by `views.interaction` (no `net.rtt_ms` / `net.wait_seconds` / `t.total_live`): rounds 0, P at 14.0 s. So 328 never reached P; the understatement was the whole 4 s.
- Options (yours / Daniel's): (a) the tolerance check evaluates the formula at the run's measured RTT (P stays at 1 ms: 16.67 s); (b) a re-run with 1 ms injected on the verifier (`tc qdisc netem delay 1ms`, A100 ~30 min, ~$1.2; needs GPU); (c) publish without the interactive record (not honest: 4,076 rounds are real).
- red-team-flock and verify-night-3 have their own handoffs (class label; re-label).

**2. Fail-fast.** The 35-minute spin was `open_set`: a missing or short replayed round left the query coins at zero, so every index repeated forever. Now the verifier stops at the transcript's first replay failure (after each phase and inside `open_set`) with a draw cap as a backstop. Negatives: 4 unit tests (dropped last round, short round, degenerate coins, honest) and, on the real 4,096 record + proof on a CPU VM: honest accept 7.1 s, dropped last round and short last round rejected in 1.0 s (`R2-prime: round 3005 ...`). cargo 39 + 4 pass.

No pods, $0.
