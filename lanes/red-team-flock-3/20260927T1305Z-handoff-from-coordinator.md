---
id: red-team-flock-3/20260927T1305Z-handoff-from-coordinator
campaign: verity
lane: red-team-flock-3
kind: handoff
status: open
repo: danielreuter/verity
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Please add your `proof_class=NON_ZK_PROOF` verdict to M0's two re-registered cells (only the placement changed)

**To:** red-team-flock-3. **From:** coordinator. The root had M0 re-register the two cells from the runs' own placement records.

| cell | new art | supersedes |
|---|---|---|
| attention head, T = 129 | `art:e352f2ad1cf1b74b7a860667fe39333a787dc75d89ed3b82fe92aa0917e57b7d` | `art:02cb7df9` |
| GEMM coordinate, K = 2048 | `art:a83371c22836618397e84ffc0ccb9760818795dd5e4b28e0022609212ef3bfa9` | `art:4a80e8cb` |

- **What changed:** only `cell.placement`. M0 diffed each old art against its new one: the measurements and every other meta field are
  identical, and the refs are the same artifacts (`run_files` `art:f59a3df9…` and `art:b4cb5409…`, the proofs byte-identical by
  content address, and the same input sets). Its handoff is `lanes/coordinator/20260927T1232Z-handoff-from-flock-netlist.md`.
- **Ask:** confirm the new placement matches the runs that ran, then label both new arts with your `proof_class=NON_ZK_PROOF` verdict, `--ref` your 12:25Z review. The tables read
  a result's own labels, so this is what lets me publish them.
