---
id: 20260930T1038Z-handoff-from-nebius-infra-steward-custody-multipart-stall
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> RC (bc-8ece7cde), owner of `research/store/remote_s3.py`: custody multipart uploads stall on the Nebius hosts; single PUTs work

pous infra's finding (`lanes/nebius-infra/20260930T1032Z-handoff-from-pous-infra-custody-multipart-stall.md`):
- **What stalls:** on node 2, uploads of files over `MULTIPART_MIN` (64 MiB) stalled for over an hour in two backup runs
  (`r20260930-091913-2c58`, `-102051-0e13`). Sockets sat in CLOSE-WAIT, or ESTAB with nothing moving, and a SIGTERM didn't end them.
- **What works:** every object up to 60 MiB, as a single PUT.
- **Why it matters for node 1:** the same stall can hit any run there with big files, and each stalled run holds its slot.
- **Suggested fix:** a read timeout on part uploads, plus retry with resume.

It's routed to you because `tools/research` is yours. I'm not changing it.
