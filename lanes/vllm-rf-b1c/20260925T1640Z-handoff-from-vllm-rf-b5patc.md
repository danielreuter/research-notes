---
lane: vllm-rf-b1c
kind: handoff
from: vllm-rf-b5patc
created: 2026-09-25T16:40Z
---
# Pod handover: `vyv-rf-b5pat-cpu` (RunPod `andiw61o3shls8`) is yours

Per the coordinator's b5patc brief, this pod passes to vllm-rf-b1c for its re-gate. Nothing of b5patc's is running on it
(last run `r20260925-163223-81eb` ended 16:33Z and is PRESERVED on R2). Terminate it when you're done; b5patc won't touch
it again.

- Shape: cpu3g, 16 vCPU, $0.64/h, 80 GB overlay (67 GB free). Registered in `machines.d` as `vyv-rf-b5pat-cpu`, guard 90
  (pod guard pid 302, idle-terminates after 90 min).
- venv: `/workspace/venv312` (`pod_bootstrap.sh --cpu` + `pytest-xdist==3.8.0`; `xgrammar 0.2.7`,
  `googleapis-common-protos 1.75.3`, `uvicorn 0.53.0` pinned). `HF_HOME=/workspace/hf`.
- Shipped trees (read-only by convention): `/workspace/research/src/{109966166e…(a4 base), ba852261…, 4537961b…}`.
- Gate (b) working copies: `/workspace/trees/{b_base=10996616, b_head=ba852261, b_rb=4537961b}`.
- Scripts: `/workspace/b5pat/{gate_b.sh,lints.sh,cpu_chain.sh}` (gate_b.sh copies a tree to `/workspace/trees/TAG`, runs
  `OMP_NUM_THREADS=3 pytest integrations/vllm/tests -ra -n 12 --dist loadfile`, logs to `/workspace/b5pat/logs/TAG.*`).
  a1's jdiff is at `/workspace/b5patb/jdiff.py`.
- Gate (b) XMLs already there: `/workspace/b5pat/logs/{b_base,b_head,b_rb}.xml` (10996616 / ba852261 / 4537961b).
- No regression fixtures on this pod (no gate (a) here).
- Known unstable in gate (b): `tests.commit.test_roundtrip::test_transient_storage_is_released` failed once in three
  full gate (b) runs (b_rb) and passed 10/10 in isolation (5 at 4537961b, 5 at 10996616; run `r20260925-163223-81eb`).
