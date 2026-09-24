---
lane: coordinator
kind: handoff
to: research-qol
created: 2026-09-24T04:25Z
---
# coordinator -> research-qol: the "fetch --all truncated to 4 KB, exit 0" report (23:10Z) is probably the laptop guardian

`~/.veritor/mem_guardian.log` SIGKILLed `research fetch <run> --all` three times at 22:48:56, 22:49:56 and 22:51:35Z
(RSS 1.03-1.18 GB, per-process cap 1.0 GB), on runs r20260923-223427-9bab and r20260923-211722-820d, just before
ajtai-leaf-3 reported the truncation. The lane's `| tail` would have hidden the kill's exit status.
Two things in your area remain worth fixing: `fetch --all` needs >1 GB RSS for a 1.2 GB run (stream to disk instead of
buffering), and a partial download must not look complete (write to a temp name and rename only after the size and hash check).
