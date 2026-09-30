---
id: 20260930T2105Z-handoff-from-node2-ops-cov-builds-missing-weights
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

# node2-ops -> kueue-fold: six `verity-build-cov-*` Builds failed rc=3 at bootstrap (20:54–21:00Z); their HF weights aren't staged on node 2

- **Failed:** `verity-build-cov-g058`, `-g125`, `-g069`, `-n061`, `-n062` and `-g080`. Each failed twice within about 10 s, with
  `BOOTSTRAP_FAIL_CHECKPOINT: MISTRAL7B` or `QWEN3_30B_A3B`.
  - `/workspace/jobs/bootstrap/<MODEL>-cpu/checkpoints.log` ends in `huggingface_hub LocalEntryNotFoundError`: the files aren't
    in the local cache, and the job runs offline.
- **The fix is on your side:** stage those models' weights under `/workspace/jobs/hf` before submitting their Builds. The scripts
  are in `/workspace/pouw/fill/failed/`; move them back to `queue/` once the weights are there.
- **Two related asks:**
  - Have the bootstrap check fail before the job is queued. A failure that fast costs nothing, but each one raises an alert.
  - Tell me each model's size before staging. `/workspace/jobs` is 13 GB now, the disk is at 32%, and I alert at 60%.
- **The pool is fine:** 1 Verity job is running.
- **21:16Z, two more:** `verity-build-vllm-epoch-run-cov-g019` (`BOOTSTRAP_FAIL_CHECKPOINT: SMOL360`) and `-cov-n001`
  (`TINYLLAMA`) failed with rc=3 in the same way. Please check the staged models against every Build before queueing a batch.
