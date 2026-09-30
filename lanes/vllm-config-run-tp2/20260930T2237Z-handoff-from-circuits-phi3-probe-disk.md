---
id: 20260930T2237Z-handoff-from-circuits-phi3-probe-disk
campaign: verity
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); cc vllm-coordinator (@old-circuits-and-proofs)
---

# @circuits: node 1's disk is near its hard stop: phi3b8m and phi3b8f are released for deletion; phi3b8g finishes, then its bundle goes

Node 1's `/workspace` is at 78%, and infra asked (Slack, 3:34 PM PDT). I answered at 3:36 PM PDT:
- `jobs/probe-jit/cfgtp2-deferred-phi3b8g` (~102 GB, Commit ended 3:32 PM, "COMMIT PENDING") **finishes**: let its CPU replay run, then
  delete the bundle (rc 0 + `config_record.json`). Send the replay's measured peak RSS and the bundle size to the steward and to me.
- `cfgtp2-deferred-phi3b8m` (61 GB) and `cfgtp2-deferred-phi3b8f` (12 GB) are **released**; infra deletes them now. If you need
  anything from them, copy it out in the next few minutes and tell infra.
- Don't start another Phi-3 B8 probe until #599's slim bundles land.
