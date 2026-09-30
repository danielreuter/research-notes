---
id: 20260930T2144Z-handoff-from-proofs-replan-2-drop-k2048-rest
campaign: verity
lane: proofs-n2-guest
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Re-plan 2, 2:44 PM PDT (supersedes 2:42 PM PDT): don't queue the K=2048 remainder; only 3 chunks per new shape class, after an environment check

Why: the old vLLM coordinator's verdict (Slack thread `1790804308.098509`). The rest of the K=2048 row is filler tonight.
Failures at scale on #554's unreviewed draft key won't survive a key change, so the full row gets rerun after that key is
reviewed. Node-2 results count only if node 2's environment matches node 1's.

1. **First, check the environment and report it** in your notes lane, without changing anything. Compare node 2 with node 1:
   - the GPU clock lock (node 1: 2,100 MHz; `nvidia-smi -q -d CLOCK`);
   - the driver (node 1: 595.91);
   - the CUDA runtime your prover build uses.

   **If they differ,** your chunks are still valid proofs, but their costs aren't comparable to node 1's: label them so.
   Don't change node 2's clocks or driver; that's a node change and needs Daniel.
2. **Drop the K=2048 remainder** (statements 10,000–50,346). Queue none of it, and remove any of it you've already
   queued and not started.
3. **Only 3 chunks per distinct shape class** (distinct K or tile pattern) among the next-largest Llama-3.2-1B
   coordinates, skipping classes already covered. Stop once each class has 3. That's likely a few GPU-h, not 60: that's
   intended.
4. The rest of the brief stands.
