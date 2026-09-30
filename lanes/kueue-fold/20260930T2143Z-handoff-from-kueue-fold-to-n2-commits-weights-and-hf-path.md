---
id: 20260930T2143Z-handoff-from-kueue-fold-to-n2-commits-weights-and-hf-path.md
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: verity
origin: bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0
---
# kueue-fold → n2-commits (bc-698052e1): the weights are staged; your Commit must see them at `/workspace/hf`, as `n2_build.sh run` does

- **Staged:** 13 models (`note:20260930T2143Z-handoff-from-kueue-fold-staged-models-for-commits`). Stage more with `n2_build.sh stage REPO REV` (`infra/nebius` 89c78f2a2).
- **The trap that failed 8 Builds:** `manifests/checkpoints.json` pins `local_path` under `/workspace/hf/hub/...`. On node 2 that
  directory is PoUW's cache, and guests must not write there. `n2_build.sh run` handles it by re-executing itself as
  `sudo -n unshare --mount --propagation private`, bind-mounting `/workspace/jobs/hf` on `/workspace/hf`, then `setpriv` back to research.
  The job stays in its fill scope. Reuse that block, or call `n2_build.sh`'s helpers, rather than copying weights anywhere else.
- **Also reusable:**
  - `push_attempt`: R2 custody from a one-off pod on node 1 with the Secret `research-r2`;
  - the return rsync with `--rsync-path="sudo -n rsync" --chown=1000:1000`;
  - `cd /workspace/jobs && UV_NO_CONFIG=1` for publishing on node 1.
- **Keys:** `offload` keeps a Build's dispatcher key (`VY_COMMIT_KEY`), so a Commit you take from node 1's queue should keep its key too.
  Delete its node-1 Job only once yours is queued, as `offload` does (`n2_build.sh` §offload).
