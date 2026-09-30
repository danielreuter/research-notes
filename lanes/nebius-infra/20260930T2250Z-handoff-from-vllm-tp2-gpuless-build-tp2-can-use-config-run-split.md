---
id: 20260930T2250Z-handoff-from-vllm-tp2-gpuless-build-tp2-can-use-config-run-split
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-tp2-gpuless-build (bc-217501a5), for the Nebius steward (bc-fd19a2fe) and vllm-epoch-run; cc vllm-coordinator (bc-ecac3029)
cursor:
  subagentId: "bc-217501a5-aa77-56c0-b6c5-dc3a7291ec1f"
---

# TP2 deployments can use `config-run` (the split template): a 0-GPU Build task, then a 2-GPU Commit task

**Needs the tree to carry** `cursor/tp2-gpuless-build-ec1f` @ `4009ec303` (PR not opened yet; see
`note:20260930T2250Z-handoff-from-vllm-tp2-gpuless-build-tp2-builds-without-gpus` in lanes/vllm-coordinator/). Without it, a
GPU-free TP2 Build fails with "World size (2) is larger than the number of available GPUs (0)".

**Evidence:** a CPU-only TP2 Build of `llama32-1b__bf16__rtxpro6000__tp2__b1__i256__o32__mixed__greedy__bi-eager`
(`r20260930-212809-14a0`: NVML refused, `CUDA_VISIBLE_DEVICES=`) gives the same per-rank Program, workload and manifest digests as
a GPU-visible Kueue Build on the same tree (`r20260930-220713-8e26`). Build wall time was 220 s, with a 14.3 GiB peak.

**What to change:**
- **Steward:** `config-run.yaml`'s `tp2` row ("until then TP deployments are unsupported") can drop that caveat once the branch
  lands. The Build task needs no GPU, and the Commit task keeps 2 GPUs and `NCCL_P2P_DISABLE=1` (unchanged: `row_tp` sets it).
  The `tp2` class's 160 GB Build is ample for a 1B model (14.3 GiB measured). Larger TP2 models have no measurement yet.
- **epoch-run:** submit TP2 items as `{"template": "config-run", "class": "tp2", …}` instead of `config-run-row`, from a tree
  with the branch. Make the first one a canary: the 2-GPU Commit reading a Build made in another pod has not been run yet.
- **Scope:** only rows with a declared target build GPU-free: `__rtxpro6000__` rows (every GPU on both nodes), or a workload
  `target`. Others still need their GPU in the Build.
