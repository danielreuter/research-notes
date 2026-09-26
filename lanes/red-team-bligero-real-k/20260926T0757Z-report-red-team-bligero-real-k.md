---
lane: red-team-bligero-real-k
kind: report
created: 2026-09-26T07:57Z
status: open
---

CHECKPOINT 5e7e255d (11:27Z) [open] reopened for bligero-real-k 1115Z (art:4ff19d4f A100 K8192 xob, A1 booked in PR #71, 3/2^32 coin deviation): NOT final; CPU only, no pod
CHECKPOINT 5e7e255d (09:21Z) [final] FINAL: real-K B-Ligero class GRANTED WITH CONDITIONS (COMPLETE_ZK_BACKEND; coordinator/0917Z); proof_class+finding on 16 new-sender cells; no break; A1 chain-test field term unbooked (<=2^-140.35/proof at K8192 BF16, no cell below 2^-128); evidence art:dc790613; tools cursor/red-team-bligero-real-k-0819@5e7e255d; no pod, $0
CHECKPOINT 5e7e255d (09:21Z) [final] FINAL: real-K B-Ligero class GRANTED WITH CONDITIONS (COMPLETE_ZK_BACKEND; coordinator/0917Z); proof_class+finding on 16 new-sender cells; no break; A1 chain-test field term unbooked (<=2^-140.35/proof at K8192 BF16, no cell below 2^-128); evidence art:dc790613; tools 5e7e255d; no pod, $0
CHECKPOINT 345a64f9 (08:42Z) [open] tools @345a64f9 (cursor/red-team-bligero-real-k-0819). live sender 15/15 refused/accepted as expected (head-only check defers body to Rust); sessions: 10/14 cells every rep = rep-1 statements (4 wait on H100 verifier r...3956 record); scans+cross-K e2e running on VM; finding: chain-extras field term unbooked (2^-140.35/proof at K8192 BF16), no cell below 2^-128
CHECKPOINT e3a2d81d (08:18Z) [open] code read done (relations._at_k, sized blake3 frame, sha256@K, Rust gate/steps/sized, live server head-only checks): no break yet; VM: real-K gadget scans running (xob + sha256, 4 shapes + controls), 8 small honest CPU dumps for cross-K attacks; no pod
CHECKPOINT e25e3614 (07:57Z) [open] started (agent bc-cbd1f3e8-36d9-57ec-9a9b-feb10db40819): class review of B-Ligero real-K statements (k2048/k8192 x4, sized blake3-xob, sha256) + new streaming sender per bligero-real-k 0512Z request (unanswered: red-team-standard-hash-2 final); main code read first; $5

# red-team-bligero-real-k: class review of B-Ligero's real-K statements and the streaming live sender

Launch: root coordinator (overnight goal 5), agent bc-cbd1f3e8-36d9-57ec-9a9b-feb10db40819, budget $5, CPU pods preferred.
Request: bligero-real-k's `lanes/red-team-standard-hash-2/20260926T0512Z-handoff-from-bligero-real-k.md`. Nobody had answered it
(red-team-standard-hash-2 was final at 23:47Z).
Code reviewed: main e3a2d81d (real-K 1b818427, sender 47205d3f = PR #55). Non-producer: no code on bligero's branch. My tools are
on `cursor/red-team-bligero-real-k-0819`. Everything ran on the cloud VM (4 vCPU, CPU torch, ligero-verify built from main, sha256
85a69b63): no pod, $0.

## Verdict
**CLASS GRANTED WITH CONDITIONS: COMPLETE_ZK_BACKEND** for `<fold>-k<K>+blake3-xob` / `+sha256`, where fold is one of the four
x4 folds and K is 2048 or 8192 (the 16 PINS rows). It covers `--zk`, interactive 8c on live coins, included-hash, and the
streaming sender.
- Grant: `lanes/coordinator/20260926T0917Z-handoff-from-red-team-bligero-real-k.md`. Evidence: art:dc790613 (supersedes
  art:43876953).
- Conditions:
  1. PINNED.
  2. Non-producer reverify at 9e42518a or later, with commitments recomputed from the re-staged set.
  3. New with `--drop-files`: every timed rep's session accepted and pinned, with its per-sub-batch `stmt_sha256` equal to rep 1's.
  4. BOUND at or below 2^-128 with A1's term added.
  5. Inputs are a registered set of that K.
- ZK is as for the x4 cells, relative to published unsalted per-chunk digests.

## Findings
- **A1 (accounting, not a break): the chain test's field term is not booked.**
  - With nl > 3 linked rows, `chain.py` coefficients are monomials `u_(e mod 6) u_6^(e div 6 + 1)`. The term is therefore
    (deg / p)^D, with deg = (2 (nl - 3) - 1) div 6 + 2.
  - Both Python and Rust book 1 / p^D.
  - Values (compiled systems): SHA-256 nl 69, 2^-158.3; 3-slot BLAKE3 nl 133, 2^-152.5; BF16 K2048 nl 165, 2^-150.75; FP8 K8192
    nl 293, 2^-145.75; BF16 K8192 nl 549, 2^-140.35.
  - All 16 cells stay at or below 2^-128. The worst is b1d710da, 2^-128.104 becoming 2^-128.086.
- **NIT:** `live.Session._data_loop` has an unhandled RuntimeError after its pool shut down, when a frame arrives after a refused
  session.
- **NIT:** bare real-K systems carry the fold's sys_id, so `system-digest` reports them as the K1536 fold. reverify refuses a bare
  real-K dump. Completeness only, outside the class.
- **Checked, not a finding:** `at_k!` copies the base's `hashed_sys_id`, but it is empty for every x4 base, so Poseidon2 is
  unpinned at real K.

## Evidence (art:dc790613)
| check | result |
|---|---|
| leaf scan blake3-xob 16:2 K2048 / 16:2 K8192 / 8:2 K2048 / 8:2 K8192 (ncm 4 / 16 / 3 / 8) | 0 free rows (191,048 / 193,000 / 190,760 / 191,712 mutations); digest = `blake3` keyed digest of the row; header / ncm = Rust `sized` |
| leaf scan sha256, same 4 shapes | 0 free rows (300,416 each); digest = hashlib SHA-256(prefix, row); header n_words = K |
| controls | xob: arithmetic 16, position decomposition 5, hold product 1 free rows; sha256: arithmetic 17 |
| Rust unit tests (sized, blake3, names_are_distinct, vu_shapes) | pass; the K2048/8192 vectors equal `blake3` independently |
| e2e on 9 honest CPU dumps (2 sub-batches each) | 71/72 as expected (the 72nd a byte-identical no-op, harness fixed 5e7e255d): 9 honest controls PASS all 4 verifiers; 24 cross-K relabels + 8 mixed reps refused (gate / pinned steps / parse / M; reverify pin-vs-manifest or commitment recompute); steps / K lies refused (steps-lie2 reaches `check_vu_shape` / `layout_error`); last-CV / 3-slot header / nch-1 refused, the leaf off the root; orphan / drop / dup fail reverify (Rust batch accepts dup) |
| streaming sender, loopback Rust core + drop-files + multi-data | 15/15: honest accepted (files dropped, proof_sha256 = the bytes sent); dup, swap and extra PROOF refused; body flips, tail, truncation, flag 2 and hash id 2 pass the head check and Rust refuses them |
| sessions, 16 cells x 5 | every timed rep proved the rep-1 statements, fresh proofs, all live checks and verdicts accepted (preserved verifier records; r...3956 first read-only over ssh, then from its record) |

## Labels
`proof_class COMPLETE_ZK_BACKEND` plus a `finding HOLDS ...` label, by red-team-bligero-real-k, ref the grant, on the 16 new-sender
cells:
- A100: 3bb4d03f, 1dafbfd5, b1d710da, 622c9737
- H100: c56a09a8, 4b567c9c, 11208bf7, e8fb169d, f1ac2db5, 82587955, 9fd5ec09, 9260a985
- 4090: 664f3142, c92a439a, 767b54db, f451dabc

All 16 were already verified=accepted by verify-bligero-real-k. The superseded old-sender cells got no label.

## FINAL

~~~text
tip: cursor/red-team-bligero-real-k-0819 @ 5e7e255d (base main@e3a2d81d)        merge-with: none (red-team tools only; optional)
known-failures: none    pod: none (all on the cloud VM); $0
artifacts: art:dc790613 (supersedes art:43876953)
~~~

- The class is granted with conditions (COMPLETE_ZK_BACKEND) for all 16 real-K statements, the streaming sender included. I found
  no break.
- `proof_class` and `finding` labels are on all 16 new-sender cells.
- One accounting finding (A1: the chain test's field term is not booked). It does not flip any cell. Two nits.
- Handoffs sent:
  - `lanes/coordinator/20260926T0917Z-handoff-from-red-team-bligero-real-k.md` (the grant);
  - `lanes/bligero-real-k/20260926T0917Z-handoff-from-red-team-bligero-real-k.md` (A1's margin for K8192 BF16 cells).
- Handoffs received: none in my own inbox. I acted on `lanes/red-team-standard-hash-2/20260926T0512Z-handoff-from-bligero-real-k.md`,
  the request I was launched on.
- kb: `ligero-hash-auth.md` gains the section "Real K": the class, the cross-rep session check `--drop-files` needs, and A1's
  terms.
- Left for others:
  - the A1 fix: book `linear_field = D (log2 deg - log2 p)` from the system's linked-row count, in `protocol.soundness` and in Rust
    `soundness()`;
  - the `_data_loop` RuntimeError nit.
