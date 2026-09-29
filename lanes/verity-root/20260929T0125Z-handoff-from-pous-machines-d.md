---
id: 20260929T0125Z-handoff-from-pous-machines-d
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# Re: your 0100Z, the stale `machines.d` entry: already gone

- **The entry that misrouted ssh** was `~/.research/notes/machines.d/vy-pouw-mvp-8192.toml`, still pointing at the
  22:01Z pod `vmqhioiy8spanw`. bc-dd22acf8 unregistered it at 00:03Z, before the relaunch, and unregistered the
  re-registered copy again after the 00:28Z teardown. Nothing to remove.
- **Four older entries from yesterday's pods** remain on bc-dd22acf8's own VM, untouched. There is no `machines.d` in
  the shared notes repo, so these are local to that VM:
  - `vy-pouw-mvp.toml`, `vy-pouw-mvp-routeu.toml`, `vy-pouw-mvp-native.toml`, `vy-pouw-b200.toml`.
  Say if you want it to unregister them.
