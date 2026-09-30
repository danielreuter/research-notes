---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-attention
created: 2026-09-30T07:56Z
---

# port-capture's setup fails from a submit.sh tree (BOOTSTRAP_FAIL_CHECKPOINT); I'm running the NVFP4 capture with a one-line setup override

- **What failed.** Kueue job 35 (`port-capture`, submitted with `submit.sh`) ended `FAILED_SETUP` after about 36 min, including one "preempted" recovery. The template's setup runs `pod_bootstrap.sh` inside the synced tree `/workspace/research/trees/<lane>`. Its `integrations/vllm` is owned by `research` with mode 755, so the job's uid 1000 can't create `out/bootstrap`. The `tee` into `bootstrap.fail` fails, and the run ends at `BOOTSTRAP_FAIL_CHECKPOINT: B0`. In GPU mode it would also try to build the native taps.
- **The override** (untracked, `jobs/port-capture-attn.yaml`): the same template with setup reduced to the `uv` guard plus a check that `/workspace/jobs/venv312` imports vLLM `d9105ea80`. That venv already exists (tc-gemm's `--cpu` bootstrap). The run step is unchanged. It's resubmitted as job 56 (`nvfp4-capture-attn-2`).
- **Suggested fix for everyone:** the template's setup passes `--cpu --out /workspace/jobs/bootstrap-<lane>` (or the tree gets group-writable `out/`). Tap-needing jobs (Commits) run through `config-run` anyway.
- **Also:** `submit.sh` needs `uv` and `rsync` on the lane VM; both were missing on mine, so I installed them. It does sync untracked files (`git ls-files --cached --others --exclude-standard`).
