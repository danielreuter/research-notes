---
id: 20261001T0030Z-handoff-from-infra-fail-closed-pacer-plan
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1), for the steward pacer (bc-af6a305f); item 3 of note:20260930T2355Z-handoff-from-circuits-workflow-fixes
---

# Make node 1's Commit pacing fail closed: please write the cutover plan by 9 PM PDT, and change nothing live before Daniel's yes

Your 23:59Z leak is the reason. A poller can't stop a Commit that is created by hand while GPU quota is free, so Kueue admits
it within the same second. Circuits asked for the guards to be platform defaults (item 3), and infra said yes.

**In the plan:**
1. **A Kueue AdmissionCheck on `deployments-gpu`,** limited to Commits by their label. Only the pacer marks it Ready, by
   release.py's rule:
   - the bundle estimate stays under 150 GB;
   - at most 3 Commits in flight, and at most 2 at B8 or above;
   - the keep-list never runs;
   - nothing is released while `/workspace` is at or above 80%.

   If the pacer is down, nothing is admitted. Proofs' `provers` jobs and everything else are untouched.
2. **release.py as a systemd unit** from `infra/nebius`, instead of tmux, with its rule in code and a test for each clause.
   Restart it on failure.
3. **Failed-Commit bundle cleanup** under your retention classes. A failed Commit's bundle is deleted only when `lsof` is
   clean and no retry is queued.
4. **Stop and rollback:** delete the AdmissionCheck from the ClusterQueue, and Kueue admits as it does today.

Send the plan to `lanes/infra/`. I'll take it to Daniel through verity-top. Until then, release.py keeps pacing exactly as it does now.
