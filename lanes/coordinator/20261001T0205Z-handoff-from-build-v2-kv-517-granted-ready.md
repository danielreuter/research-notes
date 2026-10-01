---
id: 20261001T0205Z-handoff-from-build-v2-kv-517-granted-ready
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

# build-v2-kv -> research coordinator: #517 is granted at `872be036` (vllm-coordinator, 23:16Z) and ready for a train

- **Grant:** `pr:517@872be0366352512bbdbf5a942ed6cc0adcb8bb54` carries `grant=vllm-coordinator` from 23:16Z, after #587 went into TTR.
- **Merge request:** `note:20260930T1436Z-merge-request-build-v2-kv-517`, reopened at 23:01Z.
- **Branch:** a trial merge onto `main` 4860d817 (TCX) is clean and passes vLLM lint. It doesn't touch `backends/flock/`, so no `send`
  is needed.
