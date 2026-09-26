---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-epoch
created: 2026-09-26T03:05Z
---
# REVIEW (epoch): `lane/vllm-rf-epoch` @ `101e8917`. Partial, for owner review, not merge-ready

Full packet: `lanes/vllm-rf-epoch/READY.md` (commits, recording trees, per-row digests, findings, runs, key mints). Your published
summary `docs/vllm-epoch-review.md` matches it. I'm not adding anything to that file.

- **Commits on b4c `5494e29f`:**
  - epoch: `30427930` (item 1, v2 Ampere step), `a784d421` (item 2a/b; **protected** `vllm_adapter.py`), `73a9a90a` (item 7, key-only),
    `14b321ad` (`rebaseline.py write`, #101 and #67 digest checks; owner review), `101e8917` (item 5, golden; protected; owner review).
  - non-epoch, digest-neutral: `89cd9d1a` (item 6, admission lag), `ad8050e9` (m32 `271a0952`, pre-gate).
  - Deferred as larger than S: 2c, 3, 4.
- **Recording trees:** Build+Match at `a784d421` (#67 at `89cd9d1a`); Commits at `ad8050e9`; the rebaseline ran at `ad8050e9`. The branch lacks
  a5, b1 and main since `38a8d35d` (all digest-neutral).
- **Re-baselined:** #101, #67 (digest checks only). The `expected/` were the v1 reference, so the diff is v1 -> v2 + epoch.
- **Recorded, not written:** #4 (FAIL-class, Commit now PASS: finding), #23 (GREEN, Match NO FOLD: finding), #57 (FAIL-class,
  coverage differs), #60 (Commit OOM at 119 GiB even with the admission override), #70 (TP layout: most checks don't apply).
- **Not re-baselined:** #11 and #39 (memory), #68 and #74 (time), #73 (Commit OOM at 251 GB), #75 (rank Build timeout at 7200 s).
- **Evidence:**
  - Rebaseline records `r20260926-015749-{2654,4cf2,087d,e70c}`, Commit copies `r20260926-020557-*`, small-file copies
    `r20260926-021148-{30ef,4d18}`: all PRESERVED.
  - tp70's and tp70b's small-file copies are split into < 4 GB parts by `r20260926-025813-4a23` and `r20260926-025815-7b60`, because
    the store can't verify a single object over 5 GiB.
  - The recording runs' own 12–39 GB custody uploads failed (403 / RemoteDisconnected), so raw arrays over 20 MB exist nowhere now.
- **Pods:** all terminated (moe68 02:24Z, moe67 03:00Z, tp70 and tp70b once their split runs are preserved; see FINAL). Spend about $107 of $130.
