---
lane: coordinator
kind: handoff
from: vllm-57-fix
created: 2026-09-24T07:58Z
---

# vllm-57-fix -> coordinator: laptop disk is at the guardian's 3.5 GB floor and falling ~85 MB/min; laptop `research` launches are SIGKILLed

- `~/.veritor/mem_guardian.log`: free disk 3.8 GB (07:43Z), 3.6, 3.3, 3.2 GB (07:50Z); `cursor_db` grew 69.46 -> 69.69 GB meanwhile.
  At 07:52Z it killed my `research run --on vyv-sw-57` launcher (0.57 GB, "disk floor 3.2GB free"). Any lane's laptop Python dies the same way.
- `research data evict --target-free-gb 8` freed only 0.23 GB (7 evictable blobs); `uv cache prune` found nothing. I did not touch
  others' files: `/private/tmp/rl-moved3.tar`, `~/.research/runs` (5.7 GB, not mine), `~/Library/Caches/com.openai.codex` (1.4 GB).
- At this rate the disk is full in about 40 min. The growth is Cursor's own DB, which may also be behind the Cursor crashes.
- Ask: free disk space (Daniel / coordinator decision on which caches or run records go). My #57 Commit rerun at 2c5e038b is waiting on it.
