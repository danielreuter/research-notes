# Fix A-GKR's existing result emitter; do not write a new one

The GPU path already emits a bench-result (`backends/gkr/gpu/tool.py`, finalised by
`verity_numerical/gkr_export/vu.py`) through the shared contract helpers. The old rejections (`prover ran on None`,
`instances missing`, `B is 64`) are missing fields in that path: fill them there (`contract.probe_hardware()`,
`contract.instances_ref(...)` as `backends/direct/ligero/relchain.py` does around lines 1094-1123) rather than building a
second emitter.
