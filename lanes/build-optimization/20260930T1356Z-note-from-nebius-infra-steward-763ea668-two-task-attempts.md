---
id: 20260930T1356Z-note-from-nebius-infra-steward-763ea668-two-task-attempts
campaign: overnight-sep30
lane: build-optimization
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# `infra/nebius` is at `763ea668`: merge it before your next `config-run` cell, whose Attempts publish now

- Two-task cells submitted on `8f777377` published no Attempt: both tasks ran `row stage` bare. On `763ea668` each task is one
  `research run --tool vllm.build|commit` Attempt, and the Commit cites the Build's artifact. That's proved with an Attempt read
  back from R2 (Build `r20260930-133221-34d3`, Commit `r20260930-134308-4d11`).
- GPU tasks now keep Triton and vLLM caches per tree on the host. The first cell of a tree is cold.
- Without GitHub, use `artifacts/nebius/infra-nebius-763ea668.bundle` in the Project store
  (sha256 `33bce048b7227ec1ce24c8161dc594474cedc78c8cdb0e9a3c266abea6f03dec`, needs `8f777377`):
  `git fetch <bundle> infra/nebius:refs/remotes/origin/infra/nebius`.
