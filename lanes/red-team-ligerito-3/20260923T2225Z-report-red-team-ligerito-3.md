---
lane: red-team-ligerito-3
kind: report
created: 2026-09-23T22:25Z
status: open
branch: lane/red-team-ligerito-3 (worktree ~/projects/verity-main-wt/red-team-ligerito-3, from lane/red-team-ligerito-2 @ 83d5d75)
---

CHECKPOINT none (23:17Z) [open] 23:19Z: verify-rs-3 75ec753f (own build): R3-1 FIXED (legacy -> claimed null, batch problem), zk_mode label (R3-6 verifier side); all Rust-side findings closed; Rust LGSC0004 dispatch unreachable with pinned keys. Open: R3-7 BLOCKING live claim (relation-2), R3-2 Python t_pad:0, R3-8 Python word widths, R3-9 weak neg 46, R3-10 (+abort-and-retry), R3-6 prover, R3-4/R3-5; ZK column blocked (LGSC0004 not emitted). FINAL draft current in report. Watching lanes until ~00:20Z.
CHECKPOINT none (23:15Z) [open] 23:15Z: verify-rs-3 2dfbb90a (own build): R3-2 + R3-3 FIXED in Rust (5/5 framing incl. t_pad:0, pad_a/pad_b at statement stage; six 32d3d42 dumps 2/2, 90/90). Python 32e9bd59 still takes framing "t_pad":0 (parses to identical proof) -> R3-2 PARTIAL, fixture framing_malleability_fp8-ada_32d3d42 (aeae420f). sumcheck-3 19b58309 13 coins: bound 184/|F| unchanged, _fm_big OK, R3-6 open. FINAL drafted in report; open: R3-7 BLOCKING (live claim), ZK column blocked (LGSC0004 not emitted, LGTO0001 refuses). Next: watch lanes to ~00:20Z.
CHECKPOINT none (23:09Z) [open] R3-7 confirmed (87fe4faa redteam_live_labels.py: ground label / extra commitment accepted by relation-2 _file_coins, slots never issued) -> BLOCKING for live claim. relation-2 32e9bd59: R3-2 FIXED in Python (8/8 framing re-encodings rejected), R3-3 FIXED in Python. verify-rs-3 60d9cbd1 (own build): off-end y FIXED; framing 4/4 still accepted (R3-2 open in Rust); pad-unit a/b no rule (their neg 46 = honest proof + edited stmt, passes Rust for the wrong reason: R3-9). R3-8 Python verify does not pin word_bytes/y_bytes (Rust does). R3-10 verify-session n_proofs from manifest. Handoffs 2310Z relation-2, 2312Z verify-rs-3.
CHECKPOINT none (23:01Z) [open] 23:01Z: new R3-7 candidate (BLOCKING for the live 2^-128 claim): relation-2 run.py verify_session re-derives coin slots with the MANIFEST's stream_binding.labels/commitments, never compared to the verifier's recorded rd['label'] / R commitments -> prover can grind labels after seeing r_k (FS-level soundness under an interactive claim). Next: CPU demo, then verify relation-2 32e9bd59 (R3-2/R3-3) and verify-rs-3 60d9cbd1 (off-end y) against my fixtures.
CHECKPOINT none (22:58Z) [open] Correction: off-end y malleability is REAL (end constraint masked; relation-2 0db857a9 now rejects at statement stage; Rust e2037b58 does not -> will disagree on relation-2's new negative). Handoffs to relation-2/verify-rs-3 corrected; fixture labels fixed 3575161c. Report updated with ef49a7de (15 coins, 184/|F|=2^-177.9, FS max term tau 30/|F|), e2037b58 lgsc4 review (no finding, fail-closed in LGTO0001), R3-6 prover vf<=n_c-4 not enforced. Next: re-check lanes ~23:30Z/00:00Z, FINAL by 00:30Z.
CHECKPOINT none (22:56Z) [open] Lanes moved: sumcheck-3 ef49a7de coin-lean LGSC0004 (15 coins, arity<=6, vf<=12): mask check extended to arity 6 OK; bound fp8-ada zc 3,2,2,2,2,3,6/vf10/cmb 3,3,6,6/rb 6,6 = 184/|F| = 2^-177.9; FS max per-coin term is tau n/|F| = 30/|F| (not 9/|F|): Q <= 2^52.5; NIT R3-6: prover enforces vf <= n_c only (ZK tables need vf <= n_c-4) for non-default schedules. verify-rs-3 c049225c/b01afda3/e2037b58: lgsc4.rs + sparse PCS claims reviewed (schedule sums, vf<=n_c, g-cell budget, ZK rows verifier-derived, cells/weights verifier-built, absorbed before beta); LGTO0001+LGSC0004 fails closed. relation-2 0db857a9 F5 sizing.
CHECKPOINT none (22:53Z) [open] Handoffs written: verify-rs-3 (2255Z: V1 FIXED a8a08eb, R3-1 allow-legacy labels, R3-2 framing malleability + fixtures, LGSC0004 reader gap), relation-2 (2300Z: V1 FIXED all 6 relations, R3-2, R3-3 pad-unit words, LGSC0004 adoption checklist incl. g-row overlap), sumcheck-3 (2305Z: design OK, _fm OK, bound 2^-177.8, R3-4 ZK-arg gap, R3-5). ecd69d40 framing fixtures. Reader fuzz 43,801 flips 0 accepted. Report body rewritten; FINAL pending lane re-check.
CHECKPOINT none (22:46Z) [open] ba087855 on lane/red-team-ligerito-3: mask check + stmt-tamper fixture generator; fixtures/stmt_tamper_{fp8-ada_e3ad950,fp4-nvf4_32d3d42} 14/14 rejected (batch --dir OK). zero_claims_test 3/3 (swapped-bit caught with r_c). LGSC0004 ZK argument + soundness 196/|F| = 2^-177.8 re-derived OK; tensor-claim merge -> 172/|F|, 18 coins, PCS term unchanged. Integration hazards: RowMaskLayout default sumchecks use g cells [0,762) = LGSC0004 coefficient cells; zero claims not in ligerito-zk's ZK argument. Writing handoffs + FINAL.
CHECKPOINT none (22:41Z) [open] Own release build a8a08eb (sha b91e25ed): 11 dumps (6 relations @32d3d42 incl. newly pinned bf16-ampere + fp4-nvf4, 3 @e3ad950, 2 bench 4096) all accept honest / reject 90/90; V1 06-10 rejected on every relation (PCS r1 / combined final). zero-claim values hardcoded 0. _fm (f0b9567) == schoolbook mod X^6-31. Statement edits (non-end y, pad a/b/y, end y) rejected; non-end y is forced 0 by end constraint (retract that half of NIT). New NIT: --allow-legacy batch reports union -128/claimed -64.7, problems [] for pre-V1 proofs. Rust has no LGSC0004 path. Next: coin bound, handoffs, FINAL.
CHECKPOINT none (22:35Z) [open] LGSC0004 ZkMask ported to pure-Python BabyBear check (redteam_lgsc4_mask.py): arity 1-4, eq+avg: sum-zero, bind, image == ker(round check) rank 3^v-1 (per-variable Libra leaves 4/20/72 coords); whole-mask n=9 brute force eq-sum 0. New lane heads: relation-2 e3ad950, verify-rs-3 a8a08eb (bf16-ampere + fp4-nvf4 pinned), sumcheck-3 f0b9567. Next: rebuild release at a8a08eb, rerun all gate dumps, review f0b9567.
CHECKPOINT 83d5d75 (22:32Z) [open] V1 FIXED for LGSC0003 in Python+Rust (release 02db242 rejects V1 06-10 on 4 pinned relations); LGSC0004 mask design OK on paper; next: Rust lgto pcs_verify review
CHECKPOINT 83d5d75 (22:35Z) [open] V1 FIXED (LGSC0003, Python + Rust): verifier derives blocks from its own layout/pinned key, rejects params mismatch; reconstruction set == covered set in both; release binary 02db242 (sha 885c490b) accepts honest, rejects 90/90 incl. V1 06-10 on fp8-ada/fp8-ada-zk/bf16-hopper/fp8-hopper; bf16-ampere/fp4 refused (no pin). LGSC0004 masks: degree/commit order/sum-zero OK on paper. Next: Rust lgto pcs_verify review, LGSC0004 numpy checks.
CHECKPOINT 83d5d75 (22:25Z) [open] started; relaunch brief §0/§3, ligerito brief §9, red-team-ligerito FINAL, red-team-ligerito-2 V1 handoff, verify-rs-2 FINAL read. Targets landed: relation-2 cf9a63a/32d3d42, verify-rs-3 339d910..02db242, sumcheck-3 c675bd5. Next: V1 fix review (cover per class, swapped-bit, ZK index map).

# red-team-ligerito-3: V1 fix, LGTO0001 reader, LGSC0004 ZK masks, coin reduction

No pod ($0). Laptop CPU only: no torch (coordinator rule), so Python-side evidence is the gate dumps' recorded
`python_verdict`s plus numpy/pure-Python re-implementations. Rust evidence is my own release build. One worktree
(`~/projects/verity-main-wt/red-team-ligerito-3`), one Rust target dir (`/tmp/rtl3/target`).

## Log

* 22:20Z start; briefs + predecessors read; worktree at 83d5d75.
* 22:25-22:32Z V1 fix review (relation-2 cf9a63a/32d3d42, Python `proof.py`/`prove.py`; Rust `lgto.rs`/`relation.rs` at
  02db242). Release 02db242 (sha256 885c490b…) over the 32d3d42 gate dumps: 4 pinned relations pass; bf16-ampere / fp4-nvf4
  were still refused (no pin at 02db242).
* 22:35Z LGSC0004 mask algebra re-implemented (`redteam_lgsc4_mask.py`); lanes moved: relation-2 e3ad950, verify-rs-3
  a8a08eb (bf16-ampere d42489c + fp4-nvf4 c54db0f pinned, V1 regression fixture d312ec4), sumcheck-3 f0b9567.
* 22:36-22:41Z own release build of a8a08eb (`git archive` → `cargo build --release --offline`, sha256 b91e25ed…, snapshot
  `/tmp/rtl3/ligerito-verify-a8a08eb`), all 11 dumps rerun; `_fm` checked; statement tampers; `--allow-legacy` labels.
* 22:46Z committed ba087855; LGSC0004 ZK argument and soundness table re-derived; relation-2 `RowMaskLayout` g-row overlap.
* 22:47-22:50Z LGTO0001 reader fuzz: framing-JSON re-encodings accepted (both readers); 43,801 single-bit flips, 0 accepted.
  Committed ecd69d40.
* 22:52-22:54Z handoffs to verify-rs-3 (…T2252Z), ligerito-relation-2 (…T2253Z), ligerito-sumcheck-3 (…T2254Z).
* 22:55-23:00Z lanes moved again: sumcheck-3 ef49a7de (LGSC0004 coin-lean, 15 coins, arity ≤ 6, vf ≤ 12), verify-rs-3
  c049225c/b01afda3/e2037b58 (lgsc4.rs, sparse PCS claims), relation-2 0db857a9 (F5 sizing, live-session claims,
  off-end y canonical). Mask check extended to arity 6 (696a577a); handoff addenda; the 0db857a9 message shows my
  "retraction" of the off-end y NIT was wrong (corrected below, fixture labels fixed in 3575161c).
* 23:00-23:09Z relation-2 0db857a9 `verify-session` reviewed: R3-7 (live coin slots re-derived from the dump's own
  labels / commitments). Pure-Python demo on the committed code (87fe4faa). Lanes moved: relation-2 32e9bd59 (R3-2 framing,
  R3-3 pad-unit words, both Python-side), verify-rs-3 60d9cbd1 (off-end y). Own release build of 60d9cbd1
  (`/tmp/rtl3/ligerito-verify-60d9cbd1`) over relation-2's 32e9bd59 gate dumps (bf16-ampere, bf16-hopper: 2/2, 94/94, V1
  06-10 10/10 rejected), my framing and statement fixtures. Python 32e9bd59 `read_proof` run with numpy only. Handoffs
  ligerito-relation-2 …T2308Z, verify-rs-3 …T2309Z (the 23:09Z checkpoint called them 2310Z / 2312Z; renamed to the actual
  time).
* 23:10-23:14Z lanes moved: verify-rs-3 2dfbb90a (R3-2 + R3-3 in Rust), sumcheck-3 19b58309 (13-coin default, `_fm_big`).
  Own release build of 2dfbb90a: my framing (5 incl. `"t_pad":0`) and statement fixtures all rejected at the right stage; six
  32d3d42 gate dumps 2/2 and 90/90 each. Python 32e9bd59 still takes `"t_pad":0` (parses to the identical proof). `_fm_big`
  numpy port OK. Addenda to all three handoffs; commit aeae420f.
* 23:16-23:18Z verify-rs-3 75ec753f (R3-1 legacy labels, R3-6 `zk_mode` label): own build. Legacy fixture → claimed null,
  batch problem; `zk_mode` partial / none as expected; six dumps pass. Rust LGSC0004 dispatch (60d9cbd1) reviewed:
  reachable only under a ZK-layout key, none pinned. R3-10 extended (abort and retry).
* 23:28Z lanes moved: sumcheck-3 62f24d42 (zc 3,3,3,3,3,5 / vf 10 / cmb 6,6,6 / rb 6,6 = 13 coins: 20 zero-check variables,
  arity ≤ 6, so the bound is still 184/|F|; `zc_msg3` is a prover kernel). verify-rs-3 889343d2 / 732e5d5f
  (`read_proto_commit_first` + `pcs-sparse --file` cross-check of sparse PCS claims against Python): a separate subcommand and
  tests only, not reachable from `verify` / `batch`. No finding.

## Item 1: V1 fix on lane/ligerito-relation-2 (cf9a63a..e3ad950): **FIXED** (LGSC0003, all six relations)

* Mechanism: zero claims `w~(r_i[:b] || bits(pfx) || r_c) = 0` on the aligned cover of every run of virtual rows; the
  verifier recomputes `zero_blocks` from its own `lay.virt` and rejects a mismatching `params.zero_blocks`;
  `n_claims = 1 + n_links + |zero_blocks|`. The values are 0 by construction and never read from the proof. The cover
  equals the set the verifier reconstructs from public data (every class: const, link, start, end, y16 / y_end0..2, pub:*,
  next:*).
* Swapped-bit: relation-2's `zero_claims_test.py::test_zero_claim_columns_must_be_independent` (+d at (3584, col 64),
  −d at (3648, col 0)) vanishes on rho columns and is caught on r_c; 3/3 pass on my laptop. Generally a nonzero committed
  delta on a block survives only if its (b + n_c)-variate multilinear vanishes at the independent (r_i[:b], r_c):
  ≤ (b + n_c)/|F|, since w is bound by root_1 before those coins. Adaptive forger: the claim value cannot be chosen (fixed 0);
  the block list cannot be shrunk (layout-derived); params JSON cannot be double-keyed (Rust canonical check).
* Evidence per relation, gate dumps @32d3d42 (fp8-ada, fp8-ada-zk, bf16-hopper, fp8-hopper, bf16-ampere, fp4-nvf4) and
  @e3ad950 (fp8-ada, fp8-ada-zk, bf16-hopper): python_verdict rejects 06-10 (06-09 "PCS sumcheck round 1 failed", 10
  "combined final") and the Rust release agrees 92/92 on each. Re-checked at 32e9bd59 (bf16-ampere, bf16-hopper gate dumps,
  Rust 60d9cbd1): 06-10 rejected 10/10 each, 94/94 negatives.

## Item 2: Rust side on lane/verify-rs-3 (1f30710..2dfbb90a): **FIXED** (LGSC0002/3), **LGSC0004 fail-closed in LGTO0001**

~~~text
ligerito-verify a8a08eb (own build, sha256 b91e25ed…)     honest   negatives   V1 06-10
gates-32d3d42: fp8-ada, fp8-ada-zk, bf16-hopper,           2/2      90/90       rejected (06-09 PCS r1 "message 0",
  fp8-hopper, bf16-ampere, fp4-nvf4                                             10 combined final), both coin kinds
gates-e3ad950: fp8-ada, fp8-ada-zk, bf16-hopper            2/2      90/90       same
bench-abd8f5e: fp8-ada 4096 local / live-localstream       1/1      -           -
ligerito-verify 60d9cbd1 (own build)
gates-32e9bd5: bf16-ampere, bf16-hopper                    2/2      94/94       rejected 10/10 (same stages)
ligerito-verify 2dfbb90a (own build)
gates-32d3d42: all six relations                           2/2      90/90       rejected (same stages)
~~~

Static: `relation.rs:431-440` (value `Ext::ZERO`), `lgto.rs:1123-1140` (blocks from the pinned key; `n_claims`
recomputed; a missing list is refused unless `--allow-legacy`), `lgto.rs:478-489` (params canonical). Statement: words
range-checked; off-end y must be 0 since 60d9cbd1; word widths pinned (`lgto.rs:1162`); pad-unit operand words must be 0
and the framing must be the writer's exact bytes since 2dfbb90a (R3-2 / R3-3 Rust halves closed). At a8a08eb `lgto::verify` dispatched
LGSC0002/LGSC0003 only. e2037b58 adds `lgsc4.rs` + sparse PCS claims (reviewed statically: schedule sums, `vf ≤ n_c`,
g-cell budget, ZK rows verifier-derived, sparse cells and weights verifier-built and absorbed before β, α-scaled and folded
like proto's `_Sparse`). Since 60d9cbd1, LGTO0001 dispatches LGSC0004 exactly when the key's layout has links but no
`next:*` virtual row (`is_zk_layout`, `lgto.rs:1132`). It then requires the ZK PCS, `n_claims = 2 + |zero_blocks|`, and
LGSC0004 magic; LGSC0004 under a non-ZK key is refused (l.1262). No pinned key is a ZK layout (every gate key, fp8-ada-zk
included, names `next:0..2`), so the path is reachable only with `--allow-any-key` (flagged unpinned). It is fail-closed in
practice and provisional until relation-2 emits LGSC0004.

## Item 3: LGSC0004 ZK masks on lane/ligerito-sumcheck-3 (c675bd5, f0b9567): **design OK; not deployed**

* Degree: every monomial of degree ≤ 2 per variable, 3^v − 1 coefficients per round group (v ≤ 4). Pure-Python check
  (`redteam_lgsc4_mask.py`): sum-zero, bind (K update), and image of `c → M − K·1` = kernel of the round check with rank
  3^v − 1 at v = 1..4 in both kinds. The old per-variable Libra mask reaches rank 2v and leaves 0/4/20/72 witness coordinates
  clear (F3). Whole-mask brute force n = 9: Σ eq·ĝ = 0, ĝ(r) = K_final.
* Commit order: the coefficients are g-row cells of w, bound by root_1 before `zc/tau` and all round coins; masks are
  rebuilt per proof.
* Soundness: masks add no term (sum-zero identically in the coefficients, per-variable degree kept, K checked through a PCS
  sparse claim). Re-derived 196/|F| = 2^-177.8.
* ZK: their §1 argument checks out step by step (messages uniform on the acceptance hyperplane, tables blinded by the product
  triple, values blinded by U / M, T and K solved from the final checks). Gap R3-4: the zero claims and g-row sparse claims
  are outside ligerito-zk's "fully-extension eval claims" argument.
* f0b9567 `_fm`: equal to schoolbook mod X^6 − 31 (numpy port, 2,005 pairs incl. p − 1); int64 bound 2^41.
* ef49a7de coin-lean default (arity ≤ 6, vf ≤ 12): masks checked at v = 5, 6 (rank 242/242, 728/728; 696a577a);
  `ZK_CELLS_PER_VAR = 6·122` covers any arity-6 schedule. The default keeps `vf ≤ n_c − 4` (≥ 16 product-row cells per
  final-table entry, as the table-blinding step needs), but `prove` accepts any `vf ≤ n_c` (R3-6).
* Deployment: relation-2's `--zk` is still LGSC0003 + the old masks (F3) + an unenforced product triple, labeled
  `zk_partial` since 32d3d42. No Rust reader.

## Item 4: coin reduction: **ef49a7de (wider rounds, 21 → 15 coins); bound recomputed, OK**

* The rows ↔ PCS round-1 merge saves 0 coins in LGSC0003 (the shift forces 18 combined variables = 6 coins). Not done.
* LGSC0004 at f0b9567: 21 coins (+3 row reduction), 196/|F| = 2^-177.8.
* ef49a7de reduces coins by widening rounds, not by merging. fp8-ada default zc 3,2,2,2,2,3,6 / vf 10 / cmb 3,3,6,6 /
  rb 6,6 = 15 coins: τ 30 + zc 3·20 + tables vf+2 = 12 + shift at r_c 18 + g3/β 4 + cmb 2·18 + rb 2·12 = **184/|F| =
  2^-177.9** (interactive). The PCS term (2^-128.017) is unchanged, since the claim set is unchanged.
* FS: the largest per-coin sumcheck error is the τ draw, 30/|F| (sumcheck-3's §2 used 9/|F|), so Q ≤ 2^52.5 on the sumcheck
  side. The honest FS label stays 64 + the largest PCS term ≈ 2^-64.66.
* 19b58309 default 13 coins (zc 3,2,3,3,3,6 / vf 10 / cmb 6,6,6 / rb 6,6): same variables per sumcheck and same degrees, so
  still **184/|F| = 2^-177.9**. Max arity 6 (masks checked). FS max per-coin term τ 30/|F|. `_fm_big` equals schoolbook
  (numpy port, 4,000 pairs).
* sumcheck-3's optional tensor claim (not implemented) would drop the row reduction: −2 coins at the coin-lean schedule
  (−3 at zk-small), 160/|F|, same J. Condition: the PCS verifier builds `s_w~(ρ*_i)·eq(ρ_c, ρ*_c)` itself.

## New findings

~~~text
id     sev                    where                               status (23:18Z)
R3-1   NIT                    verify-rs-3 lgto/main batch         FIXED 75ec753f: pre-V1 under --allow-legacy -> claimed null, out of the union, batch problem
R3-2   NIT                    proof.py:420 / lgto.rs:548          PARTIAL: Rust FIXED 2dfbb90a (5/5); Python 32e9bd59 rejects 4/5, still takes an explicit "t_pad":0
R3-3   NIT                    _stmt_subs / StmtRows::validate     FIXED: off-end y (0db857a9, 60d9cbd1); pad-unit a/b (32e9bd59, 2dfbb90a)
R3-4   NIT (argument)         sumcheck-3 §1 (a) / ligerito-zk     open: ZK argument does not cover zero claims / g-row sparse claims (no leak expected)
R3-5   NIT (integration)      relation-2 RowMaskLayout default    open: old mask sumchecks occupy g cells [0,762) = LGSC0004's first coefficient cells
R3-6   NIT (prover ZK)        sumcheck-3 prove / zk_schedule      PARTIAL: prove still accepts vf in (n_c-4, n_c]; Rust 75ec753f labels it zk_mode lgsc0004-underblinded
R3-7   BLOCKING (live claim)  relation-2 run.py _file_coins /     NEW: slots re-derived from the dump's own stream_binding labels/commitments, never
                              verify_session                      compared with the verifier's record: label grinding after r_k (FS-level) under the interactive claim
R3-8   NIT                    relation-2 prove.py:1089            NEW: Python verify does not pin stmt word_bytes/y_bytes (Rust does, lgto.rs:1162)
R3-9   NIT (gate)             relation-2 run.py gate neg 46       NEW: pad-unit negative = honest proof + edited stmt; Rust 60d9cbd1 rejected it at the zero-check
                                                                  without the rule (moot for Rust since 2dfbb90a; still a weak gate negative)
R3-10  NIT                    relation-2 run.py verify_session    NEW: job claim uses the prover-written manifest n_proofs; record dirs trusted as given; no union
                                                                  over abandoned sessions (abort-and-retry: N_sessions x eps)
gap    BLOCKING (ZK col)      relation-2 --zk, LGTO0001           open: LGSC0004 not emitted by relation-2; Rust dispatches it only for a ZK-layout key, none pinned
~~~

R3-7 detail (`run.py` 32e9bd59 l.442-514). `_file_coins` checks `coin_commit(r_k, s_k) == ccom[k]` and
`expand_challenge(batch_context(stmt, ccom), k, label_k, r_k) == slot_k`, with `ccom` and `label_k` from the dump's
`stream_binding`. `verify_session` checks the openings equal the record's, the STMT digest, and
`rd["label"] == SessionReplayCoins.labels[k]`, the label the *replay* requests. `stream_binding.labels` is never compared
with `rd["label"]`, and `len(commitments)` is not pinned. The server's real coin is `expand(ctx, k, label received with
MSG k, r_k)` (`live.py:1911-1915`). `redteam_live_labels.py` (87fe4faa) execs the committed functions from git. A ground
label (16 zero bits on slot 0) and an extra trailing commitment are both accepted with slots the verifier never issued; a
random slot is rejected. The verifier's `accepted` verdict covers round order only (`run.py` bench comment), so nothing
else catches it. Fix: derive slots from the record (labels, `coin_commit` of the recorded coins, exact length).

Correction to my 22:41Z checkpoint: I had "retracted" the off-end y malleability on the grounds that the end constraint
forces y = 0. That was wrong. The end constraint is masked off the chain ends (relation-2 0db857a9 says so and now rejects
such statements). My tamper fixture only shows that an honest proof fails against an edited statement, since the public rows
enter z(r_i, r_c) directly. It never showed the field is constrained. Fixture labels fixed in 3575161c.

## Fixtures (`~/.research/notes/lanes/red-team-ligerito-3/fixtures/`, batch-dir layout)

* `stmt_tamper_fp8-ada_e3ad950/`, `stmt_tamper_fp4-nvf4_32d3d42/`: honest local proof + 7 edited statements each; 14/14
  rejected by a8a08eb. Generator `redteam_stmt_tamper.py` (ba087855).
* `framing_malleability_fp8-ada_e3ad950/`: 4 framing re-encodings of the honest FS proof, `expect: reject`. Python
  32e9bd59 rejects 4/4; Rust 60d9cbd1 accepted 4/4, 2dfbb90a rejects 4/4 ("proof: non-canonical framing"; batch exit 0).
  Generator `redteam_framing.py` (ecd69d40).
* `framing_malleability_fp8-ada_32d3d42/`: 5 re-encodings of relation-2's 32d3d42 fp8-ada FS proof incl.
  `framing_t_pad_zero` (aeae420f). Rust 2dfbb90a rejects 5/5 (verdicts recorded); Python 32e9bd59 rejects 4/5 and takes
  `t_pad_zero` (parses to the identical proof).
* `stmt_tamper_fp8-ada_32d3d42/`: 8 entries incl. `tamper_words_widened` (same words at word_bytes 2; R3-8), Rust 2dfbb90a
  verdicts recorded, 8/8 rejected (`y_nonend_1`, `pad_y`, `pad_a`, `pad_b` at the statement stage; `words_widened`
  "statement shape"). Generator extended in 87fe4faa.
* `backends/direct/ligerito/redteam_live_labels.py` (87fe4faa): R3-7 demonstration, pure Python, execs relation-2's
  committed `_file_coins` / `batch_context` / `expand_challenge` / `coin_commit` (`python redteam_live_labels.py [REV]`).
  Summary "2 attack(s) accepted" today. It exercises `_file_coins` and simulates `verify_session`'s binding checks, so a fix
  inside `verify_session` needs the script updated. The durable test is the gate negative proposed in the relation-2
  handoff (a live dump with one `stream_binding.labels` entry changed and `.coins` re-derived must come out NOT
  authenticated).
* Reader fuzz (no files kept): honest fp8-ada e3ad950 FS stride 97 (3,386) + stride 1 over the first 9,241 bytes; local
  stride 13 (25,339) + stride 1 over the first 9,235 bytes; 0 accepted, 0 crashes.

## FINAL

(draft 23:18Z at relation-2 32e9bd59, verify-rs-3 75ec753f, sumcheck-3 19b58309; revised below if lanes commit before 00:30Z)

~~~text
item                                        verdict       evidence
1 V1 fix, relation-2 (cf9a63a..32e9bd59)    FIXED         every virtual-row class, 6 relations; V1 06-10 rejected in every gate dump (Python + Rust);
                                                          swapped-bit pair caught on r_c (zero_claims_test 3/3); blocks and values verifier-derived
2 Rust, verify-rs-3 (1f30710..75ec753f)     FIXED (V1)    own release builds a8a08eb (11 dumps, 90/90 neg.), 60d9cbd1 (2 dumps, 94/94), 2dfbb90a +
                                                          75ec753f (6 dumps, 90/90): honest accepted; canonical statements + framing (2dfbb90a),
                                                          legacy proofs claim nothing (75ec753f); LGSC0004 path unreachable with pinned keys
3 LGSC0004 masks, sumcheck-3 (c675bd5..)    DESIGN OK,    degree ≤ 2 per variable, 3^v - 1 coefficients, arity 1-6 checked (sum-zero, bind, full rank on
                                            NOT DEPLOYED  the acceptance hyperplane); coefficients in w under root_1 before every coin; no soundness term;
                                                          ZK argument holds step by step (R3-4 coverage gap, R3-6 prover vf bound)
4 coin reduction                            OK            rows↔PCS-r1 merge not done (saves 0 in LGSC0003); ef49a7de / 19b58309 widen rounds 21 → 15 → 13
                                                          coins: 184/|F| = 2^-177.9 interactive, PCS term 2^-128.017 unchanged; FS per-coin max 30/|F|
~~~

New findings this session: R3-1 … R3-10 (table above). None is a BREAK. One BLOCKING: R3-7, for the live claim only.

What blocks a Ligerito column tonight:

* **Non-ZK Fiat-Shamir column (LGSC0003, Python prover + Rust verifier): nothing BLOCKING from red team.** V1 is closed
  in both verifiers. The honest label is FS ≈ 2^-64.66 at Q = 2^64 (interactive union 2^-128.017 per proof, F5 sizing per
  proof since 0db857a9). Open NITs are two Python-side encoding-canonicity gaps where Rust is already strict (R3-2
  `"t_pad":0`, R3-8 word widths) and the weak pad-unit gate negative (R3-9). None lets a false statement verify. Every
  Rust-side finding is closed (R3-1, R3-2, R3-3 on verify-rs-3 75ec753f).
* **Live / interactive 2^-128 claim: BLOCKED by R3-7.** `verify-session` must derive the coin slots from the verifier's
  record (labels, commitments, exact length), not from the dump.
* **ZK column: BLOCKED.** relation-2 does not emit LGSC0004 (`--zk` is still LGSC0003 + the old per-variable masks, F3,
  labeled `zk_partial`). Rust's `lgto::verify` runs LGSC0004 only under a ZK-layout key (no `next:*` virtual rows), and
  none is pinned. The claim order there is provisional until relation-2 emits LGSC0004 and a ZK key is pinned. On adoption: enforce `vf ≤ n_c − 4` in `prove` (R3-6) and move the old mask sumchecks off
  g cells [0, 762) (R3-5).
