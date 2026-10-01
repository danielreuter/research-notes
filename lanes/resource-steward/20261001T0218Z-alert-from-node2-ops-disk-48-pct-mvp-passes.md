---
id: 20261001T0218Z-alert-from-node2-ops-disk-48-pct-mvp-passes
campaign: verity
lane: resource-steward
kind: alert
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

# Disk alert, node 2: `/workspace` at 48% at 7:15 PM PDT (39% at 5:10 PM); PoUW's MVP e2e passes write 73 GB each

**The trend:** `/workspace` went from 37% (4:10 PM) to 39% (5:10 PM) and 48% (7:15 PM), about 440 GB in two hours. At that rate,
55%, where Verity guests stop starting, comes in about 1.5 h, and the 60% alert in about 2.5 h.

**Where it is** (`du`, ionice idle):

| Path | GB | Note |
|---|---|---|
| `pouw/mvp-e2e/passes` | 800 | 11 run dirs, 73 GB each. Four came since 3:12 PM: `r20260930-221231-3dd1`, `-232308-9241`, `-235745-a3d0`, and bc-b139c29c's `r20261001-005132-35d9` (queued job) |
| `pouw/gpu3-fp8/out` | 737 | Never moved and never backed up, per the standing rule. New `fix2/` and `padded-hot-cancel/` are being written now |
| `research` | 263 | |
| `pouw/fill-out` | 178 | |
| `hf` | 169 | |
| `jobs` | 161 | kueue-fold's staged weights and Builds |

**Ask:** decide with the MVP's owner whether old e2e passes can be pruned or moved, or whether each pass can keep less than 73 GB. My
enforcement holds as before: Verity guest starts stop at 55%, and the alert fires at 60%. I'll write another line here if it crosses 52%.

- **8:36 PM PDT: 54%,** one point below the 55% guest-start stop. The rate has slowed since 7:15 PM (48%), but it's still rising. The 60% alert fires next.
