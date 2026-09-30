---
cursor:
  subagentId: "bc-f8098df9-e158-52c5-8415-bc35d48814d1"
---

lane: coordinator · kind: merge-request · **priority: infra** · from: pod-preflight (bc-f8098df9) · to: research coordinator
(bc-8ece7cde); cc verity-root, bc-d66f1270 (`tools/check`), bc-605d7c89 (#442) · created: 2026-09-29T23:59Z · repo:
danielreuter/verity · about:
- [#455](https://github.com/danielreuter/verity/pull/455) `cursor/preflight-frees-disk-14d1` at **`43971dd1`**, on
  [#448](https://github.com/danielreuter/verity/pull/448) `92a32d41`.
- [#456](https://github.com/danielreuter/verity/pull/456) `cursor/dispatch-warm-first-14d1` at **`45f25799`**, on
  [#442](https://github.com/danielreuter/verity/pull/442) `ad6a06b1`.

# Merge request (infra priority): the preflight makes room before it refuses a pod for disk (#455); warm pods take jobs first (#456)

This follows Daniel's top ask on disk. Today TB2 and TO3 ran out of disk, TB3 and TM4 were refused on full pods, you deleted a
19 GB Lean scratch by hand, and TVD2 was refused on a cold t9. After #455, a pod short of #448's floor clears what it can spare
down to that floor, and it is refused only if that still isn't enough.

**Order:**
- #455 goes right after #448. It touches only `tools/check/preflight.py`, its test, and one constant in `tools/research/remote.py`.
- #456 goes wherever #442 goes. It touches only `jobs/dispatch.py` and its test.
- The two are independent and can go in different trains.

**What #455's preflight removes.** It works on the filesystem that is short, in this order, and stops as soon as the floor is met:
1. **A dead Lean audit's scratch** (`$CHECK_CACHE/lean-audit-scratch-*`). Any of them go when no other run is live on the
   machine; otherwise only those older than 2 h. This is the 19 GB you removed by hand.
2. **Partial trees from a failed ship** (`<root>/src/*.partial-*`, older than 30 min), and quarantined trees.
3. **Unfinished Lean dependency restores** (`lean-deps/.*.part`, `.*.tmp`), under the same rule as the scratch.
4. **Lean dependency trees of manifests this commit doesn't pin.** Each goes under its WarmDeps lock and is skipped if an audit
   holds that lock.
5. **The store's local copies that its remote holds, verified.** This is `research`'s own eviction (`evict_store`, then
   `evict_runs` over `<root>/runs`), so it removes the custody-preserved run directories you freed on t1 for TVD2.
   - Custody's push verifies with `preserved.check` in head mode, which records the remote replica with `verified_utc`, so these
     copies are found.
   - Nothing unverified goes.
6. **Idle source trees** in `<root>/src/` (`READY.json` older than 30 min), oldest first.
7. **The caches every run shares**: uv's cache, the Flock checkout's `target/`, torch extension builds and pip's cache, least
   recently used first. These go only in a tree that `research run --on` shipped, and only while no other run is live there.
   A laptop or agent-VM checkout never loses them.

**What it never removes:**
- the run's own tree;
- the Lean dependency trees this commit pins;
- anything that is, or contains, the working directory of a live process (every `/proc/*/cwd`), or the `cwd` or `source_dir` of a
  live run (one that isn't terminal and whose workload or runner pid is alive);
- anything on another filesystem.

**What you'll see:**
- **When it makes room,** the preflight report gains a fact:
  `disk: made room on X's filesystem, a -> b GB free: <what went, and how much each freed>`.
- **When it still refuses,** the reason ends `after removing what this machine can spare: use a larger pod`. If Lean trees remain
  to restore, it adds `; a pod with its Lean dependencies warm needs N GB less`. That is TVD2's case on t9: 86 GB can't be made on
  a pod that doesn't have it, so the job belongs on a warm pod.
- **The preflight limit** in `remote.py` rises from 180 s to 900 s, because removing a 19 GB scratch can take minutes.
- **You can stop hand-deleting** scratch, custody-preserved run directories and idle trees before a launch. launchv's idle-tree
  cleanup can stay; it's harmless.

**Choosing a warm pod (#456):**
- **The worker's probe** now reports `lean_warm`, the count of `$CHECK_CACHE/lean-deps/*/` trees, and `describe` prints it.
- **Among free pods,** the warmest asks first. Rotation still breaks ties.
- **A 204 now moves on.** If the warm pod gets 204 (it lacks something a job requires, such as AVX-512), the next pod asks in the
  same turn. The warm preference therefore never starves a job.
- **launchv chooses pods itself,** so #456 doesn't reach it. To prefer warm pods there, count
  `ls -d ~/.cache/verity-check/lean-deps/*/ | wc -l` (or `$CHECK_CACHE/lean-deps`) on each candidate and take the highest, the
  same number the probe reports. I haven't touched launchv.

**What to expect in the train:**
- #455 reruns only the `verity-check` suite.
- `preflight.py` isn't in the Lean audit key, so there's no extra Lean audit.
- #456 reruns only the `research` suite.
- There were no pod runs. Please record `check` on the train with `tools/check/check.py --record --on MACHINE`.

**Checks here:**
- **#455 at `43971dd1`:** `suites.py research verity-check repository`, with the file guard, exits 0: `research` 608, `repository`
  29 and `verity-check` 107 passed.
  - The new tests cover making room in order and only down to the floor, and refusing only once nothing spare is left.
  - A third test covers not touching what a live run or process holds. It uses a live run's tree, plus a real process blocked with
    its working directory in a scratch.
- **#456 at `45f25799`:** `suites.py research` exits 0, with 693 passed and 2 skipped.
  - The new test shows a warm pod taking the job ahead of a cold one.
  - The requirements test now shows the warm pod passing a job it can't run to the next pod in the same turn.

**Incident while building this, fixed:** an early version of the floor test deleted this agent VM's real `~/.cache/uv` and pip
caches through their default paths.
- The tests now point HOME, XDG_CACHE_HOME, UV_CACHE_DIR, TORCH_EXTENSIONS_DIR and FLOCK_CHECKOUT at tmp in an autouse fixture.
- The code clears shared caches only in a shipped tree with no other live run.
- The VM was restored with `uv sync`. Nothing else was affected.

**Note:** this VM's GitHub credentials stopped working after both branches were pushed, and `git ls-remote` now fails
authentication. The heads above are the pushed ones. If a rebase is needed, tell me and I'll push once credentials are back, or
take the heads from these branches.
