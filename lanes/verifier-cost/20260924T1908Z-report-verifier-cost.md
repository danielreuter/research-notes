---
lane: verifier-cost
kind: report (working; updated at every checkpoint)
created: 2026-09-24T19:05Z
status: final
base: main 22741456
branch: lane/verifier-cost in ~/projects/verity-main-wt/verifier-cost
pods: vy-live2b-verifier-ro (pitmqu0zrycw5i, cpu3m 8 vCPU, EU-RO-1, $0.44/h; keep-pod until custody) + GPU provers one at a time
budget: $10; FINAL 01:10Z
---

CHECKPOINT 96c12c0b (19:53Z) [final] tip ab9573fd: D3 all 12 cells (10 B-Ligero from same-DC live records, 2 A-GKR from CPU verdicts art:8806507c art:ae9d69fb); custody art:d841eb56 + runs art:b4b33422 preserved; verifier pod terminated; no GPU pods; ~$0.36 spent
CHECKPOINT 96c12c0b (19:50Z) [open] tests on pod at ab9573fd: bench 227 passed/6 skipped; research -k vocab|label 21 passed, 1 fail test_labels_append_only (root on pod: os.access W_OK always true, env). D3 renders all 12 cells (evidence/drilldown-render.md). next: drain pod, FINAL
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

## 5. Tests (on the verifier pod, tree ab9573fd = 70be5474 + sent overlays, sha256-checked)
- run r20260924-194656-c97c: `backends/numerical/tests/bench` 227 passed, 6 skipped (incl. test_tables
  test_label_keys_are_the_store_vocabulary and the new test_drilldown D2/D3 tests); `tools/research/tests -k "vocab or
  label"` 21 passed, 1 failed: test_store.py::test_labels_append_only (`os.access(p, W_OK)` is always true for root on
  the pod; environmental, not this change). matplotlib for test_ledger went into /workspace/verifier-cost/pydeps.

## FINAL
- tip: lane/verifier-cost @ ab9573fd (pushed). Commits: a1e792c9 vocab, 70be5474 drilldown D1/D2/D3, 4f6ded5f D2 footnote,
  e6901277 vocab test pin, ab9573fd drilldown test.
- known failures: tools/research test_labels_append_only fails as root (pod env only). No bench failures.
- pod: vy-live2b-verifier-ro (pitmqu0zrycw5i) TERMINATED 19:53Z via `research pods drain` after custody passed.
  No GPU pods were created. Spend ~$0.36 (verifier pod 19:04–19:53Z at $0.44/h).
  machines.toml still lists [machines.vy-live2b-verifier-ro] (coordinator's entry; not edited).
- artifacts (all PRESERVED on R2): art:d841eb56097d5165 5.0 GB live session store (checked pod-side, run
  r20260924-191525-712d, `data preserved` rc=0; the laptop can't re-check a 5 GB tree), art:8806507c + art:ae9d69fb A-GKR
  CPU verdicts, art:b4b33422 this lane's pod run dirs (all 9 runs). The last three re-checked from the laptop 20:00Z.
- The finish checker's "4/8 cited artifacts not preserved" reads the laptop catalog, which never saw these pod-side puts;
  `data preserved` (above) says PRESERVED.

D3 as rendered (evidence/drilldown-render.md; coins/wire per live session; ‡ = CPU re-verification verdict; ° = loopback):

| Cell | Proof B | Gbit/s | Coins | Rounds | Verifier CPU s | Cores | Live tax | Record |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A100 BF16 · A-GKR | 21.2 MB | 0.126 | … | 328 | 14.6‡ | 10.8‡ | … | art:8806507c |
| A100 BF16 · B-Ligero | 85.3 MB | 2.83 | 8.46 kB | 3 | 8.56 | 35.5 | 1.06× (+15.9 ms) | art:a0af06b4 EUR-IS-1 |
| A100 BF16 · +hash | 169 MB | 1.5 | 8.47 kB | 3 | 31.1 | 34.7 | 1.01× (+11.8 ms) | art:75ff9a9a |
| H100 BF16 · A-GKR | 19.7 MB | 0.199 | … | 328 | 13.8‡ | 17.4‡ | … | art:ae9d69fb |
| H100 BF16 · B-Ligero | 135 MB | 8.37 | 8.46 kB | 3 | 7.0 | 54.2 | 1.01×° (+0.95 ms) | art:aadcd93f (cell) EU-NL-1 |
| H100 BF16 · +hash | 164 MB | 2.42 | 8.46 kB | 3 | 21.2 | 39 | 1.01×° (+3.2 ms) | art:5674f0cc |
| H100 FP8 · B-Ligero | 76.5 MB | 8.3 | 5.84 kB | 3 | 3.73 | 50.5 | 1.01×° (+0.64 ms) | art:3ef8007d |
| H100 FP8 · +hash | 87.1 MB | 2.36 | 5.82 kB | 3 | 11.4 | 38.5 | 1.01×° (+4.1 ms) | art:62018395 |
| 4090 FP8 · B-Ligero | 82.1 MB | 7.24 | 5.86 kB | 3 | 2.26 | 24.9 | 1.01× (+1.25 ms) | art:e74bfae5 EU-RO-1 |
| 4090 FP8 · +hash | 152 MB | 3.5 | 8.48 kB | 3 | 10.6 | 30.4 | 1.01× (+2.1 ms) | art:05a6ce75 |
| 5090 NVFP4 · B-Ligero | 31 MB | 7.3 | 5.86 kB | 3 | 1.67 | 49.3 | 1.03× (+1.2 ms) | art:b6125a19 |
| 5090 NVFP4 · +hash | 60.3 MB | 3.48 | 5.85 kB | 3 | 4.92 | 35.4 | 1.01× (+0.92 ms) | art:a3cc225d |

Coordinator decisions:
1. H100 rows: the live verifier ran on the prover pod (loopback, EU-NL-1). Accept as "same DC", or fund a separate-host
   same-DC H100 run (~$2–2.5; kb says RunPod had no same-DC CPU pod for H100).
2. 9 of 10 B-Ligero rows use a same-config companion live run (median verifier CPU), not the cell's own run: accept the
   companion rule (drilldown.py `live_records`) or require per-cell live runs.
3. A-GKR has no live protocol: D3 shows its offline CPU re-verification at 192 threads (1-thread CPU 8.8 / 8.2 s is lower).
   No new bench-result/v1 was registered: every B-Ligero value already had a same-DC live record at 2^-128.
Handoffs received: none. Handoffs sent: none. kb: live-verifier.md (custody, `preserved` pod-side, D3 rule, A-GKR cost).
cargo: no target/ in the worktree (all builds ran on the pod), so `cargo clean` had nothing to remove.
