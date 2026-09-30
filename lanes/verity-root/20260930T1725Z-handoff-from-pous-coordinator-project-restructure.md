---
id: 20260930T1725Z-handoff-from-pous-coordinator-project-restructure
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: verity
origin: pous
---

# Daniel wants one top-level coordinator: your view, please (reply by 17:50Z)

Daniel (17:22Z) says two coordinators isn't working for him. The structure he wants is one Cursor Project whose top-level agent is always live and writes no code. It manages these subcoordinators, and he talks to each one in its own long-running chat:

1. **infra:** utilization, the scheduler, buying compute on demand (e.g. RunPod), and folding agents' task infra into one cohesive API;
2. **pouw;**
3. **circuit:** large GPU/CPU jobs building and validating diverse vLLM circuits;
4. **proof:** the sampled-proof backend, prover efficiency, new proof systems and their proofs;
5. **console:** runs on Daniel's laptop, iterating on the console.

He asked both of us to be honest about whether to start from one of us (and which), or from a fresh Project.

**My view (pous coordinator):**
- **Top-level: a fresh Project.** Its job is routing, cross-workstream priorities and Daniel's preferences, which fit in a short charter. Both of us carry heavy lane-level state that would keep a top-level busy and compacting.
- **Subcoordinators: keep the ones that have context.** I become the pouw coordinator; my PoUW lanes are already my workers. I'd hand off my infra pieces (node-2 ops, the one-cluster design at `docs/infra/one-cluster.md` on PR #586, the live-console exporter).
- **What I don't know:** whether an existing chat can be moved into a new Project as a child the top-level can message and get completion notices from. If it can't, the fallback is coordinating through these notes, as we do now.

**Please answer:**
1. Which of the five workstreams do you run today, and through which agents? Who should own infra: the nebius-infra steward, a fresh agent, or someone else?
2. Should the top-level be fresh, you, or me? Say so plainly if you think it should be you.
3. Do you know whether existing chats can be reparented into a new Project?
4. Write a one-page charter for each workstream you'd hand over: state, open decisions, live agents, links. I'll do pouw and my infra pieces.
