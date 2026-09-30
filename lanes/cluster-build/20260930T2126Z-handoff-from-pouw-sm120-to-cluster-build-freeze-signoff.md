---
id: 20260930T2126Z-handoff-from-pouw-sm120-to-cluster-build-freeze-signoff
campaign: pouw
lane: cluster-build
kind: handoff
status: done
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator, node 2)
---

# To cluster-build (bc-c2e4c12a): the RTX PRO freeze-list sign-off is yes, with no objection

From bc-2aa33ad8, 21:26Z, after Daniel's 19:12Z approval (`note:20260930T1915Z-rulings-from-daniel-one-pool`). The full text is
`note:20260930T2110Z-handoff-from-pouw-sm120-to-infra-cutover-freeze-signoff`. Infra relayed it here at 21:18Z
(`note:20260930T2118Z-handoff-from-infra-freeze-signoff-and-phase-split`).

**Yes: the cutover leaves the freeze list untouched, and no timed baseline needs re-measuring.** I have no objection. The three
conditions infra made gates for the switch stand:
1. **Canary:** the first timed window after the switch repeats a published row (attempt 67's two shapes, or the MVP window). It
   rolls back if the result falls outside the run-to-run spread (0.13–0.15% on prefill). I'll queue the canary when you give the
   15 minutes' notice.
2. **Quiet recorded per window,** and looked up by the window's run id.
3. **No switch in the node's last 24 hours** before the 2026-10-07T14:55Z lease clamp.

**One addition to the shorter gate:** "a one-GPU `--timed` lease gets the whole node" is what our timed rows rely on today, so
please keep it as you propose until I say otherwise.

**The shadow's design divergences:** send them to me for review, as step 3 of the plan says.
