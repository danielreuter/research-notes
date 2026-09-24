# Laptop at 3.1-3.4 GB free, under mem_guardian DISK_FLOOR 3.5 GB: every `research run --on --source .` launch is killed

- mem_guardian kills the largest lane Python > 256 MB whenever free disk < 3.5 GB. `research run --on vy-merge-postwave --source .`
  (0.64 GB while shipping) was killed at 16:55:48Z, leaving r20260924-165536-47d1 in phase `shipping`; `research data evict`
  (0.28-0.32 GB) was killed twice at 16:49-16:50Z, and printed nothing.
- `research data evict --target-free-gb 8 --runs --dry-run` finds only ~70 MB evictable (4.8 GB held back as unpreserved).
- Big non-lane items I did not touch: /tmp/rl-trial 218M, /tmp/tpv2trial 173M, /tmp/rl-dry 166M, /tmp/rl-moved3.tar 163M;
  ~/Library/Caches/com.openai.codex 1.4G; Cursor state.vscdb ~72 GB and growing.
- merge-postwave is working around it with `research pods sync` + `research run --cwd /workspace/src` (no archive). Other lanes
  launching with `--source .` will hit the same kill until disk is above 3.5 GB.
