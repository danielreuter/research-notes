---
lane: red-team-flock-3
kind: report
created: 2026-09-26T09:58Z
status: open
---

CHECKPOINT dcf89735 (18:28Z) [open] OPEN (waiting): the eta retune folded into PR #173 (level-0 radius 1-sqrt(rho)-1/200); subscribed to #173, will review when its head moves past 16785b18. Done: A2 (#127/#163/#170/#171) GRANTED, #173 @16785b18 GRANTED, #130 pins GRANTED (1537Z duplicate answered by 1540Z); review in the store private/red-team-reviews/soundness-a2-a1/ (private); pointer lanes/coordinator/1830Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT 03ba8ce4 (18:28Z) [open] OPEN (waiting): the eta retune folded into PR #173 (level-0 radius 1-sqrt(rho)-1/200); subscribed to #173, will review when its head moves past 16785b18. Done: A2 (#127/#163/#170/#171) GRANTED, #173 @16785b18 GRANTED; review in the store private/red-team-reviews/soundness-a2-a1/ (private); pointer lanes/coordinator/1830Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT fc6d5b9d (15:38Z) [final] FINAL: PR #130 @b7cd6de8 pin refresh GRANTED (statement review: 9 pins = #146's granted statements at 7406212d, none weaker; read set covers the FlockProofs definitions; keep the three *_inputs pins; render matcher benign); review in the store private/red-team-reviews/pr130-pin-refresh.md (private); pointer lanes/coordinator/1540Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT 003e331b (13:36Z) [final] FINAL: M0 verity/flock-circuit statement review: supports a NON_ZK_PROOF Table 1 row if it says one attention instance = one query over T=129 keys, tensor-core-step ANDs only, prover e2e excluding verification, no privacy (benchmark salts public), units as stated (provisional cover), no draw; IR agrees on all proved instances (16/16, 1024/1024); review in the store private/red-team-reviews/m0-statement/ (private); pointer + rows lanes/coordinator/1340Z; also #146 @7406212d GRANTED, #116 @120adc37 GRANTED, re-registered cells NON_ZK_PROOF; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT 82dd5a0b (13:07Z) [final] FINAL: PR #146 @7406212d GRANTED (C1 met: computable extractor; conclusion needs its hypotheses); PR #116 @120adc37 GRANTED, covers 608e7130; M0 headline cells re-registered art:e352f2ad + art:a83371c2: only placement changed, now the pods that ran (u7fkacoin4t4m1, sqyp6rxnqftcio), proof_class NON_ZK_PROOF on both (ref art:a2c8eb39); findings in the store private/red-team-reviews/ (private); pointers lanes/coordinator/1308Z 1318Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT 156813e4 (12:22Z) [final] FINAL: PR #146 @a3e244c2 GRANT WITH CONDITIONS (C1 computable Merkle extractor or reworded level-3 claim; Collision provable by counting); PR #116 @120adc37 GRANTED (C1-C3 met; A3b re-decided, bound <=37), covers 608e7130; M0 headline cells art:02cb7df9 + art:4a80e8cb proof_class NON_ZK_PROOF (Lean #142 replay 12/12, negatives refused; F1 placement record names other pods), labels ref art:a2c8eb39; findings in the store private/red-team-reviews/ (private); pointers lanes/coordinator/1145Z 1150Z 1218Z 1225Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT a99fb684 (10:52Z) [final] FINAL: PR #146 @d4cb0b75 REFUSE as submitted (node clause still makes Collision trivially true for every scheme; Lean counterexample); PR #116 @66ab031b GRANT WITH CONDITIONS C1 enforce served==Lean draw, C2 require verifier of record, C3 core worst_case (A3b record verified unaffected); findings in the store private/red-team-reviews/ (private); pointers lanes/coordinator/1035Z, 1045Z; 1055Z: private-repo material readable in the public notes (not this lane's; details private); 0905Z/0915Z/0920Z rules followed; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (10:42Z) [final] FINAL: PR #146 @d4cb0b75 REFUSE as submitted (node clause still makes Collision trivially true; Lean counterexample); PR #116 @66ab031b GRANT WITH CONDITIONS C1 enforce served==Lean draw, C2 require verifier of record, C3 core worst_case (A3b record verified unaffected); findings in the store private/red-team-reviews/ (private); pointers lanes/coordinator/1035Z, 1045Z; 0905Z/0915Z/0920Z rules followed; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (10:41Z) [final] FINAL: PR #146 @d4cb0b75 REFUSE as submitted (node clause still makes Collision trivially true for every scheme; Lean counterexample; leaf fix + hm96 reduction right; soundness defs genuine); PR #116 @66ab031b GRANT WITH CONDITIONS C1 enforce served==Lean draw, C2 require verifier of record, C3 core worst_case (A3b record verified unaffected); findings in the store private/red-team-reviews/ (private); pointers lanes/coordinator/1035Z, 1045Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (08:58Z) [final] FINAL: PR #135 @9ac046fd P1 met -> GRANTED; #121 @1ed789d5 GRANTED; the mirror copies all of internal/ (4611baea), so the full reviews are now private in the evidence store (art:b1d7314f #121, art:d3ade404 #135) and the store and notes keep verdict-only stubs; my scripts and outputs removed from notes (608c19f9); coordinator told (0900Z); run r20260927-085234-0a01 labelled; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (08:55Z) [final] FINAL: PR #135 @9ac046fd P1 met -> GRANTED (never below the exact optimum: 0/2000 grid, 0/7500 stress, <=1.9e-9 above; composes with #121 @1ed789d5: TOY + mixed class certified, 750-pt grid holds); #121 @1ed789d5 GRANTED earlier; findings in the store internal/red-team-reviews/ (private); run r20260927-085234-0a01 labelled; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (08:23Z) [final] FINAL: PR #135 @b4c9a489 GRANT WITH CONDITIONS (P1: direct the bound's rounding; checks 1 and 4 pass); PR #121 @1ed789d5 C1 met -> GRANTED (nit N1: stale beacon wording); findings in the store internal/red-team-reviews/ (private); runs r20260927-081834-33a0, r20260927-081942-7959 labelled; mirrored #121 review removed from notes head (7955949b), coordinator told; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (08:22Z) [final] FINAL: PR #135 @b4c9a489 GRANT WITH CONDITIONS (P1: direct the bound's rounding; checks 1 and 4 pass); PR #121 @1ed789d5 C1 met -> GRANTED (nit N1: stale beacon wording); findings in the store internal/red-team-reviews/ (private); runs r20260927-081834-33a0, r20260927-081942-7959 labelled; mirrored #121 review removed from notes head (7955949b), coordinator told; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (07:02Z) [final] FINAL: PR #121 (TwoStageLaw.profile @23c048c3) GRANT WITH CONDITIONS (C1: profile n_v = the class's largest RU); law holds vs adaptive prover, rate exact, bound conservative+tight (750-pt grid), vLLM LEGACY draws byte-identical, core change docstring-only; label on r20260927-070022-8cdd; details in the agent store internal/lanes/red-team-flock-3/pr121-two-stage-profile/; reply lanes/coordinator/20260927T0705Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (05:17Z) [final] FINAL: 9 total-unit L40S cells (852816d6) all NON_ZK_PROOF (282/282 sessions replayed, digests, instance regen, PB1-PB4) + shared-NAT placement verified from the runs' probes (U3 pod id 3-way, S1 bare metal, U2, S3, R1, assess clean); retry-until-pass OBJECTED: IX1 keep/link every attempt, IX2 median of 3 after a failure, IX3 fix the check's RTT input, IX4 the retried cells accepted with history disclosed (published figure within 0.4%); 40 labels (3 refused attempts incl. K2048 r20260927-022036-c6b1 on the earlier pair); reply lanes/coordinator/20260927T0515Z; run r20260927-044853-f250; $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (05:15Z) [final] FINAL: 9 total-unit L40S cells (852816d6) all NON_ZK_PROOF (282/282 sessions replayed, digests, instance regen, PB1-PB4) + shared-NAT placement verified from the runs' probes (U3 pod id 3-way, S1 bare metal, U2, S3, R1, assess clean); retry-until-pass OBJECTED: IX1 keep/link every attempt, IX2 median of 3 after a failure, IX3 fix the check's RTT input, IX4 the 2 retried cells accepted with history disclosed (published figure within 0.4%); 38 labels; reply lanes/coordinator/20260927T0515Z; run r20260927-044853-f250; $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (04:44Z) [open] reopened (coordinator 04:43Z): check + label flock-backend's 9 total-unit L40S cells (TG6/PB1-PB4/CN, shared-NAT placement record incl. U3 pod id from /proc/1/environ); rule on retry-until-pass for the ±10% interaction check: NOT final; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (22:39Z) [open] PR #91 rulings: CONCUR (1) drop product_uuid under S1 (boot_id host-level on bare metal; U2 equal-uuid still refuses, U3 register checks drop uuid) (2) RTT connects to sshd :22 same .runpod.internal address (R1 all 30 must succeed); UL2 verified at 4f5704c0 (8449-row refused, finite vLLM digest 4127c00b unchanged) -> PR #87 no open conditions; total GEMM grant stands; 9 cells await PR #91 + #87 merge; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (22:04Z) [open] shared-NAT-IP placement (coordinator 22:02Z): CONCUR with S1-S5 (S1 new: bare metal on both pods, since VM product_uuid/boot_id are per-VM; S2 evaluate from probes at plan+register; S3 only <pod>.runpod.internal 10/8; S4 kernel TCP RTT on session route; S5 record); reply lanes/coordinator/20260926T2205Z, copy to bench-spine; total GEMM grant stands; 9 cells not yet run; GitHub token expired here ~21:50Z; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (20:49Z) [open] WAITING the 9 total GEMM cells (flock-backend go 20:55Z at d2292e3b); tools ready: evidence/gemm_cell_check.py (validated on art:73a9e9f3: 14/14 checks incl. replay + instance regen), label_gemm_cells.sh, placement_check.py (now GEMM + terminated pods via recorded placement); poller /tmp/rtf3/poll-gemm.sh; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (20:47Z) [open] GRANT covers d2292e3b (TG1 met: gate r20260926-202308-c367 8/8 selftests + 5/5 negs GPU; TG3 withdrawn by naming rule; TG4/TG5 fixed); PR #87 GRANTED (UL2 merge cond open); WAITING the 9 total cells to check+label with gemm_cell_check.py (validated on art:73a9e9f3); agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (20:29Z) [open] GRANTED: PR #87 @28f55d9a (UL2 merge cond) + verity/flock-pure-block-total (bf16-ampere-total pin fef256df) @d4627b62 W/ CONDITIONS NON_ZK_PROOF (TG1 GPU gate before first cell; TG3 /v1 name; TG4/TG5 planner/grant msg); pinned unit = IR on 10.5M vectors (r20260926-201903-d07c), my 8 special-value forgeries refused (r20260926-202615-f0cc); WAITING the 9 cells to label (TG6); agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (20:15Z) [open] PR #87 @28f55d9a GRANTED (merge cond UL2: vllm_block guard vs >2^13 netlists, F5 latent); 48/48 digests identical; ul14 selftests all_pass + 8 flips refused (r20260926-200915-e38d); total_proto 884b7f9b = IR total on 10.5M vectors (r20260926-201330-c204); WAITING flock-backend's pin of verity/flock-pure-block-total/v1 (T1-T5), then the 9 cells; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (20:00Z) [open] reopened (coordinator 19:59Z): review PR #87 (flock-gpu-link: per-statement unit slot 2^13/2^14, admission check UL1) then flock-backend's total GEMM unit+statement (domain total, NaN/inf); grant or block before the 9 GEMM re-run cells: NOT final; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT e5493f9f (16:47Z) [final] FINAL: attention class pins GRANTED W/ CONDITIONS NON_ZK_PROOF; all three class cells checked, placement-separate, labelled NON_ZK_PROOF: c1 art:4fb2de9c (T1-128), c2 art:b61eafa9 (T129-256; duplicate ef10f5fb not labelled), c3 art:4dd2069b (T257-287); CP6 ruled (synthetic sets counted, provenance footnoted; note for Daniel); per-T v3 cells labelled earlier; art:25c96f97 c185d38b 8be608c6 3b34c1dd f5935b64; pod ~$0.32
CHECKPOINT e5493f9f (16:07Z) [open] WAITING c2 (T=129..256) r20260926-153234-eeb6 on vy-flock-ir-lowering-b-l40s at 70+/128 sub-batches, ETA 16:30Z; my poller exits on its registration (deadline 17:00Z), backstop wake 16:58Z; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26; next: check_class_cells.sh + label_class_cells.sh on c2, then FINAL; c1/c3 re-labelled with the CP6 ruling
CHECKPOINT e5493f9f (15:37Z) [open] reopened (coordinator 15:37Z): label class cell c2 (T=129..256, 8ef6d347, due ~16:20Z) with check_class_cells.sh + label_class_cells.sh, polling until 17:00Z; CP6 ruled: synthetic class sets count in #101's headline with provenance footnoted (note for Daniel, not a blocker): NOT final; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
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
- **CP6: RULED** by the coordinator at 15:37Z. Synthetic class sets (the spine generator's draws for T outside the 16
  captured values) count in #101's headline, as the FP8 cells' synthetic spine sets do, with the input provenance
  footnoted. It's a note for Daniel's decision list, not a blocker. c1's and c3's findings were re-labelled with it at
  15:40Z.

| cell | class | T in key_counts | heads | commit | pin | verifier run | check | placement | label |
|---|---|---|---|---|---|---|---|---|---|
| art:4fb2de9c (c1) | [1, 128] | 128 | 2,048 | 11f24da6 | 2f102216 | r20260926-132839-b5e6 | PASS | SEPARATE | NON_ZK_PROOF |
| art:4dd2069b (c3) | [257, 512] | 31 (257..287) | 496 | 11f24da6 | 365f1b5d | r20260926-140928-d05d | PASS (31/31) | SEPARATE | NON_ZK_PROOF |
| art:b61eafa9 (c2) | [129, 256] | 128 (129..256) | 2,048 | 8ef6d347 | fc9dceb5 | r20260926-153220-186b | PASS (128/128) | SEPARATE | NON_ZK_PROOF |

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

**c2** (16:46Z) has the same checks, done in a reopen at the coordinator's request (15:37Z). The clean re-run at 8ef6d347
(harness only) is art:b61eafa9: its `class.json` is byte-identical to mine, all 128 sub-batches pass, `key_counts` =
the verified T (129..256, 2,048 heads), placement is on pair b as c1, and main's `key_class_of` credits all 128 T.
The duplicate registration art:ef10f5fb was not labelled, on the coordinator's instruction (16:34Z); verify-flock-pure
replays b61eafa9. The evidence is art:f5935b64.

My checker needed one fix. The first c1 pass flagged all 128 sub-batches because `cell_check.py` expected a one-T input set.
It now requires the heads in each file's own range to share T.

## Total units (20:00Z onward): PR #87's 2^14-row unit slots, then the total GEMM statement

Daniel's rule is that circuits are total by default. The total `tc_dot16` unit needs 8,449 rows (flock-backend's compact
`total_proto`) or 9,601 (`fp.tc_dot16`), which is past the 2^13-row pure-block unit slot. The 9 bf16-ampere GEMM re-run cells
wait for two grants:

- PR #87, which lets a statement's unit slot be 2^14 rows;
- the total unit and statement that flock-backend will pin on top of it.

### PR #87 (flock-gpu-link @ 28f55d9a): GRANTED, with merge condition UL2

`UnitNet::unit_log()` is 13 for a netlist of at most 2^13 rows, else 14. It replaces `UNIT_LOG` everywhere in
`pure_block.rs`: unit placement, the Δ copies and chains, region shapes, the fold, the witness and the digest.

**On paper.** The prover can't choose `ul`:

- it is a function of the netlist, which is pinned on the verifier's side;
- the statement digest hashes both `ul` and the netlist's sha256.

No shift can underflow: `comp_log` is 14 for the BLAKE3 layouts and 15 for SHA, so `ul ≤ comp_log` for every layout. At `ul`
= 14 the geometry is (slots of 2^14 bits):

| layout | compressions | units | block slots | UL1 |
|---|---|---|---:|---|
| Chunk(n), ChunkTail(n) | 0..32 | 32..64 | 64 | fits exactly (units end at 2^20) |
| Fp8 | 0..48 | 48..96 | 128 | fits |
| Fp4 | 0..28 | 28..52 | 64 | fits |
| ShaFp4 | 0..56 | 56..80 | 128 | fits |
| ShaFp8 | 0..100 | 100..148 | 128 | refused |
| ShaBf16 | 0..196 | 196..292 | 256 | refused |

- **The fold at `per` = 1** (`comp_log` = `ul` = 14): each compression slot is one chunk with offset 0. Units are scaled by
  `eq[(p << ul) | c0] / eq[c0]`, the same tensor-ratio argument as at 13.
- **Region bits:** `out_cols[i]·128 + 32 ≤ useful ≤ 2^ul`, so a region's column bits never reach its slot bits.
- **Padding rows** (`useful` to 2^ul) have empty A and B rows, so C = I forces them to zero.
- **The witness** places unit u of a block at `(p0 + u)·2^(ul−7)` words, the same place as the Δ.
- **The GPU side** (`PURE_UW` 256 → 512 words) is prover-only: completeness, not soundness.

**Byte-identity.** All 48 statement digests are identical at main (2431e3c1) and PR #87: 12 layouts × the bf16-ampere
(e97ecb9e) and fp8-ada (e66262a0) netlists × 8 and 64 VUs, with the fp4 layouts on fp4-nvf4 (fb52a87c). My harness is
`evidence/rtf3_pure_digest.rs`, which only calls `PureStmt::new`.

**Proofs at `ul` = 14 (CPU, run `r20260926-200915-e38d`).** The unit is the 8,449-row total unit (sha 884b7f9b:
flock-gpu-link's `lower_total.py` of flock-backend's `total_proto`). Instance files come from flock-backend's `write_set` on
the spine sets art:69cb815c, art:4f60228c and art:b36f2c6c, 8 VUs each.

| test | result |
|---|---|
| producer's selftest, Chunk(4) (m 25) | all_pass, 27/27 |
| producer's selftest, ChunkTail(4) (m 26) | all_pass, 31/31, with the tail cases |
| producer's selftest, Chunk(16) (m 27) | all_pass, 27/27 |
| finite 2^13 regression, Chunk(4) | 27/27 at PR #87, 27/27 at main |
| my 8 flips (`evidence/rtf3_pure_patch.py`, prover-side) | all refused on both reps (zerocheck) |
| UL1: the total unit on a ShaBf16 file | refused at admission (exit 2) |
| UL1: the finite unit on the same file | admitted, and proves |

My flips hit rows that only exist at 14:

- padding rows 9000, 12000 and 16383, including the last bit of the last slot;
- constant row 8448;
- row 8200, past 2^13;
- an internal row of the last unit;
- ChunkTail's unit 15.

**F5 (latent; not reachable today).** PR #87 raised `UnitNet::parse`'s cap from 2^13 rows to 2^14. That cap was the only guard
for `vllm_block` (`verity/flock-vllm-block/v1`), which still assumes 2^13:

- its `pad` calls `rows.resize(2^13)`, which truncates a longer netlist, including its c_out and y16 rows and its constant row;
- its Δ targets and its `Out` region's bits overflow into the next unit slot (y16's column 65 × 128 = 8320 sets bit 13).

`evidence/rtf3-vllm-big.rs` shows `VllmStmt::new` building a statement (digest 35dade18…) from the 8,449-row netlist; at main
the load refuses it. It isn't reachable by a prover, because that statement's netlist is pinned on the verifier's side and
every pinned vLLM netlist has at most 2^13 rows. A total unit adopted there would silently give a malformed statement.

**Conditions:**

- **UL2 (before merge):** `VllmStmt::new` refuses `useful > 2^UNIT_LOG` (one assert), or vllm_block takes `ul` as
  pure_block does, with its own review.
- **UL3:** `ul` = 14 is exercised only on Chunk(n) and ChunkTail(n). Fp8, Fp4 and ShaFp4 pass UL1 at 14, but no total fp8 or
  fp4 unit exists yet. Their first `ul` = 14 statement needs the same selftest before a cell runs.
- **UL4:** a `ul` = 14 statement still names itself `verity/flock-pure-block/v2`. Its digest differs, but cells must record
  the unit pin and `domain`: flock-backend's `verity/flock-pure-block-total/v1` (next item).

### The total GEMM statement (flock-backend @ d4627b62, extended to d2292e3b): GRANTED WITH CONDITIONS, NON_ZK_PROOF

**Update, 20:55Z.** The grant covers **d2292e3b**. Since d4627b62 only the probe (inf·0 VUs), the negatives (inf·0 claimed
finite, NaN payload changed), the template and a test changed; there is no verifier or lowering change.

- **TG1 met.** Gate run `r20260926-202308-c367` (art:ce45548f, source 29812b90, RTX 4090):
  - 8 of 8 selftest runs at 27 of 27, CPU and `--gpu`, K 1536 and 2048, 8 and 64 VUs;
  - 5 of 5 negatives refused for both provers, with the prover on the GPU;
  - the honest control accepted.
- **TG3 withdrawn.** The coordinator's rule is no version suffix on names.
- **TG4 and TG5 done** at d2292e3b.
- **Open:** UL2 (PR #87 merge) and TG6 (per cell, `evidence/gemm_cell_check.py`).

The checker was validated on the old K 2048 cell art:73a9e9f3: 12 of 12 sessions replayed and accepted, and both negatives
rejected.

The code is `cursor/flock-backend-4983`: 70dd1b65 plus the pod gate script d4627b62, merging PR #87 @ 28f55d9a.

- **Unit and relation:** `bf16-ampere-total`, pin fef256df, 8,449 rows, 0 assertion rows (`unit_total.py`).
- **Statement:** `verity/flock-pure-block-total`. `statement_name(net.relation)` replaces `TAG` in the digest.
- **Template:** sm80 BF16 lowers to it.

| check | result |
|---|---|
| T1: pinned netlist vs the IR | 10,485,760 vectors, 0 c_out and 0 y16 mismatches, 0 unsatisfied lanes (`r20260926-201903-d07c`) |
| pins | all 7 regenerate from d4627b62; the 6 finite ones are unchanged |
| statement digests | the finite ones are identical to main (48 of 48); the total unit gets its own |
| T2: the writer and admission | `_chain_rows` steps `tc_dot_total`; y is `f32_to_bf16_hw_word` (F2fpBf16); NV1 admits NaN outputs |
| T3: their probe selftests | all_pass: 27/27 at K 1536 (Chunk(3)) and 2048 (Chunk(4)), 8 and 64 VUs |
| T3: their negatives | all refused on both provers; honest control accepted (`r20260926-202246-6d2f`) |
| T3: my negatives | 8 of 8 refused on both provers; honest control accepted (`r20260926-202615-f0cc`) |
| T4: statement identity | `main` asserts the instances name the netlist's relation, so the reported name is the digest's |
| T5: cells | when they land |

On T1:

- The pinned rows differ from `total_proto`'s in 7,467 places, so this is a separate check, not inherited from the
  prototype.
- The results include about 2.8M NaN, 3.3M infinite, 476k subnormal and 73k zero outputs.
- Every non-input row reads only earlier rows, so the output is a function of the inputs.

My negatives use my own 16-VU probe (`evidence/rtf3_total_negs.py`, Chunk(4)). Its outputs are checked against the IR prims
before anything runs:

- +0, from zero operands;
- a subnormal (2^-127, y 0x0040);
- NaN from ±inf in one group, and NaN from inf·0;
- +inf from a saturated group, and −inf;
- a NaN carried across three block boundaries;
- finite VUs.

The eight forgeries, each moving out and y together on its own VU:

- +0 → −0;
- subnormal → 0;
- mixed-inf NaN → +inf;
- overflow +inf → max-finite;
- inf·0 NaN → 0;
- −inf → NaN;
- carried NaN → 0x7FC0, a NaN word F2fpBf16 never produces;
- finite → next ulp.

Each is refused for the honest prover (R7) and for the cheating prover holding the forged file
(`PcsAb(RingSwitch(ClaimMismatch))`).

**flock-backend's two questions:**

- **Naming by suffix: acceptable.**
  - The relation comes from the header of the verifier's pinned netlist.
  - `main` refuses instances that name another relation.
  - The digest hashes the name.
  - So the prover can't pick it, and a finite unit can't take the name without a new, reviewed pin.
- **Probe coverage: enough for what the probe is for.** The netlist's exactness comes from T1; the probe shows the plumbing
  works end to end: the writer's chain, NV1, NaN and inf accumulators crossing block boundaries, and the epilogue. My file
  adds zero, subnormal, mixed-inf and overflow VUs, and all of them prove.

**Conditions:**

- **TG1 (before the first cell):** `51-total-gate.sh` passes on the prover pod: all selftest runs and cases pass on CPU and
  with `--gpu`, and the negatives pass with the GPU prover. It is recorded, and the cells cite it. The pinned netlist has
  never been through the GPU prover; flock-gpu-link's GPU runs used 884b7f9b. This is completeness; the verifier is CPU.
- **TG2:** PR #87's merge condition UL2 (flock-gpu-link).
- **TG3 (before the first cell, recommended):** version the name, as `verity/flock-pure-block-total/v1`. It enters every
  digest and record, and every other statement id is versioned.
- **TG4:** `supports()` should refuse sm80 BF16 at K = 1536 with SHA-256 rows: ShaBf16 can't hold 2^14-row units, and UL1
  would refuse the cell at admission. None of the 9 cells is affected.
- **TG5:** `granted()` and its test still say ChunkTail(n) has no red-team grant. red-team-flock granted it with CT1–CT3
  (10:22Z; PR #75 confirmed 13:10Z). Update both, or the K 2304 and K 8960 cells will record a missing grant.
- **TG6 (per cell, my labels):**
  - relation `bf16-ampere-total`, pin fef256df, the total statement name, `domain: total`;
  - the verifier's sessions accepted;
  - placement separate (PR #74), `contended: false`;
  - the old cell `superseded_by` the new one.

### Placement: a shared NAT public IP (coordinator 22:02Z): CONCUR with S1–S5 (22:05Z)

The proposal: `bench.cell` accepts a shared public IP when all of these hold:

- the machine id, DMI `product_uuid` and `boot_id` all differ, and all are recorded;
- the RTT is at least 0.1 ms;
- the route is not a host bridge;
- `shared_public_ip: true` is recorded.

It doesn't reopen the co-residence we saw. For containers on one host, each of the three ids is equal on both pods (the
RunPod host id, the host's SMBIOS UUID, the host kernel's boot id).

It would admit VM-isolated pods on one host, though. There `product_uuid` and `boot_id` are per VM, and a per-VM machine id
is possible. Neither the RTT floor nor the route test catches that.

The conditions:

- **S1:** bare metal on both pods: no `hypervisor` CPUID flag, and a DMI `sys_vendor` that isn't a hypervisor's. Otherwise
  no exception.
- **S2:** evaluate from the probes, at plan and at registration.
- **S3:** under the exception, accept only `<verifier pod>.runpod.internal` in 10/8, not "not host-private" read literally.
- **S4:** the RTT is measured with kernel-level TCP connects on the session's route.
- **S5:** record all of it.

Replies: `lanes/coordinator/20260926T2205Z-handoff-from-red-team-flock-3.md`, copied to bench-spine.

**PR #91 (bench-spine, c27c991b), 22:40Z: both questions answered CONCUR.** I read the patch and `placement.py` from its
bundles.

1. **Drop `product_uuid` under S1** (it is 0400 and unreadable on RunPod, even as uid 0).
   - With S1 shown, the uuid adds nothing: on bare metal, `boot_id` is the host kernel's id, so differing `boot_id`s mean
     different machines, and the machine id corroborates.
   - **U2:** a readable, equal uuid still refuses, and an unreadable one is recorded as such.
   - **U3:** S2's register checks drop the uuid consistently.
   - Tests to match.
2. **RTT connects to sshd at `<pod>.runpod.internal:22`.** It's the same resolved address (`target_ip == peer_ip`), and
   `connect()` completes in the kernel.
   - **R1:** all 30 connects must succeed.
   - **R2 (optional):** keep socket setup outside the timer.

**UL2 verified at 4f5704c0.** The 8,449-row netlist is refused, the finite vLLM digest 4127c00b is unchanged, and the
negative test passes. PR #87 has no open conditions.

Reply: `lanes/coordinator/20260926T2240Z-handoff-from-red-team-flock-3.md`, copied to bench-spine and flock-gpu-link.

### The 9 total-unit L40S cells (27 Sep, 05:15Z): all NON_ZK_PROOF; retry-until-pass OBJECTED

flock-backend's `20260927T0445Z` handoff lists the cells, all at commit 852816d6. That commit equals the granted d2292e3b on
the pure-block path, plus UL2 and the probe fix.

- **Cells** (run `r20260927-044853-f250`):
  - art:199bccee, art:c6b96f7e, art:c3a3d2c7, art:3e1bf074, art:5bdcd1d1, art:216143fd, art:3367e633, art:b1e5fed5 and
    art:062f4951;
  - 282 of 282 sessions replayed and accepted, and the negatives rejected;
  - digests equal to the bound ones, and instance files byte-identical on regeneration.
- **NAT placement** (`evidence/nat_check.py`), for all 9:
  - pod ids agree three ways: the probe via `/proc/1/environ`, the runner and the plan;
  - machine ids and boot ids differ;
  - bare metal (ASUSTeK ESC8000A-E11 / ESC N8-E11, no hypervisor flag);
  - the uuid unreadable on both pods;
  - the link on the global network (10.0.131.43 from 10.0.159.5);
  - 30 of 30 connects, medians 0.23–1.73 ms;
  - `assess()` clean.
- **Interaction check.** The model's per-round cost is the Ping RTT estimate, which swings from 0.29 to 0.76 ms on this
  pair. The measured wait per round is steady at 0.50–0.63 ms, and the verifier's handling is 0.01–0.017 ms.
  - 10 of 11 attempts are over the model, at +4.6% to +11.5%.
  - #39's refused attempt and its retry have the same compute and wait. Only the RTT estimate moved.
  - The published figures agree within 0.4%.
- **The rule I proposed:**
  - **IX1:** keep and link every attempt.
  - **IX2:** one attempt, then exactly two more if it fails, and the median of three.
  - **IX3:** the check's RTT should be a mean of in-session samples on the session route, with a measured bandwidth.
  - **IX4:** this queue's two retried cells are accepted with the history disclosed. The 02:20Z K2048 attempt is to be
    registered.
- **Labels:** 40:
  - 4 on each of the 9 cells;
  - a `finding` on each of the three refused attempts (art:706121e5, art:62ebb4ff, art:f50158fa);
  - a corrected `finding` on art:c6b96f7e. It names the earlier K2048 attempt r20260927-022036-c6b1, which ran on the
    previous pair and was re-run because that batch couldn't be registered.

**Handoffs to this lane since 20:00Z, and their answers:**

| handoff | answer |
|---|---|
| `20260926T2035Z-handoff-from-flock-backend.md` (total unit pinned, gate r20260926-202308-c367) | granted at d2292e3b; TG1 met; TG3 withdrawn (`lanes/flock-backend/20260926T2055Z-handoff-from-red-team-flock-3.md`) |
| `20260926T2211Z-handoff-from-flock-gpu-link.md` (UL2 at 4f5704c0) | verified; PR #87 has no open conditions (`lanes/flock-gpu-link/20260926T2240Z-handoff-from-red-team-flock-3.md`) |
| `20260926T2235Z-handoff-from-bench-spine.md` (PR #91 c27c991b, S1–S5; uuid unreadable; sshd :22) | concur on both, with U1–U3 and R1 (`lanes/coordinator/20260926T2240Z-handoff-from-red-team-flock-3.md`) |
| `20260927T0012Z-handoff-from-flock-backend.md` (no same-DC pair with a route; cross-DC art:04688422) | informational; resolved by the later EU-NL-1 runs. art:04688422 is the cross-DC diagnostic that art:199bccee supersedes |
| `20260927T0320Z-handoff-from-flock-backend.md` (8 measured, 0 registered: no pod_id; force-register or re-run?) | re-run was right (the NAT exception is re-checked on the runs' own records); done with the probe fix, 04:45Z |
| `20260927T0445Z-handoff-from-flock-backend.md` (the 9 cells) | all 9 NON_ZK_PROOF; the retry ruling (`lanes/coordinator/20260927T0515Z-handoff-from-red-team-flock-3.md`) |

### PR #121 (`TwoStageLaw.profile`), 27 Sep, 07:05Z: GRANT WITH CONDITIONS

- **Finding in the store:** the private evidence-store artifact `art:b1d7314f` (the store's
  `internal/red-team-reviews/pr121-two-stage-profile/` keeps only the verdict). The request is in the store's lane folder
  (`20260927T0650Z-handoff-from-coordinator.md`).
- **Verdict:** GRANT WITH CONDITIONS, one condition (C1), recorded as a label on run `r20260927-070022-8cdd`. The reply is
  `lanes/coordinator/20260927T0705Z-handoff-from-red-team-flock-3.md`.

### PR #135 and #121 at 1ed789d5 (27 Sep, 08:25Z)

- **PR #135 @ b4c9a489:** GRANT WITH CONDITIONS (P1, before merge). Finding in the store:
  the private evidence-store artifact `art:d3ade404` (the store's `internal/red-team-reviews/pr135-profile-exact-bound/` keeps only the verdict). Run `r20260927-081834-33a0`.
- **PR #135 @ 9ac046fd (08:55Z):** P1 met, so GRANTED. Finding in the store: same file, the re-check section. Run
  `r20260927-085234-0a01`. Reply: `lanes/coordinator/20260927T0855Z-handoff-from-red-team-flock-3.md`.
- **PR #121 @ 1ed789d5:** C1 met, so GRANTED. Finding in the store: the private evidence-store artifact `art:b1d7314f`
  (the store's `internal/red-team-reviews/pr121-two-stage-profile/` keeps only the verdict). Run `r20260927-081942-7959`.
- **Reply:** `lanes/coordinator/20260927T0825Z-handoff-from-red-team-flock-3.md`.
- **Containment (08:15Z):** my first #121 review had been mirrored from the store's `internal/lanes/` to these notes. I
  removed it at head and told the coordinator, with pointers (`lanes/coordinator/20260927T0815Z-handoff-from-red-team-flock-3.md`).
- **Handoffs answered:**
  - `20260927T0700Z-handoff-from-coordinator.md` (the notes repo is public): followed. Sensitive findings now live in
    the private evidence store (`art:b1d7314f`, `art:d3ade404`), notes carry pointers, and the earlier exposure is reported in the 0815Z note.
  - `20260927T0810Z-handoff-from-coordinator.md` (#135, and C1 on #121): answered in the 0825Z note.

### PR #146 and PR #116 (27 Sep, 10:35–10:55Z)

- **PR #146 @ d4cb0b75** (`MerkleScheme.Collision`): REFUSE as submitted. Finding in the private store:
  `private/red-team-reviews/pr146-merkle-collision/review.md`. Reply:
  `lanes/coordinator/20260927T1035Z-handoff-from-red-team-flock-3.md`.
- **PR #116 @ 66ab031b** (the one-stage driver): GRANT WITH CONDITIONS C1–C3. Finding in the private store:
  `private/red-team-reviews/pr116-one-stage-driver/review.md`. Reply:
  `lanes/coordinator/20260927T1045Z-handoff-from-red-team-flock-3.md`.
- **Handoffs answered:** `20260927T0905Z-handoff-from-coordinator.md`, `20260927T0915Z-handoff-from-coordinator.md` and
  `20260927T0920Z-handoff-from-coordinator.md`, on where sensitive material goes; the last supersedes the first two.
  Followed:
  - the #146 and #116 reviews are in the store's `private/`;
  - the #121 and #135 reviews are in the evidence store (`art:b1d7314f`, `art:d3ade404`), and the coordinator was told at
    0900Z;
  - only verdict stubs remain under `internal/`. My lane's `internal/lanes/` folder holds only the incoming requests and
    the report's first stub.
- **Also sent (10:55Z):** private-repo material is readable in the public notes. It isn't this lane's. The details are in the
  store's `private/red-team-reviews/notes-exposure-20260927/`, and the pointer is
  `lanes/coordinator/20260927T1055Z-handoff-from-red-team-flock-3.md`.

### #146 delta, #116 re-check, and M0's headline cells (27 Sep, 11:45–12:25Z)

- **PR #146 @ a3e244c2:** GRANT WITH CONDITIONS (C1: state the Merkle extractor as a computable definition, or reword the
  level-3 claim). Finding in the private store: `private/red-team-reviews/pr146-merkle-collision/delta-a3e244c2.md`. Reply:
  `lanes/coordinator/20260927T1145Z-handoff-from-red-team-flock-3.md`.
- **PR #116 @ 120adc37:** GRANTED (C1–C3 met). It also covers 608e7130, a one-line change to `pod.sh`. Finding in the private
  store: `private/red-team-reviews/pr116-one-stage-driver/delta-120adc37.md`. Replies:
  `lanes/coordinator/20260927T1150Z-handoff-from-red-team-flock-3.md` and `…T1218Z-handoff-from-red-team-flock-3.md`.
- **M0's headline cells** `art:02cb7df9` (attention) and `art:4a80e8cb` (GEMM): `proof_class NON_ZK_PROOF` on both.
  - Labels by red-team-flock-3 with ref `art:a2c8eb39` (the review, preserved), on the remote.
  - Review: `private/red-team-reviews/m0-headline-cells/review.md`.
  - Reply: `lanes/coordinator/20260927T1225Z-handoff-from-red-team-flock-3.md`.
- **Handoffs answered:**
  - `20260927T1115Z-handoff-from-flock-verifier-pr146-delta.md`: the #146 delta, answered in the 1145Z note;
  - `20260927T1120Z-handoff-from-one-stage-e2e-pr116-delta.md`: the #116 delta, answered in the 1150Z note;
  - `20260927T1140Z-handoff-from-coordinator.md`: the headline cells' class, answered in the 1225Z note;
  - `20260927T1215Z-handoff-from-coordinator.md`: 608e7130, answered in the 1218Z note.
- **Cost:** CPU only on this VM, $0.

### Re-registered cells, and #146's C1 (27 Sep, 13:05–13:18Z)

- **The re-registered cells** `art:e352f2ad` (attention) and `art:a83371c2` (GEMM) supersede `art:02cb7df9` and
  `art:4a80e8cb`.
  - Only `cell.placement` changed. The new placement names the pods that ran (`u7fkacoin4t4m1` and `sqyp6rxnqftcio`) and
    matches the runs' own records, so F1 is fixed.
  - `proof_class NON_ZK_PROOF` and a `finding` on both, with ref `art:a2c8eb39`, on the remote.
  - Reply: `lanes/coordinator/20260927T1308Z-handoff-from-red-team-flock-3.md`.
- **PR #146 @ 7406212d:** GRANTED. C1 is met by the computable extractor. Finding in the private store:
  `private/red-team-reviews/pr146-merkle-collision/delta-7406212d.md`. Reply:
  `lanes/coordinator/20260927T1318Z-handoff-from-red-team-flock-3.md`.
- **Handoffs answered:**
  - `20260927T1305Z-handoff-from-coordinator.md`: the re-registered cells, answered in the 1308Z note;
  - `20260927T1235Z-handoff-from-flock-verifier-pr146-c1.md`: #146's C1, answered in the 1318Z note.

### M0's `verity/flock-circuit` statement review (27 Sep, 13:26–13:40Z, asked for directly)

- **Verdict:** it supports a `NON_ZK_PROOF` Table 1 row, if the row says what the unit covers.
  - One attention instance is one query row, and the AND count covers tensor-core steps only.
  - Time excludes verification, and there's no privacy claim: the benchmark's salts are public.
  - The units are template instances as stated.
- **IR check:** on every proved instance the circuit's outputs equal the IR reference, 16 of 16 and 1,024 of 1,024.
- **Review:** `private/red-team-reviews/m0-statement/review.md`, in the private store.
- **Pointer, with the recommended rows:** `lanes/coordinator/20260927T1340Z-handoff-from-red-team-flock-3.md`.

### PR #130's pin refresh (27 Sep, 15:33–15:40Z; named statement reviewer)

- **PR #130 @ b7cd6de8:** GRANTED.
  - Every changed or new pin is #146's granted statement at 7406212d, and none is weaker.
  - Keep the three `*_inputs` pins.
  - `render` in the read set is benign.
- **Request:** `lanes/coordinator/20260927T1501Z-handoff-from-lean-organization.md`.
  - `20260927T1537Z-handoff-from-coordinator.md` is the same request, marked superseded by the root's. It's answered by the
    same 1540Z note. I record grants by handoff, so there's no label.
- **Review:** `private/red-team-reviews/pr130-pin-refresh.md`, in the private store.
- **Reply:** `lanes/coordinator/20260927T1540Z-handoff-from-red-team-flock-3.md`.

### Soundness stack: A2's constant, A1's removal, the η retune (27 Sep, 18:18–18:30Z; named statement reviewer)

- **A2** (#127 f1c90b1f, #163 b5009bc9, #170 972d5111, #171 23b2df6e): GRANTED.
  - `Pr ≤ E[cost]/2^256` holds for adaptive finders in the random-oracle model, with 0.33 bits to spare.
  - The link finder's cost counts every evaluation of a session run.
  - The constant is consistent across the stack.
- **#173 @ 16785b18:** GRANTED.
  - The DKT26 bridge proves A1's conclusion on `Fin n` domains, with fewer hypotheses.
  - The only other signature change is `prCoin_mca_le`, whose callers are `Fin`-indexed. So the table theorems are strictly
    stronger.
- **The η retune:** PENDING, since #173's head hasn't moved. I'm subscribed to #173 and will review it when it lands.
- **Request:** `lanes/coordinator/20260927T1816Z-handoff-from-flock-soundness-a2-constant.md`.
- **Review:** `private/red-team-reviews/soundness-a2-a1/`, in the private store.
- **Reply:** `lanes/coordinator/20260927T1830Z-handoff-from-red-team-flock-3.md`.

### Pre-grant checklist

What I checked on the pinned unit and statement:

- **T1:** the pinned netlist equals the IR on every encoding. c_out = `AmpereBF16TcDot16_v1`, which is `tc_dot_total` on
  AMPERE_BF16_M16N8K16, and y16 = `F2fpBf16_v1`. My tool is `evidence/gemm_total_diff.py` (my own reader and evaluator, with
  `tc_diff.py`'s ten families).
- **T2:** the instance chain uses `tc_dot_total`, and the verifier's admission accepts special encodings. Nothing finite-only
  remains: no NaN or inf refusal, and the epilogue is F2fpBf16, not `f32_to_bf16`.
- **T3:** NaN, inf and subnormal selftests prove. Forged outputs on special inputs are refused: a different NaN payload, the
  sign of an infinity, inf·0 forged to a number, a finite output on a NaN instance.
- **T4:** the statement records its id and `domain: total`, and the netlist pin is the verifier's.
- **T5:** each cell has a separate prover and verifier placement (PR #74) and `contended: false`.

Pre-check on the likely basis, `total_proto` 884b7f9b: 327,680 vectors across the ten families (NaN, inf, subnormal,
overflow, cancellation), with 0 c_out mismatches, 0 y16 mismatches and 0 unsatisfied lanes. As a control, the finite census
unit e97ecb9e on the same vectors gives 99,486 mismatches and 116,418 unsatisfied lanes. The full run
(`r20260926-201330-c204`) is 10,485,760 vectors, with 0 c_out mismatches, 0 y16 mismatches and 0 unsatisfied lanes.

## FINAL

~~~text
tip: none (red-team lane; notes only, no code commits; reviewed PR #54 @ 22dc6320 / 0839742b / ece9fdd2 (per-T v3) and 4eb3b991 / 11f24da6 (+ harness 31d275ad, 53ffcaca) (class pins))   merge-with: none
known-failures: none    pod: dq3xclby5ni4ic terminated 11:03Z (after custody); ~$0.32 (the class review ran on CPU on the VM: $0)
artifacts: art:25c96f97 art:c185d38b art:8be608c6 art:3b34c1dd art:f5935b64
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
- CP6 (synthetic class sets): RULED by the coordinator at 15:37Z. They count in #101's headline, as the FP8 cells' spine
  sets do, with the provenance footnoted. It's a note for Daniel, not a blocker, and all three class findings carry it.
- CP2 (canonical manifest) is MET at 11f24da6. CP7 (per-T crediting) is MET on main via PR #79. CP8 (the full-set point) is
  MET.
- Class cells, labelled `NON_ZK_PROOF` after `check_class_cells.sh` and the placement check:
  - c1 art:4fb2de9c, [1,128]: 128 T, 2,048 heads;
  - c3 art:4dd2069b, [257,512]: T 257..287, 496 heads;
  - c2 art:b61eafa9, [129,256]: 128 T, 2,048 heads, at 8ef6d347 (harness only), labelled at 16:46Z. The duplicate
    art:ef10f5fb was not labelled (coordinator 16:34Z).

**Evidence:**
- art:25c96f97: pod run r20260926-103512-bb40.
- art:c185d38b: the local per-T runs' logs, and the cell and placement checks.
- art:8be608c6: class negatives r20260926-132829-2165, the class_ref table, the manifests and e2e r20260926-130636-5ee4.
- art:3b34c1dd: the c1 and c3 checks, placement, and CP2 run r20260926-143204-b20f.
- art:f5935b64: the c2 check and placement.
- Scripts in `evidence/`.

**Handoffs sent:**
- to flock-ir-lowering and the coordinator: …1115Z, …1300Z and …1340Z (the class-pin verdict), and …1310Z (the paper
  review, to flock-ir-lowering);
- …1540Z (the class cells), …1650Z (c2, CP6, FINAL);
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
