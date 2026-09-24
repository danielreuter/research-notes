---
lane: pod-runs
kind: handoff
from: coordinator
created: 2026-09-24T17:12Z
---

# coordinator -> pod-runs: suite shows 3 failures in test_store_prov.py and 7 in test_store_vllm_tools.py; say in FINAL whether main fails the same

Run just those two files against main's tools/research (PYTHONPATH=~/projects/verity-main-wt/cli/tools/research/src) and
report failures as "pre-existing on main" or "introduced by pod-runs"; fix any you introduced. Laptop disk is 4.1 GiB free
(the guardian's kill floor is 3.5 GiB): delete /tmp/pod-runs scratch before FINAL and run nothing else large locally.
