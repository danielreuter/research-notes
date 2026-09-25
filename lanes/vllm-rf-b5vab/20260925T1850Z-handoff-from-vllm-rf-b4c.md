---
lane: vllm-rf-b5vab
kind: handoff
from: vllm-rf-b4c
created: 2026-09-25T18:50Z
---
# Pod handover: `vyv-rf-b4b-g1` (RunPod nplcyinf9r2si8, 1x L40S) is yours

Nothing of b4c's runs on it (last run `r20260925-184105-e73e` finished; every b4c run on it is PRESERVED on R2). Registered in
machines.d as `vyv-rf-b4b-g1`, guard 90, $1.09/h; b4c no longer touches it.

- Driver 580.159.04 / CUDA 13.0; the image's toolkit is nvcc 12.4 (`/usr/local/cuda-12.4`).
- venv `/workspace/venv312` (pod_bootstrap.sh gpu mode; no pytest-xdist). HF_HOME `/workspace/hf` holds B0 and LLAMA32_1B.
- Taps built: hidden_gpu (`/root/.cache/torch_extensions/py312_cu129/hidden_gpu_tree/`) and the FA2 matReq tap
  `/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so`. **The FA2 tap build fails with the default MAX_JOBS=nproc (128)**
  on this pod; with `MAX_JOBS=12` it builds in about 7 min. The bootstrap is idempotent, so a re-run keeps the .so.
- #101 at b4c head `9689a1ef` (a5's CLI: `ops/row_pod.sh` is gone): `/workspace/b4c/g1_cli.sh TAG`, run as
  `research run --on vyv-rf-b4b-g1 --project verity --custody-r2 --source <tree> --cwd source -- env MAX_JOBS=12 bash /workspace/b4c/g1_cli.sh TAG`.
  Its non-interference step uses the old module entry, which exits 0 silently after a5; use
  `/workspace/b4c/nonint_cli.sh TAG` (`python -m verity_vllm.pipeline.cli noninterference ...`) instead.
  b4c's result at `9689a1ef` (`r20260925-180228-0dda`, `r20260925-184105-e73e`): program `ccc21347…`, manifest `90f81868…`
  (7043), run root `7adcef49…`, commit PASS, non-interference 992/992 = record. Outputs under `/workspace/b4c/`; please use your own TAG.
