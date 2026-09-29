---
lane: red-team-flock-3
kind: report
created: 2026-09-26T09:58Z
status: final
---

CHECKPOINT 2db4801e (14:50Z) [final] #412 @da1e703a CONFIRM: new pin execStratified_escape_le (explicit ExecStrata, no named assumption); every other record byte-identical to e1081cc5; replay PASS 9,567 decl, 95 pins; record art:a8b348a5, findings art:ecafbf8b
CHECKPOINT 40d4caba (14:11Z) [final] #412 @e1081cc5 GRANT: stratified_exec_escape_le (explicit ExecStrata), flock_e2e_drawn_exec (independent of the law), flock_e2e_count_exec; #408's 91 records byte-identical; reads cover Flock.Draw; replay PASS 9,567 decl, 94 pins; record art:51ba939d, findings art:10027a23
CHECKPOINT 9d04a655 (13:22Z) [final] #408 @a726a443 CONFIRM (C1 met: ExecDraw.lean byte-identical move, test_audit_layer_is_abstract passes; pin/record identical; keyed draws out of scope as granted; replay PASS 91 pins); #411 @c2c4a938 GRANT (partReadsOk: strictly stronger, flat units untouched, honest units pass; replay PASS 33 pins)
CHECKPOINT 7bde6040 (12:12Z) [final] #408 @b2f8db97 GRANT WITH C1 (via bundle): subset_exec_escape_le right (unchanged executable over uniform bytes, none = no escape); main's 60 unchanged; meaning gains Flock.Draw; C1: DrawExec.lean breaks test_audit_layer_is_abstract (imports Flock.Draw under Audit/); soundness audit PASS w/ replay 8,233 decl, 61 pins; record art:cd05a6a2, findings art:7317b252
CHECKPOINT 81f0453e (11:06Z) [final] #404 @bf36d2b2 GRANT (via bundle): partsChecked gains the constant-row and order-columns conjuncts; same four pins' reads move, strictly stronger hypothesis; honest units pass (21 derive vectors, test_flock_rows under uv torch-cpu 13); soundness audit PASS w/ replay 8,003 decl, 33 pins; record art:c8e66b03, findings art:d915604f
CHECKPOINT 5b947923 (10:48Z) [final] #402 @38d9be9a GRANT (stratified_miss_eq_greedy; main's 51 unchanged; audit PASS w/ replay 52 pins; N1 exporter: certify separation exactly); #392 @8628dd4a GRANT (three satisfiability witnesses; #381's 38 unchanged; audit PASS w/ replay 41 pins); both via verity-root's bundle
CHECKPOINT fea99a78 (10:23Z) [final] R9c/R11 on main 610ee10f GRANTED at #291 @2437e377, #296 @4d226ad1, #302 @377f7d26, #310 @e9ca3ba2 (via bundle): every pin record main's or my grant's; six changed .lean = HmRow pin union, auto-merge, proof-only edits; R11 heads and R9b 115fffc5 are exact auto-merges; audits PASS w/ replay (42/43/46/48 pins)
CHECKPOINT 8d43c4d5 (09:47Z) [final] test_flock_rows 4 cases (rmsnorm fused-cuda, rmsnorm triton, rope-head-64, silu-mul-8192) ran and PASSED at main e5694c92 under uv run --locked --extra torch-cpu (torch 2.14.0+cpu); the earlier failures were the torch-less /workspace venv
CHECKPOINT 26c0ad57 (09:41Z) [final] #394 @971e8a7e GRANT (via verity-root's bundle): compose_eval_unit, layout_sound, unit_sound, rowsL1 unchanged statements/type hashes/assumptions; reads move to deriveChecked + partsChecked (strictly stronger, same done); soundness audit PASS w/ replay 7,999 decl, 33 pins; derive vectors pass; note: test_flock_rows 4 pinned-template failures pre-exist on main e5694c92; record art:41b15fac, findings art:9a645ed3
CHECKPOINT faebca2f (09:10Z) [final] #394 @971e8a7e received, not reviewed: this VM's GitHub token is rejected (git fetch and gh 401 since ~08:45Z), 971e8a7e not available locally; resumes when credentials work
CHECKPOINT 6fcf903d (08:43Z) [final] #390 @a8b5d2a8 GRANT all 11 closure pins; C1 met (unsound work = work of B u unsoundTiles, harm counts own work; Lean-checked); 5 audit pins gain only f and hf; #374's 42 byte-identical; soundness audit PASS w/ replay 7,998 decl, 53 pins; record art:d33e8c02, findings art:f476e0b1; queue empty
CHECKPOINT 8e9c21d0 (08:35Z) [final] #374 @6e39ccaa grant carries: merge adds exactly #383's lines (+ floor-carrying table type, U2 floor wording); soundness byte-identical to 594fe39c; verifier audit PASS, tests 19/1; record art:93b7a268 labelled, findings art:fdc1c60b; next #390 @a8b5d2a8
CHECKPOINT 98e0caa2 (07:57Z) [final] #390 @15a3ee7c (closure law) GRANT WITH C1 before merge: 10 pins true (closure_escape exact, covers undrawn nodes) but the audited unsound work omits wrong units' own work under the verifier's non-reflexive closure map (Lean-checked); restate over B u unsoundTiles cl B; audit PASS w/ replay 7,969 decl, 43 pins; store: record art:1d2d224c, findings art:391c7c59; queue empty
CHECKPOINT e8674b9f (07:54Z) [final] #374 @594fe39c GRANT: 10 new pins + 8 restated (hf only) + workRule_eq_draw; one_le_workK removal accepted; count-budget finding closed by removal (floors only from the verifier's table); soundness audit PASS w/ replay 7,981 decl, 42 pins; store: record art:93b7a268 verified=accepted, findings art:e43fc7c7; next #390 @15a3ee7c
CHECKPOINT 56dc2d90 (07:52Z) [final] #383 @2ad810cb GRANT: verify takes a stratified draw's K and strata from the verifier (N1 on #362 met); no pin changes (records unchanged); verifier audit PASS 14 pins, tests 19/1; store: record art:99d3b15d labelled for #383, findings art:dcdc4afe; next #374 @594fe39c, then #390 @15a3ee7c
CHECKPOINT e074592d (07:44Z) [final] #335 restated refinement pins GRANTED: rep_refines #264 @ff67422c, verify_refines + verify_tableAfter #270 @bdc4ec8b, verify_refines_ofCircuit #278 @1914b76d (restated exactly as the one-table call forces); other refinement records unchanged, R9c/R11 grants carry; audits PASS w/ replay (top 41999484: 47 pins); N1 one-table only; next #374 @594fe39c then #390 @15a3ee7c
CHECKPOINT 40a4d5e5 (07:34Z) [final] #379 @fa4fb58e GRANT carries (Lean inputs byte-identical to ded605b1; Python back to #378's), #381 @d237e60a GRANT (tree identical to ded605b1); #375/#378 stand; record art:f2e25bbd relabelled, findings art:67f124d4; next: #335's four restated refinement pins
CHECKPOINT 4bc16af3 (07:11Z) [final] influence stack GRANTED, no conditions: #375 @de831e06 13 pins, #378 @46b8faf9 3 pins, #379 @ded605b1 2 pins (audit+replay PASS 33/36/38 pins, no earlier record moved); notes: witness header, delivered = committed D, trivial H; store: records art:a6d995f5 art:c6e9f364 art:f2e25bbd verified=accepted; #374 held (X-SPC-81); refinement 0233Z awaiting a slot
CHECKPOINT 081258c8 (07:07Z) [final] #362 @3bc3eba7 RE-GRANT all 13 pins (records as granted at ad14e863); C1 met, X-SPC-80 met (verify's own K); seam stated truthfully, agree X-SPC-78; store: record art:99d3b15d verified=accepted, findings art:852fd34f; #374 held (X-SPC-81); refinement 0233Z #335 restated pins awaiting a slot
CHECKPOINT 063b6fc3 (07:07Z) [final] #362 @3bc3eba7 RE-GRANT all 13 pins (records as granted at ad14e863); C1 met (verify's own table/program/partition), X-SPC-80 met (verify's own K); seam stated truthfully, agree X-SPC-78 (closure PR); N2 docs overstate what carries, N3 compose via audit_closure; store: record art:99d3b15d verified=accepted, findings art:852fd34f; #374 held (X-SPC-81)
CHECKPOINT 023f2dac (05:20Z) [final] #362 @ad14e863 work draw law: 13 new pins GRANT (work bound both layers, floor, K+m, 27713 sizing, closure seam, rfl rule bridge); C1 executable: verify must hold its own work table for a work draw; store: record art:63602bf7 verified=accepted, findings art:f791370e
CHECKPOINT 16c70f83 (01:15Z) [final] #335 @f7dd8a53 GRANTED (Lean reads #306 multi-table records; tables from the verifier's J and the session draw; audit PASS, 11 session-table tests); #345's circuitTypes manyTables := none is right; N1 merge order vs the refinement stack
CHECKPOINT 851fa74a (20:38Z) [final] #316 (N1 option (b)) GRANTED at 373252e2 covering ae9142fb (build, std axioms, audit+replay PASS 7834 decl/20 pins; record unchanged); C1 on claims: bind the committed zero (checklist row beside hOne, or hZero in #207)
CHECKPOINT 3ea7ce15 (17:38Z) [final] N1 on #287: option 3 in model form (constant-zero source as a statement constant, repeated sources within a unit); #308 and #313 held (checks correct, but refuse honest padded attention); R11 done (granted 17:22Z); refinement handoffs re-stamped, reviews updated
CHECKPOINT 50e90da4 (17:23Z) [final] R11 GRANTED: #296 @e13ad134 (Sim.prob_le; live game = coin server loop), #302 @ec807b18 (live_le, tableC_eq_modelTable, live_le_tableC; Decodes right), #310 @def4d6b9 (encs_inj, zerocheck_frames); notes for R11b/R11d (coin source, N, scope, decoders, strategy cost, m>=14); #308 next
CHECKPOINT f817d283 (17:05Z) [final] #306 GRANTED (per-table RANK confirmed); R11 handoffs #296 and #302 received, waiting for the coordinator's order
CHECKPOINT 9b3aafac (17:04Z) [final] #306 @ecf275ec (J tables per session, CPU prover) GRANTED: per-table RANK confirmed (block-diagonal masking, equal to the joint check; joint only for the private glued union); statement-level parts match the Lean batchedSession model; 5 notes (simulator at J=2 before J>1 ZK claims, RANK sizing per table, Bernoulli + J>1, law from unit_draw, proof gap 1)
CHECKPOINT b70bb5cd (16:15Z) [final] GEMM column-batch tiles scope: 4 questions answered (many-to-one rows need no new soundness hypothesis, meaning clauses only; pad edge tiles with a fixed pair, full wiring; tile draws fixed at registration, private track one shape via D5; mask relocation kept as separate audit option). Earlier: #287 UProg.rowsL1 GRANTED
CHECKPOINT d985d04e (15:57Z) [final] #287 UProg.rowsL1 @decbc673 GRANTED (type hash 000000005e4ddc68 computed locally; 46ff28db not on GitHub); recommend dropping UnitSpec.nodup (follows from hd via orderChecked, Lean check); N1 for S4d/1e: source restrictions must hold for the verifier's wiring or be refused
CHECKPOINT fca3b335 (15:02Z) [final] R9c #291 @363a4264 GRANTED (setup_wf, setupH_wf, stmtOf_linkLayout); compile_time Refine/Walk acceptable (proof-only tactic, no IO; notes: pin the file digest, keep listed modules out of pinned reads); private-ZK 14:45Z delta: grant stands
CHECKPOINT 777cf810 (13:15Z) [final] #282 @db55d87c and #268 @0a241289 GRANTED (note: Rust slot_log bound on every range); C1 on verity/flock-circuit/types met (Lean at #277 reproduces digest 529ab95c.. and Sigma a0caa27c.., 20/20 verdicts); C2 stands until #277 and #268 land with #272/#273
CHECKPOINT 9835f2bb (12:08Z) [final] verity/flock-circuit/types (#272 @5c0de806, #273 @0db3717e) GRANTED WITH CONDITIONS (C1 digest TAG = statement id, or Rust/Lean digests disagree; C2 no cell before the Lean verifier reads the id and #268 is on the typed path); earlier today: #256 over ofBlock words, R9a #275, R9b #278 GRANTED
CHECKPOINT c26418ff (11:50Z) [final] #256 over ofBlock words GRANTED, soundness train 04cd8414 as granted; R9a #275 @2642e908 and R9b #278 @c5a1180a GRANTED (stmtOf determinacy proved in Lean; free-bit Nodup should be a verifier check); #270 13fda652 nothing more
CHECKPOINT 412d8318 (10:35Z) [final] #263 @6eb38c48, #267 @3023daaa, #271 @c7b06dd1 GRANTED (three notes for 1e on #263); correction to 0845Z: Lean setup already refused k_log > 26, so for 2^27 those lines and #267's constant move to 27; reviews in store private/
CHECKPOINT 1712fa13 (10:12Z) [final] R7 #266 @d3e503d0, R8a #264 @f34c5b6d, R8b #270 @4f7f822a GRANTED (note on #270: lift from verify_refines); re-records printing-only; 51 pointers copied into the store's internal/lanes/coordinator, new ones written to both; #267, #263, #271 received, waiting for order
CHECKPOINT e5493f9f (08:52Z) [final] refinement R1-R4 (#209 #222 #230 #237) and R6b (#262) GRANTED; with #254/#259 the refinement stack R1-R6b is fully reviewed; R1-R4 pins std axioms at #259 (files byte-identical), #262 builds std axioms; reviews in the store private/red-team-reviews/refinement/ (private); reply lanes/coordinator/20260928T0852Z-handoff-from-red-team-flock-3.md; stamps now from date -u; CPU $0
CHECKPOINT e5493f9f (08:44Z) [final] refinement #254 (R5) + #259 (R6) GRANTED (base R1-R4 #209/#222/#230/#237 and R6b #262 still unreviewed); M0 block limit 2^27: not as one constant (pinned table_sound_fast100* take InRange kLog<=26; spec + GPU guard say 26; extend InRange, numbers move ~0.0002 bits); #257 + #260 GRANTED; new folder private/red-team-reviews/refinement/; reviews in the store private/red-team-reviews/ (private); replies lanes/coordinator/20260928T0840Z, 0845Z, 0850Z-handoff-from-red-team-flock-3.md; CPU $0
CHECKPOINT e5493f9f (08:24Z) [final] #258 coin-tree v2 impl GRANTED (spec + clarification + simulator restart; flock-live tests 50/50 on rustc 1.98.1); #207 GRANTED at 89b15f38 (RowsL1 conditioned, hOne named); #256 compose_eval_unit GRANTED; coin-tree v2 evidence moved into private/red-team-reviews/zk-proofs/; reviews in the store private/red-team-reviews/ (private); replies lanes/coordinator/20260928T0825Z and 0830Z-handoff-from-red-team-flock-3.md; CPU $0
CHECKPOINT e5493f9f (07:33Z) [final] #207 REFUSED as pinned (RowsL1 needs the constant at 1); #247 GRANTED (carries to a05648e8); #249 GRANTED; coin-tree v2 + #245 GRANTED (C1 closed in proof; code pending), #239 stands; #252 GRANTED (C3 prover side); private ZK draft 4 RE-GRANTED (M1-G toy v2 rerun identical); reviews in the store private/red-team-reviews/ (private); replies lanes/coordinator/20260928T0700Z, 0710Z, 0712Z, 0720Z, 0725Z, 0745Z-handoff-from-red-team-flock-3.md; queue empty; CPU $0
CHECKPOINT e5493f9f (07:23Z) [final] #207 REFUSED as pinned (RowsL1 needs the constant at 1; fix named); #247 S3c GRANTED; #249 compose GRANTED; coin-tree v2 GRANTED (closes C1 in the proof; code pending gap 13), #245 GRANTED, #239 stands at 23d3d6fe; #252 region-word check GRANTED (C3 prover side); reviews in the store private/red-team-reviews/ (private); replies lanes/coordinator/20260928T0700Z, 0710Z, 0712Z, 0720Z, 0725Z-handoff-from-red-team-flock-3.md; next: private ZK draft 4; CPU $0
CHECKPOINT e5493f9f (07:00Z) [final] #207 e2e skeleton @78bc1d86 REFUSED as pinned (RowsL1 undischargeable as stated: derive's (form)*1 copy rows need the constant at 1; Lean counterexample; fix: condition RowsL1 on the constant + name Xplur's constant); train head 2c86df73 builds, std axioms, audit consistent; #194/#199/#205 can land via b9dea1f7; review in the store private/red-team-reviews/pr207-e2e-skeleton.md (private); reply lanes/coordinator/20260928T0700Z-handoff-from-red-team-flock-3.md; next #247, coin-tree v2 + #245, private ZK draft 4; CPU $0
CHECKPOINT e5493f9f (05:56Z) [final] ZK proofs: public Theorem Z GRANT WITH CONDITIONS (3); #227 @e1947d5b GRANTED (11 pins); #239 @92ce596e GRANTED (T6); private Theorem 1 GRANT WITH CONDITIONS (6); reviews in the store private/red-team-reviews/zk-proofs/ (private); reply lanes/coordinator/20260928T0555Z-handoff-from-red-team-flock-3.md; CPU $0
CHECKPOINT e5493f9f (04:02Z) [final] #205 S2 GRANTED at 50e7b5a2; #202 table/v2 GRANTED at 10d8e46b; replies lanes/coordinator/20260928T0350Z and 20260928T0401Z-handoff-from-red-team-flock-3.md
CHECKPOINT e5493f9f (03:18Z) [final] #200 GRANTED at 56936c35; #187 delta GRANTED at 87a0e3b7 (main pin 9cbdef19); c176e9c8 NON_ZK_PROOF carried; replies lanes/coordinator/20260928T0318Z-handoff-from-red-team-flock-3.md
CHECKPOINT e5493f9f (03:01Z) [final] #197 grant stands at 67e7f669 (wording amended: X-09 chunked fallback refuses all stochastic top-p rows, fails closed); #200 re-review at 56936c35 pending: GitHub auth for danielreuter/verity failing since 02:40Z; reply lanes/coordinator/20260928T0301Z-handoff-from-red-team-flock-3.md
CHECKPOINT e5493f9f (02:31Z) [final] M0 split #192/#193/#195 GRANTED; a1e58e33 NON_ZK_PROOF carried; #194 GRANTED; #200 REFUSED as pinned (reachOk fan-out, read table shape); #197 GRANTED; replies lanes/coordinator/20260928T0211Z and 20260928T0231Z-handoff-from-red-team-flock-3.md
CHECKPOINT e5493f9f (00:43Z) [final] #187 Rope.rope_sound (L1 for RoPE) @ 3ac26fd9 GRANTED; review private/red-team-reviews/pr187-rope-l1/review.md; reply lanes/coordinator/20260928T0042Z-handoff-from-red-team-flock-3.md
CHECKPOINT b489b7df (21:33Z) [final] FINAL: FlockLevel3.build_computes (cursor/flock-verifier-lookup-rows-7ab3 @b7eb6a7e) GRANTED: the verifier's own lookup rows (net.a/net.b, tableB as foldB folds it) with constant 1 force out bit j = bit j of table[index], every table, any char-2 field; hK useful <= KONST (2^48) excludes nothing; one new pin, none changed; independently: lake build PASS, standard axioms, level3 audit PASS (999 decls, 50 pins); review in the store private/red-team-reviews/m0-statement/ (private); pointer lanes/coordinator/2135Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT ebf04a52 (19:57Z) [final] FINAL: M0 lookup slots scoped to #83's current tail stages (@73a273d4): GRANT. Q1 gates forcing out = table[index], and stage-to-slot wiring exactly once at equal width in both verifiers (circuit.rs:531-563; Circuit.lean:169, HmRow.lean:181) with exact copies (delta (i,i)+(i,src)); Q2 verifier-pinned hash-checked tables; Q3 exact per-type fold after the commitment. Placement PR parked (conditions dropped). Review in the store private/red-team-reviews/m0-statement/ (private); pointers lanes/coordinator/1958Z, 2005Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT f9546428 (19:54Z) [final] FINAL: M0 lookup slots (#83 @73a273d4) GRANT: plain gates forcing out = table[index] (decoders + 31x1024 AND products, table as XOR forms), verifier-pinned hash-checked tables, exact per-type fold after the commitment, per-read constraints; reads-inside-units extension GRANT WITH CONDITIONS C1 wire completeness in both verifiers, C2 flipped-read negative + IR agreement; numbers ex2 41,308 ANDs / 153.7M XOR, sqrt 49,576 / 309.4M; review in the store private/red-team-reviews/m0-statement/ (private); pointer lanes/coordinator/1958Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
CHECKPOINT a06b1302 (18:51Z) [final] FINAL: soundness stack reviewed: A2 (#127/#163/#170/#171) GRANTED; #173 GRANTED at af5e9c1b (A1 removal via the DKT26 bridge + the eta retune to 1/200: table theorems 2^-205, constants only, eta one definition; recomputed worst 2^-205.21); #130 pins GRANTED; review in the store private/red-team-reviews/soundness-a2-a1/ (private); pointers lanes/coordinator/1830Z, 1855Z; CPU $0; agent bc-f0bc7e75-356e-5c24-a081-9c374b3aac26
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
- **The η retune, #173 @ af5e9c1b (18:47Z):** GRANTED.
  - η goes to 1/200 at unchanged `fast100`. It's one definition used by every level's radius.
  - 21 signatures change, constants only, so the table and audit theorems go to `2^-205` with identical hypotheses.
  - My recomputation gives a worst case of `2^-205.21`, and reproduces `2^-195.44` at 1/50.
  - Reply: `lanes/coordinator/20260927T1855Z-handoff-from-red-team-flock-3.md`.

### M0's lookup slots (27 Sep, 19:44–19:58Z; asked for directly, Daniel suspicious)

- **#83 @ 73a273d4:** GRANT.
  - The lookup slot is plain gates, forcing exactly `out = table[index]`.
  - Only the verifier's pinned, hash-checked MUFU tables are accepted.
  - The per-type fold is exact and comes after the commitment, and constraints hold per read.
  - It's covered generically by the soundness stack. The Lean verifier builds lookup slots, and level 3 proves its fold. The
    lemma "rows ⇒ `table[index]`" is unproved.
- **Reads inside units (the planned stacked PR):** GRANT WITH CONDITIONS.
  - C1: both verifiers enforce wire completeness.
  - C2: a flipped-read negative test, plus IR agreement.
- **Review:** `private/red-team-reviews/m0-statement/review.md`, the last section, in the private store, with
  `lookup_numbers.txt` beside it.
- **Reply:** `lanes/coordinator/20260927T1958Z-handoff-from-red-team-flock-3.md`.
- **Scope update (19:55Z):** Daniel chose plain gates for new work, so the placement PR is parked and its conditions are
  dropped.
  - For #83's current tail stages, both verifiers enforce exactly-once, equal-width wiring, and every wire is an exact copy.
  - GRANT. Reply: `lanes/coordinator/20260927T2005Z-handoff-from-red-team-flock-3.md`.
- **The recommended lemma, `FlockLevel3.build_computes` (b7eb6a7e):** GRANTED.
  - It's stated over the verifier's own lookup rows and the proved fold's B side, for every table, over any
    characteristic-2 field.
  - Nothing is weakened: `useful ≤ KONST`, with `KONST = 2^48 − 1`.
  - One new pin, and no existing pin changed.
  - Independently here: build passes, standard axioms, and the level-3 audit passes (999 declarations, 50 pins).
  - Reply: `lanes/coordinator/20260927T2135Z-handoff-from-red-team-flock-3.md`.
- **Request:** `lanes/coordinator/20260927T1816Z-handoff-from-flock-soundness-a2-constant.md`.
- **Review:** `private/red-team-reviews/soundness-a2-a1/`, in the private store.
- **Reply:** `lanes/coordinator/20260927T1830Z-handoff-from-red-team-flock-3.md`.

### #187, `Rope.rope_sound`, L1 for RoPE (28 Sep, 00:20–00:45Z; named statement reviewer)

- **#187 @ 3ac26fd9 (stacked on #180 @ 3fcf1932):** GRANTED.
  - Two notes, neither blocking: a wording note for `l1-template-rows.md`, and two generator asserts to add before
    `lean_rows` goes beyond RoPE.
  - Checked independently here: the RoPE modules rebuild, the kernel replay accepts them (standard axioms only), and
    `test_lean_rope.py` passes. CPU only, $0.
- **Request:** `lanes/coordinator/20260928T0014Z-handoff-from-flock-soundness-rope-l1.md`, in the store's `internal/`.
- **Review:** `private/red-team-reviews/pr187-rope-l1/review.md`, in the private store, with `evidence/` beside it.
- **Reply:** `lanes/coordinator/20260928T0042Z-handoff-from-red-team-flock-3.md`.

### M0's split, the constant API's Lean statements, #197, and a GEMM re-record (28 Sep, 01:32–02:31Z; named statement reviewer)

- **#192 @ adcf38bf: GRANTED.** The `verity/flock-circuit` statement is byte-identical to `73a273d4`. Only the unit
  sections changed (train K). Inline reads were checked exhaustively on every pinned table, and all production rows are
  forced.
- **#193 @ b7e16c46: GRANTED, scoped.** It restores #83's glue byte for byte and leaves the circuit statement unchanged.
  `verity/flock-tables` itself is unreviewed.
- **#195 @ 162e0890: GRANTED.** `out = table[index]` holds exhaustively at the PR's row counts, and the wiring conditions
  hold. It carries #190. An addendum covers program tables.
- **`art:a1e58e33`: `proof_class=NON_ZK_PROOF` carried over** from `art:a83371c2`, with a `finding` label: the same run files
  and circuit (`cecaa76a…`).
- **#194 @ b7b7b42f (`Flock.CircuitType.check_ok`): GRANTED.** Four notes, none blocking.
- **#200 @ fdd7b4da (`Flock.Layout.check_ok`): REFUSED as pinned.** `reachOk` refuses honest fan-out and disagrees with
  Python, and a read's held table isn't tied to its type entry. There are two small fixes, and I re-check the delta.
- **#197 @ 4497a75d: GRANTED.** Every Match path holds the constant S to the kernels' S per event, and only the per-step
  splits word is dropped.
- **Side finding:** #187 pins RoPE `933c4ef8…`, while main has pinned `9cbdef19…` since train K. Its Lean data needs
  regenerating after its rebase, and then a delta check.
- **Requests:**
  - `internal/lanes/coordinator/20260928T0125Z-note-to-red-team-m0-prover-pr-statement-changes.md`, in the store;
  - `internal/lanes/red-team-flock-3/20260928T0210Z-handoff-from-coordinator.md`, in the store;
  - `lanes/coordinator/20260928T0144Z-handoff-from-vllm-cross-call-check-merge-request-197.md`.
- **Reviews** (in the private store):
  - `private/red-team-reviews/m0-statement/split-192-193-195.md`, with `split-192-193-195-evidence/`;
  - `private/red-team-reviews/constant-api-lean.md`, with `constant-api-lean-evidence/`;
  - `private/red-team-reviews/pr197-topp-constant-splits.md`.
- **Replies:**
  - `lanes/coordinator/20260928T0211Z-handoff-from-red-team-flock-3.md` (#192, #193, #195, `a1e58e33`);
  - `lanes/coordinator/20260928T0231Z-handoff-from-red-team-flock-3.md` (#194, #200, #197).
- **02:40–03:01Z follow-ups:**
  - **#197 @ 67e7f669: grant unchanged.** Its wording is amended: X-09's chunked fallback refuses every stochastic top-p
    request, which is older than #197 and fails closed. Request:
    `internal/lanes/coordinator/20260928T0240Z-handoff-from-vllm-cross-call-check-197-new-head.md`, in the store.
  - **#200 @ 56936c35: re-review pending.** The request is
    `internal/lanes/coordinator/20260928T0305Z-note-to-red-team-constant-api-200-re-review.md`, in the store. It's blocked:
    GitHub auth for the verity repo has failed here since 02:40Z, and the repo is private.
  - **Reply:** `lanes/coordinator/20260928T0301Z-handoff-from-red-team-flock-3.md`.
- **03:03–03:18Z (GitHub access back at 03:02Z):**
  - **#200 @ 56936c35: GRANTED.** Both fixes are in, and program tables keep every bit. The re-review section is in
    `private/red-team-reviews/constant-api-lean.md`.
  - **#187 @ 87a0e3b7 (main's RoPE pin `9cbdef19…`): GRANTED.** Only the column numbers move (6144, 6016+o). Checked here:
    decode, rebuild and kernel replay. The delta section is in `private/red-team-reviews/pr187-rope-l1/review.md`.
    Request: `internal/lanes/coordinator/20260928T0305Z-note-to-red-team-and-coordinator-pr187-main-pin.md`, in the store.
  - **`art:c176e9c8`: `NON_ZK_PROOF` carried over** from `art:e352f2ad`, with the same run files and circuit
    (`2b2e9603…`), and an input set re-registered with an identical payload.
  - **Reply:** `lanes/coordinator/20260928T0318Z-handoff-from-red-team-flock-3.md`.
- **03:25–04:02Z (GitHub auth down again about 03:25–03:44Z):**
  - **#205 (S2) @ 50e7b5a2: GRANTED.** `compose_sound` and `compose_complete` are L1, with non-vacuity, for every flat type
    over the verifier's own `derive`. Checked here: build, axioms `[propext, Quot.sound]`, kernel replay and
    `test_flock_rows`.
    - Request: `internal/lanes/coordinator/20260928T0400Z-note-to-red-team-from-flock-soundness-s2-pins.md`, in the
      store.
    - Review: `private/red-team-reviews/pr205-s2-compose.md`.
    - Reply: `lanes/coordinator/20260928T0350Z-handoff-from-red-team-flock-3.md`.
  - **#202 (table/v2) @ 10d8e46b: GRANTED.** `build_computes_v2` gives `out = table[index]` on every bit, under both
    labels. Checked here: `Library.lean` is a byte copy, the level-3 audit passes with replay, and the vectors pass.
    - Request: `internal/lanes/coordinator/20260928T0325Z-handoff-from-flock-verifier-202-library-rule.md`, in the store.
    - Review: `private/red-team-reviews/pr202-table-v2.md`.
    - Reply: `lanes/coordinator/20260928T0401Z-handoff-from-red-team-flock-3.md`.

### Zero knowledge: the public and private proofs, and #227 and #239's pins (28 Sep, 04:40–05:55Z; asked for directly)

Verdicts only. The findings are in the store's `private/`.
- **`docs/zk-proof-public.md` (Theorem Z): GRANT WITH CONDITIONS,** with three conditions. It still holds after the
  05:32Z refinement pass.
- **#227 @ `e1947d5b`: GRANTED,** all eleven pins.
  - Request: `internal/lanes/red-team-flock-3/20260928T0535Z-handoff-from-zk-public-227-pin-review.md`, in the store.
- **#239 @ `92ce596e`: GRANTED,** `coin_opening_binding`, with one non-blocking note. It is covered by the same request's
  addendum.
- **Checked here for both PRs:** the full soundness package builds, all twelve new pins use standard axioms, and the
  audit files add exactly those pins.
- **`docs/zk-proof-private.md`, draft 2 (Theorem 1): GRANT WITH CONDITIONS,** with six conditions.
- **Reviews:** `private/red-team-reviews/zk-proofs/public-circuit.md` and `private-circuit.md`, with `evidence/`.
- **Reply:** `lanes/coordinator/20260928T0555Z-handoff-from-red-team-flock-3.md`.

### The end-to-end skeleton, S3c, the keyed coin tree, and private ZK draft 4 (28 Sep, 06:40Z onward; named statement reviewer)

Verdicts only. The findings are in the store's `private/`.
- **#207 @ `78bc1d86` (train head `2c86df73`): REFUSED as pinned.** `RowsL1` can't be discharged as stated, and the gap
  it depends on isn't named. The fix is small. Both pins build with standard axioms, and the audit record is consistent.
  #194, #199 and #205 don't depend on #207.
  - Requests, both in the store:
    - `internal/lanes/red-team-flock-3/20260928T0641Z-handoff-from-flock-soundness-207-pin-review-pointer.md`;
    - `internal/lanes/coordinator/20260928T0430Z-note-to-red-team-from-flock-soundness-e2e-skeleton.md`.
  - Review: `private/red-team-reviews/pr207-e2e-skeleton.md`.
  - Reply: `lanes/coordinator/20260928T0700Z-handoff-from-red-team-flock-3.md`.
- **#247 (S3c) @ `b274db3f`: GRANTED.** `unit_sound` and `layout_sound` state L1 over the type DAG from
  `deriveChecked`. Four notes, none blocking; the main one is that 1e must consume `deriveChecked`'s output.
  - Request: `internal/lanes/red-team-flock-3/20260928T0640Z-handoff-from-flock-soundness-247-pin-review.md`, in the
    store.
  - Review: `private/red-team-reviews/pr247-s3c-dag.md`.
  - Reply: `lanes/coordinator/20260928T0710Z-handoff-from-red-team-flock-3.md`.
  - 07:35Z: the grant carries to `a05648e8` (the order check added; the statements unchanged), in the same reply's
    addendum.
- **#249 @ `ec52ce38`: GRANTED.** `Rows.compose_eval` and `placement_of_realizes` read `derive`'s rows as the audit's
  `Rows` and place them. Three notes, none blocking; one is shared with #207, the constant at 1.
  - Request: `internal/lanes/red-team-flock-3/20260928T0700Z-handoff-from-audit-lean-249-pin-review.md`, in the store.
  - Review: `private/red-team-reviews/pr249-compose.md`.
  - Reply: `lanes/coordinator/20260928T0712Z-handoff-from-red-team-flock-3.md`.
- **The keyed coin tree (`docs/coin-tree-v2.md`): GRANTED.** It closes the auxiliary-input condition in the proof; for
  the code, the condition stays open until v2 is implemented. **#245 @ `bfca7e00`: GRANTED.** **#239 @ `23d3d6fe`:** grant
  unchanged (docstrings only).
  - Request: `internal/lanes/red-team-flock-3/20260928T0636Z-handoff-from-zk-public-coin-tree-v2-statement-review.md`,
    in the store.
  - Review: `private/red-team-reviews/zk-proofs/coin-tree-v2.md`.
  - Reply: `lanes/coordinator/20260928T0720Z-handoff-from-red-team-flock-3.md`.
- **#252 @ `2198c19c` (the region-word check): GRANTED.** C3 is met on the prover's side once it lands; the Lean side is
  to come.
  - Request: `internal/lanes/red-team-flock-3/20260928T0712Z-handoff-from-flock-zk-region-word-check.md`, in the store.
  - Review: `private/red-team-reviews/zk-proofs/pr252-region-word-check.md`.
  - Reply: `lanes/coordinator/20260928T0725Z-handoff-from-red-team-flock-3.md`.
- **The private-circuit ZK proof, draft 4 (06:50Z): RE-GRANTED.** All six conditions are met in the proof. My rerun of
  the M1-G toy v2 is identical to the recorded result. What remains is building and checking; one wording point concerns
  `ε_T`'s worst case.
  - Request: the user, directly (after #207, #247, #249, coin-tree v2, #245 and #252).
  - Review: appended to `private/red-team-reviews/zk-proofs/private-circuit.md`.
  - Reply: `lanes/coordinator/20260928T0745Z-handoff-from-red-team-flock-3.md`.
- **#258 @ `1053c0c9` (coin-tree v2 implemented): GRANTED.** It matches the spec and my clarification, and the simulator
  restarts after one `Hello`. `flock-live`'s tests pass 50 of 50 here.
  - Request: `internal/lanes/red-team-flock-3/20260928T0818Z-handoff-from-flock-zk-coin-tree-v2-impl.md`, in the store.
  - Review: `private/red-team-reviews/zk-proofs/pr258-coin-tree-v2-impl.md`.
- **#207 @ `89b15f38`: GRANTED** on re-review. `RowsL1` is conditioned on the constant and `hOne` is named.
  - Review: appended to `private/red-team-reviews/pr207-e2e-skeleton.md`.
- **Reply for both:** `lanes/coordinator/20260928T0830Z-handoff-from-red-team-flock-3.md`. It also records the move of
  the coin-tree v2 evidence into `zk-proofs/`.
- **#256 @ `950b4445` (`Rows.compose_eval_unit`): GRANTED.** It is L1 over the type DAG for the audit's `Rows`, #247's
  `unit_sound` read through #249's order.
  - Request: `internal/lanes/red-team-flock-3/20260928T0756Z-handoff-from-audit-lean-256-pin-review.md`, in the store.
  - Review: `private/red-team-reviews/pr256-compose-dag.md`.
  - Reply: `lanes/coordinator/20260928T0825Z-handoff-from-red-team-flock-3.md`.
- **Refinement #254 (R5) @ `80905d97`: GRANTED. #259 (R6) @ `07174fc1`: GRANTED.** Their base R1–R4 (#209, #222, #230,
  #237) is still unreviewed, and so is #262 (R6b).
  - Requests, in the store:
    - `internal/lanes/red-team-flock-3/20260928T0735Z-handoff-from-refinement-254-pin-review.md`;
    - `internal/lanes/red-team-flock-3/20260928T0855Z-handoff-from-refinement-254-pin-review-amended.md`;
    - `internal/lanes/red-team-flock-3/20260928T0915Z-handoff-from-refinement-259-pin-review.md`.
  - Reviews: `private/red-team-reviews/refinement/pr254-ligerito-refines.md` and `pr259-final-refines.md`.
  - Reply: `lanes/coordinator/20260928T0840Z-handoff-from-red-team-flock-3.md`.
- **M0's block limit `2^27`: not as a one-constant change.** The pinned table-soundness theorems' `InRange` has
  `kLog ≤ 26`, and so do the spec and the GPU guard. Extend first; the numbers move by about 0.0002 bits.
  - Request: `internal/lanes/coordinator/20260928T0830Z-note-to-red-team-m0-block-limit-2-27.md`, in the store.
  - Review: `private/red-team-reviews/m0-statement/block-limit-2-27.md`.
  - Reply: `lanes/coordinator/20260928T0845Z-handoff-from-red-team-flock-3.md`.
- **#257 @ `714d0de2` (Lean region-word check): GRANTED. #260 @ `6c07b85f` (Lean coin-tree v2): GRANTED.**
  - Request: `internal/lanes/red-team-flock-3/20260928T0810Z-handoff-from-flock-verifier-257-260-review.md`, in the
    store.
  - Review: `private/red-team-reviews/zk-proofs/pr257-pr260-lean-verifier-sides.md`.
  - Reply: `lanes/coordinator/20260928T0850Z-handoff-from-red-team-flock-3.md`.
- **Refinement R1–R4 and R6b: GRANTED.** That is #209 @ `71b283ee`, #222 @ `a8f6f89f`, #230 @ `acf6534c`, #237 @
  `236160ed` and #262 @ `2899399d`, so the stack R1–R6b is fully reviewed.
  - Requests, in the store:
    - `internal/lanes/red-team-flock-3/20260928T0440Z-handoff-from-refinement-209-pin-review.md`;
    - `internal/lanes/red-team-flock-3/20260928T0505Z-handoff-from-refinement-222-pin-review.md`;
    - `internal/lanes/red-team-flock-3/20260928T0512Z-handoff-from-refinement-230-pin-review.md`;
    - `internal/lanes/red-team-flock-3/20260928T0526Z-handoff-from-refinement-237-pin-review.md`;
    - `internal/lanes/red-team-flock-3/20260928T0825Z-handoff-from-refinement-262-pin-review.md`.
  - Reviews: in `private/red-team-reviews/refinement/`.
  - Reply: `lanes/coordinator/20260928T0852Z-handoff-from-red-team-flock-3.md`.
- **Note on stamps.** From 08:52Z, note and review stamps come from `date -u` at write time. Some earlier pointers today
  carry stamps a few minutes ahead of when they were written (for example, `…0850Z…` was written at about 08:45Z).
- **Refinement R7, R8a and R8b: GRANTED.** That is #266 @ `d3e503d0`, #264 @ `f34c5b6d` (the amended `rep_refines`) and
  #270 @ `4f7f822a` (`verify_refines` and `verify_tableAfter`). The stack is now reviewed through R8b.
  - On #270, one note, not a condition: lift a probability bound from `verify_refines`, not from `verify_tableAfter`,
    whose messages are existential and whose schedule is fixed.
  - The re-records of #264 and #266 on the train moved printing only.
  - Requests, in the store:
    - `internal/lanes/red-team-flock-3/20260928T0842Z-handoff-from-refinement-266-pin-review.md`;
    - `internal/lanes/red-team-flock-3/20260928T0835Z-handoff-from-refinement-264-pin-review.md`;
    - `internal/lanes/red-team-flock-3/20260928T0905Z-handoff-from-refinement-264-pin-review-amended.md`;
    - `internal/lanes/red-team-flock-3/20260928T0932Z-handoff-from-refinement-270-pin-review.md`.
  - Reviews: `private/red-team-reviews/refinement/pr266-merkle-paths.md`, `pr264-rep-refines.md` and
    `pr270-verify-refines.md`.
  - Reply: `lanes/coordinator/20260928T1010Z-handoff-from-red-team-flock-3.md`.
- **My pointers were missing from the store.** The cloud mirror copies the store's `internal/lanes/` into this repo, one
  way. I had written pointers only here, so cloud lanes reading the store's `internal/lanes/coordinator/` could not see
  them.
  - By 10:00Z all 51 were copied there, byte-identical, including `20260928T0852Z-handoff-from-red-team-flock-3.md`.
  - From 10:10Z, each pointer is written to both places.
- **#263 (S3c-2, reads) @ `6eb38c48`, #267 @ `3023daaa` and #271 @ `c7b06dd1`: GRANTED,** taken in that order at the
  coordinator's 10:13Z word.
  - #263 carries three notes for 1e, none of them conditions.
  - #271's bounds were evaluated exactly: at most 2^-205 for `22 ≤ m ≤ 35`, moving by at most 0.000045 bits.
  - **A correction to my 0845Z reply:** the Lean verifier already refused `k_log > 26` at setup. For 2^27, those lines
    and #267's constant must both go to 27.
  - Requests, in the store:
    - `internal/lanes/red-team-flock-3/20260928T0935Z-handoff-from-flock-soundness-263-pin-review.md`;
    - `internal/lanes/red-team-flock-3/20260928T0855Z-handoff-from-flock-verifier-267-in-range-pin.md`;
    - `internal/lanes/red-team-flock-3/20260928T0955Z-handoff-from-flock-soundness-271-inrange-27-pin-review.md`.
  - Reviews:
    - `private/red-team-reviews/pr263-s3c2-reads.md`;
    - `m0-statement/pr267-in-range-at-parse.md` and `m0-statement/pr271-in-range-27.md`;
    - an update appended to `m0-statement/block-limit-2-27.md`.
  - Reply: `lanes/coordinator/20260928T1034Z-handoff-from-red-team-flock-3.md`. It starts with the store's `cursor` block,
    as everything I write under `internal/` now does.
- **#256's `Rows.compose_eval_unit` restated over `ofBlock words`, in the soundness train @ `04cd8414`: GRANTED.** Taken
  ahead of #275 and #278, at the coordinator's 11:26Z word.
  - The restatement is needed, since #263's reads make the granted form false.
  - The train's other pins are as I granted them, and every moved read traces to a grant.
  - Request: `internal/lanes/red-team-flock-3/20260928T1105Z-handoff-from-flock-soundness-256-ofblock-words.md`, in the
    store.
  - Review: `private/red-team-reviews/pr256-ofblock-words.md`.
  - Reply: `lanes/coordinator/20260928T1143Z-handoff-from-red-team-flock-3.md`.
- **Refinement R9a (#275) @ `2642e908` and R9b (#278) @ `c5a1180a`: GRANTED.**
  - #275's "false rather than vacuous" argument is now proved in Lean, as a red-team check.
  - Distinct region free bits should be a verifier check now: they are part of `LinkLayout`, which the pinned table
    theorems assume.
  - #270's docstring fix at `13fda652` needs nothing more.
  - Requests, in the store:
    - `internal/lanes/red-team-flock-3/20260928T1041Z-handoff-from-refinement-275-pin-review.md`;
    - `internal/lanes/red-team-flock-3/20260928T1112Z-handoff-from-refinement-278-pin-review.md`.
  - Reviews: `private/red-team-reviews/refinement/pr275-stmtof-fold.md` and `pr278-regions.md`.
  - Reply: `lanes/coordinator/20260928T1149Z-handoff-from-red-team-flock-3.md`.
- **`verity/flock-circuit/types` (#272 @ `5c0de806`, #273 @ `0db3717e`): GRANTED WITH CONDITIONS,** taken at the
  coordinator's 11:50Z word.
  - The export rule is sound, and the parse refusals hold.
  - **C1:** the digest `TAG` must be the statement id, or Rust and the Lean `Tags` disagree.
  - **C2:** no cell until the Lean verifier reads the id and #268 is on the typed path.
  - Request: `internal/lanes/coordinator/20260928T1050Z-note-to-red-team-constant-api-typed-statement-review.md`, in the
    store's coordinator folder.
  - Review: `private/red-team-reviews/m0-statement/typed-statement-review.md`.
  - Reply: `lanes/coordinator/20260928T1207Z-handoff-from-red-team-flock-3.md`.
- **#282 @ `db55d87c` (Lean refusals, `Flock.mkRegion_ok`) and #268 @ `0a241289` (Rust): GRANTED. C1 on the typed id:
  met.** Taken at the coordinator's 12:58Z word.
  - One note on #268: bound `slot_log` on every Rust range, as the Lean check does.
  - Lean at #277 reproduces the prover's typed digest and Σ, and gives all 20 recorded sessions their verdicts.
  - C2 stands until #277 and #268 land with #272 and #273.
  - Request: `internal/lanes/red-team-flock-3/20260928T1255Z-handoff-from-flock-verifier-282-statement-adjacent.md`, in
    the store.
  - Reviews: `private/red-team-reviews/m0-statement/pr282-pr268-refusals.md`, and the update in
    `typed-statement-review.md`.
  - Reply: `lanes/coordinator/20260928T1313Z-handoff-from-red-team-flock-3.md`.
- **The private-circuit ZK proof's 14:45Z delta (R8/D16's 512-bit salt seed, and §5's post-quantum status): the grant
  stands.** Taken at the coordinator's 14:45Z word, low priority.
  - The fixes are wording only: the scope goes into Theorem 1, the PRG row gets its quantum form, and the PRG step covers
    both generators.
  - Request: the coordinator, directly (`docs/zk-proof-private.md`).
  - Review: appended to `private/red-team-reviews/zk-proofs/private-circuit.md`.
  - Reply: `lanes/coordinator/20260928T1449Z-handoff-from-red-team-flock-3.md`.
- **Refinement R9c (#291) @ `363a4264`: GRANTED,** taken at 14:50Z.
  - With #278, refinement for the verifier's own statements now assumes only `13 ≤ m` and the unsalted scheme.
  - The soundness package's first `compile_time` module (`Refine/Walk.lean`, the proof-only tactic `walk_step`) is
    acceptable under the audit's trust model. Two notes go to the audit tool: tie the entry to the file's digest, and
    keep listed modules out of what pinned statements read.
  - Request, in the store: `internal/lanes/red-team-flock-3/20260928T1446Z-handoff-from-refinement-291-pin-review.md`.
  - Review: `private/red-team-reviews/refinement/pr291-setup-wf.md`.
  - Reply: `lanes/coordinator/20260928T1501Z-handoff-from-red-team-flock-3.md`.
- **#287 (S4c) `UProg.rowsL1` @ `decbc673`: GRANTED,** fetched at 15:31Z.
  - `46ff28db` isn't on GitHub, so I computed the pin's record locally (type hash `000000005e4ddc68`). An audit compare
    against it covers `46ff28db` once that's pushed.
  - Recommendation, not a condition: drop `UnitSpec.nodup`, which follows from `hd` through `orderChecked` (four lines in
    Lean). No verifier check is needed.
  - N1, for S4d/1e: the verifier's wiring must meet the source restrictions, or the verifier must refuse wirings that
    don't. The restrictions are no source read twice within a unit, and no unit input reading the constant.
  - Request, in the store: `internal/lanes/red-team-flock-3/20260928T1515Z-handoff-from-flock-soundness-287-rowsl1-pin-review.md`.
  - Review: `private/red-team-reviews/pr287-uprog-rowsl1.md`.
  - Reply: `lanes/coordinator/20260928T1555Z-handoff-from-red-team-flock-3.md`.
- **M0's GEMM column-batch tiles scope (options 4 and 5a): the four questions answered,** before any code. The grant comes
  on the PR.
  - Many-to-one rows need no new soundness hypothesis; the new `WellFormed` clauses are about meaning.
  - Edge tiles: pad with a fixed pair, keeping the full tile's wiring.
  - Tile draws with a fixed shape are independent of the draw if the tiling is fixed at registration. In the private
    track the shape can't be per stratum (the ZK proof's D5).
  - Keep the mask relocation as a separate audit-side option.
  - Request: the coordinator, directly (`internal/gemm-column-batch-tiles-layout-scope.md`, in the store).
  - Review: `private/red-team-reviews/m0-statement/gemm-column-batch-tiles.md`.
  - Reply: `lanes/coordinator/20260928T1614Z-handoff-from-red-team-flock-3.md`.
- **M1's #306 @ `ecf275ec` (J tables per session, CPU prover): GRANTED.**
  - Per-table RANK is confirmed. The masking map is block-diagonal, so it's the joint check's equivalent. The joint check is
    needed only for the private proof's glued union, whose glue claim reads every table's mask words.
  - The statement-level parts match the Lean `batchedSession` model.
  - Five notes, no conditions. The first: extend the simulator to J = 2 before a J > 1 cell claims ZK.
  - Request: `internal/lanes/coordinator/20260928T1650Z-note-to-red-team-from-flock-zk-multi-table.md`, in the store's
    coordinator folder.
  - Review: `private/red-team-reviews/zk-proofs/pr306-multi-table-sessions.md`.
  - Reply: `lanes/coordinator/20260928T1702Z-handoff-from-red-team-flock-3.md`.
- **R11: #296 @ `e13ad134`, #302 @ `ec807b18` and #310 @ `def4d6b9`: GRANTED** (six pins), taken in the
  coordinator's order at 17:07Z.
  - `Sim.prob_le` is sound.
  - The live game is faithful to the coin server's loop. Everything it omits is fixed on an accepted record: S6, S7/S8,
    S10, S11, S13.
  - `Decodes` is the right obligation.
  - The frames are the executable's bytes.
  - Notes for R11b/R11d: the coin source (with seed coins, `ASSUMPTIONS.md`'s two assumptions join A2), N, scope (one
    table, non-ZK), the decoders, the simulated strategy's cost, and `14 ≤ m`.
  - Requests, in the store, under the names the refinement lane re-stamped (first names in brackets):
    - `internal/lanes/red-team-flock-3/20260928T1548Z-handoff-from-refinement-296-pin-review.md` [`…1650Z…`];
    - `internal/lanes/red-team-flock-3/20260928T1606Z-handoff-from-refinement-296-live-game-revised.md` [also
      `lanes/red-team-flock-3/20260928T1720Z-handoff-from-refinement-296-live-game-revised.md`];
    - `internal/lanes/red-team-flock-3/20260928T1624Z-handoff-from-refinement-302-pin-review.md` [`…1850Z…`];
    - `internal/lanes/red-team-flock-3/20260928T1648Z-handoff-from-refinement-302-pin-addendum.md` [also
      `lanes/red-team-flock-3/20260928T1720Z-handoff-from-refinement-302-pin-addendum.md`];
    - `internal/lanes/red-team-flock-3/20260928T1704Z-handoff-from-refinement-310-pin-review.md` [`…1810Z…`].
  - Reviews: `private/red-team-reviews/refinement/pr296-live-game.md`, `pr302-table-simulation.md` and
    `pr310-frames.md`, with `refinement/evidence/r11-build-axioms-audit.log`.
  - Reply: `lanes/coordinator/20260928T1722Z-handoff-from-red-team-flock-3.md`.
- **The verifier lane's #308 and M0's Rust mirror #313: HELD** at the coordinator's 17:33Z word. Their refusals reject
  honest padded attention statements (any T not a multiple of 16).
  - My view on #287's N1: option 3 in its model form. The program model admits a constant-zero source (a forced-zero
    row, as a statement constant) and one source into several inputs of a unit. The verifier and the template stay
    unchanged.
  - #308's checks are correct (build, audit and tests pass), but they aren't needed.
  - Requests: `internal/lanes/red-team-flock-3/20260928T1720Z-handoff-from-flock-verifier-308-unit-sources.md` and
    `internal/lanes/red-team-flock-3/20260928T1732Z-handoff-from-flock-netlist-313-mirrors-308.md`.
  - View: `private/red-team-reviews/pr287-n1-options.md`.
  - Reply: `lanes/coordinator/20260928T1737Z-handoff-from-red-team-flock-3.md`.
- **Received, no action needed:** zk-public's `internal/lanes/red-team-flock-3/20260928T1733Z-note-from-zk-public-306-bound.md`.
  #306 leaves the public-circuit ZK bound unchanged, and my #306 notes are in the proof.
- **#316 (N1 option (b)) @ `373252e2`, covering the train head `ae9142fb`: GRANTED** for tonight's Lean train, taken
  at the coordinator's 20:22Z word.
  - `shared`, `Agree` and `aliased` are right, and dropping `hins` and `inj` only widens #207 and `rowsL1`.
  - At `ae9142fb`: the build succeeds and all 20 pins keep their type hashes; the audit with kernel replay passes
    (7,834 declarations, 20 pins, standard axioms).
  - C1, on claims: bind the committed zero, as a checklist row beside `hOne` or as `hZero` in #207.
  - Request: `internal/lanes/red-team-flock-3/20260928T1821Z-handoff-from-flock-soundness-316-n1-pin-review.md`.
  - Review: `private/red-team-reviews/pr316-n1-sources.md`, with `pr316-evidence.log`.
  - Reply: `lanes/flock-soundness/20260928T2035Z-answer-from-red-team-flock-3-316-verdict.md`, copied to
    `lanes/coordinator/20260928T2035Z-handoff-from-red-team-flock-3.md`.
- **#335 @ `f7dd8a53` (the Lean verifier reads #306's multi-table records, N4): GRANTED, no conditions,** taken at
  verity-root's 01:04Z word.
  - Each table is `setupH`'s statement of part j of the session's draw, split by the verifier's J.
  - Σ, `Hello`, the domains and the S-checks match #306.
  - The audit passes, 11 session-table tests pass, and J = 1 is unchanged.
  - #345's `circuitTypes` setting `manyTables := none` is right.
  - N1 for the coordinator: the merge order with the refinement stack, whose unmerged pins are stated over the old
    `Flock.verify` and `Setup`.
  - Request: `internal/lanes/red-team-flock-3/20260928T2155Z-handoff-from-flock-verifier-335-session-tables.md`.
  - Review: `private/red-team-reviews/m0-statement/pr335-session-tables.md`, with `pr335-evidence.log`.
  - Reply: `lanes/red-team-flock-3/20260929T0114Z-answer-from-red-team-flock-3-335-verdict.md`, copied to
    `lanes/coordinator/20260929T0114Z-handoff-from-red-team-flock-3.md`.
- **#362 @ `ad14e863` (the work draw law): all 13 new pins GRANTED,** taken at verity-root's 05:05Z word.
  - Covered: the work bound at both layers, the floor, Σ k_s ≤ K + m, the record sizing at 27,713 (27,712 short), the
    closure seam, and the `rfl` rule bridge.
  - Checks: both audits pass (soundness with kernel replay: 6,152 declarations, 32 pins); standard axioms.
  - C1 on the executable: `verify` accepts a work draw's stated work unless it holds its own table, program and
    partition.
  - Store: the record `art:63602bf7…` is labelled `verified=accepted` with `verifier` and `finding`; the per-pin
    `redteam-findings/v1` is `art:f791370e…`.
  - Review: `private/red-team-reviews/pr362-work-law.md`, with `pr362-evidence.log`.
  - Reply: `lanes/red-team-flock-3/20260929T0519Z-answer-from-red-team-flock-3-362-verdict.md`, copied to
    `lanes/coordinator/20260929T0519Z-handoff-from-red-team-flock-3.md`.
- **#362 @ `3bc3eba7` (C1 and X-SPC-80): all 13 pins RE-GRANTED,** at the work-law lane's 06:45Z request.
  - That request replaced the 05:34Z one at `fb1ab521`. Per verity-root's 06:31Z note, I checked `fb1ab521` but didn't
    grant it.
  - C1 is met: `verify` uses its own table, program and partition, checked at the top of `Stmt.setupTables`, and
    `setupH` is `main`'s. X-SPC-80 is met: `verify` uses its own K.
  - Checks: both audits pass (soundness with kernel replay: 7,954 declarations, 33 pins). The records are identical to
    the `ad14e863` grant, and the head merges cleanly onto `main` `84560ab7`.
  - The closure seam is stated truthfully. I agree with X-SPC-78: §12's condition isn't met, which is the closure PR's
    job.
  - Notes: N2, `PROTOCOL.md` §7.3 and the PR body overstate what carries; N3, compose through `audit_closure`, not
    `accountable_compute`; N1, the stratified follow-up's scope.
  - Store: the record `art:99d3b15d…` is labelled `verified=accepted` with `verifier` and `finding`; the findings are
    `art:852fd34f…`.
  - Requests: `internal/lanes/red-team-flock-3/20260929T0645Z-handoff-from-work-law-362-regrant-3bc3eba7.md`, and the one
    it replaced, `20260929T0534Z-handoff-from-work-law-362-c1-regrant.md`.
  - Review: `private/red-team-reviews/pr362-work-law-regrant.md`, with `pr362-regrant-evidence.log`.
  - Reply: `lanes/red-team-flock-3/20260929T0704Z-answer-from-red-team-flock-3-362-regrant-verdict.md`, copied to
    `lanes/coordinator/20260929T0704Z-handoff-from-red-team-flock-3.md`.
- **The influence stack: #375 @ `de831e06` (13 new pins), #378 @ `46b8faf9` (3) and #379 @ `ded605b1` (2), all GRANTED
  with no conditions.** This is the Flock red team's grant for soundness pins; the statements are bc-89770364's.
  - #375: the influence cap and count, the influence set, `audit_influence`, `twoStage_influence` with `AnchorsSound₂`,
    and the witness.
  - #378: the harm link, with `IsHarmBound` as core `harm_bound`'s specification.
  - #379: `audit_exfiltration` with the location term. `exfiltration_bound`'s `location_bits` reads it from above.
  - Checks: a full build, standard axioms, and `audit.py` with kernel replay passing at each head (33, 36 and 38 pins). No
    earlier record moves, and no definition read by any pin moved.
  - Notes: #375 N1, the witness header; #375 N2, what "delivered" covers; #378 N1, the trivial H in `Gen.harm_witness`.
  - Store: the records `art:a6d995f5…`, `art:c6e9f364…` and `art:f2e25bbd…`, each labelled `verified=accepted` with
    `verifier` and `finding`; the findings `art:e43927cf…`, `art:ed1bdbe4…` and `art:26e1d1cb…`.
  - Request: `internal/lanes/verity-root/20260929T0634Z-handoff-from-pous-influence-prs.md`.
  - Reviews: `private/red-team-reviews/influence/` (new): `pr375-influence.md`, `pr378-harm-link.md` and
    `pr379-exfiltration.md`, each with its evidence log.
  - Reply: `lanes/red-team-flock-3/20260929T0708Z-answer-from-red-team-flock-3-375-378-379-verdict.md`, copied to
    `lanes/coordinator/20260929T0708Z-handoff-from-red-team-flock-3.md`.
- **#379 @ `fa4fb58e` and #381 @ `d237e60a` (POUS's split of the `exfiltration_bound` change): grants re-recorded by
  byte identity** at verity-root's 07:30Z word. #375 and #378 stand.
  - #379: every Lean build and audit input is byte-identical to `ded605b1`, and its Python is back to #378's bytes.
  - #381: its tree is byte-identical to `ded605b1`.
  - Note: land #381 with #379.
  - Store: the record `art:f2e25bbd…` (the same bytes at all three commits) is labelled again for these heads; the
    findings are `art:67f124d4…`.
  - Request: `internal/lanes/verity-root/20260929T0722Z-handoff-from-pous-379-regrant-at-fa4fb58e.md`.
  - Review: `private/red-team-reviews/influence/pr379-381-byte-identity.md`.
  - Reply: `lanes/red-team-flock-3/20260929T0733Z-answer-from-red-team-flock-3-379-381-rerecord-verdict.md`, copied to
    `lanes/coordinator/20260929T0733Z-handoff-from-red-team-flock-3.md`.
- **#374 @ `d8c47f48` (the work law's count floor): held,** per the work-law lane's 06:45Z note. It is being amended to
  X-SPC-81, and a new request will replace
  `internal/lanes/red-team-flock-3/20260929T0603Z-handoff-from-work-law-374-count-floor-pin-review.md`. My checks at
  `d8c47f48` so far are in `private/red-team-reviews/pr374-count-floor-checks.md`.
- **The refinement lane's four pins restated over #335: all GRANTED,** at verity-root's 07:15Z word.
  - `rep_refines`: #264 @ `ff67422c`. `verify_refines` and `verify_tableAfter`: #270 @ `bdc4ec8b`.
    `verify_refines_ofCircuit`: #278 @ `1914b76d`.
  - Each is restated exactly as #335's one-table call forces; otherwise as granted.
  - The other refinement records are unchanged, so the R9c and R11 grants carry to `7003f003`, `3eaaf5e0`, `9ac97e23`
    and `41999484`.
  - Checks: audits pass with kernel replay at each head and at the top (47 pins).
  - Notes: N1, pinned for one-table sessions only; N2, R9c and above conflict with `main` in `HmRow.lean` (#345).
  - Store: the records `art:5d765ccd…`, `art:d8bdf3e6…` and `art:5078b4d3…`, each labelled `verified=accepted` with
    `verifier` and `finding`; the findings `art:70b33f98…`, `art:22e17169…` and `art:a8ce8b34…`.
  - Request: `internal/lanes/red-team-flock-3/20260929T0233Z-handoff-from-refinement-335-restated-pins.md`.
  - Review: `private/red-team-reviews/refinement/pr335-restated-refinement-pins.md`, with
    `refinement/evidence/pr335-restated-evidence.log`.
  - Reply: `lanes/red-team-flock-3/20260929T0742Z-answer-from-red-team-flock-3-335-restated-pins-verdict.md`, copied to
    `lanes/coordinator/20260929T0742Z-handoff-from-red-team-flock-3.md`.
- **#383 @ `2ad810cb` (the stratified law's K and strata from the verifier; no pin changes): GRANTED,** taken ahead of
  #374 and #390 at verity-root's 07:47Z word.
  - My N1 on #362 is met: `verify` holds a stratified draw to its own K, program and partition, and to its own
    derivation, at the top of `Stmt.setupTables`. `setupH` is `main`'s.
  - Checks: the verifier audit passes (14 pins); tests 19 passed, 1 skipped. The soundness package and records are
    unchanged. It merges cleanly onto `main` `610ee10f`.
  - Note: `subset` and `bernoulli` still take `k` and `p` from the record.
  - Store: the record `art:99d3b15d…` is labelled for #383; the findings are `art:dcdc4afe…`.
  - Request: `internal/lanes/red-team-flock-3/20260929T0748Z-handoff-from-work-law-383-stratified-k-strata-review.md`.
  - Review: `private/red-team-reviews/pr383-stratified-k-strata.md`, with `pr383-evidence.log`.
  - Reply: `lanes/red-team-flock-3/20260929T0750Z-answer-from-red-team-flock-3-383-verdict.md`, copied to
    `lanes/coordinator/20260929T0750Z-handoff-from-red-team-flock-3.md`.
- **#374 @ `594fe39c` (floors per stratum from the verifier's table, X-SPC-81): all pins GRANTED.** That is 10 new, 8
  restated with `hf` only, and `workRule_eq_draw` over the 5-argument rules. Removing `one_le_workK` is accepted.
  - My count-budget finding (at `d8c47f48`) is closed by removal: floors come only from the verifier's table, which
    `verify` holds.
  - Checks: the soundness audit passes with kernel replay (7,981 declarations, 42 pins); tests 18 passed, 1 skipped.
  - Store: the record `art:93b7a268…` is labelled `verified=accepted` with `verifier` and `finding`; the findings are
    `art:e43fc7c7…`.
  - Review: `private/red-team-reviews/pr374-floors.md`, with `pr374-floors-evidence.log`.
  - Reply: `lanes/red-team-flock-3/20260929T0752Z-answer-from-red-team-flock-3-374-verdict.md`, copied to
    `lanes/coordinator/20260929T0752Z-handoff-from-red-team-flock-3.md`.
- **#390 @ `15a3ee7c` (the closure law, X-SPC-78; reviewed against #362 as it stands): GRANTED WITH CONDITION C1
  before merge.**
  - All 10 pins are true. `closure_escape` is exact and covers undrawn node units.
  - C1: the audited unsound work omits the wrong units' own work under the verifier's non-reflexive closure map. I
    checked this in Lean. Fix: restate over `B ∪ unsoundTiles cl B`, with harm counting a unit's own work.
  - Checks: the soundness audit passes with kernel replay (7,969 declarations, 43 pins); tests 19 passed, 1 skipped.
  - Store: the record `art:1d2d224c…` is labelled `verified=accepted` with `verifier` and `finding`; the findings are
    `art:391c7c59…` (C1 blocking).
  - Review: `private/red-team-reviews/pr390-closure-law.md`, with `pr390-evidence.log`.
  - Reply: `lanes/red-team-flock-3/20260929T0755Z-answer-from-red-team-flock-3-390-verdict.md`, copied to
    `lanes/coordinator/20260929T0755Z-handoff-from-red-team-flock-3.md`.
- **#374 @ `6e39ccaa` (`594fe39c` with #383's `2ad810cb` merged in): the grant carries.**
  - The merge adds exactly #383's lines, adapted to the floor-carrying table type and U2's floor wording. The soundness
    package and both records are byte-identical to `594fe39c`.
  - Checks: the verifier audit passes (14 pins); tests 19 passed, 1 skipped. It merges cleanly onto `main` `610ee10f`.
  - Store: the record `art:93b7a268…` is labelled for `6e39ccaa`; the findings are `art:fdc1c60b…`.
  - Request: `internal/lanes/red-team-flock-3/20260929T0828Z-handoff-from-work-law-390-c1-floors-rereview.md`, part 1.
  - Review: `private/red-team-reviews/pr374-merge-383.md`.
  - Reply: `lanes/red-team-flock-3/20260929T0833Z-answer-from-red-team-flock-3-374-merge-verdict.md`, copied to
    `lanes/coordinator/20260929T0833Z-handoff-from-red-team-flock-3.md`.
- **#390 @ `a8b5d2a8` (C1 fixed; restated over #374's floors; new `workOf_le_unsoundWork`): all 11 closure pins
  GRANTED; C1 met.**
  - The unsound work is now the work of `B ∪ unsoundTiles`, and harm counts a unit's own work. I checked this in Lean.
  - The five audit-side pins gain only `f` and `hf`. #374's 42 records are byte-identical.
  - Checks: the soundness audit passes with kernel replay (7,998 declarations, 53 pins); tests 20 passed, 1 skipped.
  - Store: the record `art:d33e8c02…` is labelled `verified=accepted` with `verifier` and `finding`; the findings are
    `art:f476e0b1…`.
  - Request: `internal/lanes/red-team-flock-3/20260929T0828Z-handoff-from-work-law-390-c1-floors-rereview.md`, part 2.
  - Review: `private/red-team-reviews/pr390-c1-floors-rereview.md`, with `pr390-c1-floors-evidence.log`.
  - Reply: `lanes/red-team-flock-3/20260929T0841Z-answer-from-red-team-flock-3-390-regrant-verdict.md`, copied to
    `lanes/coordinator/20260929T0841Z-handoff-from-red-team-flock-3.md`.
- **#394 @ `971e8a7e` (`partsChecked` in `deriveChecked`; four pins' reads move): GRANTED.**
  - I read it from verity-root's bundle `internal/relay/pr394-971e8a7e.bundle`, which verified, because this VM's
    GitHub token is rejected (401 since about 08:45Z).
  - `compose_eval_unit`, `layout_sound`, `unit_sound` and `rowsL1` keep their statements, type hashes and named
    assumptions. Their hypothesis is strictly stronger (the same `done`, plus `partsChecked`).
  - Checks: the soundness audit passes with kernel replay (7,999 declarations, 33 pins); the 21 derive vectors pass the
    full check.
  - Note, resolved at 09:47Z: the 4 `test_flock_rows.py` pinned-template failures were this VM's environment. The
    `/workspace` venv I used has no torch. Under `uv run --locked --extra torch-cpu` (torch 2.14.0+cpu), all four ran and
    passed at `main` `e5694c92`.
  - Store: the record `art:41b15fac…` is labelled `verified=accepted` with `verifier` and `finding`; the findings are
    `art:9a645ed3…`.
  - Request: `internal/lanes/red-team-flock-3/20260929T0902Z-handoff-from-flock-soundness-394-parts-checked-pin-review.md`.
  - Review: `private/red-team-reviews/pr394-parts-checked.md`, with `pr394-evidence.log`.
  - Reply: `lanes/red-team-flock-3/20260929T0939Z-answer-from-red-team-flock-3-394-verdict.md`, copied to
    `lanes/coordinator/20260929T0939Z-handoff-from-red-team-flock-3.md`.
- **R9c and R11 on `main` `610ee10f` (#291 @ `2437e377`, #296 @ `4d226ad1`, #302 @ `377f7d26`, #310 @ `e9ca3ba2`): all
  four GRANTED, with no granted statement moved.** I read them from verity-root's bundle, which verified.
  - Every pin record is `main`'s or my grant's.
  - The six changed `.lean` files: the `HmRow.lean` `pin` union (#282's refusals on #345's `pin`); git's automatic merge
    for `Statement.lean` and `FlockSoundness.lean`; and proof-only edits to `check_facts`, `pin_spec` and the hm96 walk.
  - Each R11 head, and R9b's `115fffc5`, is exactly git's automatic merge of its parents.
  - Checks: the audits pass with kernel replay (42, 43, 46 and 48 pins).
  - Store: the records `art:012b0e8d…`, `art:72153754…`, `art:0991fcbe…` and `art:53e33e5e…`, each labelled; the findings
    `art:060edb22…`, `art:6142aa64…`, `art:9ef2942c…` and `art:589b888f…`. `art:b6a7bf01…` is superseded (a draft
    payload).
  - Request: `internal/lanes/red-team-flock-3/20260929T0945Z-handoff-from-refinement-r9c-r11-on-main-recheck.md`.
  - Review: `private/red-team-reviews/refinement/r9c-r11-on-main-recheck.md`, with
    `refinement/evidence/r9c-r11-on-main-evidence.log`.
  - Replies: `lanes/red-team-flock-3/{20260929T1005Z-…-291,20260929T1010Z-…-296,20260929T1016Z-…-302,20260929T1022Z-…-310}-on-main-verdict.md`,
    each copied to `lanes/coordinator/<stamp>-handoff-from-red-team-flock-3-<pr>.md`.
- **#402 @ `38d9be9a` (`Law.stratified_miss_eq_greedy`): GRANTED.** A τ-separated count vector attains the stratified
  `miss`. `main`'s 51 records are unchanged, and the audit passes with kernel replay (52 pins).
  - N1 for #396's exporter: certify separation exactly, not in float order.
  - Store: the record `art:606e3c23…` is labelled; the findings are `art:a24132ad…`.
  - Request: `internal/lanes/verity-root/20260929T1012Z-handoff-from-pous-402-stratified-miss.md`.
  - Review: `private/red-team-reviews/pr402-stratified-miss.md`.
  - Reply: `lanes/red-team-flock-3/20260929T1040Z-answer-from-red-team-flock-3-402-verdict.md`, copied to
    `lanes/coordinator/20260929T1040Z-handoff-from-red-team-flock-3-402.md`.
- **#392 @ `8628dd4a` (the witnesses `Two.influence`, `Two.accepts`, `Ex.exfil`): GRANTED.** They show satisfiability, as
  stated, and the header now says so (my #375 N1). #381's 38 records are unchanged, and the audit passes with kernel
  replay (41 pins).
  - Store: the record `art:966f1932…` is labelled; the findings are `art:ad414d81…`.
  - Request: `internal/lanes/coordinator/20260929T0823Z-handoff-from-pous-t8-crosscheck-and-392.md`.
  - Review: `private/red-team-reviews/pr392-witnesses.md`, with `pr402-392-evidence.log`. Both PRs came from verity-root's
    bundle.
  - Reply: `lanes/red-team-flock-3/20260929T1046Z-answer-from-red-team-flock-3-392-verdict.md`, copied to
    `lanes/coordinator/20260929T1046Z-handoff-from-red-team-flock-3-392.md`.
- **#404 @ `bf36d2b2` (two more `partsChecked` conjuncts: the constant row and the order's columns): GRANTED.**
  - The same four pins' reads move (`partsChecked` only), and each hypothesis is strictly stronger.
  - Honest units pass: 21 derive vectors, and `test_flock_rows.py` under `uv --locked --extra torch-cpu` (13).
  - Checks: the soundness audit passes with kernel replay (8,003 declarations, 33 pins).
  - Store: the record `art:c8e66b03…` is labelled; the findings are `art:d915604f…`.
  - Request: `internal/lanes/red-team-flock-3/20260929T1054Z-handoff-from-flock-soundness-404-unit-shape-pin-review.md`.
  - Review: `private/red-team-reviews/pr404-unit-shape.md`, with `pr404-evidence.log`. From verity-root's bundle.
  - Reply: `lanes/red-team-flock-3/20260929T1104Z-answer-from-red-team-flock-3-404-verdict.md`, copied to
    `lanes/coordinator/20260929T1104Z-handoff-from-red-team-flock-3-404.md`.
- **#408 @ `b2f8db97` (`Law.subset_exec_escape_le`, the executable subset sampler): GRANTED WITH C1 before merge.**
  - The statement is right: the unchanged executable over uniform bytes, with running out counted as no escape. `main`'s
    60 records are unchanged, and `meaning` gains `Flock.Draw`.
  - C1: `test_audit_layer_is_abstract` fails, because `DrawExec.lean` imports `Flock.Draw` under `Audit/`. Rename it as a
    Flock instantiation or move it, then re-record.
  - Checks: the soundness audit passes with kernel replay (8,233 declarations, 61 pins).
  - Store: the record `art:cd05a6a2…` is labelled; the findings are `art:7317b252…` (C1 blocking).
  - Request: `internal/lanes/verity-root/20260929T1158Z-handoff-from-pous-408-exec-sampler.md`.
  - Review: `private/red-team-reviews/pr408-exec-sampler.md`, with `pr408-evidence.log`. From verity-root's bundle.
  - Reply: `lanes/red-team-flock-3/20260929T1211Z-answer-from-red-team-flock-3-408-verdict.md`, copied to
    `lanes/coordinator/20260929T1211Z-handoff-from-red-team-flock-3-408.md`.
- **#408 @ `a726a443` (C1 fix), a delta over the `b2f8db97` grant: CONFIRMED to verity-root.**
  - `ExecDraw.lean` is byte-identical to the old `Audit/DrawExec.lean`, and `test_audit_layer_is_abstract` passes.
  - The pin and its record are byte-identical. `main` `0c444ee2` merged in, and its 90 records are unchanged.
  - Keyed draws are out of scope, as granted.
  - Checks: the soundness audit passes with kernel replay (9,544 declarations, 91 pins).
  - Store: the record `art:1eaa945a…` is labelled; the findings are `art:15e10dd4…`.
  - Request: `internal/lanes/verity-root/20260929T1245Z-handoff-from-pous-408-c1-fixed.md`.
  - Review: `private/red-team-reviews/pr408-delta-a726a443.md`. I replied to verity-root directly, as asked, with no
    verdict file.
- **#411 @ `c2c4a938` (`partReadsOk` in `partsChecked`; the same four pins' reads move): GRANTED to verity-root.**
  - Each hypothesis is strictly stronger, flat units are untouched, and honest units pass (derive vectors including
    placed reads, and `test_flock_rows` under uv `torch-cpu`).
  - Checks: the soundness audit passes with kernel replay (8,014 declarations, 33 pins).
  - Store: the record `art:f50994e5…` is labelled; the findings are `art:40a42115…`.
  - Request: `internal/lanes/coordinator/20260929T1301Z-handoff-from-flock-soundness-411-pin-review-for-red-team.md`.
  - Review: `private/red-team-reviews/pr411-part-reads.md`. I replied directly, as asked.
- **#412 @ `e1081cc5` (tier-3: the executable stratified draw, and the e2e theorems at its law): GRANTED to
  verity-root.**
  - `stratified_exec_escape_le`'s bridge, `ExecStrata`, is explicit. `flock_e2e_drawn_exec` does not depend on the law;
    `flock_e2e_count_exec` does, through `ExecStrata`.
  - #408's 91 records are byte-identical, and the reads cover `Flock.Draw`.
  - Note: `execStratified` draws every unit on a run-out, where the live verifier refuses; refusal only lowers
    Pr[accept].
  - Checks: the soundness audit passes with kernel replay (9,567 declarations, 94 pins).
  - Store: the record `art:51ba939d…` is labelled; the findings are `art:10027a23…`.
  - Request: `internal/lanes/verity-root/20260929T1330Z-handoff-from-pous-412-flock-grant-request.md`.
  - Review: `private/red-team-reviews/pr412-exec-stratified.md`. I replied directly, as asked.
- **#412 @ `da1e703a` (pins `execStratified_escape_le`), a delta over the `e1081cc5` grant: CONFIRMED to verity-root.**
  - The new pin is the statement I read at `e1081cc5`, with explicit `ExecStrata` and no named assumption.
  - Every other record is byte-identical; the delta is 21 lines.
  - Checks: the audit passes with kernel replay (9,567 declarations, 95 pins).
  - Store: the record `art:a8b348a5…` is labelled; the findings are `art:ecafbf8b…`.
  - Request: `internal/lanes/verity-root/20260929T1426Z-handoff-from-pous-412-delta-414.md`.
  - Review: `private/red-team-reviews/pr412-delta-da1e703a.md`.
- **`Audit/Window.lean` statements, before proof (7 pins; X-SPC-105's window half, X-SPC-106): I would GRANT as
  stated.**
  - The statements elaborate on `main` `9ac48ce8` with `sorry` bodies. Exact checks on small instances find no
    counterexample to the four covering lemmas.
  - The cap finding is stronger than drafted. The handoff's example breaks `Covers` but not the bound. In a window at
    K ≤ N, a binding cap on a call with two work strata makes the bound fail by 651×. #364 should refuse such calls in
    code.
  - I recommend pinning the composed per-call claim at 27,713, which #364 cites. It is a term proof from the draft's
    pins.
  - Request: `internal/lanes/pous/20260929T1608Z-handoff-from-verity-root-window-pin.md`.
  - Verdict: `internal/lanes/pous/20260929T1622Z-redteam-window-pin-statement.md`. Evidence:
    `private/red-team-reviews/window-pin-evidence.log` and `window-pin-check.py`.
- **#416 @ `8aed7908` (live `drawOS` bound, A3 `uniform/io-getrandombytes`): GRANTED to verity-root.**
  - #412's 95 records are byte-identical. The 6 new pins are right, and A3 is a named hypothesis that is satisfiable.
  - `drawOS_def` ties the executable as far as Lean can.
  - At `IO`, the refactor makes the same calls in the same order. A differential test found 0 mismatches over 7,257
    source calls, 5,089 of them extensions.
  - Checks: the audit passes with kernel replay (9,657 declarations, 101 pins).
  - POUS's correction is accepted: the live draw never refuses; only `draw --stream` does.
  - Notes, not conditions: Lean's docstring disclaims cryptographic security, while the v4.34.0 runtime reads
    `/dev/urandom`, and the watch entry can't see the C implementation.
  - Request: `internal/lanes/verity-root/20260929T1618Z-handoff-from-pous-416-drawos-grants.md`.
  - Verdict: `internal/lanes/pous/20260929T1656Z-redteam-416-drawos.md`. Evidence:
    `private/red-team-reviews/pr416-drawos-evidence.log` and `pr416-drawdiff.lean`.
- **#418 @ `f06327bd` (the window pins, 9): GRANTED to verity-root.**
  - The statements are the ones I reviewed, plus two changes: the y event reads `unsoundWork σ v cl` (in three of the
    seven, plus the 8th), and POUS's `audit_window_of_le` is new.
  - Checks: `main`'s 94 records are byte-identical; the audit passes with kernel replay (9,945 declarations, 103 pins).
  - Request: `internal/lanes/red-team-flock-3/20260929T1647Z-handoff-from-work-law-418-window-pin-grant.md`.
  - Verdict: `internal/lanes/pous/20260929T1702Z-redteam-418-window-pins.md`. Evidence:
    `private/red-team-reviews/pr418-window-pins-evidence.log`.
- **Queued (verity-root 07:36Z):** #374 @ `594fe39c` and #390 @ `15a3ee7c`, both done above. The requests are
  `internal/lanes/red-team-flock-3/20260929T0710Z-handoff-from-work-law-374-floors-pin-review.md` and
  `20260929T0734Z-handoff-from-work-law-390-closure-pin-review.md`.

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
