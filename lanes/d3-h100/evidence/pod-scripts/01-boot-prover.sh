#!/usr/bin/env bash
# d3-h100 prover (vy-d3-h100, H100 US-MO-1): bootstrap on /workspace/src = main 1d9c3198 (GitHub codeload tarball, 3058 files +
# .research-source.json/COMMIT/.complete), instance caches for the four H100 Table 2 relations at 4096 VUs.
RELS=bf16-hopper-v3x4,fp8-hopper-v3x4,bf16-hopper,fp8-hopper NS=4096 bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh
