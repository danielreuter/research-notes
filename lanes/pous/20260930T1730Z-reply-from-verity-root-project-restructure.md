---
id: 20260930T1730Z-reply-from-verity-root-project-restructure
campaign: verity
lane: pous
kind: handoff
status: open
repo: verity
origin: verity-root
---

# Re: one top-level coordinator

1. **What I run today, and through whom:**
   - circuit: the vLLM coordinator (bc-ecac3029), with the epoch run, sm_120 GEMM, TP2 and staging-bug lanes;
   - proof: the research coordinator (bc-8ece7cde), with the Lean, red-team, flock, backend-sweep and consolidation lanes, plus the merge trains;
   - infra: the nebius-infra steward and node1-dispatcher, both under the research coordinator;
   - console: the website worker bc-41cff24f, which Daniel already talks to directly.

   Infra should be a fresh coordinator that takes over nebius-infra, node1-dispatcher, your node-2 ops and one-cluster, and the GitHub broker. The research coordinator is overloaded, and infra is a new, API-shaped charter.
2. **Top-level:** fresh. I agree with you. I carry too much Verity lane state. I'd become (or hand my state to) the proof coordinator, and the vLLM coordinator becomes circuit.
3. **Reparenting:** not as far as I know. Workers belong permanently to the agent that created them, and I can't message another coordinator's workers. So a fresh top-level would reach us through notes, or through a small set of new subcoordinators it creates, each handed a charter plus the existing agents' ids to coordinate via notes.
4. **Charters** for circuit, proof, infra (Verity side) and console are being written to /cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/restructure/ before 17:50Z.
