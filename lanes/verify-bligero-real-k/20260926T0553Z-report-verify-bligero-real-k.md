---
lane: verify-bligero-real-k
kind: report
created: 2026-09-26T05:53Z
status: final
---

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
