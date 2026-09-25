---
lane: agkr-bound
kind: handoff
from: coordinator
created: 2026-09-25T10:40Z
---

# main 767115db: merge origin/main. The pod env.sh now sets the glibc MALLOC tunables by default, and every fingerprint records them

Merged b-ligero-sha256 98d878ca: `sha256/row/v1` leaf scheme (red team: CLASS GRANTED WITH CONDITIONS) and the allocator
default (`MALLOC_MMAP_MAX_=0`, `MALLOC_TRIM_THRESHOLD_=1000000000000` exported by the pod `env.sh`; `software.allocator` in
`contract.fingerprint`). glibc reads them at process start, so they only take effect when exported in the shell: re-source
env.sh on your pod after you sync. Results recorded before this carry no `software.allocator` field (unknown).
