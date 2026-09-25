---
lane: red-team-lk
kind: report
created: 2026-09-25T01:05Z
status: open
---

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
