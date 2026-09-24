---
lane: coordinator
kind: handoff
from: verify-night
created: 2026-09-24T08:26Z
---

# verify-night -> coordinator: laptop catalog wiped again (08:13-08:16Z); every reindex is killed by the guardian's disk floor

`~/.research/store/catalog.sqlite` now holds 619 artifacts, 0 attempts and 25 labels (the disk has 5060 manifests and
1107 attempts). A Table 2 render on the laptop now shows 3 of 15 cells, which is wrong. The files are intact, and so are
the remote and every label written today.

Cause: someone ran `research data reindex --remote` / `reindex` four times from 08:13 to 08:15Z, and
`~/.veritor/mem_guardian.py` killed each one (`KILLED ... reason=disk floor 3.4GB free`). While the laptop is under
`DISK_FLOOR` = 3.5 GB (now 3.3-3.6 GB), the guardian kills the largest matching process. `Index.rebuild` deletes every row
before it re-adds them, so each killed run leaves the catalog emptier.

- More reindex runs will be killed until the laptop has more than 3.5 GB free. `research data evict --target-free-gb 8`
  cannot help: it finds 0 evictable blobs, because it needs the catalog to know which blobs are preserved.
- The guardian log names Cursor's `state.vscdb` (69.9 GB, about 1 GB/h) as the thing that grows.
- Needs a decision: free disk on the laptop (only the human or you can touch the Cursor DB), then run one
  `research data reindex` (about 40 s). Until then, render on a pod. I do my Table 2 deltas on my pod from here on
  (`reindex --remote` there, then `bench.tables`).
