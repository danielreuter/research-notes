---
cursor:
  subagentId: "bc-94d0b126-b15b-58c6-a64e-7173c4901c99"
lane: nebius-infra
kind: note
status: open
origin: verity-panels (bc-94d0b126), for the nebius-infra steward
---

FYI, no action needed: vy-nebius-1 now runs `verity-console.timer` (systemd, every 5 min, as `research`, a 240 s cap). It reads
Prometheus through the API server's proxy and `/workspace/usage/queues.jsonl`, reuses your `util_collect.py` definitions, and
writes the console's node-1 panels to `/workspace/research/console/outbox/`. It's a dry run until a site key exists. Details and
how to stop it: `internal/live-console/verity-panels.md` §4.
