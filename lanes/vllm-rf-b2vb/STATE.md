---
id: vllm-rf-b2vb/state
lane: vllm-rf-b2vb
kind: state
updated: 2026-09-25T14:40Z
---
# b2vb (one verdict and `properties/` records): state

> **Coordinator, 14:27Z: the vyv- pod deadline is now 2026-09-25T18:30Z (11:30 AM PT)**, extended in steps of at most 4 h while the coordinator runs. It replaces every earlier deadline line in this file.

> **Coordinator, 14:20Z: a4 is MERGED** (main `33e4d8d1`; its `integrations/vllm` and `packages/verity` trees are identical to `10996616`). Rebase now: `git fetch origin main && git rebase --onto origin/main 10996616 lane/vllm-rf-b2vb`, then `git push --force-with-lease`. Gate evidence gathered on 10996616 carries over unchanged, so record both heads in READY.md.

> **COORDINATOR, 12:26Z, URGENT (laptop disk):** no laptop-side fetch of run outputs; new runs with `--custody-r2`; inspect on the pod or from R2.

**STATUS: READY (14:40Z).** `READY.md` in this directory. **b2vb succeeds b2v** (agent bc-7d05cc29, hung at the 12:30Z host
disconnect). **Start commit `8d847755`** (`origin/lane/vllm-rf-b2v`). Agent bc-9bde181d; coordinator bc-ba6cec03. Worktree
`~/projects/verity-wt/rf-b2vb`, branch `lane/vllm-rf-b2vb`.

## Commits
- **Head `ed8f6625`** (pushed), = `8d847755` rebased onto main `33e4d8d1` (14:36Z, clean; `integrations/vllm` and `packages/verity`
  identical to `8d847755`). b2vb added no code commits; the 10 commits are b2v's (map in READY.md, Rebase notes).

## Spend
- L40S ~1.98 h x $1.09 + TP2 09:30Z-14:31Z ~5.0 h x $2.18 = **about $13.1 of $30**. No pods left.

## Done by b2vb (14:05Z-14:40Z)
- **#70 Commit** (`r20260925-111729-3301`, tree `66eaaa50`, PAIRS=1) ended 12:20:11Z: commit FAIL rc=1, pass False, tp run root
  `0b91229f06480ce4…`. Against f1's base Commit of record (`r20260924-221949-8668`, PAIRS=3) with b4's `cmp70.py`: **32/32 equal**
  (`evidence/cmp70-66eaaa50-vs-f1base.txt`); against the 09-22 record on the pod: roots equal, pre-v2 fields differ (`evidence/cmp70.txt`).
- **#70 from-record** (`evidence/fr70.txt`): base `10996616` = run tree `66eaaa50` byte for byte; head `8d847755` = that text plus
  one inserted `properties` block citing noninterference `442979b3…` ok. Outcome INSUFFICIENT_EVIDENCE on all three (TP rows have no
  commit/verdict.json; pre-existing).
- **#70 world 2** (`evidence/ni70.txt`): stored record ok, digest recomputes, rebuilt from the Match arms at the head = stored;
  worlds 3, 4 refused; `records_of(row)` = [noninterference 442979b3…, ok].
- **Custody**: 7 TP2 attempts pushed to R2 (`evidence/custody_tp2.sh`, laptop-minted delete-free key, deleted after 43 s); their
  logs, #70's row evidence (22 MB), gate outputs and pod scratch preserved by the `--custody-r2` run `r20260925-142514-883f`
  (`evidence/preserve.sh`; run record `art:b250b632…`, 207 files, PRESERVED sha256-readback). `vyv-rf-b2v-tp2` terminated 14:31Z by
  `research pods drain` ("all 8 attempt(s) preserved").
- Removed b2v's two clean /tmp worktrees (`/private/tmp/b2v-66e` at 66eaaa50, `/private/tmp/b2v-base` at 10996616; both on
  origin; ~490 MB). b2v's other /tmp files and its `rf-b2v` worktree untouched.
- Rebased onto main and pushed with `--force-with-lease` (`8d847755` -> `ed8f6625`).

## Running
- nothing

## Open questions
- none

## Found, not fixed
- In READY.md. New from b2vb: TP rows have no `commit/verdict.json`, so `from_record` gives INSUFFICIENT_EVIDENCE there (a5's TP
  pipeline / heredoc); `research data custody --triage` suggests a `custody waived` label the store vocabulary refuses.
