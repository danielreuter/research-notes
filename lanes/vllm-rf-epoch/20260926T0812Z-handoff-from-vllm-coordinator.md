---
lane: vllm-rf-epoch
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T08:12Z
---
# Money: the project burns $21.6/h, so hold goal 8 to $60 hard

- vLLM spend is $648.27 of $770. At the current $21.61/h, the vLLM total would pass $770 at about 13:50Z. The cap only holds if
  each lane stops at its budget.
- Goal 8 pods are $13.52/h: g8-73 2x H100 $6.98, plus dropped-75, dropped-68b and bisect-23 at $2.18 each. **Your $60 for goal 8
  runs out at about 12:30Z.** Plan each row to end by then. If one can't, stop it at your budget and report what it reached.
- **I terminated `pdzgz3xqiqvkli`**, a second `vyv-rf-epoch-dropped-68b` that was unregistered, with no runs and nothing running.
  Your registered `se1yqv9bnshs0l` (run `d929`) is untouched.
- Terminate bisect-23 as soon as `b866` is preserved.
