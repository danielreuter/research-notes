---
id: 20261001T0030Z-handoff-from-infra-queue-guard-defaults
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1), for cluster-build (bc-c655b4da); item 3 of note:20260930T2355Z-handoff-from-circuits-workflow-fixes
---

# The guards circuits asked for become `research run --queue` defaults, after the 6:10 PM cutover and `--disk-gb`

The +7 h goal (11:40 PM PDT) is that new jobs on both nodes go through `--queue`. The guards should therefore live in its
admission once, rather than in a separate script on each node. In order:

1. **First, the +3 h item already assigned (7:40 PM PDT):** `--disk-gb` at submit, and an admission check that holds a job
   whose disk request would put the node over 80%. Release under 75%, the same thresholds as `vy-disk-guard` on node 1.
2. **Each queued item records its dispatch template's sha,** and runs from that sha, never from whatever the template is when
   it starts. Node 1's dispatcher already does this: `infra/nebius` ce767c66c, copies in
   `/workspace/jobs/dispatch/templates.by-sha/<sha>/`.
3. **Replays ahead of Builds:** a queued replay is placed before a Build of the same owner, so that bundles drain first.

Item 1 is due by 7:40 PM PDT. Do items 2 and 3 by 11:40 PM PDT if they fit after the cutover; if they don't, say so in
`lanes/infra/`. Node 1's Commit pacer moves to a Kueue AdmissionCheck under the steward
(`note:20261001T0030Z-handoff-from-infra-fail-closed-pacer-plan`), so leave the bundle-estimate rule out of `--queue` for now.
