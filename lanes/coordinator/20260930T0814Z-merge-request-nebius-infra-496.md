---
id: 20260930T0814Z-merge-request-nebius-infra-496
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Merge request: #496 (`infra/nebius` at `eb2553d6`), the shared Nebius server code; it supersedes landing #485, #488 and #504 separately

- **PR:** [#496](https://github.com/danielreuter/verity/pull/496), now ready. It merges cleanly onto main `f0da69ad`, and its 23
  changed files are all under `tools/research/`.
- **Carries:** #485 (head `fa03a5c8`), #488 (`0ad80ec2`), #504, and the fixes both sides pushed tonight. The details are in the PR
  body.
  - The #485 × #488 conflict is resolved, as is the `gpu_lease.sh` conflict.
  - The two host-leak test fixes node-1 checks need (`b20aa7e1`, `e5a7fbd2`) are in, beyond #504.
- **Tests:** `suites.py research repository` passes on `eb2553d6`. Only the research and repository suites are affected.
- **Where:** any train. If #488 is already in TNC, take #496 after TNC, and it merges as a superset.
- **Afterwards:** the steward merges main back into `infra/nebius`. Please take the tip current when your train starts, and post
  its sha here. Both sides push to it all night.
