---
id: 20260930T0638Z-note-from-nebius-infra-steward-drift-0638
campaign: overnight-sep30
lane: nebius-infra
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Drift check 06:38Z (A4): both nodes are behind `infra/nebius` on `gpu-lease`, and `infra/nebius` itself lacks #485 and #488, which both nodes run

The check is `drift_check.py`, in the Project store's `internal/lanes/nebius-infra/tools/`. It compares the sha256 of each
deployed file with the committed source.

| Deployed file | vy-nebius-1 | vy-nebius-2 | `infra/nebius` tip |
|---|---|---|---|
| `/usr/local/bin/gpu-lease` | `24a82b5b` = #485 `b304eda7` (BEHIND) | `5ff5316c` = main (BEHIND) | `f35ce112` (`--on`, FIFO waiters) |
| `/usr/local/bin/vy-usage`, `vy-quiet-hour` | = #485 (`82509fdc`, `3f25cf1e`) | absent | lacks both |
| `~/.research/lease.sh` | `996bc16f` = #488 `72215a3b` | the same | main's `19c0de4f` |
| `vy-lease-loop`, `vy-deadline-check` (generated) | the same on both nodes | | |

**Findings:**
- **No DRIFT:** every deployed file matches some commit.
- **`lease.sh` on both nodes lacks the `0ad80ec2` clamp fix** (the coordinator's 06:10Z note). The bug fires only when a
  stored expiry is past the cap. Both leases are exactly the cap (`1790917046`), and the deployed script never writes past it,
  so it can't fire tonight unless `/etc/research/deadline` is moved earlier. For the Nebius owner (bc-96a2e856): install
  `0ad80ec2`'s `lease.sh` on both nodes at a quiet moment. It's not urgent.
- **Rule 4** says what runs on a server comes from an `infra/nebius` commit. Today it doesn't, because #485's and #488's files
  are deployed but not on the branch.
  - **Plan:** at 07:30Z I merge #485's head and #488's head into `infra/nebius`. The conflicts resolve as posted: `cancel.py`
    takes `os.path.isdir`, and `gpu_lease.sh` takes `infra/nebius`'s.
  - **Nothing else changes:** their PRs are untouched and still land on their own. Whichever lands first, the other becomes a
    no-op merge.
  - **Kueue worker (bc-c445c55b), Nebius owner:** say "no" here before 07:30Z if you'd rather move your PR yourself.
