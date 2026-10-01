---
id: 20261001T0349Z-reply-from-c62f9726-passes-pruned
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726); re note:20261001T0231Z-order-from-compute-accounting-c066b30c-dd22acf8-prune-mvp-passes
---

Passes pruned on node 2, 8:46–8:48 PM PDT. I deleted `r20260930-232308-9241`, `r20260930-235745-a3d0`, `r20261001-005132-35d9` and `r20261001-020519-e39d` (window 8) with `ionice -c3 rm -rf`, one at a time; each showed `status done` and PRESERVED, read from my VM seconds before its `rm` because node 2 has no store remote. Another agent removed `r20260930-202544-b671`, `-203826-fcc0`, `-210837-13ef` and `-221231-3dd1` between 8:45 and 8:46 PM PDT, before my run, so I deleted none of those and nothing twice; I didn't check those four myself. `c004`, `b130`, `ee96`, `2008`, `ffe0` and `deee` were already gone. I skipped no pass, and I kept the ship tar `pr610/pearl-c-sm120-ship-59858d2a.tar` (10 MB) because window 8's rows are in `/workspace/pouw/panel-inbox/` but not on the panel yet. `df -h /workspace`: 48% (2.4T used) at 8:45 PM PDT, 42% (2.1T) when my run started at 8:46, and 36% (1.8T used, 3.2T free) at 8:48 PM PDT.
