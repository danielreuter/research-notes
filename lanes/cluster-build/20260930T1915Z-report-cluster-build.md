---
id: 20260930T1915Z-report-cluster-build
campaign: verity
lane: cluster-build
kind: report
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a), worker of the infra coordinator (bc-17cc41f1); takes over tools/cluster from bc-c3ade0aa
---

CHECKPOINT 24ae54f35 (19:12Z) [open] started: read plan+design+replies, copied node-2 logs read-only; next: #586 step 1 (workstreams, ledger-only state, usage/v1, 2b, defaults)
# cluster-build: the node-2 cutover's code (#586 follow-ups, the adapter, the agent, gpu-lease's agent mode) up to a shadow run ready to start

Branch `cursor/cluster-foundation-7e9f` (#586), base tip `24ae54f3`. Node-2 side on `infra/nebius` (#496), base `13f402b2`.
Nothing is started on either node until the infra coordinator relays Daniel's approval of the cutover plan.

Read: `note:20260930T1858Z-handoff-from-pous-one-cluster-to-infra-cutover-plan`, `note:20260930T1858Z-draft-one-cluster-design`,
the 17:21Z, 17:27Z, 18:05Z, 18:07Z and 17:22Z replies, and `note:20260930T1856Z-handoff-from-pous-infra-hand-back`.

## Log

- 19:12Z: copied today's node-2 logs off the node, read-only at `nice 19` outside a window (`preempted.log`, `quiet.jsonl`,
  fill `events.jsonl`, the sampler's `util/2026-09-30.jsonl`, and the live `node_ops.py`, `gpu_util_sampler.py`, `gpu-lease`).
  Live `gpu-lease` sha256 `0d172cf3…`, as the hand-back says.
