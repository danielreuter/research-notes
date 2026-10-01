---
id: 20261001T1217Z-handoff-from-circuits-80k-rerun
campaign: verity
lane: circuits-bool-norms
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (5:17 AM PDT): re-run the Gemma-2 chain's 80k-row comparison on `a009c1cbc`, chunked, after 5:55

Your 80k-row comparison ran on the chain's former copies of the eight shared ids. On `a009c1cbc` (built on `boolean_dense`'s rows) it needs
re-running for PR 2. Run it in chunks of 500 rows (2 GB each) as parallel CPU jobs, not one 3-hour core: node 2's Verity CPUs (cores 48–83 for
circuits, as a `gpus=0` fill guest) or node 1's CPU queue after 5:55 AM PDT. Keep it under about 30 minutes of wall time. Write the result (rows,
mismatches, run ids) to lanes/circuits-bool-switch/ for PR 2's body.
