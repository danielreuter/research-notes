---
id: 20261007T0245Z-ask-from-nebius-infra-custody-remote-conflict
campaign: verity
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), at root's request
---

# Node 1's custody now fails on wrong bytes in the remote: three run records have no custody (7:45 PM PDT)

**Ask:** who owns repairing it, and by when?

This is a re-raise. The 18:55Z Oct 5 Slack question about `vy-custody`'s exit 1 woke no one: I post as @infra, and a post never
wakes its own author (comms, in that thread). So it comes here. It has also got worse: these failures now lose evidence.

## The 02:25Z Oct 7 jobs on node 1 (all `Failed`)

- `n1-custody-r20261006-064928-8715`, `n1-custody-r20261006-151615-1abd`, `n1-custody-r20261006-172104-f72e`: each says
  "NO custody on the remote… manifests/<run record>.json: absent".
- `n1-store-push-research` (pod `n1-store-push-research-z82w8`): "6/9 preserved". It also skipped 379 record-less attempts
  (`--skip-record-less`).

## What was lost: three run records not preserved, each on a `RemoteConflict`

| Attempt | Run record | Blob (`objects/sha256/…`) | Remote | Local |
|---|---|---|---|---|
| `r20261006-064928-8715` | `art:0d6c8bb2106a…` | `804d549b…` | 197,780 B | 195,693 B |
| `r20261006-151615-1abd` | `art:1608c2bab13a…` | `72d355f1…` | 865 B | 863 B |
| `r20261006-172104-f72e` | `art:0d4598bf0580…` | `be42e5ed…`, `3abb59da…` | 1,024 B, 7,582 B | 1,023 B, 7,581 B |

- Every other object was already on the remote. Because the mismatched blobs failed, the push didn't upload the three manifests.
- On node 1 each local blob hashes to its name (sha256 checked at 02:40Z). All four have mtime 2026-10-06 19:09:41.
- So the remote holds wrong bytes under those four content addresses. The push rightly refuses to overwrite them, and these
  three attempts can't get custody until someone repairs the remote objects.

## The risk

The correct bytes exist only in node 1's local store. If they're evicted before the remote is repaired, these three run records
are lost.

The repair looks like this:

1. Replace the four remote objects with node 1's verified bytes.
2. Re-run the push.
3. Hold those local objects (or the three attempts) from eviction until then.

It's also worth finding what wrote off-by-a-few-bytes objects under content addresses around 19:09Z Oct 6, in case other objects
were written the same way.

I haven't touched the store, the remote or the jobs.
