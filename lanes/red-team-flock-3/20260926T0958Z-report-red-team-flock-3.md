---
lane: red-team-flock-3
kind: report
created: 2026-09-26T09:58Z
status: open
---

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

### The ece9fdd2 re-runs (14 threads; the cells the producer cites), checked and labelled NON_ZK_PROOF at 12:11Z

| cell | T | pin | B | verifier run | check |
|---|---|---|---|---|---|
| art:3b8280fa | 1 | fa983f8b | 64 | r20260926-115337-4e65 | PASS |
| art:baa539f8 | 2 | 26e82ebc | 64 | r20260926-115635-65c6 | PASS |
| art:0051325c | 3 | 40aae6da | 64 | r20260926-115949-4f4e | PASS |
| art:327e9366 | 258 | 8cfef22b | 16 | r20260926-110539-ec03 | PASS |
| art:a552878e | 259 | 572c4a2d | 8 | r20260926-113109-f951 | PASS |
| art:186b9949 | 260 | 91e5e009 | 8 | r20260926-113647-48f1 | PASS |
| art:f52bf885 | 261 | 52bb1734 | 8 | r20260926-114224-b5ce | PASS |
| art:298d4c14 | 287 | 5969034c | 8 | r20260926-114800-e0b2 | PASS |

Every pin equals my reviewed per-T pin. The same checks as above apply: one sub-batch, 6 accepted verifier sessions plus the
probe, link exchange and require_link. Labelled with `evidence/label_cells.sh`.

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
- **AC4:** the PB/FA analogs as before: a separate verifier pod, a non-producer replay by a verify-* lane (pending), and
  link_mode, require_link and Σ in the record.

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
