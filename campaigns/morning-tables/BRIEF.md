---
kind: brief
campaign: morning-tables
written: 2026-09-24T05:30Z by coordinator
deadlines: fused-phases 07:45Z; tables-fix 08:30Z; fill + gkr + sp1 12:00Z; verify-night 12:30Z; render 12:30-13:30Z; user sees it 14:00Z (07:00 PDT)
---

# Morning tables (2026-09-24)

The user wakes up to six tables that answer three things: how fast each candidate proves the Table 2 workload on each
target, what we tried, and what each variant assumes and guarantees. Solid numbers only: every cell traces to an `art:` id
and was verified by someone other than its producer. Rules for every lane: `kb/LANE-CONTRACT.md`.

## 1. The tables (fixed; do not redesign)

Frozen, rendered only by `python -m verity_numerical.bench.tables --root ~/.research/store --format md` (definitions: its
docstring and `backends/AGENTS.md`; no definition change without the user):

- **Table 1**: candidate proof systems (A-GKR, B-Ligero, SP1).
- **Table 2**: headline overhead. Rows A100 BF16 | H100 BF16 | H100 FP8 | RTX 4090 FP8 | RTX 5090 NVFP4. Columns native
  spec | native measured | A-GKR | B-Ligero | SP1 | B-Ligero + in-proof hash.
- **Table 3**: prover phase decomposition of every populated Table 2 cell.

Drill-downs, rendered by `python -m verity_numerical.bench.drilldown` (lane tables-fix builds it) from the same store with
the same validity predicate. Non-canonical, layout fixed here:

- **D1 variants and security properties**: Variant | ZK | Operands hidden from verifier | Binding rests on | Soundness |
  In Table 2? (which column, or why not).
- **D2 fastest measured `t.total` per variant x target** (A100 BF16, H100 BF16, H100 FP8, 4090 FP8, 5090 NVFP4). Cell
  `seconds · overhead×`; `✓` = Table-2-valid, else the first reason as a letter: U not independently verified, I different
  instance set, P phase-sum, S shared hashing, Z class/ZK not the column's, K prover not on the row's SKU, B batch != 4096,
  X other (footnote).
- **D3 communication and verifier cost, one row per Table 2 cell**: proof bytes per batch | prover -> verifier Gbit/s to keep
  pace (bytes x 8 / t.total) | verifier -> prover bytes (coins) | rounds | verifier CPU s per batch | verifier cores to keep
  pace | same-datacenter live tax (t.total_live / t.total).

## 2. User decisions in force (2026-09-24 ~05:10-05:25Z)

- Column 2 stays Poseidon2 per row, no sharing. The shared 64x64 tile is a drill-down.
- Phase-sum: a result whose phase buckets exceed `t.total` beyond the contract tolerance is out of Tables 2/3. Fix the
  accounting, never the rule.
- Re-packed instances: a result whose instance ref differs from the frozen set counts as the frozen set only if an
  `instance-equiv/v1` artifact, labelled `verified=accepted` by a non-producer (coordinator or verify-night), shows the
  decoded x, W, y values byte-identical. The cell's footnote says so.
- SP1 column = the best valid SP1 variant. The TC_DOT precompile fork is an SP1 variant, labelled "modified SP1 (TC_DOT
  chip)" in its backend name and footnote.
- A-GKR column = the best valid A-GKR implementation in its declared class (`NON_ZK_PROOF_DIAGNOSTIC` / `NON_ZK_PROOF`).
- Hill-climb A-GKR and SP1 on the new infrastructure (user, 05:25Z).

## 3. What a Table 2 cell needs (tables.py is the judge)

K = 1536, B = 4096, the row's frozen instance set (A100 BF16 = `vu-k1536` of `bench-instances/v1`, manifest `059103cf…`,
`FROZEN_INSTANCES[FIRST.name]`), prover on the row's device SKU, soundness 2^-128 target AND achieved, the candidate's declared
proof class, validation passed, phase buckets summing to `t.total`, proof bytes dumped and preserved, `verified=accepted`
by a non-producer, no red-team downgrade. Before calling a cell done, run the renderer over the store: its "Rejected" list
names the reason for each of your results.

## 4. Lanes

| lane | base | pod | budget | FINAL | goal |
|---|---|---|---|---|---|
| tables-fix | main 0b0768ed | none | $0 | 08:30Z | two validity gaps, instance-equiv rule, VARIANTS registry, drill-down renderer |
| fused-phases | lane/post-wave 3adf4c28 | 1x 4090 | $3 | 07:45Z | fused-hints phase accounting; v3x4 instance question; equivalence checker |
| agkr-table | main 0b0768ed | 1x A100 SXM4 80GB | $12 | 12:00Z | A-GKR A100 BF16 cell, then hill-climb |
| sp1-table | main 0b0768ed | 1x A100 SXM4 80GB | $12 | 12:00Z | unmodified SP1 A100 BF16 cell, then hill-climb |
| sp1-tcdot | main 0b0768ed | A100 SXM4 80GB (+4090 dev; +1 pod per target while proving) | $25 | 12:00Z | TC_DOT fork as an SP1 variant on ALL targets (chip parameterised per format), A100 first |
| sp1-formats (05:45Z) | lane/sp1-table | dev pod + H100 / 4090 / 5090 per cell | $20 | 12:00Z | SP1-stock for fp8-ada, fp8-hopper, bf16-hopper, fp4-nvf4 |
| fill-* (~07:45Z) | fused-phases tip | per target | ~$25 | 11:30Z | B-Ligero bare + column 2 on frozen instances, 3 rounds, dumps |
| verify-night (~07:45Z) | main | CPU pod | $4 | 12:30Z | independent verification + labels for every candidate cell |

File ownership: sp1-table owns `backends/sp1/{common,guest,host}`; sp1-tcdot adds a sibling crate under `backends/sp1/tcdot/`
and only reads `common/`. agkr-table owns `backends/gkr`. tables-fix owns `verity_numerical/bench/{tables,drilldown}.py` and
the instance-equiv schema; fused-phases owns the ligero runner and `bench/instance_equiv.py`.

Everyone handing a result to verification writes `lanes/verify-night/<ts>-handoff-from-<you>.md`: art ids, the verifier
binary and how to build it, the exact command, the expected output.

## 5. `instance-equiv/v1` (fixed; fused-phases writes it, tables-fix reads it)

One JSON file per (target, candidate instance ref), registered with `research data put ... --preserve`. The producer never
labels it; verify-night or the coordinator re-runs the checker and labels `verified=accepted`.

~~~json
{
  "schema": "instance-equiv/v1",
  "target": "<Target.name, e.g. fp8-ada-mma-draft/2026-09-22>",
  "frozen": {"...": "the FROZEN_INSTANCES[target] ref, field for field"},
  "candidate": {"...": "the instances ref the re-packed results carry, field for field"},
  "canonical": "how both sides were decoded: per array the element type (datatype bit words), byte order, and index order (VU-major, then K)",
  "arrays": {
    "x": {"frozen_sha256": "…", "candidate_sha256": "…", "dtype": "…", "shape": [4096, 1536]},
    "W": {"frozen_sha256": "…", "candidate_sha256": "…", "dtype": "…", "shape": ["…"]},
    "y": {"frozen_sha256": "…", "candidate_sha256": "…", "dtype": "…", "shape": ["…"]}
  },
  "equal": true,
  "tool": "verity_numerical.bench.instance_equiv@<commit>"
}
~~~

`equal` is true only if every array's two digests are equal. Each side is decoded by its own loader: the point is that
the numbers are the same, whatever the layout.

## 6. Appendix (coordinator broadcasts)
