---
lane: verify-bligero-real-k
kind: report
created: 2026-09-26T05:53Z
status: open
---

CHECKPOINT e77d40c9 (13:31Z) [open] no CPU pod (~20 tries); pod = RTX 3090 rk1g146smgnjwk (32 vCPU, $0.50/h, CPU use only); run launched at main e77d40c9 (pins + dd6b0cac + c64377df). Separation from harness job.json/launch.json + verifier session peer: distinct boot ids, hosts, GPU UUIDs, public IPs. Handoff 1316Z acted on
CHECKPOINT e48ec526 (13:23Z) [open] reopened for #101 L40S B-Ligero cells art:dd6b0cac (K2048, 2^-128.03) + art:c64377df (K8192, 2^-128.265) incl. chain-term bound and prover/verifier machine separation: NOT final; agent bc-30d7a020-fc45-5944-9ceb-1ac513232a9e; $1
CHECKPOINT e48ec526 (11:46Z) [final] FINAL (reopen 3): art:4ff19d4f verified=accepted at 2^-128.265 w/ chain_field (independently recomputed; ref r20260926-113155-ffa4, main e48ec526, pins 16/16); below_bar=true on art:b1d710da (2^-127.97, proofs verify); pod terminated 11:44Z ~$0.10
CHECKPOINT e48ec526 (11:32Z) [open] pod cpu3c-16 uxjdwpkx4di1bo; run launched at main e48ec526 (>= e8ec5e19): pins + 4ff19d4f + b1d710da re-check under chain_field booking; sessions for 4ff19d4f from store record art:f4567196. Handoffs 1030Z + 1115Z acted on
CHECKPOINT 49cc39ef (11:26Z) [open] reopened for art:4ff19d4f (A100 K8192 xob re-run, supersedes b1d710da; A1 chain term bound 2^-128.265) + non-producer below_bar label on b1d710da: NOT final; agent bc-30d7a020-fc45-5944-9ceb-1ac513232a9e; $1
CHECKPOINT 49cc39ef (09:09Z) [final] FINAL (reopen 2): e8fb169d + 9260a985 verified=accepted (ref r20260926-085735-35b1, main 49cc39ef, pins 16/16); all 16 real-K new-sender cells verified; snapshot r20260926-073309-3956 = preserved record (320/320); pod terminated 09:08Z ~$0.10
CHECKPOINT 49cc39ef (08:59Z) [open] snapshot_vs_record r20260926-073309-3956: 320/320 files = preserved record art:af3a9928; sessions for e8fb169d 9260a985 from that record; pod cpu3c-16 t258al5w5tu80i ($0.48/h); run launched (pins + 2 cells at main 49cc39ef). Handoff 0845Z acted on
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

## Reopen 2 (08:53Z-09:12Z): the last 2 cells; the 16-cell real-K matrix is verified

Request: the coordinator's launch message.
- Received and acted on: `20260926T0845Z-handoff-from-bligero-real-k.md`. It lists the final five cells, three of which I
  had already verified in Reopen 1.
- Base: main 49cc39ef. The verifier, reverify, relchain, relations, hashchain, serialize, leaf and input_sets code is
  unchanged since 2bd8ce2f.
- Pod: vy-verify-bligero-real-k, a cpu3c with 16 vCPU, pod t258al5w5tu80i. Re-registered with `--replace`. $0.48/h,
  08:56-09:08Z, about $0.10. There were no 32-vCPU CPU pods.
- Run r20260926-085735-35b1 (PRESERVED): pins 16/16 at 49cc39ef (pod build 6fd31a3d), then both cells.
- **snapshot_vs_record, r20260926-073309-3956:** the session files I read live over ssh equal its preserved record art:af3a9928:
  320/320 files plus system.bin (`evidence/snapshot-vs-record-3956.json`).
  - This closes Reopen 1's open item. Addendum `note` labels on art:4b567c9c, art:f1ac2db5, art:9fd5ec09 and art:82587955
    record it (ref art:af3a9928).
  - Every verifier run whose sessions I read live now matches its preserved record: 7d7b, a6fe, 4ad5, ca25 and 3956.

| cell | relation | set (re-staged; IR-equal) | batch | sessions |
|---|---|---|---|---|
| art:e8fb169d | bf16-hopper-x4-k8192+sha256 | art:ee183a74 synthetic, 4096/4096 | 32/32, 2^-128.35 | 5/5 (US-GA-2, store record) |
| art:9260a985 | fp8-hopper-x4-k8192+sha256 | art:d5578eff synthetic, 1920/1920 | 16/16, 2^-128.03 | 5/5 (US-GA-2, store record) |

- Both cells are verified=accepted, labels by verify-bligero-real-k with ref r20260926-085735-35b1. All labels are on both sides.
  Evidence: `evidence/sessions-check-reopen2.json`.
- **Matrix:** all 16 new-sender cells (4 folds × K ∈ {2048, 8192} × {blake3-xob, sha256}) are now verified=accepted:
  - c56a09a8, 664f3142, 3bb4d03f, 11208bf7, c92a439a, b1d710da, 767b54db, 1dafbfd5
  - f1ac2db5, 9fd5ec09, f451dabc, 4b567c9c, 622c9737, 82587955, e8fb169d, 9260a985
  - Round 1's four cells, since superseded, are also verified=accepted.
- Not judged: the interaction notes.

## FINAL (reopen 2)

~~~text
tip: lane/verify-bligero-real-k @ 49cc39ef (base main@49cc39ef; no commits, not pushed)        merge-with: none
known-failures: none    pod: terminated 09:08Z (t258al5w5tu80i cpu3c-16); ~$0.10 this round, lane total ~$0.75
artifacts: labelled art:e8fb169d art:9260a985 (+ addendum notes on art:4b567c9c art:f1ac2db5 art:9fd5ec09 art:82587955, ref art:af3a9928); run r20260926-085735-35b1
~~~

## Reopen 3 (11:25Z-11:50Z): art:4ff19d4f (the A100 K8192 xob re-run) and below_bar on art:b1d710da

- **Request:** the coordinator's launch message. Received and acted on: `20260926T1030Z-handoff-from-coordinator.md` (write the
  non-producer below_bar on b1d710da) and `20260926T1115Z-handoff-from-bligero-real-k.md` (the cell at 2^-128.265 over 32 sub-batches).
- **Base:** main e48ec526, which contains e8ec5e19 and PR #71's d7656f9c. main's ligero-verify books `chain_field`.
- **Pod:** vy-verify-bligero-real-k, a cpu3c with 16 vCPU, pod uxjdwpkx4di1bo, re-registered with `--replace`.
  - No CPU pod was available on the first 10 tries; the retry after the session gather got one.
  - $0.48/h, 11:31-11:44Z, about $0.10.
- **Run r20260926-113155-ffa4 (PRESERVED):** pins 16/16 at e48ec526 (pod build 161b68db), then both cells.
- **art:4ff19d4f: verified=accepted** (ref r20260926-113155-ffa4).
  - Input set art:927a4c3a re-staged: IR-equal (1920/1920) and equal to the prover's copy.
  - reverify PASS: custody 97/97, PINNED, commitments recomputed from my set, batch 32/32 at 2^-128.265.
  - 5/5 sessions: verifier run r20260926-103731-fe03, read from its store record; the verifier's batch is also 2^-128.265.
  - Bound, my own exact recomputation (Fractions) from the statement: n 16384, l 4096, t 202, D 6, t_pad 256.
    - 549 linked chain rows, counted in my own compile of the system, give E = 1092, degree 183, and chain_field
      (3·183/2^32)^6 = 2^-137.396.
    - Per proof 2^-133.2655; whole proof over 32 sub-batches **2^-128.2655**; without chain_field 2^-128.350.
    - This equals the Rust verifier's figure (single-proof `verify` on sub_00: per proof -133.265, union -128.265, terms
      identical) and the producer's.
- **art:b1d710da: below_bar=true** by verify-bligero-real-k (ref r20260926-113155-ffa4), with a note.
  - Same checks at e48ec526: custody 181/181, PINNED, commitments recomputed, and 60/60 proofs accept individually.
  - The batch at `--target-bits 128` REJECTS on the bound only: 2^-127.97 over 60 sub-batches. The single-proof `verify`
    rejects with "parameters give 2^-127.97".
  - My recomputation (t 203): per proof 2^-133.879, whole 2^-127.972, and 2^-128.104 without chain_field, which is the
    figure my 08:17Z verified=accepted used. That label stands for the proofs; below_bar moves the cell out of Table 2.
  - Label correction: my first note at 11:45Z misstated that label's time. A replacement note says so.
- **Evidence:** `evidence/sessions-check-reopen3.json`, `evidence/session-sources.json`, `evidence/session-system-sha256.json`.
- **Not judged:** the interaction note (38% under the model), and the plateau-point rule (Daniel's decision).

## FINAL (reopen 3)

~~~text
tip: lane/verify-bligero-real-k @ e48ec526 (base main@e48ec526; no commits, not pushed)        merge-with: none
known-failures: none    pod: terminated 11:44Z (uxjdwpkx4di1bo cpu3c-16); ~$0.10 this round, lane total ~$0.85
artifacts: labelled art:4ff19d4f (verified=accepted), art:b1d710da (below_bar=true); run r20260926-113155-ffa4
~~~

## Reopen 4 (13:22Z-13:45Z): #101 B-Ligero cells on the L40S, art:dd6b0cac (K2048) and art:c64377df (K8192)

- **Request:** the coordinator's launch message. Received and acted on: `20260926T1316Z-handoff-from-bligero-real-k.md`.
- **Base:** main e77d40c9. The verifier, reverify and chain-term code is unchanged since e48ec526.
- **Pod:** no CPU pod in about 20 tries over 5 minutes, so an RTX 3090 used for its 32 vCPUs only: rk1g146smgnjwk, $0.50/h,
  13:28-13:38Z, about $0.09.
- **Run r20260926-133012-30ab (PRESERVED):** pins 16/16 at e77d40c9 (pod build 64975433), then both cells.

| cell | relation | set (re-staged; IR-equal) | batch | bound (my recomputation) | sessions |
|---|---|---|---|---|---|
| art:dd6b0cac | bf16-ampere-x4-k2048+blake3-xob | art:123dc234 captured, 6272/6272 | 16/16 | 2^-132.03/proof, **2^-128.03** (165 chain rows, chain_field 2^-147.802) | 5/5 |
| art:c64377df | bf16-ampere-x4-k8192+blake3-xob | art:927a4c3a captured, 1920/1920 | 32/32 | 2^-133.2655/proof, **2^-128.2655** (549 rows, chain_field 2^-137.396; 2^-128.350 without) | 5/5 |

- **Both verified=accepted** (ref r20260926-133012-30ab).
  - reverify PASS: custody, PINNED, commitments recomputed from my set.
  - Sessions: verifier run r20260926-122717-c116, read from its store record art:012d0166. They match the dump and my compiled
    system, and the coins are distinct.
  - Bounds: my exact Fractions recomputation from each statement, with the chain rows counted in my own compile, equals the
    Rust verifier's figure.
- **Machine separation**, from records the research harness writes itself, not the cell script (`evidence/separation-l40s-101.json`):

| | prover (r20260926-122746-a284, r20260926-130128-a83c) | verifier (r20260926-122717-c116) |
|---|---|---|
| kernel boot id (job.json) | c878c736-6098-4887-84cd-e456f033aa4b | 1ae4223a-b967-47ed-ba09-360af7348bf0 |
| hostname (job.json, launch.json) | 13837d713f4a | 4d9fbee72571 |
| GPU UUID (job.json) | GPU-129a3a88-… | GPU-0c4713c5-… |
| host memory (job.json) | 1081799454720 B | 1081799475200 B |
| pod / ssh host (launcher, launch.json) | 8loxygl068ukkc / 64.247.206.218 | vdel26rpc47d2g / 64.247.206.229 |

  - Every session's TCP peer, as the verifier saw it, is 64.247.206.218, the prover's address.
  - Containers on one host share the host kernel's boot id, so different boot ids mean different machines.
  - RunPod machine ids 9sng1e8op7yw and mszbaoah5eb7 are only in the producer's plan record, captured from the RunPod API at plan
    time. Both pods are terminated, and RunPod's pod query now returns null.
- **Evidence:** `evidence/sessions-check-reopen4.json`, `evidence/separation-l40s-101.json`.
- **Not judged:** the interaction notes (45% / 41% under the model).

## FINAL (reopen 4)

~~~text
tip: lane/verify-bligero-real-k @ e77d40c9 (base main@e77d40c9; no commits, not pushed)        merge-with: none
known-failures: none    pod: terminated 13:38Z (rk1g146smgnjwk RTX 3090, CPU use only); ~$0.09 this round, lane total ~$0.95
artifacts: labelled art:dd6b0cac art:c64377df (verified=accepted); run r20260926-133012-30ab
~~~
