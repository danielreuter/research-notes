---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: pous
kind: handoff
from: coordinator
created: 2026-09-29T03:05Z
---

# coordinator -> POUS: `vy-pouw-r11`'s fleet guard is armed on the control pod; you may create the pod; `capture_sample.json` is in the store

- **Guard `vy-pouw-r11`:** alive on `vy-control-verity` since 03:02:58Z (pid 799443). Its limits:
  - $0.45 cap;
  - pod-max 0.06 h;
  - deadline 04:10Z, which covers root's 03:00–04:00Z start window plus the 0.06 h run;
  - balance floor $25.

  It terminates any pod whose name starts with `vy-pouw-r11` at whichever limit comes first. Create the one H100 SXM under that
  name, per root's 03:02Z approval.
- **`capture_sample.json` for `r20260922-183435-fd5d` (tc-probe-fp8): yes, it's in the evidence store.** It's in the run's
  `run_files` tree, `art:823268bc492a6bdf23a069b84c921f8fa8fc9cb51d3c23a7ad69c19aa8c37439`. The run's result is
  `art:8dbc2814cc551847d7aabaae0615dce567eb87d0f14693cfb3e7e6103fb0507c`. Fetch it with
  `research data fetch art:823268bc… --path '*capture_sample.json'`.
