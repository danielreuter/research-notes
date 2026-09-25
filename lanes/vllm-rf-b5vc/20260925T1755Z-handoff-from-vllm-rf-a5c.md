---
lane: vllm-rf-b5vc
kind: handoff
from: vllm-rf-a5c (bc-ac8c8a30)
created: 2026-09-25T17:55Z
---
# vyv-rf-a5-t1 (RunPod cyu8vao39x21th, 32 vCPU / 755 GB, $1.76/h) is yours

Nothing of a5c's is running on it; all my runs are preserved on R2. Registered in machines.d, guard 90.

- venv `/workspace/venv312` (pytest 9.1.1 + xdist). HF `HF_HOME=/workspace/hf`. Shipped trees `/workspace/research/src/<sha>/`.
- **Gate (a) fixtures:** all 26 rows in the local store `/workspace/research/store`; no key on the pod (`/root/r2ro.env` deleted).
  Script `/workspace/a5/gate_a.sh TREE TAG` (copy it into your own dir; don't edit). Base XML
  `/workspace/a5/gate_a-t0t1-base-72884c8a-samepod.xml.gz`, jdiff `/workspace/a5/jdiff.py` (sha256 363304c0…). Gate (a) T0+T1
  takes about 1 h 40 min.
- **Gate (b):** `/workspace/a5c/gate_b.sh TAG` from the tree root (`research run --cwd source`): lints then `-n 12 --dist loadfile`,
  about 14 min each. A base run at main `f7de4620` is already there: `/workspace/a5c/logs/base-f7de4620-{lints,gate_b}.xml`
  (run `r20260925-173534-b495`) — reuse it if your base is `f7de4620`.
