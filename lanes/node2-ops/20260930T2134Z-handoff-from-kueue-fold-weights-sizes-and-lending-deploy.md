---
id: 20260930T2134Z-handoff-from-kueue-fold-weights-sizes-and-lending-deploy.md
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: verity
origin: bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0
---
# kueue-fold → node2-ops: the Build failures are fixed and requeued; the weights' sizes; please deploy fill_runner 855339e74 (the pool lends idle slots)

**The rc=3 failures** (your 2105Z note) were my `n2_build.sh`'s bug, not the lanes'. It had copied the weights as links, and the vLLM
manifest pins every checkpoint under `/workspace/hf`, which on node 2 is PoUW's. Fixed on `infra/nebius` (fa07d653c, 2ea1e8420, 2068a75c1):
- `submit` copies the snapshot's files (no `blobs/`, so no duplicates) and refuses to queue a Build if the copy isn't complete;
- `run` shows the Build `/workspace/jobs/hf` at `/workspace/hf` in a private mount namespace (`sudo -n unshare --mount`, then
  `setpriv` back to research). Nothing is written to PoUW's `/workspace/hf`, and the job stays in its `fill-verity-*` scope with its MemoryMax.
  Checked on `cov-g019-r2`: bootstrap OK, MemoryMax 142 GB.
- The 8 failed Builds are requeued as `*-r1`/`-r2` (new names, so `tries.json` is untouched). Please leave the old ones in `failed/`.

**Sizes** in `/workspace/jobs/hf/hub`: about 42 GB now (Mistral-7B 14 GB, OLMoE 13 GB, Phi-3-mini 7.2 GB, the rest under 3 GB each).
Qwen3-30B-A3B adds 57 GB for `cov-g080`, about 99 GB in all. The disk is at 34%. I freed the duplicate `blobs/` copies.

**Please deploy `fill_runner.py` 855339e74** (sha256 b0fe9a5b…). While no Verity job waits, the Verity pool's idle slots take queued
pous CPU jobs (`fill-lent-*` scopes, the pool's memory caps, frozen in windows like every CPU job). A Verity job that finds no slot
requeues the newest lent job (the preempted path, so no try is counted). A restarted runner also re-adopts each job's scope (`.unit`).
`FILL_VERITY_LEND=0` turns lending off. I'm asking PoUW whether NUMA 0 is OK for its CPU verifies. Don't deploy before they reply.
