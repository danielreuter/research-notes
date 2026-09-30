---
id: 20260930T2305Z-handoff-from-infra-storage-plan-tonight-resource-steward
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# resource-steward: tonight's storage-plan items. Make bypass writers visible, attribute RAM per lane, and enforce retention classes

The storage plan is in the Project store at `docs/storage-plan.md`; infra wrote it at 4:05 PM PDT, and you co-own it. Tonight:
1. **Bypass visibility:** each tick, list processes writing to `/workspace` at more than 10 MB/s (`/proc/<pid>/io` deltas) and match
   them against the ledger's and Kueue's live allocations. Post unmatched writers to `#agent-alerts` with PID, command line, path and
   user.
2. **RAM per lane:** read `memory.current` per `gpu-lease-*` and `fill-*` scope on node 2 and per pod on node 1, attribute it via the
   ledger, and publish it per lane in the pool files.
3. **Retention classes:** `evidence`, `intermediate`, `cache` and `pinned`, per the plan's table. Enforce `intermediate` (deleted on
   success; after 6 h on failure) and `cache` (LRU, link count 1, never while open). Ask owners about `pinned`, and never delete
   unpreserved evidence.
4. **A lesson for your policy:** HF model dirs are symlink trees into a shared `hub/blobs` store, so a move must carry the blobs. Infra's
   first move carried only links; they are restored, and nothing was lost.
