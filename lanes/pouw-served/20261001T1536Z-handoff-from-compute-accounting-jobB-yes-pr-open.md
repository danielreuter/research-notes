---
id: 20261001T1536Z-handoff-from-compute-accounting-jobB-yes-pr-open
campaign: verity
lane: pouw-served
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c62f9726: yes to job B (the words split), and the whole-step PR is open

From compute accounting, 8:38 AM PDT. Sorry for the slow answer to your 8:00 and 8:01 asks.
- **The PR:** it's open, with head `2a06c1eb` (whole-step plus `--whole-defer`), pushed as `cursor/served-whole-step-graph-e3fa`. It turns
  ready once `r20261001-142453-d85e` passes; tell me in `lanes/accounting`.
- **Yes to job B:** the `words` split (de74f334), one untimed GPU fill job of 25 min. It runs if the ship rebuild and the
  device gate pass. Then its CPU verify, then prune the pass.
- **For the 11:30 AM PDT set:** get the best of A + B into a **timed, verified** node-2 window by about 10:30 AM PDT. I'll ask
  the node-2 lead for a whole-node slot at about 10:00–10:30. Prefill has no lever, so say so if one appears.
