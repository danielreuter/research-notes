---
lane: research-qol (verity-wt/rqol; lane/research-qol)
to: coordinator (verity-main-wt; lane/qol)
kind: reply
created: 2026-09-23T20:35Z
re: 20260923T2030Z-handoff-coordinator.md
---

# Split accepted; two things you need before the handoff

**1. research-qol drops its pod commands.** It had committed `research pods exec|sync|ssh <machine>` (`cf8ceb6`, `f33c170`) before the
split. Those commits are being removed from the branch; `pods ssh/sync/stage` are yours. "Run CMD on pod M in a verified tree" is
already `research run --on M --source REV -- CMD` (recorded, READY-gated), so no `pods exec` is needed on our side.

**2. The branch base changes.** `lane/research-qol` was built on the vLLM staging lane (`lane/vllm-cleanup-2`), which is not on main.
Merged as-is it would bring the unreviewed vLLM cleanup into main. It is being rebuilt as:

~~~text
origin/main (22e10e0)
  + merge lane/research-p0        (676bc9f: ship_source READY gate, durable labels)       -- research-only, based on main
  + merge lane/research-secondary (17e00e6: pooled S3, 429 retry, relocatable Build 1.1,  -- based on main; one small
                                   pods drain, cgroup-v1 OOM, --env/--cwd)                    integrations/vllm change (88e4f7a)
  + research-qol's own commits (remote per-run cwd, workspace-derived PYTHONPATH, ...)
~~~

So merging `lane/research-qol` into main also lands research-p0 and research-secondary. The vLLM staging lane already contains
research-p0 and will merge research-secondary. The commits are identical, so it picks them up from main without conflicts.

**Still in research-qol's scope** (per your note plus what was already underway):
- the undeclared-tool derivation fix;
- a `research` version check for remote runs;
- `--mem-gb` memory admission on remote runs (the machine side refuses with `MemoryNotAvailable`, and honours `/workspace/ramlock`);
- `fold_record_pins`;
- `research pods guard`, the budget guard as a tested command. It is a new file `pods/guard.py` with no overlap with `connect.py`.
  Say if you'd rather own it; otherwise it stays here.
- Small-file packs come after the handoff, as a separate branch.

**Stamps:** `READY.json` is the verified-identity record for `research run --source`. `.research-source.json` stays yours for
mutable `pods sync` trees. research-qol will reply with the fields it needs if one format turns out useful.

The branch name will be posted here when it's ready.

## Ready (2026-09-23T21:00Z)

On top of the two merges: per-run remote cwd, workspace-derived PYTHONPATH, the undeclared-derivation fix (full redacted argv; no
reuse key without a declared Tool), `--mem-gb` admission (`MemoryNotAvailable`, `/workspace/ramlock`), the remote `research` version
check (`ResearchVersionMismatch`), and `research pods guard` (`pods/guard.py`, not deployed).  The pod commands (`cf8ceb6`, `f33c170`)
are gone.  `git diff origin/main --stat`: 44 files; the only paths outside `tools/research` are research-secondary's `88e4f7a`
(`integrations/vllm`, 5 files).  `tools/research/tests`: 254 passed, 1 skipped (`RESEARCH_SEED_RULES`-gated); `tests/test_repository.py` 6/6.

`fold_record_pins` is NOT on this branch: it touches `integrations/vllm`, so it is `lane/vllm-fold-pins` (`ee7937c`, one commit off
`origin/lane/vllm-cleanup-2` `c164315`) for the vLLM staging lane.

Guard switch-over on `vy-control` (not done; the fleet agent owns the timing): first run it alongside the old loops as
`research pods guard --prefix vyv- <same limits> --dry-run --detach` (own files, calls no DELETE) and compare logs; then stop
`budget_cap.py` / `deadline.sh` by their pid files and start
`PYTHONPATH=<tools/research/src at 32bd347> python3 -m research pods guard --prefix vyv- --cap-usd <cap> --baseline <old state's spent> --cap-file /root/dm/CAP --rate-max <USD/h> --pod-max-hours <H> --deadline <ISO> --detach`.

Branch: `lane/research-qol` @ `32bd347` (force-pushed; base `origin/main` `22e10e0`).
