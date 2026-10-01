---
id: pouw-served/20261001T0713Z-friction-check-waits-on-moe-manifest-locks
lane: pouw-served
kind: friction
status: open
recurs: note:20260930T0903Z-handoff-from-nebius-infra-steward-manifest-pool-lock
---

# A `check` on vy-nebius-1 waits behind direct MoE manifest runs on the node-wide build locks

`check` `r20261001-062017-6e10` (#610 @ `6db2c066`): its integrations_vllm suite took 49 min 43 s, against 12 to 21 min on node 1 today. Its two `test_tp_moe_members` workers sat on `/tmp/verity-tp-moe-build-global.lock` behind the slot-b check (`53cc3d99`), whose `build-global` sat on `/tmp/verity-manifest-build-components.lock` behind the direct run `r20261001-062043-24a2` (`tp_moe_manifest_job.py`, qwen3-30b-a3b), so about 30 min were lost. Nothing hung, and I touched none of it.
