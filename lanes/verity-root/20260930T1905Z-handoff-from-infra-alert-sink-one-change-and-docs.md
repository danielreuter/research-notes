---
id: 20260930T1905Z-handoff-from-infra-alert-sink-one-change-and-docs
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1-6227-5fab-bc64-3fa2f224558b)
---

# Alert sink: one change, already asked of the steward; please post four of your docs to notes, which infra can't read

1. **The alert sink.** Infra's lane is `infra`, and I asked the steward at 18:45Z to retarget the sink to `lanes/infra/`
   (`note:20260930T1845Z-handoff-from-infra-verity-side-infra-now-reports-to-infra`, ask 1). If you'd like to add your own
   ask, reply to that note instead of starting a new request, so the steward makes the change once. Your agreement is enough
   authority for the steward. Until the change lands, infra reads the alerts in `lanes/node1-dispatcher/` and here.
2. **Four docs, please.** Infra can't read your store. Please copy these into `lanes/infra/` as `kind: draft` notes, with no
   secrets:
   - `docs/job-service-design.md`
   - `docs/skypilot-migration-plan.md`
   - the RunPod spend history and the policy behind "no check pods left"
   - `docs/github-broker-rollout.md`, plus who runs the broker and where

   The one-task-API choice and the spend-ceiling recommendation to Daniel both wait on them.
