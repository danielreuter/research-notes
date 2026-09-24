# TODO post-wave: one `contract.result(...)` builder for every bench-result emitter (user asked 05:31Z; delete this note when merged)

Why: about 20 scripts assemble the bench-result by hand from the shared helpers in
`backends/numerical/python/verity_numerical/bench/contract.py` (`fingerprint`, `probe_hardware`, `instances_ref`,
`measurement`, `rate_measurements`, `validate`). B-Ligero's assembly alone is ~160 lines (`backends/direct/ligero/relchain.py`
~1094-1255). Every new backend re-does it and drops fields (A-GKR: no device / instances; SP1: B=1).

Do: `contract.result(backend=..., proof_class=..., security=..., K=..., B=..., instances=..., phases={bucket: s}, t_total=...,
proof_dir=..., **extra)` that fills hardware (probe), software + source stamp, rates, schema, then `validate()` and refuses to
return a non-conforming record. Port emitters one at a time; each port's output must equal the old one on a recorded run
(except added fields). Tests.

Candidates (grep `bench-result/v1|workload_fingerprint`; some only read the record): direct/ligero/relchain.py,
direct/ligero/fp8/tool.py, direct/encode/envelope.py, direct/src/main.rs (Rust), gkr/src/main.rs (Rust), gkr/bench_result.py,
gkr/gpu/tool.py, gkr_export/vu.py, gkr/tensor/bench.py, gkr/tensor/fused/bench.py, gkr/packed/{bench,logup_bench,
logup_graph_bench}.py, gkr/verifier/e2e.py, vole/bench.py, shared/anchor_a100/report.py, checker/{sweep,search}.py,
redteam/{campaign,z3_babybear}.py, benchmarks/dot_product/vector_run.py, plus tonight's SP1 / TC_DOT / A-GKR emitters.

When: after the morning render (not mid-campaign). One lane, laptop + one pod for the recorded-run comparisons.
Done = builder merged into main and the live emitters ported; then delete this file.

Addendum 06:20Z (tables-fix FINAL): 220 bench-results keep their measurements only in the payload, not the manifest meta,
so tables.py never sees them. The builder should write the canonical fields into meta; a one-off backfill can re-put them.
Also pre-existing: backends/numerical/tests/bench/test_tables.py::test_label_keys_are_the_store_vocabulary fails on main 0b0768ed.
