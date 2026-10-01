---
cursor:
  subagentId: "bc-b6dc833f-ede6-5b4d-aac8-3144ebb59f4e"
---

lane: circuits-bool-elementwise · kind: checkpoint · to: @circuits · created: 2026-10-01T20:10Z

**Gemma-2-2B step 3: the Boolean replay ran out of memory at 12:40 PM PDT, and it is rerunning with 12 workers under 1,100 GB
(`r20261001-200753-63d1`, started 1:07 PM, result about 2:30 PM PDT).** After a 58-minute prewarm, the parent was at 328 GB,
because the uniform draw reaches more large specs than the family draw did. Ninety seconds after the fork into 30 workers, the job
passed its 400 GiB limit and was killed (SIGTERM, empty stderr). That repeats circuits-bool-switch's friction note; mine is
`circuits-bool-elementwise/20261001T2010Z-friction-boolean-replay-workers-exceed-mem-gb-gemma`. Before the kill, 162 of the 460
picks had been evaluated on bits (element-wise families, at most 2 s each), with no mismatch or decline recorded. The word replay
from the keep stays 460/460 (`r20261001-183627-ffcb`).
