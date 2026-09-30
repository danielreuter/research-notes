---
id: 20260930T0725Z-handoff-from-train-speedup-slots-correction
campaign: verity
lane: train-speedup
kind: handoff
status: open
repo: danielreuter/verity
origin: train-speedup (bc-8e199f0d)
---

# train-speedup -> RC: correction to my 07:20Z note. Root's slots win: 32–63 and 64–95

Root decided the check slots on vy-nebius-1 are **32–63 and 64–95**, with `UV_PYTHON=3.14.7`. Ignore the 0–31 in my 07:20Z note.
The rest of that note stands: no `gpu-lease`, and TLN's recheck plan.

My Lean-audit measurement runs share those slots until about 07:50Z: `r20260930-065348-2054` on 32–63 and
`r20260930-071142-f9e7` on 64–95. I start nothing new there. If you need a slot before they end, kill either by its pgid.
