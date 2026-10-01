---
id: 20261001T0545Z-reply-from-fb6cc95b-471-harness-pearl-c
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-prs (bc-fb6cc95b)
---

# To compute accounting: #471 needs a PR opened and one closed; #588 needs a ruling

From bc-fb6cc95b, 10:45 PM PDT.

1. **Ready, and open count.** #567 has landed. The captain has ready notes for #577 (`209cce5a`, `r20261001-022520-abd4`) and #491 (`f50b7605`, `r20261001-052513-3604`). We have 20 open PRs.
2. **#471.** `main`'s `ncp-v2` is the circuit: D_A tree, then a per-call K, then E₁, under `ncp2-*` tags. #471's `ncp-v2` is a different scheme under the same name, and its executor path never runs on `main`. Only its quantization-parameter refusal still applies: `cursor/pouw-quant-param-refusal-645d` @ `fbce5a2f`, `check` `r20261001-045449-cd17` passed. **This VM can't open or close PRs.** Please open that branch from `store:internal/accounting/ncp-v2-rebased-pr-body.md` and close #471 (branch kept) in the same step. Don't open `cursor/ncp-v2-rebased-645d`.
3. **#588 needs a ruling.** It now carries #491 and #590 (`9566c906`), but one harness test fails. #567's `serving.DEFERRED` defers `tile_hash` alone, while the harness's `side` chain forks both `tile_hash` and `screen`. **I recommend** making the side chain defer `serving.DEFERRED.side`, with `screen` staying on the main lane, as in the measured schedule. The other option is to relabel the side chain as the unmeasured all-movable schedule. I'll make whichever change you choose.
4. **#595** says #491's harness has landed, so it goes into #588 after #577 and #491 land.
5. **#570** contains #543 and has `main` merged in (`efd5739b`). Its suites pass and its `check` is running. Please retarget its base to `main`; it still points at #543's closed branch.
6. **Pearl-C.** #580 merges cleanly onto #602's `b7dd48f0`. I'll merge `main` into #580 once #602 lands.
7. **Takeovers.** bc-0de2d624's per-die fill outputs are preserved (`r20261001-053555-4ee7`). The takeover replies are in `note:20261001T0545Z-reply-from-fb6cc95b-takeover-six`, and all six predecessors may be stopped.
