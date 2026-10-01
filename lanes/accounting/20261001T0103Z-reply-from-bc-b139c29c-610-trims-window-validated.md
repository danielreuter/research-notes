---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
id: 20261001T0103Z-reply-from-bc-b139c29c-610-trims-window-validated
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: hash-cut-change3 (bc-b139c29c)
---

# #610 with the trims: the untimed served window passed its validation (6:01 PM PDT); both verifies are running

**The window** is `r20261001-005132-35d9`: #610 at `e442d494`, `SCHEME=pearl-c-sm120-v1-h2 GRAPHS=1 FP8_GRAPHS=1 SCHEDULE=serial ROWS_FORM=s`, with #610's ship. It ran untimed on GPU 2 from 5:56 to 6:01 PM PDT, on a preemptible lease, at 2,085 MHz.
- **The validation passed:**
  - every arm gate held;
  - the prefill and decode verify passes repeat their timed commitments;
  - both eager replays repeat;
  - nothing was JIT-built;
  - `rows_form` is `s`.
- **The verifies started at 6:01 PM PDT** in the same run, 48 jobs each at `nice 19`: one on these passes, and one on the untrimmed `r20260930-235745-a3d0`'s (the fallback). **The verdicts are due at about 6:45 PM PDT.**
- **The ms, untimed and not comparable:** prefill was 452.5 ms (1.623× over graphed FP8 at 278.8 ms). Decode was 28.32 ms a step (3.786× over graphed FP8 at 7.48 ms), but the host was loaded: window 7's 48-process verify ran beside it from 5:45 PM PDT. Every eager mode slowed together: eager FP8 decode went from 16.2 to 20.4 ms and BF16 from 15.3 to 22.7, against the 5:15 PM PDT runs. So this run doesn't measure the trims. Window 8's quiet node will.
- **If you want an untimed timing of the trims before window 8:** one more 5-minute window, with no verify, once window 7's verify ends (about 6:20 PM PDT). I won't start it unless you ask.
