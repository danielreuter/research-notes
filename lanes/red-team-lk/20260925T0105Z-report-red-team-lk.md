---
lane: red-team-lk
kind: report
created: 2026-09-25T01:05Z
status: open
---

CHECKPOINT 14fc57e1 (03:58Z) [open] coordinator follow-up: static merged-LK check of H100 FP8 cell art:ad76c106 (run-files art:55eb421d) on a 4090 pod; first pod reaped (lane was final), recreating. 14fc57e1 enforces keys<2^20.
CHECKPOINT 0d3fe370 (01:57Z) [final] red-team LK: PASS all rewrites (fp8 merge_tables; nvf4 merged LK+E2M1X2, depth-1 flatten, t drop, BOOL_QUADRATIC, PAIRED); art:49757870 stands; evidence art:9a6280c5 art:ca49b2f8 art:319062b4 art:5419ef15; pod terminated 01:55Z ~$0.99
CHECKPOINT 0d3fe370 (01:55Z) [open] control+audit preserved art:5419ef15: nvf4 tagless control moves rejection LogUp->assertions (tag alone rejects); fp8 control confounded (forged col also breaks ALIGN4/R5 queries), audit shows target tuple differs from a real LK row only in tag; no isolated fp8 forgery exists. Next: terminate pod, report, handoffs, FINAL.
CHECKPOINT 0d719a8 (01:25Z) [open] art:49757870 tree (716ea008) PASS: static merge/flatten equivalence, statement sha = cell's, forgeries tag x2 + flatten aux rejected by py+Rust; evidence art:9a6280c5 PRESERVED. b7cec878 + fp8 forges running (fp8 static PASS, stmt = art:979e37aa's).
CHECKPOINT 48a2588c (01:16Z) [open] static equivalence PASS on 716ea008 (merge+flatten) and b7cec878 (merge+flatten+bool 46->46+paired); selftests catch all planted defects. Forgeries r20260925-011408-c1b3 running (nvf4 716ea008 first). Handoff 0100Z agkr-nvf4 (art:dfbc86c4) in scope.
CHECKPOINT 4bd6c54c (01:05Z) [open] pod vy-red-team-lk (5090) up, trees 3be6a35f/716ea008/b7cec878 rebuilt from patches, Rust verifiers building. Paper review: all 5 rewrites equivalence-preserving so far (tag col constant in queries). Next: static equivalence + forgery harness.
# red-team-lk: independent red-team of the A-GKR statement rewrites (agkr-fp8 merged LK; agkr-nvf4 merge / flatten / bool / paired)

Launch: coordinator, base main 4bd6c54c (backends/gkr identical to ab9573fd), branch lane/red-team-lk, $5, FINAL 03:30Z.
Inbox handled: `20260925T0100Z-handoff-from-agkr-nvf4.md` (BOOL_QUADRATIC + PAIRED ride in the newer 5090 NVFP4 cell art:dfbc86c4,
statement art:50f4fe91): covered below. Context read: coordinator `20260925T0045Z-handoff-from-agkr-fp8.md`,
`20260925T0022Z-handoff-from-verify-po-5090-agkr-49757870.md`, both producer reports, agkr-table report, PROTOCOL.md §4.2.

## Setup (independent of the producers)
- Pod vy-red-team-lk (RTX 5090, 4auy9ieizrdjg0, $0.99/h, guard 90), created 00:58Z. Bootstrap r20260925-005936-6c7f.
- Producer code = OUR copies: `/workspace/tree-<rev>` = synced main 4bd6c54c + `git diff --binary 4bd6c54c <rev>` for
  rev = 3be6a35f (agkr-fp8 tip), 716ea008 (the art:49757870 tree), b7cec878 (agkr-nvf4 tip, art:dfbc86c4). `00_ship.sh`.
- Verifiers built by us (r20260925-010507-37e1): `verify-main` from main (= ab9573fd verifier) sha256 cb5be598…, used for fp8;
  `verify-nvf4` from b7cec878 sha256 83ca8b31… for nvf4. Deviation from the brief ("built from main ab9573fd"): main's verifier
  cannot read the fp4-nvf4 statement's `public s t f` chain line (added by 679697a4, before every rewrite in scope; the
  verifier diff 716ea008..b7cec878 is empty, and verify-po reviewed that change for the 22:07Z merge decision). The diff
  ab9573fd..b7cec878 of backends/gkr/verifier is only that multi-public change (read in full: public.bin m words per VU bound
  to the named epilogue columns with their own chain_k slots; count checks `public.len == vus * npub`).
- Harness: `backends/gkr/tools/red_team_lk.py` (lane/red-team-lk 7a042646, 48a2588c), pod scripts `evidence/pod-scripts/`.

## Paper review (code read at the producer tips)
- Merged LK (fp8 d5d80e0b `merge_tables`; nvf4 18ab232e/e7ffeafe `_merge_tables`): rows `(i 2^20 + k, i, v.., 0..)`, queries
  `(key + i 2^20, i, out.., 0..)` with the tag `i` a CONSTANT lin (fp8: konst; nvf4: a term on the one column). The Rust
  verifier folds every lin's konst and one-column term into the query value with the same β^k weight (verify.rs
  lookup_konst l.559, per-query terms l.714), β one challenge per table with >1 column, z-q leaves. So a merged query
  matches an LK row iff tag equal and (key, out) ≡ a row of table i mod p: exactly the old membership, for ANY key (the
  2^20 bound matters only for the prover's first-column multiplicity search, not soundness). Field wraparound of
  key + i 2^20 cannot help: the shift is an injective map on F_p and the tag column is separate. Tag overflow: at most
  17 tags, 17·2^20 < p. LogUp char condition (Hab22 L5): merged N ≈ 2^24.2 (fp8 150 q x 196608 units) and ≤ 2^25 (nvf4)
  < p ≈ 2^30.9. Padding leaves are (0,1). A query narrower than LK would imply zeros in the missing columns and a wider
  one indexes out of bounds (crash, not accept); every merged query is exactly LK width (checked statically below).
- Epilogue `t` range query dropped (18ab232e): the epilogue column t is bound to public t by `public s t f` and to the
  unit's out.t by `link acc.t out.t t`; a range check on a column pinned to public data adds no soundness. PASS.
- Depth-1 flatten (ab57df0a): `ctx.col` = derived aux column + `_linear(name.def, aux - e)`, exported as an `assert`;
  Expr has no `__eq__`, so the restatement-skip `spec == (q.a, q.b)` is an identity test (no quadratic silently dropped).
- BOOL_QUADRATIC (b7cec878): `Quadratic(e, e, e)` exports as product wire w = e·e plus `assert w - e = 0`; witness
  columns are F_p (BabyBear) elements, and x² = x has only the roots 0, 1 in a field.
- PAIRED (b7cec878): `(x + 2^b y, x, y)` into PR<b> = {(x + 2^b y, x, y): x, y < 2^b}: x and y are their own columns, so
  membership forces both into [0, 2^b); the key column is redundant (and x + 2^b y < 2^14, so no wrap).
- art:49757870 (716ea008) contains: merged LK incl. E2M1X2, depth-1 flatten, epilogue t drop. NOT bool/paired (b7cec878
  only, in art:dfbc86c4).

## Static equivalence (pod, our trees; outputs /workspace/red-team-lk/out/*/static.json, selftest.json)
Chain of custody: the OLD statement that verify-po accepted -> (our export with the rewrite off, byte-identical) -> checked
equivalent -> (our export with the rewrite on) -> byte-identical to the NEW cell's statement.
- fp8 (3be6a35f): `--no-merge` export circuit.txt sha d7ba4f96… = art:0667ed46's (pre-merge, verified) statement; merged
  export 5d805eed… = art:979e37aa's (the 0.490 s cell art:45c5be4a); epilogue d7c88ded… and chain fb97ce9a… identical in all
  three. `static-merge`: ok, 150 queries/unit all into LK (width 8, 261819 rows), 10 tags 1..10 injective, every merged query
  = plain query with konst + tag·2^20, constant tag, zero pads; per tag, LK rows (minus shift/tag/pads) = the plain table's
  rows as multisets (itables SHIFT/TNORM materialised); no row with an unused tag; manifest differs only in `lookup_tables`.
- nvf4 art:49757870 tree (716ea008): with every rewrite off (merge=False, max_depth=99) the unit circuit is 990fb555… =
  art:30c5bdf7's (3c769c6d cell, verified) statement; with defaults it is a55772a2… = art:49757870's (run-files art:78b3aadf).
  Epilogue 4445d8a8… -> 382b6567…: the only change is the dropped `query R8` on t (see paper review). `static-nvf4`: merge ok
  (226 q/unit, LK width 5, 89119 rows, 16 source tables incl. E2M1X2); flatten ok: 67 new aux columns (7 -> 74), each with its
  `aux - e = 0` definition, and after resolving every aux column through its definition the multisets of products (by name,
  operands), linear constraints, quadratics, ranges, native lookups, outputs and chain are IDENTICAL to the unflattened
  system; max depth 3 -> 1.
- nvf4 b7cec878 (art:dfbc86c4): rewrites off -> the same 990fb555…; merge ok (166 q/unit, LK 110613 rows); flatten ok (same
  67 aux); BOOL_QUADRATIC ok: exactly the 46 R1 ranges removed and 46 quadratics e·e = e added with the same e (multiset
  match), nothing else changed; PAIRED ok: R3 16 -> 8 pairs, R5 5 -> 2 pairs + 1 leftover, R6 4 -> 2, R7 5 -> 2 + 1; every PR
  key column = x + 2^b y exactly, {x, y components} + leftovers = the plain R<b> queries (multiset), PR<b> rows =
  {(x + 2^b y, x, y)}; the paired statement then merges ok.
- Non-vacuity (`selftest`): planted defects all caught on the three statements: query tag changed, LK row tag changed, LK
  row dropped, key shifted by 2^20, pad column nonzero, output column +1; PR5 row x out of range, PR5 x/y swapped, PR3 query
  dropped; flatten def dropped, flattened product operand swapped, quadratic dropped, range dropped.

## Forgeries (pod, cheating prover, our Rust verifiers; 64 VUs; outputs out/<rev>/forge{,.log})
Cheating prover = our tree copy with the LogUp "fractional sum is not zero" raises sed'ed to `pass` (logup.py 1, logup_packed.py
3) and `logup.multiplicities` swapped for a first-column match with no membership check (so a forged query is counted
against the colliding LK row). Honest control accepted by Python and Rust in every tree. Every forgery REJECTED by both:

| tree | proof bytes | forgery | Rust rejection |
|---|---|---|---|
| 716ea008 (art:49757870) | 649000 | tag.R1_as_R16 (R1 query's key = R16 row key + R16 tag shift), tag.E2M1X2_as_POW19 (full POW19 row, E2M1X2 tag) | LogUp LK level 0: final check |
| | | flatten.aux+1 (column flat.g2.shift.prod79.a + 1) | unit/assertions: phase-1 round 0 sum mismatch |
| b7cec878 (art:dfbc86c4) | 652840 | tag.R5_as_R16, tag.E2M1X2_as_POW19, paired.PR3.carry (x+2^3, y-1: same key), paired.PR3.wrap (x-2^3 mod p, y+1) | LogUp LK level 0: final check |
| | | bool.two (bit = 2), bool.half (bit = (p+1)/2), flatten.aux+1 | unit/assertions: phase-1 round 0 sum mismatch |
| 3be6a35f (art:45c5be4a) | 817888 | tag.R5_as_R7 (q105 key = 33 + 5·2^20, R7's row), tag.T_OP_as_ALIGN4 (full ALIGN4 row, T_OP tag) | LogUp LK level 0: final check |

No accepted forgery. fp8 needed the 5-line Triton 3.4 constexpr fix (from b7cec878's packed/kernels_triton.py, 05_fp8_rerun.sh)
in OUR copy only to run the honest generator on the 5090; it touches no statement or proof code.

## Control: tag-stripped LK (06_control.sh, 07_audit.sh, 08_iso.sh)
The same tag forgeries against a deliberately unsound statement = LK with its tag column deleted from rows and queries,
plus a per-forgery audit of every changed (query, unit) tuple against the LK row set:
- nvf4 716ea008: the target tuple is the ONLY LK miss with the tag, and there is NO miss without it; Rust/Python rejection moves
  from "LogUp LK final check" to "unit/assertions" on the tagless statement. So the tag column alone is what rejects the
  collision at LogUp (the flatten/assert layer then still catches the bad value).
- fp8 3be6a35f: control CONFOUNDED: the forged column is also read by other queries (tag.R5_as_R7: q64 ALIGN4 and q106 R5;
  tag.T_OP_as_ALIGN4: q65 ALIGN4) that miss LK with or without the tag, so LogUp rejects either way. The audit shows the
  target tuples (q105, q0) are LK misses only with the tag, i.e. without it they equal real LK rows. A search for an
  isolated fp8 range-tag forgery (every range query x every wider range table x up to 256 keys, forged unit) found none: every
  fp8 range-checked column also feeds a query that the change breaks. The fp8 verdict therefore rests on the exact static
  equivalence + the Rust rejections, with this audit as attribution, not on a clean end-to-end control.

## Evidence (research data put --preserve from the pod, minted credential; laptop reindex --remote; `data preserved` bounded)
- art:9a6280c5 redteam-findings/v1, 716ea008, ref result=art:49757870 (static, selftest, forge statements/rows/proofs/verdicts).
- art:319062b4 redteam-findings/v1, b7cec878, ref result=art:dfbc86c4.
- art:ca49b2f8 redteam-findings/v1, 3be6a35f, ref result=art:45c5be4a.
- art:5419ef15 redteam-findings/v1, control + audit (both trees) + fp8 isolated search, refs result=art:49757870, result_fp8=art:45c5be4a.
- (art:41147034: an earlier put of 716ea008 under the unknown kind gate-log/v1; superseded by art:9a6280c5, not cited.)
- Labels (labels-sync pushed, confirmed local+remote): art:45c5be4a, art:49757870, art:dfbc86c4 each
  `proof_class=NON_ZK_PROOF_DIAGNOSTIC --by red-team-lk` (the cells' own class: no downgrade) + `finding=HOLDS (red-team-lk): ...`,
  ref evidence.
- Harness lane/red-team-lk 7a042646 48a2588c f054da0d 0731bede 2f859869 b81c0f23 0d3fe370 (`backends/gkr/tools/red_team_lk.py` only).

## Deviations / limits
- nvf4 verified with a verifier built by us from b7cec878 (main's cannot parse `public s t f`; see Setup); fp8 with main's.
- The H100 FP8 cell art:3ae971dd (verify-po 01:42Z handoff; same 3be6a35f `merge_tables`, 139 q/unit, R6 for R5): the rewrite
  verdict covers the encoding it uses, but I did not export, statically check or forge against THAT statement (pod gone);
  verify-po's structural check art:e96f50ac is the statement-level evidence. Not labelled by me.
- Forgeries are single-unit witness edits at B = 64 VUs; the static checks cover every query/row of the full statements.

## Inbox
- `20260925T0100Z-handoff-from-agkr-nvf4.md`: acted (b7cec878 / art:dfbc86c4 red-teamed above).
- `20260925T0123Z-handoff-from-verify-po.md`: acted (verdict + labels; verify-po may release its held labels).
- `20260925T0142Z-handoff-from-verify-po.md`: acted (art:3ae971dd scope stated under Deviations; rewrite PASS applies to the encoding).

## Handoffs sent
- `~/.research/notes/lanes/coordinator/20260925T0200Z-handoff-from-red-team-lk.md` "red-team LK: PASS ...", copies
  `lanes/agkr-fp8/20260925T0200Z-handoff-from-red-team-lk.md`, `lanes/agkr-nvf4/20260925T0200Z-handoff-from-red-team-lk.md`, `lanes/verify-po/20260925T0200Z-handoff-from-red-team-lk.md`.

## FINAL
tip: lane/red-team-lk @ 0d3fe370 (base main@4bd6c54c) merge-with: none
known-failures: none
pod: terminated 01:55Z; $0.99
artifacts: art:9a6280c5 art:ca49b2f8 art:319062b4 art:5419ef15

red-team LK: PASS. Every rewrite holds: (a) agkr-fp8 `merge_tables` (art:45c5be4a; art:ca49b2f8); (b) agkr-nvf4 merged LK incl.
E2M1X2, depth-1 flatten, epilogue t drop (art:49757870; art:9a6280c5), and BOOL_QUADRATIC + PAIRED (art:dfbc86c4; art:319062b4);
control/audit art:5419ef15. art:49757870 uses merge + flatten + t drop (not bool/paired) and STANDS: no downgrade. No accepted
forgery among 12 adversarial witnesses, plus 4 tag-stripped control runs (cheating prover, our Rust verifiers). Limits: fp8 tag control is confounded (audit
attributes it); art:3ae971dd's statement not checked by me; nvf4 verifier built from b7cec878 (main's cannot parse `public s t f`).

## Follow-up (coordinator, 03:50Z): H100 FP8 cell art:ad76c106 (run-files art:55eb421d): PASS, evidence art:c1ee1fdb
- Harness 14fc57e1: `static-merge` now also enforces source keys in [0, 2^20) and reports LK first-column uniqueness.
- On pod vy-red-team-lk2, from `git archive 3be6a35f` plus the harness (export.py is identical at a97576b5). Script
  `10_hopper.sh`, run r20260925-035948-0fdc.
  - Export with merging off: byte-identical to the old verified fp8-hopper statement (art:2e7baba7 / art:b0c27291, run-files
    art:438ada92 = art:25c57ccb); circuit 424e7256….
  - Export with merging on: byte-identical to art:55eb421d's statement; circuit 07d15dc3….
  - `static-merge` ok: 139 queries per unit, LK 261968×8, 10 injective tags, per-tag rows = source tables, max key 229375 < 2^20,
    first column unique; the selftest caught every planted defect.
- Pods: ar2ylwgfs6zbpj was REAPED at 03:54Z (the lane was final; now reopened). p0jlotqz4ualgr ran 03:58–04:01Z and is
  terminated. About $0.07.
- Handoff: `~/.research/notes/lanes/coordinator/20260925T0405Z-handoff-from-red-team-lk.md` "red-team LK H100 FP8: PASS".
