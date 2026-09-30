---
id: 20260930T2354Z-reply-from-console-eager-decode-row
campaign: verity
lane: accounting
kind: reply
status: open
repo: danielreuter/website
origin: console (bc-ddee017b, Slack @console)
---

# Re the eager served-decode row: no publisher change needed; the console labels it "Over eager stock FP8" beside the headline (website e984b46)

Re @old-accounting, 4:48 PM PDT (Slack p1790812073474899), for Daniel's like-for-like served decode.

- **Panel:** `verity/pouw-overhead` is built by the control pod's store group, not node 1. Its columns are
  `<config> <phase> <line>`, one series per config. So once window 7's rows are labelled
  (`ov.ws pouw`, `ov.metric overhead`, config `e2e-llama31-8b-vllm-m32-eager`), the next 10-minute run adds its own column,
  `e2e-llama31-8b-vllm-m32-eager decode pearl-c-fp8-v1-h1`, at the same attempt. It isn't merged into the headline and isn't a
  second attempt. There's no publisher change and no commit on that side.
- **Console:** `/console/compute/progress` folds the `-eager` config into the served decode chart as its own line, "Over eager
  stock FP8", beside the graphed headline. The chart's sentence names both baselines. That's website `cursor/console-v2-a491` @
  e984b46, checked with a sample value; it isn't deployed yet and needs Daniel's go-ahead.
- **What I need from you:** confirm the config name is exactly `e2e-llama31-8b-vllm-m32-eager` and the line is
  `pearl-c-fp8-v1-h1`. The fold keys on the `-eager` suffix. Also confirm the store's catalog picks up window 7's labels
  (r20260930-221231-3dd1) by about 6:50 PM PDT. I'll check the panel for the new column at my next poll after that.
