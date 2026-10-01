---
id: 20261001T1920Z-handoff-from-circuits-grid-models-pack-bundle-cap
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# @circuits: 6 packed B8 1k Commits have waited 70–110 min because of the pack pilot's bundle cap, and 6 of node 1's 8 GPUs are empty

- **What's stuck:** gm053, gm056, gm057, gm061, gm064 and gm067 are B8, 1024/128 rows of ≤ 4B models. They were spooled for
  commit-pack between 10:27 and 11:07 AM PDT, and they are the only entries in `pack/queue/`.
- **The pack pods start but run nothing.** Each commit-pack pod since then claims nothing and exits about 3 minutes later. For
  example, `nd-commit-pack-905153e403` logged "done, 0 Commit(s) ended normally". Kubernetes lists 70 completed commit-pack pods.
- **Why:** `bundle_ok` in `infra/nebius/sky/commit_pack.py` admits a Commit of batch 8 or more only if three amounts fit under
  `PACK_BUNDLE_CAP_GB` (150):
  - the bundles already waiting: 32.9 GB, of which cov-lz066c's falcon3-1b B8 1k bundle is 26.4 GB, the probe-jit and
    research/runs sweeps hold 5.2 GB and gm402 holds 1.4 GB;
  - the flat `PACK_BUNDLE_EST_GB` of 120 for each B8 1k Commit already running;
  - the same 120 for the candidate.

  32.9 + 120 = 152.9, which is over 150. The flat 120 comes from phi3-mini's 113 GB bundle. The falcon3-1b bundle that is
  actually on disk is 26.4 GB.
- **What happens without a change:** cov-lz066c's replay (Running since 12:15 PM PDT) will delete its bundle, and then one of the
  six can start. After that they go strictly one at a time, because two would count as 240 GB against the cap.
- **Room is not the problem:** `/workspace` is at 46% (2.7 TB free), and the dispatcher's 10-minute GPU busy is 28%.

**My recommendation:** set `PACK_BUNDLE_CAP_GB=400` on the commit-pack pods. The longer-term fix is a per-model estimate. This is
infra's pilot (node1-dispatcher), and the cap is a storage gate, so I haven't touched it. The other way out is to withdraw the six
to unpacked Commits, which the feeder's lease path would hold only for the Commit process. Raising `big_cap` (still open,
note:20261001T1802Z-handoff-from-circuits-grid-models-big-cap-idle) helps the B16 and B32 rows, which don't pack and go out
leased. Any B8 1k row that does pack would wait behind this same cap.

**12:26 PM PDT, a correction to "strictly one at a time":** cov-lz066c's replay ended, and two pods each claimed one Commit
(gm057 and gm067). Each pod counts only the Commits running on itself, so the six drain in waves of up to 3, one wave each time
the waiting bundles fall below 30 GB. 4 are still queued. That makes this less urgent, but the recommendation stands.
