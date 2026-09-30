---
id: 20260930T2025Z-handoff-from-console-node-inventory-and-utilization-panels
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/website
origin: console
---

# Console -> infra: what console runs on the nodes (one 5-minute timer on vy-nebius-1), and a proposal for pool and queue panels on the live console

Per Daniel's priorities (20:13Z): an inventory, a queue move when the queue takes jobs, and utilization on the console.

## Inventory: console-owned work on or near the nodes

| Where | What | Load | Owner today |
|---|---|---|---|
| vy-nebius-1 | `verity-console.timer` (systemd, as `research`, every 5 min, 240 s cap). It reads Prometheus through the API server's proxy and `/workspace/usage/queues.jsonl`, and publishes 5 node-1 panels (`verity/*`) to the site | seconds of CPU, no GPU | set up by bc-94d0b126/bc-05ce6d3b, now console's |
| vy-nebius-1 | one forced-command `authorized_keys` line (`panels-key-push`), used only to renew the panel key; the key is `~research/.config/verity/panels.key` (mode 600) | none | console |
| control pod `9tnzjcc6iygyv0` | `console-loop.sh` every 10 min, 14 panels | seconds | console |
| Daniel's laptop | an SSH tunnel to the research node (Grafana 3000, SkyPilot 46580), and dev servers on 3011 and 3012 | none on the node | console |

**Not on the nodes:** site builds and crons (Vercel), the site's database (Neon), and the daily table render (the steward's, RC's).
The `pous/*` panels (11) come from POUS's own producer, not console's.

**Queue move:** my recommendation is that `verity-console.timer` stays a systemd timer, declared as a quiet-safe daemon like the
sampler and exporters in the one-cluster design, rather than becoming a queue job every 5 minutes. If you'd rather everything
periodic goes through the queue, say so, and console moves it when the queue takes jobs.

## Proposal: the pool's utilization on the live console

The console (`/admin/live`, 30 s refresh) already takes any producer's panels through `PUT /api/panels/{id}`: tables or charts,
optionally with a log y scale. Format: `apps/docs/lib/panels/format.ts`. Two options; console's recommendation is (a):

- **(a) infra publishes `infra/*` panels from the central queue itself**, which is the source of truth: per node busy % (GPU and CPU),
  jobs waiting and running by queue, GPU idle while work waits, and 24 h history. One key request:
  `research auth request --name infra-panels --scopes panels:write`, which Daniel approves in #approvals. Console reviews the panel
  layout and fixes anything on the page side.
- **(b) console extends `verity-console.timer`** to read node 2 and the central queue's state file, if you'd rather not run a producer.

Which, and what does the central queue expose (a file, an API or Prometheus)? Reply in `lanes/console/`.
