---
id: 20260930T1902Z-handoff-from-verity-top-circuit-charter
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-top (the top-level coordinator, bc-7f347b4b)
---

# You're the circuit subcoordinator now, under the top-level: please ack in lanes/verity-top/

- **Who you report to:** the top-level coordinator, lane `verity-top` (Slack `@top-level`), no longer verity-root. Your
  remit, workers and open items are as in your charter, `note:20260930T1900Z-handoff-from-verity-root-charter-circuit`.
- **Infra items:** send your "hands to infra" items to `lanes/infra/`, for the infra coordinator
  bc-17cc41f1-6227-5fab-bc64-3fa2f224558b. Those are the three-task config-run layout (Kueue templates, persistent caches, the
  ~2 min Commit GPU hold) and the GPU-idle alerts on coverage jobs.
- **Daniel's decisions:** bring them to `lanes/verity-top/` with your recommendation (for example, closing #483 and #501).
- **Merges:** unchanged. The research coordinator runs the trains; you grant the vLLM parts.
- **Ack:** one line in `lanes/verity-top/<ts>-reply-from-vllm-coordinator-circuit-ack.md`, and correct the charter there if
  anything in it is wrong.
