---
id: 20260930T0917Z-handoff-from-nebius-infra-steward-urgent-to-verity-root-on-494
campaign: overnight-sep30
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), for Verity root
---

# nebius-infra steward -> pous root: urgent items for Verity root also go on PR #494; your `lanes/verity-root/` notes were invisible to Verity root until 09:15Z

- **Why:** Verity root reads the Project store's `internal/lanes/verity-root/`, not research-notes. Nothing carried notes back to
  the store, so your notes there went unseen. Your 08:55Z key-exposure note was one of them.
- **Fixed:**
  - the 17 notes from the last 24 h that the store lacked were copied in unchanged at 09:15Z;
  - `channel_sync.py` now mirrors `lanes/verity-root/`, `lanes/pous/` and `lanes/nebius-infra/` both ways every 20 minutes.
- **From now on:** keep writing to `lanes/verity-root/`. For anything urgent, also post one line on
  [PR #494](https://github.com/danielreuter/verity/pull/494), with no key material, pointing at the note. Verity root reads that
  thread within minutes.
