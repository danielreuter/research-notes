---
lane: agkr-flock-cell
kind: report
created: 2026-09-25T17:38Z
status: final
---

CHECKPOINT 7585828d (19:35Z) [final] reopened round NOT completed: same-DC sweep code + statements (serving commit 38.6 s at 4096) done, but no co-located sessions (I waited without a wake; verifier idled out). Headline stays art:8f7ef58b. Pods terminated 19:34Z; lane ~$5.2
CHECKPOINT 7585828d (18:46Z) [open] WAITING: chose (a) A100 (cell capped at 4096; 8192+ tiled = timing only). (b) H100 not now: prime side supports bf16-hopper but no H100 stock in a DC with a same-DC CPU verifier via REST (H100 only AP-IN/JP, CA-MTL-1 no hairpin, EUR-NO-2, US-GA-2, US-NE-1 GraphQL-only) and ~70 min left. Prep run r20260925-184103-5c18 at 8192 statements; check ~19:00Z
CHECKPOINT 7585828d (18:45Z) [open] WAITING: chose (a) A100 (cell capped at 4096; 8192+ tiled = timing only). (b) H100 not now: prime side supports bf16-hopper but no H100 stock in a DC with a same-DC CPU verifier via REST (H100 only AP-IN/JP, CA-MTL-1 no hairpin, EUR-NO-2, US-GA-2, US-NE-1 GraphQL-only) and ~70 min left. Prep run r20260925-184103-5c18 at 8192 statements; check ~19:00Z
CHECKPOINT 7585828d (18:42Z) [open] WAITING: sweep prep run r20260925-184103-5c18 on vy-agkr-flock-cell-a100-2 (yeerzt741imi2s, US-MD-1 secure A100): setup + fresh statements (timed serving commit) for 1024/4096/8192/16384/32768 VUs (>4096 tiled, flagged). cell-verifier building same-DC verifier (US-MD-1). Next: publish statements to evidence/sweep + READY, then the timed sweep. Check ~19:00Z
CHECKPOINT c95dd13a (18:34Z) [open] reopened: re-time route (a) cell with a same-DC verifier (1-2 ms RTT), 1 warm-up + 5 timed, time the serving commit; NOT final. Budget $6
CHECKPOINT c95dd13a (18:28Z) [final] route (a) cell art:8f7ef58b: A100 BF16 4096 VUs, 143.3 s (3.55e9x), 2^-130.19 (C8: A-GKR hash SHA-512 2^-384, no change). PR #28 @ c95dd13a (main merged). 5/5 sessions accepted by cell-verifier. A100 terminated 18:19Z; ~$3.1
CHECKPOINT a1664ac9 (18:25Z) [final] route (a) cell art:8f7ef58b: A100 BF16 4096 VUs, 143.3 s (3.55e9x), 2^-130.19 (C8: A-GKR hash term SHA-512 2^-384, no change). E0/E1/P1-P3 in PR #28 @ a1664ac9; 5/5 sessions accepted by cell-verifier. A100 terminated 18:19Z; ~$3.1. Handoff to coordinator for red-team re-audit
CHECKPOINT a83d7de7 (17:38Z) [open] timed run r20260925-173611-8cb5 launched 17:36Z (1 local warm-up + 5 sessions vs cell-verifier 157.157.221.30:26732, verifier run r20260925-172927-6883; writes result.json). Check back ~17:45Z; then gate, handoff, FINAL. PR #28 open (draft)

# agkr-flock-cell: the first route (a) cell (A-GKR + Flock + link), A100 BF16, 4,096 VUs

Checkpoints from 16:01Z to 17:36Z are in `20260925T1601Z-report-agkr-flock-cell.md`. That file is the same report: the
checkpoint CLI started this second file after a store error.

**The cell:**
- **Result:** bench-result/v1 art:8f7ef58b (run r20260925-173611-8cb5). t.total 143.3 s (5 timed sessions, min 134.0,
  max 145.1), **3.55e9× native**, composed bound 2^-130.19 (contract problems []).
- **Verifier:** lane cell-verifier's pod, round 2 (r20260925-172927-6883, art:3b185b68), 5 of 5 sessions accepted.
- **Earlier runs:**
  - round 1: 3 accepted sessions (verifier r20260925-164419-448b art:5a7ccc3b, prover r20260925-165446-17f9
    art:79d8d4a5). There Flock took about 21 s at 18 ms RTT, 5.3e8×.
  - loopback self-test (r20260925-165039-cc6b): prime 2.5 s, Flock 9.2 s, 2.3e8×.
- **Where the time goes:** Flock's 1,070 live-coin round trips (129–142 s of waits in round 2) dominate whenever the
  verifier is remote.
- **Sizes:** the prime proof is 58,994,344 B; the Flock proofs are 2 × 461 KB.

**Conditions:** all implemented; details in PR #28, PROTOCOL §17.5 and `lanes/coordinator/20260925T1830Z-handoff-from-agkr-flock-cell.md`.
- E0: the library refuses the ungated exchange.
- E1: `tools/cell_gate.py`.
- P1: root_F handed to the session; the points and y come from the record.
- P2: two GF(2^128) points.
- P3: keyed-BLAKE3 row leaf (two constants in Flock's circuit, no big-endian Λ, nothing broke).

**Tests:**
- flock-link selftest: all cases pass at 8 and 64 VUs (r20260925-170814-6f81, and again at 8 after the main merge).
- gkr pytest (test_circuit_pins, test_cell_gate, test_commit): 27 passed.
- gkr cargo test: pass.
- The producer gate preview admits a real session and refuses a swapped proof, the empty probe session and a
  producer-operated record.

**C8:** A-GKR's hash term is SHA-512 Merkle, 2^-384, so counting it leaves the composed bound at 2^-130.19. I changed
no parameter and did not re-run. The 2^-127.7 figure was from the SHA-256 era. Open for the coordinator: the other
256-bit hashes (Flock's BLAKE3 Merkle tree, the prime SHA-256 transcript, the leaves) under the same convention.

Handoffs received:
- `20260925T1816Z-handoff-from-coordinator.md` (C8): answered in `lanes/coordinator/20260925T1830Z-handoff-from-agkr-flock-cell.md`.
- `20260925T1830Z-handoff-from-coordinator.md` (merge main): done. Merged origin/main as c95dd13a, which touches no
  gkr or flock file; cargo test and the 8-VU selftest pass; pushed.

Handoff written: `lanes/coordinator/20260925T1830Z-handoff-from-agkr-flock-cell.md`, asking for the red-team re-audit.

## FINAL

~~~text
tip: lane/agkr-flock-cell @ c95dd13a (merged origin/main; base lane/flock-link@4b560b2b + lane/agkr-bound@89433d06)   merge-with: none (PR #28)
known-failures: tests/test_repository.py::test_no_tracked_blob_exceeds_limit (on main too, per flock-link)    pod: vy-agkr-flock-cell-a100 terminated 18:19Z; ~$3.1 (A100 ~2.0 h × $1.39/h + cell-verifier ~$0.76)
artifacts: art:8f7ef58b art:9464fe7a art:3b185b68 art:5a7ccc3b art:79d8d4a5
~~~

## Reopened round (18:34–19:35Z): same-DC re-time and batch sweep, NOT completed

- **Asked:** re-time the cell with a same-datacenter verifier, sweep batch size to the plateau, record rounds, bytes,
  RTT and the compute-vs-wait split (coordinator 1836Z, handoff `20260925T1836Z-handoff-from-coordinator.md`), and
  time the serving commit.
- **Done:**
  - Code for the sweep and the interactive record (7585828d): the frozen set tiled past 4,096 VUs and flagged;
    per-session rounds, bytes up and down, RTT (median TCP connect to the verifier pod's ssh port, plus in-session
    wait / round trips), and the Flock prover-compute / network-wait / verifier-compute split, in the sessions and in
    the result envelope.
  - A secure A100 in US-MD-1 (yeerzt741imi2s).
  - Fresh statements for 1,024, 4,096, 8,192, 16,384 and 32,768 VUs, with the serving commit timed (run
    r20260925-184103-5c18, preserved). The 4,096 prime commitment is 950d40bc…, unchanged.
- **Serving commit** (CPU reference committer, `gpu.commit`, blake3-keyed/row/v2 + frame-v3):

  | VUs | 1,024 | 4,096 | 8,192 | 16,384 | 32,768 |
  |---|---|---|---|---|---|
  | seconds | 10.7 | 38.6 | 76.2 | 151.3 | 304.1 |

  It is linear, about 9.3 ms per VU, and at 4,096 VUs it is more than the co-located proving time. A GPU committer
  would change this.
- **Choice (a):** the cell stays on the A100, capped at 4,096 VUs (the renderer rejects tiled A100 batches). Not (b):
  the prime side supports bf16-hopper, but no H100 was available in a datacenter with a proven same-DC CPU verifier,
  and the time was too short.
- **Not done, my error:** I ended my turn WAITING at 18:46Z expecting a wake-up when the prep run finished. None came.
  - READY was never published, so cell-verifier's same-DC pod (4vmp4qarp4dko7, US-MD-1, confirmed) idled out at 19:27Z.
  - My A100 idled from about 19:00Z until I terminated it at 19:34Z.
  - No co-located sessions and no sweep timings exist. The headline result stays art:8f7ef58b (the remote verifier).
  - Next step: recreate both pods in US-MD-1 together, publish READY at once, and run `10-cell.sh` with
    VUS="1024 4096 8192 16384 32768" WARMUP_LOCAL=1 SESSIONS=5 RTT_PROBE=<verifier ssh>.

## FINAL (19:35Z)

~~~text
tip: lane/agkr-flock-cell @ 7585828d (PR #28)        merge-with: none
known-failures: tests/test_repository.py::test_no_tracked_blob_exceeds_limit (on main too)    pod: vy-agkr-flock-cell-a100 terminated 18:19Z, vy-agkr-flock-cell-a100-2 terminated 19:34Z (+ 2 stray A100s terminated within minutes); lane ~$5.2 (A100s ~$3.7 + cell-verifier ~$1.46)
artifacts: art:8f7ef58b art:9464fe7a art:3b185b68 art:5a7ccc3b art:79d8d4a5
~~~

Handoffs received this round: `20260925T1836Z-handoff-from-coordinator.md` (sweep + interactive record): code done, runs
not done (above).
