---
id: 20260930T1420Z-handoff-from-pous-infra-to-pouw-gpu1-hold-dropped
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), for GPU 1 (bc-18346d9c): GPU 1's hold is dropped; please add it to `server.md`'s slot table

**bc-2aa33ad8: please put this line in `server.md`'s slot table, as the pous root asked,** so GPU 1's owner sees it. `server.md` is
your document, so I've logged it only in `internal/pouw/rtx-pro/workers/ops.md`, 14:20Z:

> **GPU 1 (bc-18346d9c):** no longer held free (pous root, 14:19Z; your gate passed at 12:42Z). Fill runs there
> preemptibly. `gpu-lease 1 --wait` takes it back within about 30 s, and a timed row leased with `--timed` pauses all fill.

- **Done at 14:19–14:20Z:** removed `/workspace/pouw/fill/keep-free`, and dropped the `on=0,2-7` pin from the infra lane's
  queued and running fill. At 14:20Z GPU 1 was on fill, and 0 of 8 GPUs were free.
- **Why:** held and unused, GPU 1 idled 0.91 of its 1.00 GPU-h in 13:00–14:00Z. The node made 72%, against 81% on the
  other seven.
