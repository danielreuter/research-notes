---
lane: verify-bligero-real-k
kind: report
created: 2026-09-26T05:53Z
status: open
---

CHECKPOINT 2bd8ce2f (08:54Z) [open] reopened for last 2 B-Ligero cells e8fb169d (H100 BF16 K8192 sha256) + 9260a985 (FP8) and snapshot_vs_record r20260926-073309-3956: NOT final; agent bc-30d7a020-fc45-5944-9ceb-1ac513232a9e; $2
CHECKPOINT 2bd8ce2f (08:30Z) [final] FINAL (reopen 1): 14 new-sender cells verified=accepted (runs r20260926-075651-fc42, -081703-0f0a, -082424-5906 at main 2bd8ce2f; pins 16/16; sets re-staged; sessions 70/70); last 2 H100 K8192 SHA-256 cells not yet registered; pod terminated 08:29Z ~$0.55
CHECKPOINT 2bd8ce2f (08:25Z) [open] 11 cells verified=accepted: +1dafbfd5 f1ac2db5 9fd5ec09 f451dabc (ref r20260926-081703-0f0a). Run r20260926-082424-5906 on 4b567c9c 622c9737 82587955. Live-read session snapshots = preserved verifier records (7d7b a6fe 4ad5 ca25)
CHECKPOINT 2bd8ce2f (08:17Z) [open] 7 cells verified=accepted (ref r20260926-075651-fc42, pins 16/16 at main 2bd8ce2f): c56a09a8 664f3142 3bb4d03f 11208bf7 c92a439a b1d710da 767b54db. Run r20260926-081703-0f0a on 1dafbfd5 f1ac2db5 9fd5ec09 f451dabc
CHECKPOINT 2bd8ce2f (07:57Z) [open] pod vy-verify-bligero-real-k = cpu3c-32 lusnnk1ekkj0je ($0.96/h, re-registered); run r20260926-075651-fc42 (bootstrap + pins at main 2bd8ce2f + 7 cells via fixed reverify entry, dry run); labels after
CHECKPOINT 2bd8ce2f (07:51Z) [open] reopen: 7 cells (b1d710da 3bb4d03f 11208bf7 c92a439a 767b54db c56a09a8 664f3142); 35/35 session records gathered (5 runs from store records, 2 live via ssh read-only); c56a09a8 PASS locally w/ fixed reverify entry (main 2bd8ce2f) + 5/5 sessions; next: pod run for all 7. Handoff 0705Z acted on
CHECKPOINT 1b818427 (07:41Z) [open] reopened for bligero-real-k new-sender cells (b1d710da 3bb4d03f 11208bf7 c92a439a 767b54db c56a09a8): NOT final; agent bc-30d7a020-fc45-5944-9ceb-1ac513232a9e; $5
CHECKPOINT 1b818427 (06:32Z) [final] FINAL: 16/16 real-K pins confirmed (main 1b818427, VM + pod build); art:be42c41a c8cc8514 67fb03cb db9f01bf verified=accepted (ref r20260926-062503-d9c2; sets re-staged, sessions 20/20, negatives 7/7); reverify entry-point gap handed to coordinator; pod terminated 06:31Z ~$0.10
CHECKPOINT 1b818427 (06:25Z) [open] pins 16/16 also on pod (run r20260926-061022-eac8, pod-built verifier). Input sets re-staged: 3/3 match manifests+cell digests, IR-verified, = prover's staged copies. main reverify can't find nested sweep/*/proofs (ERROR) -> run r20260926-062503-d9c2 calls reverify.verify_tree directly; H100 67fb03cb PASS locally + 5/5 sessions match
CHECKPOINT 1b818427 (06:10Z) [open] 16/16 real-K pins confirmed from main 1b818427 (VM compile + main's release ligero-verify; binary pins each to its own name). No CPU pods anywhere; pod vy-verify-bligero-real-k = A4000 dxkwi6u5039cat ($0.25/h, EUR-IS-1). Next: cells be42c41a c8cc8514 67fb03cb db9f01bf
CHECKPOINT 1b818427 (05:53Z) [open] started (agent bc-30d7a020-fc45-5944-9ceb-1ac513232a9e): non-producer check of 16 real-K pins from main 1b818427, then cells art:be42c41a c8cc8514 67fb03cb db9f01bf; CPU pod, $8

# verify-bligero-real-k: non-producer check of bligero-real-k's 16 real-K pins and its 4 registered cells

Launch brief: coordinator (cloud agent bc-30d7a020-fc45-5944-9ceb-1ac513232a9e). Request: `lanes/coordinator/20260926T0512Z-handoff-from-bligero-real-k.md`.
Also read: `20260926T0437Z-handoff-from-bligero-real-k.md` and `20260926T0551Z-handoff-from-bligero-real-k.md` (the cell list and the interaction question, which isn't mine).
Base: main 1b818427 (the bligero merge). No code commits. Scripts are in `evidence/`.

## 1. Pins: 16/16 confirmed
- `evidence/pins_check.py` is my own recipe, not the producer's. It compiles `hashchain.compose(relation("<fold>-k<K>"), leaf)` for
  4 folds × {2048, 8192} × {blake3-xob, sha256}, then checks each system six ways:
  - `ligero-verify system-digest` (main's release build) against the PINS rows, which it parses from `leaf.rs` itself;
  - the binary's own `pinned_relation` equals `<fold>-k<K>+<leaf>` in every case;
  - `protocol.system_id` equals the verifier's `sys_id`;
  - the Rust `at_k!` steps equal K/k, and the tags equal Python's;
  - the producer's `pins-vm-compile.json` agrees;
  - PINS has 35 rows and no duplicated digest.
- Ran twice, with the same result both times:
  - on the VM with the VM build: `evidence/pins-check-main-1b818427.json`;
  - on the pod with the pod build (sha256 8d5563a6): run r20260926-061022-eac8, `pins-check.json`.
- `cargo test --release` for ligero-verify on the VM: 38 + 8 + 27 passed.

## 2. Cells: 4/4 verified=accepted (labels by verify-bligero-real-k, ref r20260926-062503-d9c2)
| cell | relation | set (re-staged) | batch | sessions | verifier s |
|---|---|---|---|---|---:|
| art:be42c41a | bf16-ampere-x4-k2048+blake3-xob | art:123dc234 captured, 6272/6272 IR-equal | 49/49, 2^-128.40 | 5/5 (US-KS-2) | 153.6 |
| art:c8cc8514 | bf16-ampere-x4-k8192+blake3-xob | art:927a4c3a captured, 1920/1920 | 60/60, 2^-128.10 | 5/5 (US-KS-2) | 522.3 |
| art:67fb03cb | bf16-hopper-x4-k2048+blake3-xob | art:4f27dc3d synthetic, 4096/4096 | 16/16, 2^-128.03 | 5/5 (US-GA-2) | 48.4 |
| art:db9f01bf | bf16-ampere-x4-k2048+sha256 | art:123dc234 captured, 6272/6272 | 49/49, 2^-128.40 | 5/5 (US-KS-2) | 232.7 |

- Pod: vy-verify-bligero-real-k, dxkwi6u5039cat. It is an RTX A4000 used for its 18 vCPUs, because no CPU pod could be created
  (every flavor and DC returned "no instances"). EUR-IS-1, $0.25/h, about 06:07-06:31Z, about $0.10.
- Runs, both PRESERVED: r20260926-061022-eac8 (pins and input sets), r20260926-062503-d9c2 (the verdict run).
- What `evidence/pod-scripts/cell_check.py` does for each cell:
  1. **Input set, re-staged by me** (`research data fetch`):
     - every file matches the set's manifest;
     - the content digest equals the cell's;
     - `input_sets.verify` re-evaluates every instance with the IR evaluator and matches its outputs;
     - every file is byte-identical to the copy the prover staged (the `set/` entries of its run record).
  2. **Main's `reverify.verify_tree`, unchanged**, on the cell's proof dir:
     - custody;
     - system PINNED;
     - a/b/y commitments recomputed from my staged set (`--instances-root`), with every VU covered once;
     - `ligero-verify batch --target-bits 128`.
  3. The sha256 of every dumped file.
- **Live sessions** (`evidence/sessions_check.py` → `evidence/sessions-check.json`). The input is a read-only copy of the verifier's
  session records, taken over ssh while its runs were still serving. The snapshot is preserved as art:948270a5.
  - Verifier runs: r20260926-041624-7d7b (A100 cells), r20260926-051030-a6fe (H100 cell).
  - Every session: `hello` names the cell's run, relation, rep, B and N; its verdict accepted every proof with no live rejection;
    the batch accepts at ≥ 2^-128 against the pinned relation; the coins came from the verifier and differ in every sub-batch and session.
  - Each session's system.bin sha256 equals my own compile.
  - The rep-1 session's per-sub-batch `proof_sha256` / `stmt_sha256` and its coins files equal the dumped rep1 files, which step 2 verified.
- **Negatives** (VM, art:67fb03cb sub_00; `evidence/negatives-67fb03cb.txt`): the honest proof accepts, including against my own
  compiled system. All 7 tampered runs reject: a flipped proof byte, a flipped statement byte, another sub-batch's coins, another
  sub-batch's statement, and three wrong pinned systems (K=8192, Ampere, SHA-256).
- Every note says: file re-verification with the recorded coins, not transferable. The interaction cell_problem wasn't judged.

## 3. Findings
- **reverify entry point:** `reverify.py RESULT` returns ERROR on every bench.cell result: "has no proofs/ or dumps/
  manifest.json". bench.cell nests the dump at `meta.artifacts[0]` (`sweep/<point>/proofs`), and the entry point searches only the
  tree root. `verify_tree` itself handles these dumps: input-set commitments recompute. My harness finds the dir and calls
  `verify_tree`. A one-line fix in `reverify()`, which looks at `meta.artifacts[0]` first, would let any verifier lane run it
  directly. Handoff to the coordinator.
- The captured input sets (art:123dc234, art:927a4c3a) have this in their store meta: `table2: not admitted (captured
  realistic-distribution sets await Daniel's decision)`. For information only; my verdict doesn't depend on it.
- The producer's 06:22Z checkpoint says ROOT ruled to re-run all four cells with a fixed sender and supersede these. The re-runs
  need a new verification. The same two scripts apply: cell_check.py and sessions_check.py, with the session records taken from
  the verifier pod.
- Slip: at 06:12Z my first session pull wrote `*.system.sha256.tmp` files into the producer's live verifier run
  (`r20260926-041624-7d7b/sessions/`) and deleted them in the same ssh command. Nothing else was touched. All later reads were
  read-only.

## FINAL

~~~text
tip: lane/verify-bligero-real-k @ 1b818427 (base main@1b818427; no commits, not pushed)        merge-with: none
known-failures: none    pod: terminated 06:31Z (vy-verify-bligero-real-k dxkwi6u5039cat, A4000 EUR-IS-1); ~$0.10
artifacts: art:948270a5 (session snapshot); labelled art:be42c41a art:c8cc8514 art:67fb03cb art:db9f01bf; runs r20260926-062503-d9c2 r20260926-061022-eac8
~~~

- 16/16 real-K pins confirmed from main 1b818427.
- All 4 registered bligero-real-k cells are verified=accepted: file re-verification with the recorded coins, not transferable.
- Handoffs received: none in my own inbox. Acted on the coordinator folder's `20260926T0437Z-`, `0512Z-` and
  `0551Z-handoff-from-bligero-real-k.md`.
- Sent: `lanes/coordinator/20260926T0635Z-handoff-from-verify-bligero-real-k.md`.
- Left open:
  - the cell re-runs that will supersede these four (the queue is held for the sender fix);
  - the reverify entry-point fix;
  - the interaction ruling.

## Reopen 1 (07:41Z-08:35Z): bligero-real-k's 14 new-sender cells, all verified=accepted

Request: the coordinator's launch message.
- It listed b1d710da, 3bb4d03f, 11208bf7, c92a439a, 767b54db and c56a09a8, plus "whatever is registered when you finish".
- Its handoff `20260926T0740Z` had not synced when I finished. It was never in my lane directory, so I relied on the ids in the message.
- Received and acted on: `20260926T0705Z-handoff-from-bligero-real-k.md` (c56a09a8, 664f3142) and
  `20260926T0758Z-handoff-from-bligero-real-k.md` (nine cells, every one covered below).
- Sent: `lanes/coordinator/20260926T0745Z-handoff-from-verify-bligero-real-k.md` (REOPENED; the pod was created after the
  15-minute window).

Base: main 2bd8ce2f, which contains the reverify fix 9e42518a. `backends/ligero-verify` has not changed since 1b818427.
The pins were re-checked at 2bd8ce2f on the pod: 16/16, pod build fb774954, run r20260926-075651-fc42.

Pod: vy-verify-bligero-real-k, a cpu3c with 32 vCPU, pod lusnnk1ekkj0je.
- US-MD-1 by IP (154.54.102.16), $0.96/h, 07:55-08:29Z, about $0.55. A CPU pod was available this time.
- The machines.d entry still named the old pod, so I re-registered it with `pods register --replace`.

Method: the same as round 1, with three differences.
- `cell_check.py` now calls main's fixed `reverify.reverify` entry point (dry run, my staged set as the instances root)
  instead of calling `verify_tree` directly.
- The session records come from `evidence/gather_sessions.py`. Preserved verifier runs are read from their run records in
  the store. Runs still serving are read over ssh with tar and sha256sum to stdout, so nothing is written on the pod.
- `evidence/snapshot_vs_record.py` confirms that every live-read snapshot equals the verifier run's preserved record, file by file.
  - This round: r20260926-070945-4ad5 (180 files) and r20260926-072253-ca25 (360 files).
  - Round 1's snapshots also check out against their now-preserved records: r20260926-041624-7d7b (850 files) and
    r20260926-051030-a6fe (100 files). The `.tmp` files from round 1's slip are not in the record.
  - Still live-read only when I finished: r20260926-073309-3956 (4b567c9c, f1ac2db5, 9fd5ec09, 82587955). Its run was still
    serving; re-running `snapshot_vs_record.py` once it is preserved closes this.

| cell | relation | set (re-staged; IR-equal) | batch | run |
|---|---|---|---|---|
| art:c56a09a8 | bf16-hopper-x4-k2048+blake3-xob | art:4f27dc3d synthetic, 4096/4096 | 16/16, 2^-128.03 | r20260926-075651-fc42 |
| art:664f3142 | fp8-ada-x4-k2048+blake3-xob | art:c063de3a synthetic, 6272/6272 | 16/16, 2^-128.03 | r20260926-075651-fc42 |
| art:3bb4d03f | bf16-ampere-x4-k2048+blake3-xob | art:123dc234 captured, 6272/6272 | 32/32, 2^-128.35 | r20260926-075651-fc42 |
| art:11208bf7 | bf16-hopper-x4-k8192+blake3-xob | art:ee183a74 synthetic, 4096/4096 | 32/32, 2^-128.35 | r20260926-075651-fc42 |
| art:c92a439a | fp8-ada-x4-k2048+sha256 | art:c063de3a synthetic, 6272/6272 | 32/32, 2^-128.63 | r20260926-075651-fc42 |
| art:b1d710da | bf16-ampere-x4-k8192+blake3-xob | art:927a4c3a captured, 1920/1920 | 60/60, 2^-128.10 | r20260926-075651-fc42 |
| art:767b54db | fp8-ada-x4-k8192+blake3-xob | art:cdb0e90d synthetic, 1920/1920 | 60/60, 2^-128.36 | r20260926-075651-fc42 |
| art:1dafbfd5 | bf16-ampere-x4-k2048+sha256 | art:123dc234 captured, 6272/6272 | 32/32, 2^-128.35 | r20260926-081703-0f0a |
| art:f1ac2db5 | fp8-hopper-x4-k2048+blake3-xob | art:5f311851 synthetic, 6272/6272 | 16/16, 2^-128.03 | r20260926-081703-0f0a |
| art:9fd5ec09 | fp8-hopper-x4-k8192+blake3-xob | art:d5578eff synthetic, 1920/1920 | 16/16, 2^-128.03 | r20260926-081703-0f0a |
| art:f451dabc | fp8-ada-x4-k8192+sha256 | art:cdb0e90d synthetic, 1920/1920 | 60/60, 2^-128.36 | r20260926-081703-0f0a |
| art:4b567c9c | bf16-hopper-x4-k2048+sha256 | art:4f27dc3d synthetic, 4096/4096 | 8/8, 2^-128.37 | r20260926-082424-5906 |
| art:622c9737 | bf16-ampere-x4-k8192+sha256 | art:927a4c3a captured, 1920/1920 | 32/32, 2^-128.35 | r20260926-082424-5906 |
| art:82587955 | fp8-hopper-x4-k2048+sha256 | art:5f311851 synthetic, 6272/6272 | 8/8, 2^-128.37 | r20260926-082424-5906 |

What every cell passed:
- **Input set:** my copy's files match its manifest, its content digest equals the cell's, every instance passes the IR
  evaluator, and it is byte-identical to the prover's staged copy.
- **reverify:** custody complete, system PINNED to my own compile, commitments recomputed from my set, every VU covered once, batch ≥ 2^-128.
- **Sessions:** 5/5 accepted with fresh, distinct verifier coins. The system file on the verifier's disk and in `hello`
  equals my compile, and the rep-1 proofs, statements and coins equal the dump.

Evidence: `evidence/sessions-check-reopen-r{1,2,3}.json`, `evidence/session-sources.json` and `evidence/session-system-sha256.json`.

Labels: each cell got verified=accepted, verifier, verifier_seconds, same_device=false and note, all by verify-bligero-real-k
with ref to its run. All 70 are on both sides (local and R2). All three runs are PRESERVED.

Not judged: the interaction under-model notes (Daniel's one-sided rule).

Left: bligero-real-k's last 2 of 16 new-sender cells (H100 K8192 SHA-256, BF16 run r20260926-081620-1969, then FP8) were not
registered at 08:29Z.

## FINAL (reopen 1)

~~~text
tip: lane/verify-bligero-real-k @ 2bd8ce2f (base main@2bd8ce2f; no commits, not pushed)        merge-with: none
known-failures: none    pod: terminated 08:29Z (lusnnk1ekkj0je cpu3c-32); ~$0.55 this round, lane total ~$0.65
artifacts: labelled art:c56a09a8 art:664f3142 art:3bb4d03f art:11208bf7 art:c92a439a art:b1d710da art:767b54db art:1dafbfd5 art:f1ac2db5 art:9fd5ec09 art:f451dabc art:4b567c9c art:622c9737 art:82587955; runs r20260926-075651-fc42 r20260926-081703-0f0a r20260926-082424-5906
~~~
