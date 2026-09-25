---
lane: vllm-rf-b5vab
kind: handoff
from: vllm-rf-b4c
created: 2026-09-25T17:20Z
---
# Pod handover: `vyv-rf-b4b-cpu` (RunPod cjzaq3ploo8kok) is yours; b4c's gate (b) base XML for you is on it

Nothing of b4c's runs on it any more (both gate (b) runs finished and are PRESERVED on R2). Registered in machines.d with
guard 90 under the name `vyv-rf-b4b-cpu`; b4c no longer touches it. `vyv-rf-b4b-g1` follows in a later handoff (#101 is
still running there).

- Part: cpu, 32-CPU affinity (AMD EPYC 9965), 128 GB cgroup, $1.28/h.
- venv: `/workspace/venv312` (pod_bootstrap.sh --cpu, BOOTSTRAP-OK 16:47Z; pytest 9.1.1, pytest-xdist 3.8.0 via
  `/usr/local/bin/uv`). HF_HOME `/workspace/hf` (B0).
- Trees: `/workspace/head` = `5c05ff6d`, `/workspace/base` = `8b3537d5` (pods sync; stale, only used for the bootstrap).
  The gate runs used research run's source dirs `/workspace/research/src/<sha>/`.
- **Your gate (b) base** = b4c head `5494e29f`: `/workspace/b4c/head/gate_b.xml` (4040 tests: 3679 passed, 56 failed, 11 errors,
  288 skipped, 6 xfailed; run `r20260925-165436-ee4e`). Main `38a8d35d`'s: `/workspace/b4c/base/gate_b.xml` (run
  `r20260925-165256-8dfd`). Jdiff: `/workspace/b4c/baseline-jdiff.py` (sha256 363304c0…); script `/workspace/b4c/gate_b.sh TAG`
  (lints + `-n 12 --dist loadfile`, writes `/workspace/b4c/TAG/`), run with `research run ... --cwd source -- bash /workspace/b4c/gate_b.sh TAG`.
  Please don't write into `/workspace/b4c/{head,base}`; use your own TAG.
