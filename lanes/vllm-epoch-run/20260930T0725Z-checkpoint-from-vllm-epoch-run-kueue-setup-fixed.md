---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T07:25Z

**sm_120 cells are on Kueue.** k01 (SmolLM2-135M) is RUNNING and building the FA2 tap; k02–k05 are queued. PR #503 carries #470's two follow-ups, and its merge request is filed. Every `config-run` job failed setup until these five fixes, which the TP2 preview also needs:
- **Template:** `jobs/config-run-night.yaml`, an untracked sweep-night copy. The bootstrap gets `--out /workspace/jobs/bootstrap-cov/$ROLE`, and runs under `env -u REPO`: the job's `REPO` (the model) was read by `pod_hidden_gpu.sh` as the tree.
- **Taps directory:** `/workspace/cp` is now mode 1777 (the taps build there as uid 1000).
- **Tree output directory:** `<tree>/integrations/vllm/out` is pre-created at mode 1777. It is gitignored, so syncs keep it.
- **CUDA toolkit:** the job image has no `nvcc` and the host's is 13.0. A CUDA 12.9 toolkit from NVIDIA's redist archives (nvcc 12.9.86, cudart, cccl, nvtx, nvrtc, plus the venv's cuBLAS/cuSPARSE/cuSOLVER headers) is at `/workspace/jobs/cuda-12.9`, and jobs get `CUDA_HOME` pointing there.
- **Shared build cache:** `TORCH_EXTENSIONS_DIR=/workspace/jobs/torch-extensions`.

`REVISION` stays the checkpoint's HF revision: the template's `row run ROW ROLE REPO REVISION` takes it. The tree is the `submit.sh` sync of `cursor/coverage-v0-2622` @ `a8e331c7`.
