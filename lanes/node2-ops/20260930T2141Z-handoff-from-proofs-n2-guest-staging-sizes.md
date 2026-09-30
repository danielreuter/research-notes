---
id: 20260930T2141Z-handoff-from-proofs-n2-guest-staging-sizes
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-n2-guest (bc-c951b059), worker of @proofs (bc-8416bc72); infra approval 2:28 PM PDT
---

# node2-ops: Verity guest staging for Llama-3.2-1B whole-row proving: about 0.2 GB copied, about 3.5 GB kept, at most about 165 GB transient

Everything goes under `/workspace/verity-guest/wholerow/` (nothing under `/workspace/pouw`, `/workspace/hf` or `/workspace/research`).
The copy comes from node 1 over `ssh vy-n2`, and it waits whenever `fill/status.txt` says `timed True`. Disk was 35% at 2:41 PM PDT.

| What | Size | From |
|---|---|---|
| `tree/`: backend-sweep-2's tree, `70e99f57e`, clean | 84 MB | node 1 `/workspace/research/trees/backend-sweep-2` |
| `flock/flock-circuit/bin-4d568a3cb558b005-g1-sm120/`: prover and selftest binaries (#554's draft key) | 28 MB | node 1 `/workspace/jobs/flock-sweep2/flock-circuit/` |
| `sweep2/llama32-1b__…/`: `counts.json` and `shapes.tsv` | 3.5 MB | node 1 `/workspace/jobs/sweep2/` |
| `flock/flock-circuit/py/`: venv with numpy 2.5.3 and blake3 1.0.10 (uv, PyPI; `/workspace/jobs/cache/python`'s CPython 3.12.14) | ~0.1 GB | built on node 2 |
| `flock/stage-cache/`: about 14 staged shapes, by gpus=0 stage jobs | ~1.5 GB | built on node 2 |
| `runs/`, `done/`: each chunk keeps its summary, records and 3 session transcripts | ~20 MB a chunk, ~2 GB total | written by jobs |
| Transient: a running chunk's session transcripts, about 1.6 MiB a statement, pruned to 3 at the chunk's end | ≤ ~20 GB a chunk, ≤ ~160 GB with 8 at once | written by jobs |

- **No model weights are needed.** The statements are staged from synthetic lanes (`class_statement.class_lanes`), not from the checkpoint.
- **CUDA:** the binaries use node 2's own `libcudart.so.13` (`/usr/local/cuda`, driver 580.173.02, the same as node 1). Nothing is installed.
- **Jobs:**
  - gpus=0 stage jobs: `cpus=16 mem_gb=64 max_min=60`. They get a stub `nvidia-smi` on `PATH`, so they make no NVML calls.
  - gpus=1 chunk jobs: `cpus=16 max_min=30`, each about 15 min of proving. The owner is bc-8416bc72, and the names start with `pn2g-`.
  - Each loopback verifier binds its own free port on 127.0.0.1, not 7710.
- **Refill loop:** tmux `proofs-n2-guest` on node 2 keeps 8–12 chunk scripts queued, and logs to `/workspace/verity-guest/feed.log`.
- **Cleanup:** I delete a chunk's transient files when it ends. I delete the whole tree once the rows are done and their outputs are back on node 1.
- **One slip to report:** at about 21:35Z (2:35 PM PDT) I ran one `nvidia-smi --query-gpu=driver_version,name` over ssh, before I saw a timed window was on. I've made no NVML calls on node 2 since, and I'll make none outside jobs.
