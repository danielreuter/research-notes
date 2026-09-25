---
lane: sp1-committed
kind: handoff
from: coordinator
created: 2026-09-25T08:23Z
---

# WRAP UP NOW (agent cap): finish at the next clean point, preserve, terminate your pod, write FINAL

The project is over its 20-agent cap and your lane is the lowest Table 2 value tonight (SP1 cannot reach 2^-128 without protocol
changes, so a committed SP1 result stays out of the published filter). Within ~20 minutes:
1. commit and push what you have (`research notes push sp1-committed`); register and preserve any measured result and hand it
   to verify-night-2 as usual;
2. terminate your pod;
3. write your report's FINAL: what works (guest committed path, host tree check, vectors), what is left, exact next steps, so a
   successor can resume later from your branch;
4. `research notes checkpoint sp1-committed final "..." --require-pushed`, then end.
