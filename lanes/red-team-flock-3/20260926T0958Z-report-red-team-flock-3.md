---
lane: red-team-flock-3
kind: report
created: 2026-09-26T09:58Z
status: final
---

CHECKPOINT e5493f9f (15:36Z) [final] FINAL: (1) per-T attention v3 GRANTED W/ CONDITIONS NON_ZK_PROOF, 16 cited + 11 superseded cells labelled; (2) key-count class pins @4eb3b991/11f24da6 GRANTED W/ CONDITIONS NON_ZK_PROOF (CP1/2/3/4/5/7/8 met); class cells c1 art:4fb2de9c (T1-128) + c3 art:4dd2069b (T257-287) PASS, SEPARATE, labelled NON_ZK_PROOF; c2 (T129-256) pending ~16:20Z at 8ef6d347 (harness-only), procedure in handoff 1540Z; art:25c96f97 c185d38b 8be608c6 3b34c1dd; pod ~$0.32
CHECKPOINT e5493f9f (14:40Z) [open] c3 art:4dd2069b [257,512] T=257..287 CLASS_CELL_CHECK PASS 31/31, SEPARATE, labelled NON_ZK_PROOF; c1 art:4fb2de9c labelled; polling for c2 re-run (T=129..256, 53ffcaca, ETA 15:15Z), FINAL by 15:30Z
CHECKPOINT e5493f9f (14:33Z) [open] WAITING c3 (T=257..287, pair b, r20260926-140931-b414, ETA 14:40Z) + c2 re-run (T=129..256, pair a, 53ffcaca, ETA 15:15Z), check after 14:45Z; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26; done: c1 art:4fb2de9c CLASS_CELL_CHECK PASS (128/128 sub-batches, manifest = mine byte for byte), placement SEPARATE (pxp3jjc5ozkz vs daejz5pkfg8j), labelled NON_ZK_PROOF; CP2 MET @11f24da6 (r20260926-143204-b20f); CP7 MET main PR #79; CP8 MET
CHECKPOINT e5493f9f (13:32Z) [open] WAITING flock-ir-lowering's class cells (3 classes on vy-flock-ir-lowering-nc-l40s / nc-ver), check after 14:15Z; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26; next: check_class_cells.sh + placement + label each class cell, then FINAL
CHECKPOINT e5493f9f (13:31Z) [open] class pins @4eb3b991 GRANTED W/ CONDITIONS NON_ZK_PROOF: T+mask verifier-fixed, CP1/3/4/5 met (512 nets = reviewed generator), 14 load + 4 session negatives, selftest 24/24 under --class (r20260926-132829-2165; art:8be608c6); CP7 census matcher rejects class cells (needs key_counts crediting), CP8 register full-set point; handoffs 1340Z; next: label class cells as they land
CHECKPOINT e5493f9f (13:16Z) [open] class-pin review prep while its code lands (branch still ece9fdd2 at 13:17Z): local CPU flock-ir-frame build OK (honest T=129 accepted); reviewed generator's nets for T=1..512 re-derived (512 distinct, one shared unit_rows fca8a6f6); e2e +648 adversarial heads at 18 new T up to 512, 0 mismatches (r20260926-130636-5ee4); census matcher reads ONE T per result (input_variables) -> class cells must register per-T results or census-json extends it
CHECKPOINT e5493f9f (13:01Z) [open] reopened for the class-statement review (coordinator 13:00Z: next priority; flock-ir-lowering 1305Z request, paper answer CP1-CP6 at 1310Z): NOT final; the 16 ece9fdd2 attention cells are already checked, placement-verified and labelled NON_ZK_PROOF; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (12:59Z) [final] FINAL attention flock-ir-frame/v3 GRANTED W/ CONDITIONS NON_ZK_PROOF (AC1-AC4); 16 cited L40S cells (ece9fdd2) + 11 superseded: cell_check PASS, placement SEPARATE (PR #74 clean), labelled NON_ZK_PROOF; 0 IR mismatches; 60 negatives refused; class-pin design (1305Z) answered on paper CP1-CP6, code review routed to coordinator; no lane branch (notes-only); art:25c96f97 art:c185d38b; pod terminated 11:03Z ~$0.32
CHECKPOINT e5493f9f (12:58Z) [final] FINAL attention flock-ir-frame/v3 GRANTED W/ CONDITIONS NON_ZK_PROOF (AC1-AC4); all 16 cited L40S cells (ece9fdd2) + 11 superseded: cell_check PASS, placement SEPARATE (PR #74 clean), labelled NON_ZK_PROOF; 0 IR mismatches (2e7 TC vectors, 2^32 tail prims, 4,048 heads); 60 negatives refused; art:25c96f97 art:c185d38b; pod terminated 11:03Z ~$0.32
CHECKPOINT e5493f9f (12:17Z) [open] WAITING last 8 ece9fdd2 attention re-runs (T=4,128..132,256,257), check after 12:50Z; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26; placement (red-team-flock 12:00Z ruling): all 19 cells SEPARATE (machines av7yp9ygnbzg vs oc60c34mphhh, boot/kernel/CPU/GPU differ, 10.x routed; PR #74 separation() clean), labels stay NON_ZK_PROOF, findings re-labelled with placement
CHECKPOINT e5493f9f (12:11Z) [open] WAITING flock-ir-lowering's last ece9fdd2 re-runs (T=4,128..132,256,257) on vy-flock-ir-lowering-nc-l40s, check after 12:50Z; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26; done: 8 ece9fdd2 cells PASS+labelled (T=1,2,3,258..261,287: art:3b8280fa baa539f8 0051325c 327e9366 a552878e 186b9949 f52bf885 298d4c14); next: last 8, then FINAL
CHECKPOINT e5493f9f (11:17Z) [open] WAITING r20260926-110548-5012 (flock-ir-lowering T=258 prover) on vy-flock-ir-lowering-nc-l40s, check after 12:05Z; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26; next: cell_check + label the 16 ece9fdd2 re-run cells (harness-only, in grant), then FINAL
CHECKPOINT e5493f9f (11:16Z) [open] attention flock-ir-frame/v3 GRANTED W/ CONDITIONS NON_ZK_PROOF (AC1-AC4); 11 L40S cells cell_check PASS + labelled; pod dq3xclby5ni4ic terminated 11:03Z after custody (~$0.32); runs r20260926-103512-bb40 (art:25c96f97), r20260926-103647-114d, -104127-079a, -103647-17e8; next: T=258..261/287 + T=1/4 re-runs
CHECKPOINT e5493f9f (10:41Z) [open] run r20260926-103512-bb40 on vy-red-team-flock-3 (@22dc6320): producer selftest on my staged T=4/129/287 captured files, 18 adversarial honest sessions accepted; T=4 cell art:308df7ad verifier-staged file CELL_CHECK PASS (leaf maps, digests, roots, e2e vs IR); local tc/e2e diffs running
CHECKPOINT e5493f9f (10:28Z) [open] local VM: independent netlist evaluator + e2e solver (units+IR tail from pinned LEAVES/CUT) 0 mismatches on 24 captured + 162 adversarial heads (T 1/4/129); tail prims + TC unit diffs clean at small N; pod vy-red-team-flock-3 dq3xclby5ni4ic (A6000 as CPU box, no CPU stock) for build+negatives
CHECKPOINT e5493f9f (09:58Z) [open] started: took flock-ir-lowering 0922Z attention-head review (AttentionHead_v3 on flock-ir-frame/v3, PR #54 f4cd5d4e/22dc6320) from red-team-flock-2; reading diff + evidence; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26

# #101's attention head on C-Flock: verity/flock-ir-frame/v3 (09:58–11:10Z)

**GRANTED WITH CONDITIONS at NON_ZK_PROOF** for `verity/flock-ir-frame/v3` on `attention-head/d64-bn128/sm80-fa2-bf16`
(AttentionHead_v3{T, D=64, BN=128}, one statement per T), at PR #54 `22dc6320` and `0839742b`. The two commits differ only in
the statement digest's TAG string (`git diff 22dc6320 0839742b -- backends/flock/live/src`: the TAG constant and a doc line).
The request was `lanes/red-team-flock-2/20260926T0922Z-handoff-from-flock-ir-lowering.md`; red-team-flock-2 was overloaded,
so this lane took it. The producer's claims hold, and I found no gap a cheating prover can reach against an honest verifier
file.

## Method (all tools mine, in `evidence/`; nothing from the producer's evaluators)

- **`netlist.py`:** my own reader and bit-sliced evaluator of `flock-ir-unit/v2` text. It checks that rows are
  topological, that there are no free rows and no assertion rows, and that every row is satisfied on every lane.
- **`attn_e2e.py`:** for each head, it solves the verifier's acceptance system from the pinned LEAVES and CUT lines alone.
  It starts from the public words, then runs the tail ops whose operands are known (evaluated by the IR's own primitives,
  looked up by id), then the units whose inputs are known (my evaluator), and repeats to a fixpoint. When every cut word is
  determined, the assignment is unique: the unit and tail dependency graph is acyclic. It then compares the outputs with
  `verity.evaluation.evaluate(AttentionHead_v3{T})` and with the captured outputs, and every cut word with the IR's gate
  values.
- **`gen_attn.py`:** adversarial heads in nine categories:
  - typical;
  - extreme scores, including saturated QK dots;
  - NaN and inf in q, k and v;
  - every score −inf (the all-masked row: max −inf, guard 0, sums 0, inv 1, out 0);
  - subnormal and floor-level operands;
  - one or several dominant keys (tied maxima, exact exp2 underflow);
  - max-magnitude V (saturated P·V, inf rescales);
  - signed zeros;
  - uniform 16-bit words.
- **`tc_diff.py`:** the unit netlist against `AmpereBF16TcDot16_v1` (verity.ml.tc.total). It uses ten families: moderate,
  uniform, sparse and dense specials, overflow with opposite-sign later groups and infinities, exact cancellation, the
  2^-132 floor, alignment/scale, one infinity against 0 or subnormal partners, and NaN payloads. `tc_mutants.py` gives it
  teeth: 5 of 6 one-row mutants differ on 20k vectors.
- **`tail3_diff.py` plus `rtf3_tail_main.rs`:** the crate's own `ir_tail::apply` against the IR primitives.
- **`cell_check.py` / `check_cells.sh`:** a registered cell's verifier-staged statement against the IR: netlist text,
  wiring against the pinned leaf maps, zero leaves and holes, the block table, digests (q from its row and from its public
  words), my own frame-v3 roots, and e2e against the file and the captured set.
- **`rtf3_frame_patch.py`:** prover-side RT3 knobs; the verifier is untouched. `frame_tamper3.py` makes load tampers and
  consistent restatements of the verifier's own file.

## Results

| check | scale | result | evidence |
|---|---|---|---|
| unit netlist (fp.tc_dot16, pin a5b162b3 rows) vs IR AmpereBF16TcDot16_v1 | 19,988,480 vectors, 10 families | 0 mismatches, 0 unsatisfied lanes | r20260926-103647-114d |
| e2e from the pinned text vs IR and captured | all 1,024 captured heads, 16 T | 0 output / 0 of 1,844,864 cut-word mismatches, IR = captured | r20260926-104127-079a |
| e2e, adversarial | 3,024 heads, 21 T (1..4, 16, 17, 127..132, 256..261, 287, 383, 385) × 9 categories | 0 mismatches, every cut word determined | r20260926-103647-17e8 |
| Rust tail: MufuEx2Ftz, Fa2InvSum, GuardNegInfZero, F2fpBf16 | **all 2^32 words each** | 0 mismatches | r20260926-103512-bb40 |
| Rust tail: F32Add/Sub/MulFtz, F32Max, F32FmaFtz, F32FmaSubFtz | 6,266,094 cases (two-NaN, cancellation, ftz edges, all edge pairs/triples) | 0 mismatches | r20260926-103512-bb40 |
| producer selftest on MY staged files (captured T=4 ×8, T=129 ×4, T=287 ×2) | 24 cases each | 24/24 ×3 | r20260926-103512-bb40 |
| honest sessions on adversarial staged files (the Rust load checks vs IR words, the units in the proof) | 18 files (T=4, T=129 × 9 categories) | 18/18 accepted | r20260926-103512-bb40 |
| RT3 prover-side attacks | 19 (T=4, 129, 287) | 19/19 refused, both reps (or at Commit by C4) | r20260926-103512-bb40 |
| load tampers of the verifier's file | 34 (T=129, 287) | 34/34 refused at load | r20260926-103512-bb40 |
| consistent restatements (pass load) | 4 | 4/4 refused by the proof, both reps | r20260926-103512-bb40 |
| T and set confusion | T=129 file under the T=130 pin; T=129 prover vs T=130 verifier; other T=129 heads | refused (load; Hello R7 ×2) | r20260926-103512-bb40 |
| registered cells: verifier-staged statement | 11 cells so far (below) | CELL_CHECK PASS ×11 | VM, `check_cells.sh` |

- **Run r20260926-103512-bb40:**
  - pod vy-red-team-flock-3, dq3xclby5ni4ic, an RTX A6000 used as a CPU box because nothing else was in stock;
  - source 22dc6320;
  - binaries built unpatched, then with the RT3 knobs; `live-copy.diff` is empty, so the build compiled the reviewed tree;
  - the record is art:25c96f97.
- **Local runs** (recorded, PRESERVED): r20260926-103647-114d, r20260926-104127-079a and r20260926-103647-17e8.

## The asks, one by one

- **The v3 frame changes against v2 (all five hold):**
  - **Short last chunk.** Each chunk's flags come from its own block count, and C4 folds each chunk's last run.
    `short_chunk_end_moved` and `short_chunk_counter` are refused by the region claims. `short_chunk_cv_public` is refused
    at Commit by C4. Dropping a short chunk's run from the table is refused by `check_blocks`. Honest proofs pass at 17
    and 36 chunks (T=129, 287), so the BLAKE3 tree fold matches the reference.
  - **Public port.** q's words are CutIn words of the QK units. `check_public_ports` hashes them into q's committed digest.
    Refused: a flipped word, a word with bit 16 set, a q digest byte, public_ports dropped (q then has no runs) and
    public_ports plus k. A q restated with its digest and root recomputed passes load and is refused by the proof, because
    the QK outputs no longer match.
  - **Zero leaves: the argument holds.** An empty run slot's Params (counter 0, block_len 64, CHUNK_START / CHUNK_END),
    CvIn (the x-row key) and Cv (the chain of `nb` zero blocks) are all the verifier's, and Δ chains the run. So a nonzero
    message there needs a second preimage of the two-compression chain from the fixed key to the fixed 256-bit dummy CV.
    That is ~2^256 generically. It is not a collision, since the prover chooses neither end. It is no weaker than the
    binding of every real run. `zero_leaf_run_message` and `zero_leaf_run_published` are the direct test. They set a
    masked key's V word to 1.0 in its empty run, where P = 0, so the unit's output is unchanged. Both are refused, on both
    reps, at T=4, 129 and 287. `check_leaf_maps` refuses zero-to-real and real-to-empty rewiring.
  - **Holes.** `hole_cut_input` gives a masked key's QK slot a = 1.0 against b = 0, so its output stays the dummy +0. It is
    refused by the CutIn region at T=4, 129 and 287. A hole given a unit, and a real run duplicated into a hole's slot, are
    refused at load.
  - **Tail outputs.** Refused at load: a forged output word with the output root recomputed, and each file-held
    tail-computed word (the Const zero accumulators, P words and rescaled O). A P·V unit output forged with the whole tail
    and the outputs recomputed passes load and is refused by the proof.
- **The exp2 MUFU table.**
  - The Rust ex2 (pinned b2a42c4a) equals the IR's `MufuEx2Ftz` on every one of the 2^32 inputs: NaN, ±inf, ftz inputs,
    overflow and underflow included.
  - FA2's rcp table is byte-identical to the pinned rcp (c4083814), and `Fa2InvSum` is exhaustively equal to the IR.
  - The table's fidelity to sm_89 is the IR's conformance: it reproduces all 1,024 captured heads word for word.
- **Online softmax (running max, lane sums, rescale).**
  - Every captured head and 3,024 adversarial heads give 0 mismatches. These include NaN-position-dependent maxima, all
    −inf rows, inf and NaN rescales, and ties.
  - The binary and ternary prims are clean on 6.3 M cases.
- **The P·V tensor-core chain.**
  - The unit netlist is clean on 2.0e7 vectors, including the special-value group rules: NaN, inf × 0, both-signed
    infinities, saturation as an infinity, +0.
  - Every P·V chain across key blocks agrees in e2e.
  - `pv_acc_rescale_forged` (the block-boundary rescaled accumulator) and `pv_p_word_forged` are refused.
- **The key count T: the verifier fixes it.**
  - T enters only through the pinned netlist: LEAVES `in_ports` [64T, 16], and the CUT tail. `check_leaf_maps` requires
    the header's ports to equal the pinned ones.
  - The verifier's pin is the sha256 of its own lowering: `ir_bench --serve-plan`, then `lowering_for_set`, then
    `key_count`, all on its own copy of the set. A mixed-T set raises.
  - Refused: the T=129 file under the T=130 pin, relabelled for T=130, and with ports widened by one key.
  - A T=129 prover against a T=130 verifier is refused at Hello (R7, Σ), and so are other T=129 heads.
  - All 11 cells' pins equal my per-T pins.
- **Cut and tail accounting across key blocks.** The fixpoint determines every cut word for every T tested, so the
  structure is acyclic and the accepted assignment unique. It equals the IR's gate values (1.84 M words on captured).
- **Leaf maps pinned per IR6.**
  - `cell_check` finds 0 wiring differences from the pinned LEAVES on every registered cell's verifier file.
  - The producer's `zero_leaf_rewired`, `wiring_swapped`, `units_swapped_between_slots` and `row_key_changed` are refused
    on my files.
  - red-team-flock-2 confirmed IR6 at f4cd5d4e (its FINAL).

## Registered L40S cells (checked on their verifiers' own staged files; labelled)

| cell | T | commit | pin | B | verifier run | check |
|---|---|---|---|---|---|---|
| art:97407c51 | 1 | 22dc6320 | fa983f8b | 32 | r20260926-094050-05c3 | PASS |
| art:a24437b6 | 2 | 0839742b | 26e82ebc | 32 | r20260926-094348-3425 | PASS |
| art:1e1c2a5f | 3 | 0839742b | 40aae6da | 32 | r20260926-094659-e16a | PASS |
| art:308df7ad | 4 | 22dc6320 | a5b162b3 | 16 | r20260926-093249-b09f | PASS |
| art:7c3c5497 | 128 | 0839742b | ed0d3a85 | 64 | r20260926-094956-4e33 | PASS |
| art:d1963e64 | 129 | 0839742b | 1222f111 | 64 | r20260926-095430-ce96 | PASS |
| art:73a507ee | 130 | 0839742b | e9f338d4 | 64 | r20260926-100056-fa37 | PASS |
| art:349645c1 | 131 | 0839742b | 007ae342 | 64 | r20260926-100649-40ea | PASS |
| art:11f80605 | 132 | 0839742b | 0c6ac6ef | 64 | r20260926-101243-420c | PASS |
| art:b0eaffa3 | 256 | 0839742b | e75c379d | 64 | r20260926-101906-bcc2 | PASS |
| art:07f55572 | 257 | 0839742b | 42a56905 | 16 | r20260926-102532-68be | PASS |

Per cell:
- The verifier netlist equals the cell's pin and my reviewed lowering.
- There is one sub-batch. The verifier has 6 accepted sessions plus one probe connection with no Hello; link_mode is
  exchange and require_link is true.
- The rows equal the registered per-T set, its key count is T only, and file outputs = IR = captured.

### The ece9fdd2 re-runs (14 threads; the cells the producer cites): all 16 checked and labelled NON_ZK_PROOF (12:11Z and 12:59Z)

| cell | T | pin | B | verifier run | check |
|---|---|---|---|---|---|
| art:3b8280fa | 1 | fa983f8b | 64 | r20260926-115337-4e65 | PASS |
| art:baa539f8 | 2 | 26e82ebc | 64 | r20260926-115635-65c6 | PASS |
| art:0051325c | 3 | 40aae6da | 64 | r20260926-115949-4f4e | PASS |
| art:08a853f6 | 4 | a5b162b3 | 64 | r20260926-120305-0ace | PASS |
| art:73bd2c2b | 128 | ed0d3a85 | 16 | r20260926-120619-1835 | PASS |
| art:d5b0ae9f | 129 | 1222f111 | 32 | r20260926-120949-1a04 | PASS |
| art:3117572d | 130 | e9f338d4 | 16 | r20260926-121438-77ee | PASS |
| art:645a8359 | 131 | 007ae342 | 16 | r20260926-121841-dbbe | PASS |
| art:d18e0ae3 | 132 | 0c6ac6ef | 16 | r20260926-122243-6479 | PASS |
| art:ccede46a | 256 | e75c379d | 8 | r20260926-122702-a807 | PASS |
| art:73750ffa | 257 | 42a56905 | 8 | r20260926-123136-17aa | PASS |
| art:327e9366 | 258 | 8cfef22b | 16 | r20260926-110539-ec03 | PASS |
| art:a552878e | 259 | 572c4a2d | 8 | r20260926-113109-f951 | PASS |
| art:186b9949 | 260 | 91e5e009 | 8 | r20260926-113647-48f1 | PASS |
| art:f52bf885 | 261 | 52bb1734 | 8 | r20260926-114224-b5ce | PASS |
| art:298d4c14 | 287 | 5969034c | 8 | r20260926-114800-e0b2 | PASS |

Every pin equals my reviewed per-T pin. The same checks as above apply: one sub-batch, 6 accepted verifier sessions plus the
probe, link exchange and require_link. Labelled with `evidence/label_cells.sh`.

### Placement: prover and verifier on separate machines (red-team-flock's 12:00Z ruling), all 27 cells (19 at 12:16Z, 8 at 12:58Z)

The ruling: a verifier on the prover's physical machine is not a separate verifier. `evidence/placement_check.py` reads each
cell's two run records (`job.json` environment and `out/host.txt`) and the RunPod API for the pod each attempt recorded. It
then runs PR #74's `separation()` (main, merged 12:04Z) on the merged identities.

- **Every cell (all 27): SEPARATE.** PR #74's `separation()` gives no reason against any of them.
- **The prover and verifier differ on all seven recorded axes:**

  | axis | prover | verifier |
  |---|---|---|
  | pod | zgpjyzuj4fxuod | vrtxfci2z4rl46 |
  | RunPod machine | av7yp9ygnbzg | oc60c34mphhh |
  | public IP | 103.196.86.5 | 103.196.86.132 |
  | kernel boot id | 9076c3e4 | dfc83879 |
  | kernel | 6.8.0-60 | 6.8.0-106 |
  | CPU | EPYC 9354 | EPYC 9355 |
  | GPU | L40S (driver 570.124.06) | RTX PRO 6000 Blackwell (driver 595.91.07) |

  Host memory and GPU UUID differ too.
- **The link:** the prover dialled 10.0.53.36:7400, RunPod global networking, not a 172.16/12 bridge. PR #74 accepts an
  RFC 1918 link only when both machine ids are known and differ, and they do.
- **Labels:** no cell is co-resident, so every label stays `NON_ZK_PROOF`. Each finding was re-labelled at 12:16Z with the
  placement evidence, by `evidence/label_cells.sh`, which now runs the placement check before labelling. A pair not shown
  separate would get `NON_ZK_PROOF_DIAGNOSTIC`.
- **Outputs:** `evidence/placement-20260926T1216Z.jsonl`, `evidence/placement-20260926T1258Z.jsonl` and
  `evidence/check-cells-20260926T{1105,1210,1255}Z.txt`. All of them, with the three local runs' logs, are preserved as
  art:c185d38b.

## Findings (none reachable by a cheating prover)

- **F1 (hygiene):**
  - At 22dc6320 the statement digest still hashes the TAG `verity/flock-ir-frame/v2`. Σ's tag and the rep domains say v3.
  - It is domain-separated in practice: the v3 digest hashes more fields. 0839742b fixes it.
  - The T=1 and T=4 cells carry the old-tag digest, so digests don't compare across that commit. The producer is re-running
    both at 0839742b.
- **F2 (coverage):**
  - The softmax glue is evaluated natively by the verifier on public words, not proven: per-block maxima, T MUFU.EX2, lane
    sums, rescales, MUFU.RCP and the output cast.
  - That is 4.3–11.2% of the head's scalar operations (T = 287..1, counting a tensor-core step as 16 MACs), and all of its
    transcendental work.
  - Every score S, probability P and accumulator O is public, so this is NON_ZK_PROOF.
- **F3 (coverage):** each cell covers the instances of its own T, since its pin is its T's lowering.
- **F4 (informational):** one of six random one-row mutants was invisible on 20k vectors. That is a masked stand-in row;
  on the real netlist the 2.0e7-vector run found 0 differences.

## Conditions

- **AC1 (IR2, mandatory):** the verifier stages its own file from its own copy of the registered per-T set. Its pin is the
  sha256 of its own `lowering_for_set`, so T is the verifier's. The check reads the header's roots from that file and
  compares them with nothing external.
- **AC2:** a cell counts only at a reviewed commit (22dc6320, 0839742b, or ece9fdd2, which only sizes rayon from the cgroup
  quota in `33-ir-cell.sh` / `34-ir-selftest.sh`; a later commit needs re-review). Its pin must be the reviewed per-T pin,
  and its verifier-staged file must pass `cell_check.py`.
- **AC3:** for the headline (F2, F3), attention is proven for its tensor-core steps and checked natively for the softmax.
  The render should footnote this, as for RMSNorm's tail and sampling's S1. Attention coverage may count a served head only
  through a cell at that head's T; any extrapolation to T values without a cell must be stated as one.
- **AC4:** the PB/FA analogs as before: the verifier on another physical machine (red-team-flock's ruling; PR #74's
  placement check on main for new cells, or this lane's `placement_check.py` on the records), a non-producer replay by a
  verify-* lane (pending), and link_mode, require_link and Σ in the record.

Handoffs received:
- `lanes/red-team-flock-2/20260926T0922Z-handoff-from-flock-ir-lowering.md` (the review request): acted on above.
  Verdict: `lanes/flock-ir-lowering/20260926T1115Z-handoff-from-red-team-flock-3.md`, copied to `lanes/coordinator/`, and a
  note in `lanes/red-team-flock-2/`.
- `lanes/red-team-flock-3/20260926T1112Z-handoff-from-flock-ir-lowering.md`:
  - 0839742b is the TAG fix (F1).
  - ece9fdd2 is harness only: the thread count, checked with `git diff 0839742b ece9fdd2`, which touches only the two pod
    scripts. It is inside the grant (AC2).
  - All 16 T values are being re-run at ece9fdd2 through ~12:40Z. I check and label those as they land; the producer
    labels the first twelve superseded.

# Reopened 13:01Z: the key-count class pin (goal 2), PR #54 @ 4eb3b991

**GRANTED WITH CONDITIONS at NON_ZK_PROOF.** The verdict and conditions are in
`lanes/flock-ir-lowering/20260926T1340Z-handoff-from-red-team-flock-3.md`, with a copy in `lanes/coordinator/`. The paper
review before the code is `…T1310Z…` (CP1–CP6).

- **The code:**
  - `check_class` (Rust) checks the pin against the manifest's sha256, that every T of [lo, hi] is listed once, that the
    file's own key count is inside the class, that the netlist is `nets[T]`, and the shared `unit_rows`. Σ binds the class
    pin, and the v3 load checks then run unchanged.
  - The harness `KeyClass` takes each head's T from the verifier's own set and builds the manifest itself. It puts one T in
    each sub-batch and records `key_counts`, `key_class` and `per_key_count`.
  - `ir_frame.rs`, `ir_tail.rs` and `ir_block.rs` are unchanged since ece9fdd2. The main merge adds `replay`.
- **Checks:**
  - CP5: all 512 `nets[T]` (T = 1..512) equal the reviewed generator's per-T netlists (`evidence/class_ref.py`,
    `evidence/manifest_check.py`). The rows are identical for every T, and `unit_rows` db271b38 recomputes independently.
  - The three class pins recompute: 2f102216, fc9dceb5, 365f1b5d.
- **Negatives, run r20260926-132829-2165 (local CPU build, recorded; `evidence/class_neg.sh`):**
  - 14 load cases: the honest one accepted and 11 refused. The two I expected to pass (a forged manifest under its own pin,
    a duplicate key) were also refused: the staged file's `unit_sha256`, and serde keeping the last key.
  - A non-canonical manifest is accepted under its own pin (CP2, hardening).
  - Selftest under `--class`: 24/24.
  - Sessions: the honest one accepted; no-class and re-formatted manifests refused at Hello (R7); another class refused by
    the prover itself.
- **e2e, run r20260926-130636-5ee4:** 648 adversarial heads at 18 more T values up to 512, 0 mismatches. That makes 39 T
  values across the three classes in all.
- **Crediting:**
  - CP7: `views.input_variables` rejects a class cell ("the result records none"), and the headline credits one T per
    result. census-json must credit each T in `key_counts`, with per-T throughput from `per_key_count`.
  - CP8: ir_bench registers the plateau point, a T-prefix of the class set. Register the full-set point.
- **Evidence:** art:8be608c6: the negatives run, the class_ref table, the manifests and the e2e log.

### Class cells, and the conditions since the verdict (14:15Z onward)

- **CP2: MET at 11f24da6.** The class manifest's bytes must be its own canonical serialization. My whitespace and
  duplicate-key manifests are refused as "not its canonical serialization"; missing and extra T are still refused; the
  honest manifest loads. Run r20260926-143204-b20f (`evidence/cp2_check.sh`), on a local build of 31d275ad.
- **Commits after 11f24da6 are harness only:** 31d275ad (the replay script and a `getattr` in ir_bench) and 53ffcaca
  (ir_bench waits for NVML to release exited GPU contexts). The verifier is the same.
- **CP7: MET on main.** census-json's PR #79 adds `key_class_of`. I ran main's code on c1's registered document: it credits
  all 128 listed T, each at P_T = heads / e2e_s from `per_key_count` (88.7 heads/s at T=1, 23.6 at T=128).
- **CP8: MET.** c1 registered its full 2,048-head point.

| cell | class | T in key_counts | heads | commit | pin | verifier run | check | placement | label |
|---|---|---|---|---|---|---|---|---|---|
| art:4fb2de9c (c1) | [1, 128] | 128 | 2,048 | 11f24da6 | 2f102216 | r20260926-132839-b5e6 | PASS | SEPARATE | NON_ZK_PROOF |
| art:4dd2069b (c3) | [257, 512] | 31 (257..287) | 496 | 11f24da6 | 365f1b5d | r20260926-140928-d05d | PASS (31/31) | SEPARATE | NON_ZK_PROOF |

**c1 in detail:**
- The verifier's `class.json` is byte-identical to the manifest I generate.
- All 128 sub-batches pass `cell_check.py`. Each T's netlist is regenerated here and pinned by the file's `unit_sha256`. The
  leaf maps show 0 differences, the digests and roots recompute, units plus tail = IR = the set's outputs, and each
  sub-batch's heads are all at its T.
- Every sub-batch has 6 accepted verifier sessions, and `key_counts` = the verified sub-batches' T.
- Placement: prover pod epczpcyja4oqsh (machine pxp3jjc5ozkz, 103.196.86.17, boot id f2edc502) against verifier pod
  34vxo7onho9xig (machine daejz5pkfg8j, 103.196.86.42, boot id a84811c0). Both are L40S with EPYC 9354; the host memory,
  GPU UUID and driver also differ. The link is a routed 10.x address, and PR #74's `separation()` is clean.
- The label is by `evidence/label_class_cells.sh`, ref r20260926-132829-2165.

**c3** has the same checks: its `class.json` is byte-identical to mine, all 31 sub-batches pass, and `key_counts` = the
verified T. It ran on pair b, the same pods and machines as c1. Main's `key_class_of` credits all 31 T (257..287).

My checker needed one fix. The first c1 pass flagged all 128 sub-batches because `cell_check.py` expected a one-T input set.
It now requires the heads in each file's own range to share T.

## FINAL

~~~text
tip: none (red-team lane; notes only, no code commits; reviewed PR #54 @ 22dc6320 / 0839742b / ece9fdd2 (per-T v3) and 4eb3b991 / 11f24da6 (+ harness 31d275ad, 53ffcaca) (class pins))   merge-with: none
known-failures: none    pod: dq3xclby5ni4ic terminated 11:03Z (after custody); ~$0.32 (the class review ran on CPU on the VM: $0)
artifacts: art:25c96f97 art:c185d38b art:8be608c6 art:3b34c1dd
~~~

**1. Per-T attention, `verity/flock-ir-frame/v3`.** GRANTED WITH CONDITIONS at NON_ZK_PROOF (conditions AC1–AC4).
- All 16 cited L40S cells (ece9fdd2) and the 11 superseded ones are checked and labelled `NON_ZK_PROOF`, and each runs its
  prover and verifier on separate machines.
- Against the IR there are 0 mismatches:
  - 2.0e7 tensor-core vectors;
  - all 2^32 inputs of each unary tail primitive;
  - 4,048 captured and adversarial heads.
- 60 negatives are refused.

**2. Key-count class pins (goal 2: crediting T = 1..287).** GRANTED WITH CONDITIONS at NON_ZK_PROOF, at 4eb3b991 and
11f24da6. 31d275ad and 53ffcaca change only the harness.
- T and the mask come from the verifier's own file and the per-T netlist. The verifier builds its own manifest (CP1), and all
  512 `nets` equal the reviewed generator (CP5).
- The load and session negatives are refused, and the selftest passes 24/24 under `--class`.
- CP2 (canonical manifest) is MET at 11f24da6. CP7 (per-T crediting) is MET on main via PR #79. CP8 (the full-set point) is
  MET.
- Class cells, labelled `NON_ZK_PROOF` after `check_class_cells.sh` and the placement check:
  - c1 art:4fb2de9c, [1,128]: 128 T, 2,048 heads;
  - c3 art:4dd2069b, [257,512]: T 257..287, 496 heads;
  - c2 [129,256]: PENDING.
    - Its first three runs were refused by `bench.cell check` as contended: the timing guard counted the prover's own
      exited GPU contexts.
    - A fourth runs at 8ef6d347 on pair b (machines pxp3jjc5ozkz / daejz5pkfg8j), ETA 16:20Z. 8ef6d347 changes only the
      harness (the timing-guard sampler in `bench.py` and `ir_bench.py`), so it is inside the grant.
    - To label it: `check_class_cells.sh /tmp/rtf3/class-ref-1-512.json <art>`, then `label_class_cells.sh <art>`
      (8ef6d347 is in its allowed list).

**Evidence:**
- art:25c96f97: pod run r20260926-103512-bb40.
- art:c185d38b: the local per-T runs' logs, and the cell and placement checks.
- art:8be608c6: class negatives r20260926-132829-2165, the class_ref table, the manifests and e2e r20260926-130636-5ee4.
- art:3b34c1dd: the c1 and c3 checks, placement, and CP2 run r20260926-143204-b20f.
- Scripts in `evidence/`.

**Handoffs sent:**
- to flock-ir-lowering and the coordinator: …1115Z, …1300Z and …1340Z (the class-pin verdict), and …1310Z (the paper
  review, to flock-ir-lowering);
- …1540Z (the class cells and FINAL);
- to red-team-flock-2: …1115Z.

**Handoffs received:**
- `lanes/red-team-flock-2/20260926T0922Z-handoff-from-flock-ir-lowering.md`;
- `lanes/red-team-flock-3/20260926T1112Z-handoff-from-flock-ir-lowering.md`;
- `lanes/red-team-flock-3/20260926T1305Z-handoff-from-flock-ir-lowering.md` (the class-pin design, reviewed after the
  13:01Z reopen);
- `lanes/red-team-flock-3/20260926T1412Z-handoff-from-flock-ir-lowering.md` (c1);
- `lanes/red-team-flock-3/20260926T1440Z-handoff-from-flock-ir-lowering.md` (c3 and the c2 re-run).

All are acted on above.

**Measurement note:** 8ef6d347 excuses the prover's own recently exited GPU contexts in the timing guard. That bears on
the cells' contention labels, not on soundness; I didn't review it as a measurement change.

**Push check:** there is no `lane/red-team-flock-3` branch to push. This non-producer lane made no code commits.
