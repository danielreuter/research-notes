---
id: 20260930T2150Z-handoff-from-circuits-node2-commits-first-batch
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); cc vllm-epoch-run
---

# circuits → kueue-fold: node-2 Commits as preemptible guests: environment check, a cross-node check, then 8 Qwen2.5 reruns first (running by 4 PM PDT)

Circuits' single-GPU Commits are node 2's main fill until PoUW's backlog lands at 10 PM PDT (top-level, 2:49 PM PDT). Node 1 and node 2
are the same GPU (RTX PRO 6000 Blackwell Server Edition, sm_120), so a node-2 Commit counts; its 460-unit replay checks it either way.

1. **Environment check** (outside a timed window; no NVML polling in one). Record it next to each guest Commit, and once in
   `lanes/circuits/`:
   - driver version (node 1: **580.173.02**);
   - SM clock state (node 1: unlocked, max 2,430 MHz; node 2: locked 2,100 MHz);
   - the tree's vLLM pin **`d9105ea80`**, its venv's vLLM and torch versions, and the tree commit (the run branch is
     `cursor/coverage-v1-2622`, tree `/workspace/research/trees/cursor-coverage-v1-2622` on node 1).
2. **Cross-node check first (~2 GPU-min):** Commit `cov-g217` (Llama-3.2-1B B8 256/32 greedy, which passed on node 1) on node 2, and
   compare its run root with node 1's (`/workspace/jobs/cov/cov-g217/llama32-1b__bf16__rtxpro6000__tp1__b8__i256__o32__mixed__greedy__bi-eager/`).
   Run roots are deterministic across reruns on node 1, so they must be equal here. If they differ, stop and tell me.
3. **Then these, in this order** (Commit-ready on node 1: `manifest.json` + `build_summary.json`, no `commit*`; a row is ~120 MB).
   The first eight are the Qwen2/2.5 reruns on #557, which the review ranked most valuable:
   - Qwen2.5-0.5B: `cov-n087` (B8 greedy), `cov-n088` (B8 top-p), `cov-k03-8` (B1 greedy), `cov-n082` (B1 top-p), `cov-n084`
     (B1 1k greedy), `cov-n085` (B1 1k top-p), `cov-n083` (B1 top-p p=1);
   - Qwen2.5-1.5B: `cov-n111` (B1 greedy; stage it at submit);
   - then Phi-3-mini `cov-g167`, TinyLlama `cov-g142`, `cov-g092`, `cov-g043`, SmolLM2-360M `cov-g116`, `cov-g119`, Llama-3.2-1B
     `cov-g153`.
   - Each row is `/workspace/jobs/cov/<key>/<row>/`, the only `*__*` directory under the key.
4. **No double runs:** each of these has a node-1 Commit task pending under the dispatcher key `vllm-epoch-run/<key>`. Move it the way
   `offload` moves Builds (one owner per key, results back to node 1's `SWEEP_DIR`, the Attempt to R2). The simplest standing rule:
   a Commit Kueue holds on node 1 for N minutes moves to node 2, if its model is staged there.
5. **Replay:** run the CPU replay task on node 2 beside its bundle (these bundles are ≤ a few GB), or copy the bundle back with the
   row.

Evicted guests just rerun; windows (≤5.3 min) stay under the Commit's 15-minute quiet watchdog. Send the first node-2 run id and the
run-root comparison to `lanes/circuits/`.
