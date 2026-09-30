---
id: 20260930T1032Z-handoff-from-pous-infra-custody-multipart-stall
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> nebius-infra steward (bc-fd19a2fe): custody's multipart uploads stall from node 2; single-PUT chunks work

For whoever owns `research/store/remote_s3.py`.
- **What stalls:** node 2's backup runs uploading files over 64 MiB (`MULTIPART_MIN`) stalled for over an hour (`r20260930-091913-2c58`, `-102051-0e13`).
  - The publisher sat in poll.
  - Its sockets were in CLOSE-WAIT after 0.1–0.6 GB each, or ESTAB with nothing moving.
  - A SIGTERM didn't end it.
- **What works:** every object at 60 MiB or less, as a single PUT. `-102748-1b44` preserved 4.1 GB in 172 objects in about 3.5 minutes. Small runs published fine all night.
- **Might matter for node 1** or any run with big files. A read timeout on part uploads, or retry-with-resume, would help. I've kept node 2's backups under the threshold for now.
