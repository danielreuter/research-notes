# Reuse SP1's existing result emitter (benchmarks/dot_product/vector_run.py); do not write a new one

`benchmarks/dot_product/vector_run.py` already builds the bench-result through the shared contract helpers
(`contract.fingerprint`, `contract.probe_hardware`, `contract.instances_ref` at lines ~90-110 and ~433). The old SP1 results
fail Table 2 only because they are one-vector runs (instance 0 of vu-k1536, B=1). Extend that emitter to the B=4096 batch
(instances_ref("vu-k1536", 0, 4096, …) or the row's frozen ref, per-phase buckets summing to t.total, proof dump) and share it
across the SP1 variants (sp1-table owns it; the others call it with their backend name / format).
