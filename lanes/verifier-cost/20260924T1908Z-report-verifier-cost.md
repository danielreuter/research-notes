---
lane: verifier-cost
kind: report (working; updated at every checkpoint)
created: 2026-09-24T19:05Z
status: open
base: main 22741456
branch: lane/verifier-cost in ~/projects/verity-main-wt/verifier-cost
pods: vy-live2b-verifier-ro (pitmqu0zrycw5i, cpu3m 8 vCPU, EU-RO-1, $0.44/h; keep-pod until custody) + GPU provers one at a time
budget: $10; FINAL 01:10Z
---

CHECKPOINT 70be5474 (19:33Z) [open] custody PASSED art:d841eb56 (5.0GB sessions, preserved rc=0 pod-side); A-GKR CPU re-verify verdicts art:8806507c (14.6 CPU-s) art:ae9d69fb (13.8); D3/D2/D1 + vocab committed a1e792c9..70be5474; next: pod tests, render, FINAL
CHECKPOINT 22741456 (19:08Z) [open] context read; custody put of 5.25 GB sessions running on verifier pod (run r20260924-190646-2eca); next: extract session measurements, plan GPU prover runs

# verifier-cost: real verifier cost for every Table 2 cell (D3)

Spec: campaigns/afternoon/BRIEF.md `### verifier-cost`. Inbox at start (19:04Z): nothing.

## 1. Custody of the 2026-09-23 live sessions (vy-live2b-verifier-ro:/workspace/live/sessions)

- 19:05Z: 50 session dirs (5 `c…` challenge-stream, 45 `s…` Ligero), 3782 files, 5,252,776,381 bytes (885 sub_NN.proof /
  .stmt / .coins, 45 .bin, 1080 json). Server still up (pid 14506, `live serve --jobs 8 --threads 1 --target-bits 128`).
- Whole tree (proofs included) put from the pod as one run-files/v1 with a 3 h minted credential passed via `--env`:
  run r20260924-190646-2eca, script `evidence/pod-scripts/01-preserve-sessions.sh` (also writes files.txt, sha256.txt).
- Result: art:d841eb56 (run-files/v1, whole tree), put rc=0 with `--preserve`; custody re-checked pod-side with
  `research data preserved art:d841eb56…` (run r20260924-191525-712d, `02-custody-check.sh`): rc=0, PRESERVED (etag-md5).
  One S3 socket stall, recovered by the client's 120 s per-op timeout. The laptop `data preserved` hung (rc=142 after a
  150 s alarm): it re-reads every blob, 5 GB; run it pod-side.

## 2. What the existing sessions / live records already measure
- `03-extract-sessions.py` (run r20260924-191618-90f6): per session DCs, bytes, rounds, verify CPU; groups.tsv.
- The Table 2 B-Ligero cells' live records are already in the store as bench-result/v1 with
  `validation.evidence.live_verifier` (accepted, prover_dc = verifier_dc, verify.cpu_s, t.total_live) at 2^-128:
  10 of 10 B-Ligero cells have a same-config same-DC live run (1 the cell itself, 9 companions). No new GPU prover run was
  needed; no GPU pod was created (spend: verifier pod time only).
- Caveat: the H100 rows' live verifier ran on the prover pod (loopback, EU-NL-1). Same DC, but not a separate host.

## 3. A-GKR (no live protocol): CPU re-verification of the cells' own proofs
- `04-agkr-verify.sh/.py` (run r20260924-192555-fa70): independent Rust `verity-gkr-verify` (backends/gkr/verifier @
  22741456), 3 reps x 3 runs at 192 threads + 1 run at 1 thread per rep, rusage user+sys.
  - A100 BF16 · A-GKR (art:300a526a): verdict art:8806507c PASS, 14.55 CPU-s / 2.86 s wall, 8.76 CPU-s at 1 thread.
  - H100 BF16 · A-GKR (art:c09947fd): verdict art:ae9d69fb PASS, 13.78 CPU-s / 2.89 s wall, 8.19 CPU-s at 1 thread.
  Both registered verification-verdict/v1 (refs result = cell, proof = cell run_files), preserved.

## 4. Renderer (drilldown.py; tables.py untouched) and vocab
- a1e792c9: store vocab AUTHENTICATION_VALUES += included-hash-shared (test_label_keys_are_the_store_vocabulary).
- 70be5474: D3 from live records (cell, else median-CPU same-config companion) and verdicts (‡), emitter fallback (†),
  loopback (°); D2 prefers the fastest independently verified result and marks every cell iv/nv, footnoting a faster
  unverified one (SP1 + TC_DOT now 5.81 s art:174d7b4d, footnote names art:0a66c35e 4.26 s unverified); D1 A-GKR rows:
  CPU crate SHA-256 Merkle/FS (backends/gkr/src/transcript.rs), GPU SHA-512 Merkle + SHA-256 coins, verity-gkr-verify.
- Render: evidence/drilldown-render.md.
