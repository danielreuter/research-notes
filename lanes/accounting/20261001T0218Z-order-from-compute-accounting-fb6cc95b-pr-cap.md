---
id: 20261001T0218Z-order-from-compute-accounting-fb6cc95b-pr-cap
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For the PoUW PR steward (bc-fb6cc95b): the PR cap, and how we get under it

From compute accounting, 7:18 PM PDT. Daniel approved this at 7:08 PM PDT.

**The cap.** Compute accounting and its lanes, including the migrated old PoUW work, keep at most about 10 open PRs that
aren't records. Stacked PRs count one by one. When we're over the cap, land or close a PR before opening another one. The
repository's targets are at most 110 open PRs by 8:05 PM, 90 by 10:05 PM and 60 by 2:05 AM PDT. Ours are at most 25 by
10:05 PM and at most 10 by 2:05 AM.

**Done at 7:18 PM PDT.** I closed 11 PRs, keeping their branches, each with a comment. That leaves us 36 open.
- Records: #542 (Pearl-C4 v4, rejected), #530 (FP4 emulation, parked), #464, #468 and #475 (the RTX 4090 hashing cut, parked),
  #332 and #436 (their rule is already practice), #533 (`-h3`, which waits on RowSeed and then Daniel) and #529 (it has no base
  PR).
- Contained in another PR: #505 is an ancestor of #507, and #532 is an ancestor of #572.
- I did **not** close #591. Its commit `58db3429` (`forms_table.py`) isn't in #610.

**The PR captain** is a new worker in this Project. It feeds ready trains to the research coordinator and preps conflicted
merges on its own branches; it never pushes to ours. When one of our PRs is ready (clean, with a passing recorded `check`
of its head), write `lanes/coordinator/<stamp>-handoff-from-compute-accounting-pr-captain-<prs>-ready.md`. For the format,
see `note:20261001T0214Z-handoff-from-proofs-pr-captain-630-212-ready`.

**The order of work:**
1. **Pearl-C train.** #449 → #548 → #534 → #556 → #602, on check `r20261001-020451-3aec` of #602's tip. Hand it to the captain
   when the check passes, then land #580 after it. That's 5 PRs now and 1 later.
2. **The NCP roots.** #433 (its check is recording), then #389, then #435. Also #567. That's 4 PRs.
3. **The kernel skill.** Land #577, and fold #595 into it or land #595 right after.
4. **The harness.** Rebase #491 (the conflict is in `test_store_vocab.py`) and land it. Then fold #588 and #590 into one
   harness PR, and #543 and #570 into one mainloop PR.
5. **The served-MVP tail**, once window 8's results are preserved. The port's deadline is 9:30 PM PDT; don't touch the
   served branches before then. Collapse #540 → #564 → #573 → #576 → #578 → #585 → #593 → #596 → #610, plus #572, #589 and
   #591's commit `58db3429`, into one PR per milestone. Then close the tail as contained in it.
6. **#471.** If you open the rebased PR, close #471 in the same step, so the count doesn't grow. Otherwise park it as a
   record (backlog F5).
7. **Evidence PRs.** bc-0f3f8a2f's running search uses #506, #507 and #451. Close them as records when it ends. For #492 (W1),
   #525 and #545: land each one only if a milestone needs its tooling. Otherwise close it as a record when its owner finishes.

Checkpoint one line in `lanes/pouw-prs` at each land or close, with our open count.
