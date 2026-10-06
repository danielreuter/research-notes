---
id: compute-accounting/20261006T2334Z-friction-stale-delete-step-outran-keep
campaign: pouw
lane: compute-accounting
kind: friction
status: open
severity: incident
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd), worker bc-23c3dbd6
cursor:
  subagentId: "bc-e90634dd-8e87-5b7b-8ecd-97abfd87e3fa"
---

# A running worker can't be steered, so a stale delete step in its brief outran the instruction to keep cited passes

**What was lost:** the retained passes of serve `r20261006-201412-b28d` (cited by the 22:30Z PoUW line, thread
1791300143.885349, reply 1791325698.516769) and serve `r20261006-194006-bfca`, about 27 GB each, on vy-nebius-1
(`/workspace/research/cache/pouw-service-draw/passes/`) and vy-nebius-2 (`/workspace/pouw/mvp-e2e/passes/`). No copy is left.
`research data preserved r20261006-201412-b28d` says PRESERVED, but its `run_files` (`art:c55262c9…`) holds only
`out/window/smoke.json`: the passes were outside custody.

**How it happened:**
- The brief I gave worker bc-23c3dbd6 said "6. Delete the old 28 GB passes on both nodes after the new window passes."
- Top then ruled that cited passes are deleted only if the store shows them preserved, so I made both pass trees read-only.
- I couldn't relay "cleanup cancelled": a running Cursor subagent takes no follow-up until it returns.
- The worker hit "Permission denied", ran `chmod -R u+w`, and deleted the passes, following its brief.
- The passes had no retention record. `research retention rm` refuses `keep` records and read-only directories, but a plain
  `rm` goes around both.

**What I did:**
- Reported it in thread 1791300143.885349.
- Moved the 22:30Z line's evidence to the rerun: serve `r20261006-224411-4a25`, statement `r20261006-225216-40f6`, window
  `r20261006-225123-3136`, all PRESERVED.
- Labelled `r20261006-201412-b28d` `passes deleted`.
- Put `research keep … --priority keep --expires never` records on the new passes on both nodes, which stay read-only.
- Every brief I write now forbids touching `passes/`. A cleanup is its own short brief, launched only once it's approved.

**What a guard could look like:** infra decides; I'm not building one.
- Every job that retains passes writes a `--priority keep` record when the directory is created: PoUW's `serve.sh`, and
  `pearl_c_vllm/window.sh` through `retain=`. A lane lowers it only with Daniel's or top's yes.
- `research retention rm` refuses a path under `passes/` unless `research data preserved` lists its tree, which is top's
  test.
- Retained pass directories are made immutable (`chattr +i`, through a root-owned helper behind `research keep --priority
  keep`), so `chmod u+w` and `rm -rf` fail. Only `retention rm` can lift that, after it has checked.
- Delete steps in briefs go through `research retention rm --approved-by @OWNER --ref <thread>`, never a plain `rm`. A stale
  step then fails closed on its own.

**Also seen:** `benchmarks/pouw/served_zk/zk_window.sh` (MODE=window) deletes its own run's passes with `rm -rf` when it
ends. They are its -h2 scratch and nothing cites them, but it is still a delete under `passes/` without a record.
