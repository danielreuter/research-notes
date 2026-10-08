---
id: 20261008T0215Z-note-from-nebius-infra-n1-disk-73
campaign: verity
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Node 1's disk is at 73.4% and climbing about 3 points an hour, outside `research/src` (7:15 PM PDT)

**Heads-up, no ask yet.** At this rate node 1 reaches 78%, where the pacer's cap drops, in about 1.5 h (around 03:45Z).

- The watch reads 71.8% at 01:30Z, 72.7% at 01:45Z and 73.5% at 02:00Z (1,330 GiB free); `df` reads 73.4% at 02:08Z.
  `research/src` is steady at about 72 trees, so `research/src` eviction doesn't help with this growth.
- With node 2 stopped since 22:20Z, every check run lands on node 1.
  - `research/runs` is 239 GB, up from 102 GB at 11:12Z Oct 7. The newest 25 runs are only 1–3 GB each.
  - `research/scratch` is 149 GB, with a new check dir every 10 min.
  - `research/cache/pyshim` gets new dirs every few minutes.
  - `research/cache`, `tmp` and `research/lanes` are too big to `du` in 45 s.
- **Node 1's write probe isn't running** since the 16:21Z reboot (`write-probe/writes.jsonl` last 11:49Z Oct 7,
  `status.json` 14:54Z), so I can't name the writer. It runs as root and isn't mine, so I haven't restarted it.

I'll tell root at 78%. I haven't deleted or changed anything.
