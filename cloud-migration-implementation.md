---
cursor:
  subagentId: "bc-21aca6c8-631a-51fd-8553-ad0d0947ad11"
---

# Cloud migration: implementation notes (steps c, h, d, a + stale-binary fix)

Spec: `docs/cloud-migration-requirements.md`. One PR per step against `main` in `danielreuter/verity`; none merged by me.
Test baseline on a cloud VM: the 4 known `main` failures (plus `test_sync_ships…[rsync]` if the VM lacks rsync;
`test_d6_deferred_hash…` is flaky and sometimes passes).

| Step | PR | Branch |
|---|---|---|
| (c) credentials from env | [#2](https://github.com/danielreuter/verity/pull/2) | `cursor/research-env-credentials-ad11` |
| (h) push rule | [#3](https://github.com/danielreuter/verity/pull/3) | `cursor/lane-push-rule-ad11` |
| (d) remote-first catalog | [#4](https://github.com/danielreuter/verity/pull/4) | `cursor/remote-first-catalog-ad11` |
| (a) notes sync | [#5](https://github.com/danielreuter/verity/pull/5) | `cursor/notes-sync-ad11` |
| stale Rust binary + binary provenance | [#6](https://github.com/danielreuter/verity/pull/6) | `cursor/ship-source-extract-mtime-ad11` |
| parity hang fix (deadlines, no evicted-blob downloads, progress) | [#8](https://github.com/danielreuter/verity/pull/8) | `cursor/parity-no-hang-ad11` |
| (b) git objects to pods | [#9](https://github.com/danielreuter/verity/pull/9) | `cursor/ship-git-objects-ad11` |

Switch-over runbook: `docs/cloud-switchover-runbook.md`. #2–#6 were merged by 6:00 PM PT; #8 and #9 were opened ready at about 6:45 PM PT.

## (c)

C1 passed live from a cloud VM with only the Cursor secrets (about 3:30 PM PT): `pods list`, `pods ssh 9tnzjcc6iygyv0 -- true`,
`data verify art:4f8e9ff8…` PRESERVED, `mint-credential --ttl 10m --permission object-read-only`. C3 scan: only the mode-600 key file.
The secret scanner blocks committing the bucket name, so the env fallback checks `R2_BUCKET` against the tracked `store.pod.toml`.

## (h)

Proposed text for `~/.research/notes/kb/LANE-CONTRACT.md` (apply at switch-over; not reachable from a cloud VM):

~~~text
Push after every commit: `research notes push <you>` sends lane/<you> (or your bound branch) to origin. Never push main,
never --force; a rejected push means someone else pushed your branch: fetch, rebase or merge origin/<branch>, push again.
FINAL: `research notes checkpoint <you> final --require-pushed`.
Coordinator: merge lanes from origin (`git fetch origin lane/<x>`, merge `origin/lane/<x>`), not from local branches.
`research notes branches --fetch` lists open lanes whose work origin lacks (BLOCKING) and the unpushed/ahead triage list.
~~~

Branch triage (the 163 unpushed branches), on the laptop from `~/projects/verity-main-wt/main`, once #3 is merged:
`research notes branches --fetch --json > /tmp/lane-branches.json`, then `research notes branches` for the table.

## (d): the laptop parity run (D4)

Read-only for `~/.research/store`, except that `--render` opens the catalog and may cache blobs, as the daily render already does.
It needs about 0.5 GB free in `/tmp`. Live from a cloud VM: a full build took 161 s, and parity with the render took 144 s.

~~~bash
cd ~/projects/verity-main-wt/main
git fetch origin cursor/remote-first-catalog-ad11
git worktree add --detach /tmp/parity-wt origin/cursor/remote-first-catalog-ad11
cd /tmp/parity-wt && uv sync -q
set -a; . ~/.config/verity/r2.env; set +a
STAMP=$(date -u +%Y%m%dT%H%MZ)
uv run research data parity --store ~/.research/store --fresh /tmp/parity-fresh-$STAMP --render --json-out /tmp/parity-$STAMP.json
echo "exit $?"
# afterwards: keep /tmp/parity-$STAMP.json (evidence), then
cd ~ && git -C ~/projects/verity-main-wt/main worktree remove /tmp/parity-wt && rm -rf /tmp/parity-fresh-$STAMP
~~~

Exit 0 means PARITY OK. The last lines name every unexplained difference, and the JSON lists every difference with its cause.
D7 needs two passes at least a day apart; use a new `--fresh` directory each time.

## (a): switch-over steps (after the current lanes finish; not done)

1. Daniel creates the private, empty repo `danielreuter/research-notes`. It did not exist at 3:55 PM PT, and my GitHub access is read-only.
2. On the laptop: `research notes scan --root ~/.research/notes` must print nothing (A5, before the first push). Then
   `git -C ~/.research/notes remote add origin git@github.com:danielreuter/research-notes.git && git -C ~/.research/notes push -u origin HEAD:main`.
3. Restart the watcher with `--sync` instead of `--snapshot`. Cloud agents set `RESEARCH_NOTES_SYNC=1` and clone the notes to `~/.research/notes`.
4. Replace contract §K ("never run git there") with: "after writing notes, `research notes sync` (checkpoint/bind/relaunch do it
   when `RESEARCH_NOTES_SYNC=1`); exit 3 = conflict, resolve the named file and sync again".

The test suite's git calls sometimes stall for seconds on this VM (I/O), so the A2 test takes 0.5 s to 120 s; single git calls are about 10 ms.

## Stale Rust binary (#6)

The fix is `tar -xmf` in `ship_source`. The reproducing test fails without the fix. Binary provenance: `python -m research.binprov record`
writes `BINARY.provenance.json`, and every run records job.json `run.binaries` (recorded / stale / missing). The SP1, sec128 and
Ligero bootstraps record after installing. Hand builds show as `missing` until someone runs `record`.
