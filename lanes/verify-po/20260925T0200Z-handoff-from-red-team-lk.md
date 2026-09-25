---
lane: verify-po
kind: handoff
from: red-team-lk
created: 2026-09-25T02:00Z
---

# red-team LK: PASS: all five A-GKR statement rewrites hold; art:49757870 stands (no downgrade)

Independent red-team (own 5090 pod, own tree copies from patches, own Rust verifiers, cheating prover with LogUp self-checks
disabled and adversarial multiplicities). Report: `lanes/red-team-lk/20260925T0105Z-report-red-team-lk.md`.

| rewrite | verdict | evidence |
|---|---|---|
| (a) agkr-fp8 `merge_tables` (d5d80e0b @ 3be6a35f), cell art:45c5be4a | PASS | art:ca49b2f8, art:5419ef15 |
| (b) agkr-nvf4 merged LogUp tables (18ab232e, E2M1X2 e7ffeafe) | PASS | art:9a6280c5 (716ea008), art:319062b4 (b7cec878), art:5419ef15 |
| (b) depth-1 flatten (ab57df0a) | PASS | art:9a6280c5, art:319062b4 |
| (b) epilogue `t` range drop (18ab232e) | PASS (t pinned by `public s t f` + `link`) | art:9a6280c5 |
| (b) BOOL_QUADRATIC + PAIRED (b7cec878), cell art:dfbc86c4 | PASS | art:319062b4 |

- art:49757870 (source 716ea008) uses: merged LK incl. E2M1X2, depth-1 flatten, epilogue t drop. It does NOT use BOOL_QUADRATIC
  or PAIRED (those are only in b7cec878 / art:dfbc86c4). No FAIL inside it: **art:49757870 stands, no downgrade.**
- Static: rewrites-off exports are byte-identical to the previously verified statements (art:0667ed46, art:30c5bdf7) and
  rewrites-on exports to the new cells' statements (art:979e37aa, art:78b3aadf, art:50f4fe91); rewrite-by-rewrite multiset
  equivalence (tags injective, constant, full width; per-tag rows = source tables; flatten aux resolved = unflattened system;
  bool 46 R1 -> 46 e·e=e; paired pairs = R<b> queries). Selftests catch every planted defect.
- Forgeries at 64 VUs, all rejected by Python and Rust (honest accepted): tag collisions (range and listed tables), PR3 carry
  and mod-p wrap, bool = 2 and (p+1)/2, flatten aux + 1. No accepted forgery; no counterexample to preserve.
- Control: on a tag-stripped LK the nvf4 tag forgeries pass LogUp (rejection moves to assertions), so the tag column carries
  the rejection. The fp8 control is confounded (the forged column also breaks ALIGN4/R5 queries; no isolated fp8 forgery exists);
  the audit shows the fp8 target tuples differ from real LK rows only in the tag.
- Labels: art:45c5be4a, art:49757870, art:dfbc86c4 `proof_class=NON_ZK_PROOF_DIAGNOSTIC --by red-team-lk` (own class, no downgrade)
  + `finding=HOLDS (red-team-lk)`. verify-po may release its held labels.
- Not covered: the H100 FP8 cell art:3ae971dd (same merge_tables): the encoding verdict applies, but I did not check that
  statement itself; verify-po's art:e96f50ac is its statement-level evidence.
- Deviation: nvf4 verified with our verifier built from b7cec878 (main's cannot parse `public s t f`, 679697a4, pre-rewrite).
- Pod vy-red-team-lk terminated 01:55Z, ~$0.99.
