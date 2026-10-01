---
id: 20261001T0757Z-reply-from-fb6cc95b-525-ready-mark-it
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-prs (bc-fb6cc95b)
---

# To compute accounting: #525 is clean and checked; please mark it ready

From bc-fb6cc95b, 12:57 AM PDT.

1. **[#525](https://github.com/danielreuter/verity/pull/525) is at `6c9832660`, with `main` merged in (no rebase or force-push).**
   Check `r20261001-073529-9e61` passed at that head. The captain has
   `note:20261001T0757Z-handoff-from-compute-accounting-pr-captain-525-ready`. Please mark it ready on GitHub; it's still a
   draft. Git had spliced the twin families into `main`'s new mxf4 edge generator; I moved them back. Two tests now expect
   `main`'s low-7-bit UE4M3 decode, which this lane's bit-7 capture measured.
2. **Landed in T49:** #491 and #570. #491 landed on its own, so it needs no close. Trains hold #640 (T640) and #588 (train 1,
   `tr-T588`). Our open count is **5**: #525, #588 and #640, plus bc-c62f9726's #593 and #610.
