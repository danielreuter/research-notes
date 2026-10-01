---
id: 20261001T0956Z-review-from-infra-496-fences-fix
campaign: overnight-sep30
lane: coordinator
kind: report
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1); review of the PR captain's fences heads (top-level 2:48 AM PDT)
---

# Review: the `fences` fixture fix (1e85d9ad5, and the same commit on the 645, 647 and 649 heads) is correct. Approve

to: the PR captain.

- **Reproduced and fixed.** I held one blocked flock waiter in `/proc/locks` (`1: -> FLOCK ADVISORY WRITE <pid> ...`) and ran
  `tests/test_nebius.py -k n1_lease`:
  - #496's old head `025260083`: 6 passed, **6 errors** at teardown. That's T496R's failure.
  - The fixed head `1e85d9ad5`: **6 passed**.
- **Production code is fine.** `n1_lease.lock_holders` and `cluster.nebius2.locked` keep only lines where `f[1] == "FLOCK"`, so
  they skip waiter lines. That's correct: a waiter doesn't hold the lock. Only the fixture parsed `split()[4]` blindly.
- **Non-blocking follow-up (don't re-cut for it).** The fixture still reads `/proc/<pid>/cmdline` twice after an `exists()`
  check. A lock taker that exits in between raises `FileNotFoundError` or `ProcessLookupError` at teardown. That's the same flake
  class, and it's plausible on node 1's busy check host, though the window is microseconds. I'll fold a `try/except OSError` into
  the next infra PR after these land.
- **#650 and #662 are still on #647's old head** (`be2b1e674`). They carry the old fixture. Once the fences heads land, I'll merge
  `main` into both.
