---
lane: vllm-rf-b5vab
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T17:00Z
---
# Fixture keys: you may now mint on your VM (owner-approved)

`lane-briefs/vllm-cloud-common.md`, section "Gates", bullet "Fixture keys", now allows a 3 h read-only key, minted on
your VM and scoped to `manifests/` + `objects/sha256/`, piped into your own pod, and deleted there right after the
fetch. Log each mint in your report. Read the exact conditions there before your first mint.
For you: don't wait for c4ir-reg. When your head is final, create your own gate (a) pod (cpu3m, 32 vCPU / 256 GB or more; name it `vyv-rf-b5vab-reg`), prefetch with a minted key, delete it, and run gate (a). This replaces the c4ir-reg handover.
