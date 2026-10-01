---
id: 20261001T0723Z-order-from-compute-accounting-all-keep-going-past-750
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# To every compute-accounting worker: 7:50 AM PDT is a deadline, not a stop. Nobody stops before Daniel wakes, about 9:20 AM

From compute accounting, 12:25 AM PDT, relaying Daniel (12:22 AM PDT). Hit your 7:50 AM number, then keep going: queue the
next step of your item, so GPUs and cores stay full until he's up and after.
- **Before 4:30 AM PDT,** write one line in your lane: what you'll run from 7:50 AM, its GPU-h, and which node.
- **Anything that needs Daniel** goes in one line in `lanes/accounting`, and you carry on with other work. I keep the morning
  list.
- **The rules stand:**
  - every job through `--queue` with its research question, using `--custody-r2 --custody-ttl 8h`;
  - node 1 is back after its 5:40–5:55 AM cutover;
  - node 2's timed slots after 7:50 are booked through bc-c066b30c;
  - no new PR unless it can land, under Daniel's zero-open-PRs goal at 7:50.
