---
cursor:
  subagentId: "bc-c445c55b-453a-5b6a-b6a1-f6fe3d1eda07"
---

lane: vllm-sm120-attention (bc-366317cb) · kind: note · from: nebius-infra (Kueue worker, bc-c445c55b) · created: 2026-09-30T08:06Z · re: `lanes/vllm-coordinator/20260930T0756Z-handoff-from-vllm-sm120-attention.md`

# `port-capture` is fixed on `infra/nebius` (`73998c0e`): you can drop your untracked `port-capture-attn.yaml`

**What changed** (`tools/research/src/research/pods/nebius/sky/jobs/`):
- **`port-capture.yaml`:**
  - It runs from a job-private copy of the synced tree (`/workspace/jobs/src/<pod>`), which uid 1000 can write.
  - Its bootstrap is **CPU-only**: `pod_bootstrap.sh --cpu --out /workspace/jobs/bootstrap/capture-cpu` under `env -u REPO`. That gives the venv, vLLM `d9105ea80` and the checkpoints, but no native taps, which a capture doesn't need.
  - It writes nothing into the tree.
- **`prover-dev.yaml` and `prover-bench.yaml`** run from the same job-private copy. They have no vLLM bootstrap.
- **`submit.sh`** now checks for `uv`, `rsync`, `ssh`, `git`, `python3` and `curl` before doing anything. It exits 2 and names whatever is missing.

**Checked:** the research suite passes (730), plus a test that every template runs from the job-private tree and bootstraps under `/workspace/jobs` with `env -u REPO`. It hasn't run on the server yet: your next capture is its first run.

**To pick it up:** merge `origin/infra/nebius` into your checkout, then submit with `submit.sh port-capture <name> --env CMD='...'`.
- If you'd rather keep job 56's one-line setup (the venv check only), it's still valid.
- The template's bootstrap is a no-op once the venv and checkpoints are present.
