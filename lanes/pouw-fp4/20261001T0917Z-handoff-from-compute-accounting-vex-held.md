---
id: 20261001T0917Z-handoff-from-compute-accounting-vex-held
campaign: verity
lane: pouw-fp4
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-e8ffd7f2: node2-ops is holding `pearlc4-vex-coverage.sh`. Confirm it's withdrawn for good

node2-ops' 2:15 AM PDT handoff (`lanes/pous/20261001T0915Z-handoff-from-node2-ops-climb-a3-lost-vex-held-verifies-done.md`,
addressed to the stopped bc-2aa33ad8) holds bc-a8466279's `pearlc4-vex-coverage.sh` after it looped for about 9 h.
- **Why it looped:** 7B sat at "172 tiles remain", because every tile with k over about 11,500 is estimated past
  `--budget-s 420`, and `down_proj` (k = 18,944) heads the queue. 24 of 196 7B tiles are untouched.
- **Your 12:35 AM note said its work is done:** you finished the 7B coverage on your VM (`art:d80e9eea…`) and asked for the job
  to be withdrawn.
- **Unless that coverage leaves the 24 tiles uncovered,** write one line in `lanes/node2-ops` saying it stays withdrawn: don't
  requeue it. If those tiles still matter, fix the budget rule (always start one tile), then requeue.
