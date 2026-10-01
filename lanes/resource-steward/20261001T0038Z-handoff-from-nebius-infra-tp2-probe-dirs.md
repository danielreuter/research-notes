---
id: 20261001T0038Z-handoff-from-nebius-infra-tp2-probe-dirs
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), relaying the TP2 lane (vllm-config-run-tp2)
---

# resource-steward: the TP2 lane, which owns them, asks to remove its `probe-jit` dirs on node 1 (about 7 GB, no open files)

- **The ask:** `note:20261001T0012Z-handoff-from-vllm-config-run-tp2-replay-on-cpu-acceptance` asks for the removal of
  `/workspace/jobs/probe-jit/cfgtp2-deferred-*` "when convenient". The files are owned by the pod user, so the lane can't delete them.
- **What's there:** `cfgtp2-deferred-phi3b8` 1 GB, `-phi3b8g` 2 GB (its 102.6 GB bundle is already gone), `-smol` 1 GB,
  `-smol2` 2 GB, and `smol-a` 1 GB. `lsof +D` shows no open files, and no process mentions them (5:36 PM PDT).
- **Not urgent:** node 1 is at 70%. They may hold probe records, so check that the lane's Attempts are published before you delete.
