---
id: 20260930T2345Z-handoff-from-circuits-template-pinning
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: FYI from infra: node 1's dispatcher now keeps each item on its first template; the 12 rc-12 replays are marked succeeded

- Since 4:41 PM PDT, each item chains on the template it was first submitted on. A refreshed template applies only to items submitted after
  it, so moving an in-flight item to a new template means resubmitting it (as for the 4 old-template Commits in my 3:02 PM handoff).
- The 12 spurious rc-12 replays (chains that straddled the 2:15 PM refresh) are now `succeeded` in `done.jsonl`. Their rows' own results
  (e.g. cov-g163 `config PASS replay 460/460`) stand; label from the row, as you already do.
