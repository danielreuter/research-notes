---
id: 20260930T2225Z-handoff-from-infra-circuits-overnight-yes-node2-node2-ops
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1); relaying circuits' research owner (bc-ecac3029), Slack thread 1790806675.530699, 3:18 PM PDT
---

# Overnight yes for circuits' Commits on node 2, about 8–10 GPU-h, gated on cov-g217 reproducing node 1 byte for byte (for n2-commits and node2-ops)

**The gate:** `cov-g217` must reproduce node 1's run root and record **byte for byte**. If it doesn't, none of these count, run
nothing, and node 2 stays idle. Report the comparison in `lanes/infra/`.

**Order and questions** (put each job's question in its header):
1. **The 8 #557 Qwen2.5 reruns, first** (about 2 GPU-h): cov-n087, n088, k03-8, n082, n084, n085, n083 and n111. Question: "Does
   GemmBias_v2 replay the served biased linears 460/460 on sm_120?" (Triton matmul_persistent, then a bf16 bias add).
2. **Commit-ready small-model deployments** (about 6–8 GPU-h). Question: "sm_120 coverage of distinct served code paths." Coverage by
   model:
   - Qwen3-4B: q/k norm;
   - Pythia: LayerNorm and parallel residual;
   - Phi-3-mini: fused qkv and gate_up;
   - Qwen2.5-0.5B/1.5B: biased qkv;
   - SmolLM2, TinyLlama and Llama-3.2-1B: Llama-family shapes plus top-p at B1/B8/B32.

   Scope: one deployment per (model, batch, sampler) path. **No reruns of deployments that already passed on node 1.**

**Rules:** each job is moved from node 1's pending Commit under the same dispatcher key, so nothing runs twice. Guests are evicted
first and frozen in PoUW windows. Record the driver, the vLLM pin `d9105ea80` and the clock state in each Commit's record. circuits
confirms the exact count from the staged queue.
