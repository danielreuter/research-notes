---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Day-plan checkpoint, 7 PM PT (02:10Z)

- **1 PM goals: met.** c4ir and b5pat merged.
- **4 PM goals: met.** a5, b4 and b1 merged, plus gc's fixes. Also merged: gc2, gc3, b5vc, b5vab and m32. Main is `a57628fc`.
- **7 PM goal (epoch run and ready for review): not met.**
  - Branch `lane/vllm-rf-epoch` @ `ad8050e9`: items 1, 2a/b, 6 and 7, plus the m32 cherry-pick. Deferred: 2c, 3 and 4. The golden re-record is pending as its own commit.
  - Rows: #101 PASS; #57 FAIL-class. #4, #67, #70, #60 and #23 Commits ran on the fixed tree.
  - Rebase runs: 3 of 4 ended rc 143 (moe67 `9d5e`, moe68 `ec89`, tp70 `d097`); tp70b `20d1` rc 0.
  - No `rebaseline.py write` yet. Six rows are not re-baselined: #11, #39, #68, #73, #74 and #75.
- **Confirming gate (a) on main:** m32 `e739` RUNNING, due about 03:40Z.
- Guard: $621.28/770 at $9.39/h (3 epoch pods idle after the 143s); deadline 05:00Z.
