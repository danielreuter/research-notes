---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
id: 20261001T0227Z-reply-from-bc-b139c29c-window8-ran-verify-running
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: hash-cut-change3 (bc-b139c29c)
---

# Progress, 7:27 PM PDT: window 8 (#610 `e442d494`, `-h2`+`s` plus the trims) ran clean; its verify is running

- **The window:** bc-dd22acf8's `r20261001-020519-e39d` took its timed lease at 7:20 PM PDT, and `window.sh` exited 0 at 7:25 PM PDT.
  - Its validation passed: the arm's gates held, both verify passes and both eager replays repeat, and nothing was JIT-built.
  - The verify started at 7:25 PM PDT in the same run, so it ends at about 8:05 PM PDT.
- **Its totals, from its `e2e.json`, against window 7 (`r20260930-221231-3dd1`, `-h2` on #596):**

  | | window 7 | **window 8** |
  |---|---|---|
  | prefill, one 8,192-token prompt | 461.8 ms (1.647× over graphed FP8) | **447.6 ms (1.630×)** |
  | decode, a step at 32 sequences | 26.03 ms (3.402× over graphed FP8) | **23.83 ms (3.194×)** |
  | decode over eager FP8 | 1.263× | 1.455× (eager FP8 at 16.4 ms, against 20.6 in window 7) |

- **Next:** once the verify passes, the rows go through your 0104Z chain, with bc-ccd30e80 generating them. Per the served-path exception I keep watching until window 8's results are preserved, and I'll post the verdicts here.
