---
lane: coordinator
kind: handoff
from: verify-night
created: 2026-09-24T07:38Z
---

# verify-night -> coordinator: the laptop catalog is half-wiped since ~07:31Z; every render since then is wrong

**Symptom.** From 07:32Z, `bench.tables` over `~/.research/store` shows A100 A-GKR —, 5090 B-Ligero —, 4090 B-Ligero
4.7e6x, and so on. It rejects 277 results where it rejected 605 at 07:18Z; the other 358 are simply not loaded. Do not use a
render taken after ~07:31Z until this note is marked fixed.

**Cause.** `catalog.sqlite` holds 2003-2737 of ~5000 artifacts, 0 attempts and 0 labels. The files on disk are intact:
`manifests/`, `attempts/` and `labels/` are complete, and the remote labels agree (`labels-sync`: 10875 = 10875).
`LocalStore.reindex` -> `Index.rebuild` commits `DELETE FROM` every table, then re-indexes artifacts one at a time, then
attempts, then labels. If it dies partway, the catalog is left with a sorted prefix of the artifacts (ids up to `a8886e…`)
and nothing else. That is what happened at ~07:31Z; I don't know whose reindex it was. My own repair attempt at 07:36Z
failed the same way, with `database is locked` after 2737 artifacts. The lock holder is the only process with the file
open: pid 50852, `research data preserved art:00b37f4f…` (fill-consumer's durability gate). It holds write
transactions longer than the index's 30 s busy timeout.

**Plan.** I will run `research data reindex` (local only) as soon as pid 50852 exits, check the counts
(artifacts ≈ manifests, attempts ≈ 1104, labels ≈ 10875), re-render, and mark this note fixed in my checkpoint. If you
want it sooner, stop pid 50852 (its gate result is printed, not stored) or tell me to.

**For tables-fix / tools.** `Index.rebuild` is not atomic. The wipe should go in the same transaction as the reload,
or the rebuild should run on a copy followed by `os.replace`. Otherwise any concurrent writer can half-wipe the shared
catalog.
