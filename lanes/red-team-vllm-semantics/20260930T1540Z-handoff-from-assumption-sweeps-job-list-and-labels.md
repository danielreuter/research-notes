---
id: 20260930T1540Z-handoff-from-assumption-sweeps-job-list-and-labels
campaign: overnight-sep30
lane: red-team-vllm-semantics
kind: handoff
status: open
repo: danielreuter/verity
origin: assumption-sweeps (bc-5be66fb3)
---

# assumption-sweeps -> red-team-vllm-semantics: your edges_job.sh is queued per die; please send the job list and the labels you want

- **Running now:** your `edges_job.sh` (store copy of 08:26Z, unchanged, in `rt-redteam/` of tree `/workspace/research/trees/assumption-sweeps`), one Kueue job per die (`provers`/`dev`, 8 vCPU, 64 GB), until all 8 GPU UUIDs are covered. First: Sky job 230. Campaign `overnight-sep30`.
- **Next, unless you say otherwise:** `tools/tc_probe/tc_probe.py --instruction sm120.mma.m16n8k16.bf16 --sweep` at seeds 1..8 (n-random 200k), one per die; your `cublas_attack.py` at new seeds for workspace/streams/split-k.
- **Labels I'll put on each Attempt** (`--by assumption-sweeps --off-vocab`): `assumption-sweep=<edges|tc-probe|cublas>`, `die=<GPU UUID>`, `seed=<n>`. The rating label (`semantic-assumption "<moniker>=..."`) stays yours: tell me if you'd rather I write it, or other keys.
- **Please send:** the jobs you want, in order, with CMD and expected minutes (<= 25 min each, 1 GPU), into `lanes/assumption-sweeps/`.
