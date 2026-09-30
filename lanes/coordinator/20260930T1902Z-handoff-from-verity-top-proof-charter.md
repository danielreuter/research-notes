---
id: 20260930T1902Z-handoff-from-verity-top-proof-charter
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-top (the top-level coordinator, bc-7f347b4b)
---

# You're the proof subcoordinator now, under the top-level: please ack in lanes/verity-top/, and adopt some idle agents?

- **Who you report to:** the top-level coordinator, lane `verity-top` (Slack `@top-level`), no longer verity-root. Your
  remit, workers and open items are as in your charter, `note:20260930T1900Z-handoff-from-verity-root-charter-proof`.
  You keep running the merge trains for now.
- **Infra items:** send your "hands to infra" items to `lanes/infra/`, for the infra coordinator
  bc-17cc41f1-6227-5fab-bc64-3fa2f224558b. Those are the merge-train machinery (the result cache, pod preflight, the clean-host
  guard #531), Job queue stage 1, the `provers` queue and backfill. The Verity-side infra workers that report to you today
  (steward, Kueue, node1-dispatcher, merge-train time, GPU-busy watcher, guards) move to infra, per
  `note:20260930T1900Z-handoff-from-verity-root-charter-infra`.
- **Daniel's decisions:** bring them to `lanes/verity-top/` with your recommendation (for example, who runs trains after the
  split, the four Lean-organization items, and closing #367, #372, #380 and #391).
- **Proposed adoptions**, all IDLE, left over from pous. Decline any that don't fit:
  - spot-check Lean, bc-e7e2bf3a-f0d8-5b5a-9714-9de87eb030a8;
  - Lean organization, bc-79934c4e-4f8e-5b94-b30b-9474fbcc01f7;
  - README review, bc-63c7f09e-c3a4-577c-90f0-cc091a1dd93b;
  - network timing, bc-6b78649f-a717-5744-b3d4-04b44e9386f3;
  - sampled-proofs circuit and vLLM protocol options, bc-75d1b678-7ce5-5b01-a155-7dde36338030 and
    bc-23d60f13-d4e8-52e4-8b06-ad4faa5c9924. These hold PRs #423, #367, #372, #380 and #391.
- **Ack:** one line in `lanes/verity-top/<ts>-reply-from-coordinator-proof-ack.md`, with the agents you take and the ones
  you decline.
