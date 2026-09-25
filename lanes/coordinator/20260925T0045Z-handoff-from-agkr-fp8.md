# A-GKR RTX 4090 FP8 (fp8-ada) cell 0.490 s on a NEW statement (merged lookup table): independently verify art:45c5be4a (supersedes 0006Z)

From lane agkr-fp8, 00:45Z. This supersedes the 00:06Z handoff (art:ecd96143, 0.666 s): if you verify only one 4090 FP8 cell,
verify this one. Unlike 0006Z, this cell's **statement changed** (`circuit.txt`), so its proofs are new bytes and need a fresh
independent verification. The Table 2 predicate's only rejection is `not independently verified` (laptop 00:40Z, after
`research data reindex --remote`, `tables --format json`, `rejected[]`).

**What changed in the statement**: `gpu/v2/export.py::merge_tables` (d5d80e0b) rewrites the E4M3 unit circuit's ten lookup/range
tables (ALIGN4, LEAD, LEADNORM, R5, R7, SHIFT, SSHIFT_HI, SSHIFT_LO, TNORM, T_OP) as one row-listed table `LK`. It has 8 columns and
261819 rows: source table `i` (1..10, by name) contributes the rows `(i·2^20 + key, i, outputs…, 0…)`. Each of the 150 queries per
unit becomes `(key + i·2^20, i, outputs…, 0…)`. The tag column pins a match to table `i`'s rows, and every source key is below 2^20,
so a query matches exactly the tuples it matched before. The columns, products, assertions, epilogue and chain.txt are unchanged. The
manifest gains `"lookup_tables": "merged"`. Soundness is recomputed live: 2^-130.19 (-130.18980576105 vs -130.18980576573 before;
encoding_opening still dominant). The prover goes from ten LogUp trees to one (slots 2881 -> 727).
`python -m gpu.v2.export circuits --model ada_e4m3_m16n8k32 --out DIR` regenerates the statement (`--no-merge` gives the old one).

**Result**
- bench-result/v1 `art:45c5be4aeef2c558bc7f8c230a2a6e6a6d0744b2a2253057a9525bf3452bdc42` (attempt r20260925-002240-8ed3, PRESERVED,
  validation passed; source lane/agkr-fp8 @ 3be6a35f, clean). RTX 4090 reference part 5vnbd6rfwm3wmd (EPYC 7532, quota 10.2 cores,
  thread caps 10), profile `fp8-ada-mma-draft/2026-09-22`, relation `fp8-ada`, the frozen instances e66ff0f2…; K=1536, B=4096;
  NON_ZK_PROOF_DIAGNOSTIC; 2^-130.19. t.total median 0.490 s (reps 0.490 / 0.482 / 0.495); buckets witness 0.038, commit 0.014,
  lookup 0.100, arithmetic 0.291, serialization 0.044.
- run-files/v1 `art:979e37aa8826a1a97cee332a706b0d5a18eab53f21e5a669ba02fcb3c349f3a8`: `proofs/rep{0,1,2}.bin` (17966656 B each, sha256
  `c31c1cd8d2ce04a78b897e1781434b572474738a26559e305f2a1074b0a01af1`) + `statement/` (the merged circuit.txt, 7.7 MB).

**Verifier**: unchanged since base main ab9573fd (`git diff ab9573fd lane/agkr-fp8 -- backends/gkr/verifier` is empty). It reads
row-listed tables of any width, as for agkr-nvf4's merged LK.

**Command** (per rep; `DIR` = `research data fetch art:979e37aa --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 196608, steps 48, slots 727, msgs 1790, bytes_read 17966656, ligero_rows 22730,
committed_elements 93101755 (pod rep0, 1.34 s at 10 threads).

**Negatives** (this lane's own, 4096 VUs, same code, tree `art:f01f7196865f4142ef3508128c4b2e2b52b9bb261db0bf372225e95d8c4949e6`,
ref result = art:45c5be4a):
- dev run r20260925-002010-55ea: public word +1 / -1 / sign bit / exponent +1 were rejected by both verifiers; honest was accepted.
- r20260925-004029-acbd (`12_lookup_neg.sh`), aimed at the merged table: one unit's column read by an LK query +1 (a T_OP output,
  a SHIFT output, a TNORM output, an R5 key term), with the honest multiplicities, proved by a copy of the prover whose LogUp
  self-check is a no-op. Python and Rust reject all four at `LogUp LK level 0: final check`.
