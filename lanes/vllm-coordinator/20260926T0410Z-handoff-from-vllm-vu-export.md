---
lane: vllm-coordinator
kind: handoff
from: vllm-vu-export
created: 2026-09-26T04:10Z
---

# Handoff from vllm-vu-export: #101 and #4 input sets being redrawn; the pod needs past the 05:00Z deadline (04:10Z)


- **Ask:** keep `vyv-vu-export-g2` (`wgi0grnjq6cz3i`, 1x L40S, $1.09/h, guard 90) alive past the 05:00Z vyv deadline, until about 06:45Z.
  - #4's Build is CPU-bound and takes about 75 minutes, so the row can't finish by 05:00Z.
  - Daniel's cap for this redraw is $5. Pod time from 03:55Z to 06:45Z is about $3.1.
  - If the deadline stays at 05:00Z, #101 is still done (around 04:20Z), and #4 is left as it is today, with a noted gap.
- **Why a pod:** Daniel asked for a redraw with the stratum-order fix. The preserved records hold only the units drawn earlier, not the run's other committed values, so the rows must be re-run with the export on.
- **Run:** `r20260926-035624-a133`, custody-r2, from PR #53's head `11d453e0`. It runs #101, then #4, each Build → Match → Commit (PAIRS=1) with the default-on export. The export writes the store plus its default extraction, and the run exercises the pool-fallback commit (the export uses the forked pool unless headroom is under 20%). Then the chunked-edges `program_graph` runs on each row, with sampler VUs placed through the store.
  - Tests at `11d453e0` passed with 0 failures on this pod (`r20260926-040026-4968`).
  - PR #53 is marked ready, and its merge request is with the research coordinator.
- **Sampler VUs on #4 (Daniel's item 3):** cheap, so it's done in #53 at `11d453e0`. `program_graph` places a VU addressed at the sampler by its Call id in its request's Program; the request → Build dir map comes from the store's `program.json`. #4's graph will be regenerated from the new export.
- **I haven't touched** any epoch pod or branch.
