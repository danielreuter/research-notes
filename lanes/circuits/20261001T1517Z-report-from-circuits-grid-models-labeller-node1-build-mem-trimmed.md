---
id: 20261001T1517Z-report-from-circuits-grid-models-labeller-node1-build-mem-trimmed
campaign: overnight-sep30
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

8:17 AM PDT, items 1 and 2 of your 7:55 follow-up are done:
- **Labeller:** it now runs in node-1 tmux `gm-label` as research. Its first pass there, at 15:08:33Z, wrote 40 labels, all on the remote. The local copy had already died when this VM restarted at 14:53Z.
- **Build requests:** 91 of the 215 unsubmitted requests are trimmed, 16,340 GB down to 12,574 GB, with backup `items.bak-1516Z.json`. The rule and mapping are in note:20261001T1516Z-finding-build-mem-trim.
- **Twins:** the 9 `-pk2` twins were submitted at 15:11:55Z, now that `PACK_MODELS` lists the models.
