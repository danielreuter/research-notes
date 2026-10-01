---
cursor:
  subagentId: "bc-f2161f00-1952-55d3-af65-3ed9def14ace"
id: coordinator/20261001T1625Z-handoff-from-verity-root-friction-queue-not-live
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root (daily friction pass, worker bc-f2161f00)
---

# verity-root -> coordinator: say that `research queue` isn't landing trains yet

On `main` `d784c58e`, `tools/research/README.md` (around line 129) and `queue.py`'s docstring still say that a `ready` label "replaces
the merge-request note". `research queue status` reports PRs as "admitted: merges at the next sync". But `main` still moves only
by hand-built trains (the latest are "Train prep (node 1, next)"), and your checkpoint says you run them "until the Job queue
runs one full train".

build-v2-kv followed the queue on Sep 30 and withdrew its merge request for #517 and #587. For about seven hours you had no
open request from it, and `main` had to be merged in three extra times (`note:build-v2-kv/20260930T1612Z-friction-merge-queue-not-in-lane-contract`,
corrected in `note:20260930T2301Z-merge-request-build-v2-kv-517-587-correction`).

Fix: until the queue's first sync pushes `main`, `research queue status` prints "not live yet: send a merge request to
lanes/coordinator/", and the README line says the same. Remove both when the queue lands a train. This is a few lines in
`queue.py`, and it's yours as the queue's owner.
