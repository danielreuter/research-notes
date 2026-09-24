---
lane: tables-fix
kind: report
created: 2026-09-24T05:25Z
status: final
---

CHECKPOINT b11809c1 (06:06Z) [final] FINAL b11809c1: gaps A/B + instance-equiv rule + bench.drilldown D1-D3 + AGENTS.md; Table 2: 4090 B-Ligero 6.6e6x, 4090 +hash 1.8e7x, 5090 9.5e6x (self-verified/Ajtai cells out); art:68466c4a verified would make 4090 3.0e6x (handoff coordinator).
CHECKPOINT 1ffa37c (06:00Z) [open] D4 committed fe68d886: bench.drilldown D1-D3 (20 variants; D2 marks = tables.reject_codes; D3 from cell envelopes, '…' where absent); 36 new tests pass. Real store: 3.9 s, 70 MB. Next: D5 AGENTS.md paragraph, final renders + Table 2 diff vs 05:00Z, report.
CHECKPOINT bdaf2c44 (05:38Z) [open] D1 gap A 5847c230, D2 gap B 9392d8f1, D3 instance-equiv/v1 rule bdaf2c44 (tests green except pre-existing vocab AUTHENTICATION_VALUES mismatch in tools/research). Next: VARIANTS registry + bench.drilldown D1-D3, AGENTS.md paragraph.
CHECKPOINT none (05:25Z) [open] worktree lane/tables-fix@0b0768ed. Gap A diagnosed: research data put records no registrar; attribution = meta.lane / meta.by / lane label (28 self-verified attempt-less wave-* results). Next: producer fix + tests.

## What changed (lane/tables-fix, base main@0b0768ed)

Table 1/2/3 definitions, columns, metrics, captions and rows are unchanged; only the validity predicate and the new
drill-down module moved. Each step has tests in `backends/numerical/tests/bench/` (`test_tables.py`, `test_drilldown.py`).

1. `5847c230` gap A (independent verification). `research data put` records no registrant, so an attempt-less result's
   producers are now the lanes its meta names (`lane`, `by`, `registered_by`, `constructed_by`), the lanes its `lane` labels
   name, and the asserters of its own `candidate` / `label` labels. A `verified=accepted` from any producer never counts. An
   attempt-less result that names no producer is never verified (reason letter U).
2. `9392d8f1` gap B (column "+ in-proof hash"). Accepted only as `included-hash` with hash `poseidon2-babybear-w24`
   (leaf `poseidon2`) and `sharing` = `none`. Ajtai, BLAKE3 and shared tiles are rejected with a reason naming the leaf or
   the sharing. Every reason now carries its D2 letter (`tables.reject_codes`; `reject_reasons` wraps it).
3. `bdaf2c44` re-packed instances, implementing BRIEF §5 as written. They count only through an `instance-equiv/v1` that
   passes the content checks and whose latest verdict by a non-producer (of the equivalence and of the result) is
   `verified=accepted`. The cell footnote then names it. Handoff to fused-phases (05:39Z): register equivalences with a
   producer name. They now do (`lane=fused-phases`).
4. `fe68d886` `python -m verity_numerical.bench.drilldown --root <store> --format md|json`: D1-D3 per BRIEF §1. D1 comes
   from a `VARIANTS` registry (20 seed entries, each with its recogniser and sources, and "unknown" where no source states a
   fact). D2 marks each result with the first letter of `tables.reject_codes`, imported rather than restated. D3 reads the
   cell's result envelope only, printing `…` where a field is absent and listing the fields it read.
5. `584b0357` `backends/AGENTS.md`: one paragraph naming D1-D3 and the module, "non-canonical; layout fixed 2026-09-24
   (campaign morning-tables BRIEF §1)".
6. `b11809c1` (cosmetic) an equivalence's verdict reason names its artifact once.

## Table 2 versus the 05:00Z render

Real store, read-only, at 06:02Z (full renders: `20260924T0602Z-tables-render.md`, `20260924T0602Z-drilldowns-render.md`
in this directory; about 3-4 s wall time and 70 MB each).

~~~text
| Device                  | Target        | A-GKR | B-Ligero     | SP1 | B-Ligero + in-proof hash |
| NVIDIA A100 SXM4 80GB   | BF16 (first)  | —     | 1.9e7×       | —   | 5.2e7×                   |
| NVIDIA H100 SXM5 80GB   | BF16          | —     | 5.2e7×       | —   | 7.5e7×                   |
| NVIDIA H100 SXM5 80GB   | E4M3 wgmma    | —     | 5.6e7×       | —   | 8.3e7×                   |
| NVIDIA GeForce RTX 4090 | E4M3 mma      | —     | 6.6e6× (was 4.4e6×) | — | 1.8e7× (was 9.3e6×) |
| NVIDIA GeForce RTX 5090 | E2M1 nvf4     | —     | 9.5e6× (was 5.4e6×) | — | —                   |
~~~

Three cells changed, all because of the validity fixes; the other six populated cells are the same artifacts:

- 4090 FP8 B-Ligero: `art:1a44b9c8` (0.169 s) is out. It has no attempt, and its only `verified=accepted` came from its
  own lane, wave-4090-2 (gap A). The cell is now `art:cc59294a` (0.252 s), accepted by the live verifier.
- 4090 FP8 B-Ligero + in-proof hash: `art:a657d26c` (0.352 s) is out. It uses an Ajtai n=64 leaf (gap B) and was also
  self-verified by wave-4090-2 (gap A). The cell is now `art:4ab22886` (0.693 s), Poseidon2 per row, accepted by the live
  verifier.
- 5090 NVFP4 B-Ligero: `art:7cdffa50` (0.0402 s) is out, self-verified by wave-5090-2 (gap A). The cell is now
  `art:318eed1c` (0.0714 s), accepted by the live verifier.

No re-packed result entered. About ten `instance-equiv/v1` artifacts by fused-phases pass the content checks, but only
producers have labelled them. One label would move a cell: `art:0d5b229a` (4090 FP8, v2 public selection, 0.114 s =
3.0e6×) fails only because its instances are re-packed. If a non-producer labels its equivalence `art:68466c4a`
`verified=accepted`, the 4090 B-Ligero cell becomes 3.0e6×. Handoff to the coordinator at 06:08Z. The other 99 re-packed
results also fail U, P, X or K.

## Drill-downs (trimmed)

D1, trimmed to 2 of its 6 columns (the ZK, operands hidden, binding and soundness columns are in the full render):

~~~text
B-Ligero v1                       Yes: B-Ligero column; holds A100/H100 BF16/H100 FP8/4090/5090 B-Ligero
B-Ligero v3, v3 fused, v3x4 fused (l=4096), v1x4, v3x4, v2, v2x4
                                  Yes: B-Ligero column (v2/v2x4 never the + in-proof hash column); hold no cell
B-Ligero Fiat–Shamir (HVZK)       No: HVZK is B-Ligero's drill-down class
B-Ligero + Poseidon2 per row      Yes: + in-proof hash column; holds A100/H100 BF16/H100 FP8/4090
B-Ligero + Poseidon2 shared tile, + BLAKE3, + Ajtai n=64 / n=128
                                  No: the column is Poseidon2-BabyBear per row, no sharing (keep_frozen)
B-Ligero native external auth     No: 'included' is not a Table 2 column
Ligerito                          No: not a Table 1 candidate
A-GKR CPU (Rust), A-GKR GPU       Yes: A-GKR column (recognised: verity-gkr…; GPU by gpu/triton/torch/cuda)
SP1 unmodified, SP1 + TC_DOT      Yes: SP1 column (recognised: sp1…; TC_DOT by tc-dot/tc_dot/tcdot/modified sp1)
~~~

D2: fastest `t.total` · overhead, then ✓ or the predicate's first letter (footnotes in the full render):

~~~text
| Variant                   | A100 BF16          | H100 BF16          | H100 FP8           | 4090 FP8            | 5090 NVFP4          |
| B-Ligero v1               | 0.262 s · 6.5e6× X | 0.181 s · 1.4e7× U | 0.108 s · 1.7e7× U | 0.157 s · 4.1e6× X  | 0.0383 s · 5.1e6× U |
| B-Ligero v3               | 0.265 s · 6.6e6× X | 0.197 s · 1.5e7× I | 0.121 s · 1.9e7× P | 0.114 s · 3.0e6× I  | —                   |
| B-Ligero v3 fused hints   | —                  | —                  | —                  | 0.143 s · 3.8e6× P  | —                   |
| B-Ligero v3x4 fused l4096 | —                  | —                  | —                  | 0.114 s · 3.0e6× P  | —                   |
| B-Ligero v1x4             | —                  | 0.242 s · 1.9e7× B | —                  | 0.15 s · 3.9e6× B   | —                   |
| B-Ligero v3x4             | 0.229 s · 5.7e6× I | 0.138 s · 1.1e7× P | 0.075 s · 1.2e7× I | 0.0907 s · 2.4e6× I | —                   |
| B-Ligero v2               | 0.555 s · 1.4e7× I | 0.609 s · 4.8e7× I | 0.313 s · 4.9e7× I | 0.114 s · 3.0e6× I  | —                   |
| B-Ligero v2x4             | 0.283 s · 7.0e6× I | 0.29 s · 2.3e7× I  | 0.168 s · 2.6e7× I | 0.0701 s · 1.8e6× I | —                   |
| B-Ligero FS (HVZK)        | 1.91 s · 4.7e7× Z  | 0.823 s · 6.5e7× Z | 0.422 s · 6.6e7× Z | 0.641 s · 1.7e7× Z  | 1.69 s · 2.3e8× Z   |
| + Poseidon2 per row       | 0.744 s · 1.8e7× P | 0.774 s · 6.1e7× X | 0.355 s · 5.6e7× X | 0.373 s · 9.8e6× P  | 0.149 s · 2.0e7× I  |
| + Poseidon2 shared tile   | 0.48 s · 1.2e7× X  | 0.399 s · 3.1e7× S | 0.203 s · 3.2e7× S | 0.242 s · 6.4e6× S  | —                   |
| + BLAKE3 in circuit       | —                  | —                  | —                  | 3.66 s · 9.6e7× X   | —                   |
| + Ajtai n=64              | —                  | —                  | —                  | 0.352 s · 9.3e6× X  | —                   |
| + Ajtai n=128, native auth| —                  | —                  | —                  | —                   | —                   |
| Ligerito                  | —                  | 0.688 s · 5.4e7× X | 0.393 s · 6.2e7× X | 0.397 s · 1.0e7× X  | —                   |
| A-GKR CPU (Rust)          | 54.2 s · 1.3e9× K  | —                  | —                  | —                   | —                   |
| SP1 unmodified            | 0.855 s · 8.7e10× X| —                  | —                  | —                   | —                   |
| A-GKR GPU, SP1 + TC_DOT   | —                  | —                  | —                  | —                   | —                   |
~~~

D3, one row per Table 2 cell, from its envelope. All seven columns are populated in all nine rows. The A100 B-Ligero
proof size is its `transcript.bytes`, since that envelope has no `proof_bytes`:

~~~text
| Table 2 cell            | Proof bytes | Gbit/s P→V | Coins V→P | Rounds | Verifier CPU s | Verifier cores | Live tax |
| A100 BF16 · B-Ligero    | 122 MB      | 1.25       | 8.35 kB   | 3      | 4.25 s         | 5.45           | 11.8×    |
| A100 BF16 · + hash      | 169 MB      | 0.641      | 8.37 kB   | 3      | 16.5 s         | 7.85           | 4.62×    |
| H100 BF16 · B-Ligero    | 118 MB      | 1.42       | 8.38 kB   | 3      | 11.4 s         | 17.1           | 1.33×    |
| H100 BF16 · + hash      | 164 MB      | 1.38       | 8.36 kB   | 3      | 34.3 s         | 36.1           | 3.02×    |
| H100 FP8 · B-Ligero     | 62.3 MB     | 1.4        | 5.75 kB   | 3      | 7.52 s         | 21.1           | 1.79×    |
| H100 FP8 · + hash       | 87.1 MB     | 1.32       | 5.73 kB   | 3      | 16.5 s         | 31.4           | 2.66×    |
| 4090 FP8 · B-Ligero     | 66.1 MB     | 2.09       | 5.74 kB   | 3      | 3.6 s          | 14.3           | 1.12×    |
| 4090 FP8 · + hash       | 90.9 MB     | 1.05       | 5.74 kB   | 3      | 8.35 s         | 12             | 1.07×    |
| 5090 NVFP4 · B-Ligero   | 23.5 MB     | 2.63       | 4.41 kB   | 3      | 1.76 s         | 24.7           | 1.27×    |
~~~

## Findings for the user

- 220 of the 969 `bench-result/v1` artifacts carry the result envelope only in their JSON payload, with a lane summary as
  meta. tables.py reads meta, so they can never be cells. D2 shows them with X and "payload envelope". None of them would
  be valid tonight even if registered with the envelope as `--meta`, so no cell is lost.
- Table 1's A-GKR assumption text says "BLAKE3 Merkle", but `backends/gkr` commits with SHA-256 Merkle on both the CPU
  (README) and the GPU (`gpu/ligero.py`). Table 1 is frozen, so D1 records the discrepancy and nothing else changed.
- The A100 B-Ligero cell's envelope gives a live tax of 11.8× (`t.total_live` about 9.2 s against `t.total` 0.78 s),
  against 1.1-4.6× in the other cells. Reported as recorded, not re-measured.
- The rows for A-GKR GPU, SP1 + TC_DOT and Ajtai n=128 are empty: no results in the store at 06:02Z. Names starting
  `verity-gkr…`, `sp1…` and `sp1 tc-dot…` are recognised, as tested.

## FINAL

~~~text
tip: lane/tables-fix @ b11809c1 (base main@0b0768ed)        merge-with: none
known-failures: backends/numerical/tests/bench/test_tables.py::test_label_keys_are_the_store_vocabulary (fails identically at 0b0768ed: research.store.vocab.AUTHENTICATION_VALUES lacks included-hash-shared; tools/research is not this lane's)    pod: none; $0
artifacts: art:cc59294a art:4ab22886 art:318eed1c art:1a44b9c8 art:a657d26c art:7cdffa50 art:0d5b229a art:68466c4a
~~~

All five deliverables are in, each with tests: 36 new drill-down tests plus the predicate tests. The bench suite gives
216 passed and 5 skipped, with the one known failure above. The morning render is trustworthy on the two validity
gaps: three 05:00Z cells were replaced by live-verifier-accepted results (4090 B-Ligero 6.6e6×, 4090 + in-proof hash
1.8e7×, 5090 B-Ligero 9.5e6×), and no other cell moved. The drill-downs render with
`python -m verity_numerical.bench.drilldown --root ~/.research/store --format md`.

Handoffs: sent fused-phases 05:39Z (register instance-equiv/v1 with `lane`; done) and coordinator 06:08Z (`art:68466c4a`
needs a non-producer's `verified=accepted`, which would make the 4090 B-Ligero cell 3.0e6×). None received.
Left: nothing in scope. The A-GKR GPU and SP1 TC_DOT rows fill in once agkr-table / sp1-tcdot register results.
Finish checks: ok. The custody check did not run because the installed `research` raised an AttributeError
(`Index.resolve_art_prefix` missing). This lane created no artifacts; the ids cited are other lanes' existing results.
