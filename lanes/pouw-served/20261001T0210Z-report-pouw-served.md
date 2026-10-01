---
lane: pouw-served
kind: report
created: 2026-10-01T02:10Z
status: open
---

CHECKPOINT c1e920090 (06:26Z) [open] DONE item 1: takeover note lanes/accounting 0627Z: bc-ccd30e80, bc-dd22acf8, bc-b139c29c may be stopped: yes (nothing in flight; 18 runs PRESERVED, b957 in store with read-back retrying, #572's check 7d55 not in store, superseded). Item 2 running: #610 at 6db2c066 (e442d494 + main 72aacf9b), check r20261001-062017-6e10 on vy-nebius-1.
CHECKPOINT b6e09ee44 (03:49Z) [open] Served path is mine (compute accounting 8:50 PM PDT). Node 2 passes pruned (note 0349Z): 4 deleted by me after both tests, 4 by another agent just before; /workspace 48% -> 36%. Ship tar kept until window 8's rows are on the panel. Next: takeover reply for bc-ccd30e80/bc-dd22acf8/bc-b139c29c, then the served-tail PR.
CHECKPOINT 4860d817a (02:26Z) [open] SHADOWING: window 8 r20261001-020519-e39d timed part done, validation passed; verify from 02:25:20Z (ends ~03:00-03:10Z). Totals read from e2e.json (drivers post the official line): decode 3.194x over graphed FP8 (window 7: 3.402x), 1.455x over eager FP8 (window 7: 1.263x, eager arm noisier); prefill 1.572x eager / 1.630x graphed (window 7: 1.617x / 1.647x). Next: verdicts, preservation, then takeover.
CHECKPOINT 4860d817a (02:25Z) [open] SHADOWING window 8 r20261001-020519-e39d (#610 e442d494): timed lease since 02:20Z, vLLM serving at 02:21Z, quiet paused the two checks. Verify ~03:35Z. Daniel's 7:01 PM PDT rulings already done by others (6 paused PRs closed 02:02Z; -h1 stack and #600 closed); served-tail collapse plan in lanes/accounting 0230Z. VM was reset between turns: notes re-cloned. Next: window 8 totals and verify, then takeover.
CHECKPOINT e5b720899 (02:10Z) [open] SHADOWING window 8 for compute accounting (agent bc-c62f9726; replaces bc-ccd30e80, bc-dd22acf8, bc-b139c29c). Window 8 = r20261001-020519-e39d on node 2 at #610 e442d494 (SCHEME pearl-c-sm120-v1-h2, GRAPHS=1, FP8_GRAPHS=1, ROWS_FORM=s, ship pr610/59858d2a), START 02:20Z, lease <=20 min, verify after (~35-45 min). READY lines already in (0202Z, 0203Z). Not taking over mid-flight. P10 vLLM size lint passes at #596 10b5526b, #610 e442d494 and #596+origin/main (tests/lint, 43 passed). Next: read window 8's validation + verify; take over when its results are preserved.
