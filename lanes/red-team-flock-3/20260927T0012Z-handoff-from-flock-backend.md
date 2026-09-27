---
lane: red-team-flock-3
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-27T00:12Z
---

# 9 total-unit cells: gated twice on L40S provers, but not registered. No same-DC pair had a working internal route, and the hour limit is up

**Code:** cursor/flock-backend-4983 @ 8e0d0adb (main e93da678 with PR #91 merged; bench + flock tests 654 passed; on
GitHub).

**What happened:**
1. **22:44Z, distinct public IPs.** L40S prover in US-TX-3, A100 verifier in US-KS-2 (no verifier in US-TX-3).
   - Gate run **r20260926-224635-973c**: GATE OK on the prover pod.
   - #39 K1536 registered as **art:04688422**: total statement, `domain: total`, check PASS, `contended: false`.
   - But the round trip is 19.3 ms, so it runs at 365 VU/s against 4,208 same-DC: the 260 live rounds × 19 ms dominate.
   - So when PR #91 landed I stopped the queue: the other 8 cells would have been valid but uninformative. Both pods were
     terminated.
   - I labelled art:04688422 as a DIAGNOSTIC cross-DC placement that does not supersede art:4e3f5048.
2. **23:05Z–00:10Z, same-DC EU-NL-1 pairs under PR #91** (L40S plus RTX PRO 6000, both with `globalNetworking`, different
   machine ids wmu7hc6fck55 / yk7xd5ilz6tz, and later ddz1g8oynhse8h / wqny878kp5wrog).
   - Twice, the prover could not reach `<verifier>.runpod.internal:22` within 4 and then 8 minutes.
   - RunPod global networking didn't come up for these pods, though it did for the 21:36Z EU-NL-1 pair.
   - Both pairs were terminated with no cell run.
- **Spend:** about $3 of the $25 cap. No pods are running.

**Options:**
- **(a)** Retry EU-NL-1 (or any DC with L40S plus a second GPU) later with a longer route wait; the 21:36Z pair shows it can
  work. Same-DC numbers (~4k VU/s) are what the headline wants.
- **(b)** Run the 9 cells cross-DC with distinct public IPs, as at 22:44Z: valid, but about 10× slower at this RTT.
- **(c)** A different prover GPU line with same-DC stock (e.g. an A100 pair in US-KS-2, which has several models).

The queue, gate included, is one command: `/tmp/fp/total-nl.sh`, or `evidence/gemm-workloads/launch.sh l40s` with
`GATE=1`.
