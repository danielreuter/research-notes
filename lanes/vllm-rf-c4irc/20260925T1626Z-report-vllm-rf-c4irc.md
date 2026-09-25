---
lane: vllm-rf-c4irc
kind: report
created: 2026-09-25T16:26Z
status: open
---

CHECKPOINT 26964de2 (16:47Z) [open] main moved to 38a8d35d (c2b/b5gmb/b2vb merged 16:25Z): lane/vllm-rf-c4ir 793f14af now conflicts in p10_size.json. Pushed lane/vllm-rf-c4irc 26964de2 = merge of origin/main with the resolution (keep all 3 deletions). Gating it on reg: head r20260925-164707-4f7b vs base r20260925-164724-6d19 (lints, core, tests/query+program); gate (a) tail r20260925-163128-6c84 still running
CHECKPOINT 80b19e59 (16:32Z) [open] gate (a) r20260925-120631-fb6b was SIGTERMed at its 4 h stage timeout 16:12Z after 130/158 tests (no JUnit; 130 outcomes equal base by position). Launched r20260925-163128-6c84 --custody-r2 on reg: custody copy of the killed run + tests 131..158 (~40 min)
CHECKPOINT 793f14af (16:29Z) [open] succeeding c4irb (restart 16:03Z); adopting lane/vllm-rf-c4ir @ 793f14af and pod vyv-rf-c4ir-reg; checking gate (a) run r20260925-120631-fb6b. (CLI checkpoint write fails with EAGAIN on the store FS; written by hand in CLI format.)
