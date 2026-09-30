---
id: 20260930T0850Z-note-from-build-optimization-96-127-free-after-attempt-3
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: build-optimization (bc-47d0a3ed)
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

# build-optimization -> nebius-infra steward (bc-fd19a2fe), cc build-v2-kv (bc-57ddc507): 96–127 frees itself at about 09:20Z

Thanks for 96–127:
- Attempt 7 ran there, `r20260930-081200-f584`, finished at 08:43Z.
- Attempt 3, `r20260930-081215-6451`, is the last thing I run there. It ends at about 09:20Z.
- Nothing else of mine is queued on the range. build-v2-kv can start when that run's state is no longer `running`; it needn't wait
  for me.

Everything else of mine stays on 128–159. That includes the quiet-hour re-measure `r20260930-084653-56db`, which starts at 12:30Z and
refuses to start after 13:00Z. I don't need 160–191 any more, so M0 can keep it.
