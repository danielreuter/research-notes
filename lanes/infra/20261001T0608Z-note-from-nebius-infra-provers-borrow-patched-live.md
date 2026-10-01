---
id: 20261001T0608Z-note-from-nebius-infra-provers-borrow-patched-live
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# `provers`' borrowing was patched live at 11:05 PM PDT and differs from `infra/nebius` `90599edad`; please commit it, or tell me to

- **Live** (`kubectl-patch`, 06:05:18Z): `provers` may borrow 6 GPUs, 124 vCPU and 1280Gi.
- **File** (`90599edad`, Daniel's 6:35 PM PDT "circuits' vLLM work first"): 1 GPU, 96 vCPU and 416Gi.
- The nominal quotas agree: `deployments-gpu` has 6 GPUs, and `provers` has 2.
- I left it as it is. It looks like a deliberate overnight fill, since circuits' queue has thinned to 3 Commits.
- Until the file matches, the hourly drift check reports `DIFFER`. Whoever patched it, please commit it to
  `tools/research/src/research/pods/nebius/sky/kueue.yaml`, or say so and I'll commit it. Revert:
  `kubectl apply` of `90599edad`'s `kueue.yaml`.
