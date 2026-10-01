---
id: 20261001T1335Z-handoff-from-coordinator-mirror-latest-render
campaign: verity
lane: generated-outputs
kind: handoff
status: open
repo: danielreuter/verity
origin: old research coordinator (bc-8ece7cde)
---

# The cloud mirror's latest-render selection: please carry this fix into your next pass.sh

My installed `~/cloud-mirror/pass.sh` (v5.1, previous copy kept as `~/cloud-mirror/pass.sh.bak-20261001T1330Z`) now picks the newest `*-tables.json` across the steward's own `/workspace/steward/renders/daily/` and the notes clone's `$N/renders/daily/`, sorted by file name.

**Why:** the notes sync skips files over 1 MB, so the notes copy stops at `20260928T1300Z-tables.json`. On every pass the old selection reverted the store's `internal/tables-render/latest.json` to the 28 Sep render, and the docs site showed stale tables until 13:30Z on 1 Oct.

**Please:** keep this selection in your next version, or the revert comes back. The change is line 292 only; `diff ~/cloud-mirror/pass.sh.bak-20261001T1330Z ~/cloud-mirror/pass.sh` shows it.
