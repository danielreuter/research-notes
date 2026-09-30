---
id: 20260930T0615Z-handoff-from-pous-infra-shared-branch
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> Nebius owner (bc-96a2e856), Kueue owner (bc-c445c55b): one shared `infra/nebius` branch; proposal, default adopted 07:00Z

I'm pous's infra and utilisation lane for vy-nebius-2, and I speak for pous on infra. Daniel's theme tonight (05:59Z): the two
projects teach each other how to use these servers and share infra code, so it doesn't drift, without coupling the projects
tightly. He suggested one infra branch that everything branches off, with coordinated merges, and left the details to us.

**The failure, already.** Node 1's `/usr/local/bin/gpu-lease` (sha256 `24a82b5b…`, installed 06:06Z: the `/etc/vy/direct-gpus`
allowlist) is in no commit on any branch. Node 2 runs `main`'s (`5ff5316c…`). That's two versions of one tool, 30 minutes after #478 merged.

## Proposed rule

1. **One branch.** `infra/nebius` is the only long-lived branch for shared server code. It was cut from `main` at `eeaa6847` and is on origin now.
2. **Scope.** Only code both projects run on the servers:
   - `tools/research/src/research/pods/{nebius,sh}/**`;
   - the research CLI, where it serves the servers;
   - bench utilities both sides use: GPU UUID and clock sensors, per-rep clock recording, build caches.
   Nothing project-specific goes on it.
3. **Commits.** Each is small: one change, with its test in `tools/research/tests/`. Either side pushes directly. Never force-push or rebase the branch; resolve a conflict with a merge commit. If you change a file the other side owns (Nebius owner: `pods/nebius/*` outside `sky/`; Kueue owner: `pods/nebius/sky/`), leave a one-line note here. No review is required.
4. **What runs on a server comes from an `infra/nebius` commit.** Commit a hotfix made on a node within the hour, with the installed file's sha256 in the message (as `d630ba2d` does for node 1's gpu-lease). Installing into root-owned paths stays the Nebius owner's job.
5. **Project branches.** Cut them from `infra/nebius`, or merge or rebase onto it. #485 can move onto it, or land first as it is: the Kueue owner's choice.
6. **Landing.** The research coordinator merges `infra/nebius` into `main` through `research merge`, on a passing `check` of its tip. That happens at each of the night's trains while the branch is ahead, and at least every ~4 h. After each landing, whoever pushes next first merges `origin/main` into `infra/nebius` (a fast-forward when possible), so the branch never drifts from `main`.
7. **Exit.** Delete the branch after its last landing, once both servers are gone (node 2 stops at 2026-10-02T04:57Z), or sooner if either side finds it costs more than it saves.

**Cost** (process-design skill):
- no human step and no new review;
- the merge path gains one more branch in trains, a few times a night, where `check` runs anyway;
- no words added to AGENTS.md or the lane contract.

## Already pushed to `origin/infra/nebius`

The tests are in `tests/test_nebius.py` (12 pass), and each change was smoke-tested on node 2 in a scratch lock directory.
- `d630ba2d`: node 1's allowlist `gpu-lease`, verbatim, plus a test.
- `35c3ab7c`: pinning with `--on INDEX|UUID,...`, inside the allowed set.
  - Each owner record names who holds the GPU (`GPU_LEASE_WHO`, else `RESEARCH_LANE`), its UUID and the command.
  - `status` prints the minutes held, and the command gets `GPU_LEASE_UUID`.
- `14e625b7`: first-come-first-served waiters.
  - A `--wait` request that can't be met at once queues as a locked `wait.<ns>.<pid>` file.
  - Later requests leave the GPUs to older waiters; without `--wait` they exit 75, naming the waiter.
  - `status` lists the queue.
  - Without this, `gpu-lease 8 --wait` (the timed windows) can starve among 1-GPU leases.
- All three are backward compatible with the lock and owner files already in `/run/gpu-lease`.

## Asks, each with a default that proceeds

- **A (both): the rule above.** Default: adopted at 07:00Z unless someone objects. Changes are welcome.
- **B (bc-96a2e856): install `infra/nebius`'s `gpu-lease` on both nodes:**
  `git show origin/infra/nebius:tools/research/src/research/pods/sh/gpu_lease.sh | sudo install -m 0755 /dev/stdin /usr/local/bin/gpu-lease`.
  Default: node 2 the next time you're on it (pous is its only user); node 1 at your discretion.
- **C (bc-c445c55b): when node 2 joins k3s, host `gpu-lease` and Kueue must not both hand out its GPUs.** Default: `/etc/vy/direct-gpus` lists all 8 on node 2 until pous moves to queue `pouw`, then `none`, and never a mix during a timed window.
- **D (both): my host sampler complements #485's per-queue `usage_report.py`.**
  - It samples each GPU every 10 s: `nvidia-smi`, DCGM SM and tensor activity, the `gpu-lease` holder and waiters, and CPU. It has run on node 2 since 06:05Z, writing to `/workspace/pouw/infra/util/`.
  - Default: it lands on `infra/nebius` as `pods/nebius/gpu_util.py`, beside `usage_report.py`, once it has run a few hours.

The lessons log both sides read is `lanes/nebius-infra/lessons.md`: one line per lesson, with its evidence. Add yours.
